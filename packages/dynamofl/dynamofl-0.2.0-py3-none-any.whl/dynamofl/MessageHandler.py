import ssl
import json
import logging
import os
import pathlib
import queue
import shutil
import threading
import traceback
import zipfile

import requests
import websocket

from .api.ProjectAPI import ProjectAPI
from .Datasource import _Datasource
from .Request import _check_for_error
from .State import _State
from .file_transfer.download import FileDownloader

logger = logging.getLogger("MessageHandler")

RETRY_AFTER = 5  # seconds


class _MessageHandler:
    def __init__(self, state):
        self.token = state.token
        self.wshost = state.host.replace("http", "ws", 1)
        self.state: _State = state

        self._project_api = ProjectAPI(self.state.request)
        self.task_queue = queue.Queue()

        self.ws = websocket.WebSocketApp(
            self.wshost,
            on_open=self._on_open,
            on_message=self._on_message,
            on_close=self._on_close,
            on_error=self._on_error,
        )

        self.handlers = {
            "client-info": self.client_info,
            "round-complete-test": self.state.test_callback,
            "round-complete-train": self.state.train_callback,
            "dynamic-trainer": self.dynamic_trainer,
            "round-error": self.round_error,
        }
        self.worker_handlers = [
            "client-info",
            "round-complete-train",
            "round-complete-test",
            "dynamic-trainer",
        ]

    def connect_to_ws(self):
        t = threading.Thread(
            target=self.ws.run_forever, kwargs={"reconnect": RETRY_AFTER, "sslopt": {"cert_reqs": ssl.CERT_NONE}}
        )
        t.daemon = False
        t.start()

        worker_t = threading.Thread(target=self._worker)
        worker_t.daemon = True
        worker_t.start()

    def _worker(self):
        while True:
            task = self.task_queue.get()
            try:
                logger.debug(
                    "Processing task '{}' for project '{}'".format(
                        task["event"], task["project_key"]
                    )
                )
                self.handlers[task["event"]](task["j"], task["project_key"])
            except Exception:
                logger.error(traceback.format_exc())
            self.task_queue.task_done()

    def _on_open(self, ws):
        logger.info("Connection to DynamoFL established.")
        payload = {
            "event": "auth",
            "data": {"token": self.token},
        }
        self.ws.send(json.dumps(payload))

    def _on_message(self, ws, res):
        j = json.loads(res)

        project_key = None
        if "data" in j and "project" in j["data"] and "key" in j["data"]["project"]:
            project_key = j["data"]["project"]["key"]

        if j["event"] in self.handlers:
            if j["event"] in self.worker_handlers:
                self.task_queue.put_nowait(
                    {"event": j["event"], "j": j, "project_key": project_key}
                )
            else:
                self.handlers[j["event"]](j, project_key)

    def _on_close(self, ws, close_status_code, close_msg):
        logger.info("Connection closed")
        logger.info(close_msg)

    def _on_error(self, ws, error):
        logger.error("Connection error:")
        logger.error(error)
        logger.error(f"Will attempt to reconnect every {RETRY_AFTER} seconds...")
        all_callbacks = self.state.error_callbacks
        # call all error callbacks
        for callback in all_callbacks:
            callback(msg=f"Connection error: {error}")

    """
    Message Handlers
    """

    def client_info(self, j, _):
        self.state.instance_id = j["data"]["id"]
        for ds in self.state.datasources.values():
            self.state.update_datasource(key=ds.key)
            ds.add_existing_trainers()

    def dynamic_trainer(self, j, project_key):
        if os.path.isdir(f"dynamic_trainers/{project_key}"):
            return
        # used to handle cases where the user only has access to a subset of datasources
        params = {
            "projectKey": j["data"]["project"]["key"],
        }

        filename = j["data"]["filename"]
        filepath = f"dynamic_trainers/{project_key}_{filename}"
        directory = os.path.dirname(filepath)

        file_downloader = FileDownloader(self.state.request)
        file_downloader.download_file(
            file_path=filepath,
            presigned_endpoint_url="/dynamic-trainers/presigned-url-download",
            params=params,
        )

        with zipfile.ZipFile(filepath, "r") as zip_ref:
            parent_dir_name = os.path.dirname(zip_ref.namelist()[0])
            zip_ref.extractall(directory)
        shutil.move(directory + "/" + parent_dir_name, directory + "/" + project_key)
        os.remove(filepath)

    def round_error(self, j, project_key):
        msg = f"Federation error occured:\n  {j['data']['errorMessage']}"
        logger.error(msg)
        all_callbacks = self.state.error_callbacks
        # call all error callbacks
        for callback in all_callbacks:
            callback(msg=msg)
