import base64
import hashlib
import logging
import os
import pathlib
from io import BufferedReader

import requests

from ..Request import _Request
from ..file_transfer.upload import FileUploader, ParamsArgs
from ..file_transfer.download import FileDownloader
from ..file_transfer.sha import calculate_sha1_hash_base64

logger = logging.getLogger("ProjectAPI")


class ProjectAPI:
    def __init__(self, request: _Request):
        self.request = request

    def create_project(self, params=None):
        res = self.request._make_request("POST", "/projects", params=params)
        if not res:
            raise Exception("No response")

        return res

    def get_info(self, key):
        return self.request._make_request("GET", f"/projects/{key}")

    def get_projects(self):
        res = self.request._make_request("GET", "/projects", list=True)
        if not res:
            raise Exception("No response")

        return res

    def complete(self, key):
        return self.request._make_request(
            "POST", f"/projects/{key}", params={"isComplete": True}
        )

    def update_rounds(self, key, rounds):
        return self.request._make_request(
            "POST", f"/projects/{key}", params={"rounds": rounds}
        )

    def update_schedule(self, key, schedule):
        return self.request._make_request(
            "POST", f"/projects/{key}", params={"schedule": schedule}
        )

    def update_paused(self, key, paused):
        return self.request._make_request(
            "POST", f"/projects/{key}", params={"paused": paused}
        )

    def update_auto_increment(self, key, auto_increment):
        return self.request._make_request(
            "POST", f"/projects/{key}", params={"autoIncrement": auto_increment}
        )

    def update_optimizer_params(self, key, optimizer_params):
        return self.request._make_request(
            "POST", f"/projects/{key}", params={"optimizerParams": optimizer_params}
        )

    def update_contributor(self, key, email, role):
        return self.request._make_request(
            "POST", f"/projects/{key}/contributors/{email}", params={"role": role}
        )

    def set_dynamic_trainer(self, key, dynamic_trainer_key):
        return self.request._make_request(
            "POST",
            f"/projects/{key}/files/dynamic-trainers",
            params={"dynamicTrainerKey": dynamic_trainer_key},
        )

    def delete_project(self, key):
        return self.request._make_request("DELETE", f"/projects/{key}")

    def add_contributor(self, key, email, role="member"):
        return self.request._make_request(
            "POST",
            f"/projects/{key}/contributors",
            params={"email": email, "role": role},
        )

    def delete_contributor(self, key, email):
        return self.request._make_request(
            "DELETE", f"/projects/{key}/contributors", params={"email": email}
        )

    def get_next_schedule(self, key):
        return self.request._make_request("GET", f"/projects/{key}/schedule")

    def increment_round(self, key):
        return self.request._make_request("POST", f"/projects/{key}/increment")

    def get_rounds(self, key):
        return self.request._make_request("GET", f"/projects/{key}/rounds", list=True)

    def get_round(self, key, round):
        return self.request._make_request("GET", f"/projects/{key}/rounds/{round}")

    def get_stats(self, key, params={}):
        return self.request._make_request(
            "GET", f"/projects/{key}/stats", params, list=True
        )

    def get_stats_avg(self, key):
        return self.request._make_request("GET", f"/projects/{key}/stats/avg")

    def get_submissions(self, key, params={}):
        return self.request._make_request(
            "GET", f"/projects/{key}/submissions", params, list=True
        )

    def upload_optimizer(self, key, path):
        with open(path, "rb") as f:
            self.request._make_request(
                "POST", f"/projects/{key}/optimizers", files={"optimizer": f}
            )

    def upload_file(self, key, path):
        with open(path, "rb") as f:
            self.request._make_request(
                "POST", f"/projects/{key}/files", files={"file": f}
            )

    def upload_dynamic_trainer(self, key, path):
        with open(path, "rb") as f:
            self.request._make_request(
                "POST", f"/projects/{key}/files/dynamicTrainer", files={"file": f}
            )

    def report_stats(self, key, stats):
        return self.request._make_request(
            "POST", f"/projects/{key}/stats", params=stats
        )

    """
    Bridge APIs
    """

    def create_bridge(self, project_key, params):
        return self.request._make_request(
            "POST", f"/projects/{project_key}/bridges", params=params
        )

    def get_bridge_of_project_and_datasource(self, project_key, datasource_key):
        res = self.request._make_request(
            "GET",
            f"/projects/{project_key}/bridges",
            params={"datasourceKey": datasource_key},
        )
        if not res:
            raise Exception("No response")

        return res

    """
    Moved from Projects
    """

    def pull_model(
        self,
        project_key,
        filepath,
        datasource_key=None,
        round=None,
        federated_model=None,
    ):
        params = {"usePresignedUrl": True}
        if round is not None:
            params["round"] = round
        if federated_model is not None:
            params["federatedModel"] = federated_model

        if datasource_key is None:
            presigned_endpoint_url = f"/projects/{project_key}/models"
        else:
            presigned_endpoint_url = f"/projects/{project_key}/models/{datasource_key}"
        logger.debug(f"Params: {params}")

        file_downloader = FileDownloader(self.request)
        file_downloader.download_file(
            file_path=filepath,
            presigned_endpoint_url=presigned_endpoint_url,
            params=params,
            request_method="GET",
        )

    def push_model(self, project_key, path, datasource_key, round=None, params=None):
        if params is not None:
            self.request._make_request(
                "POST",
                f"/projects/{project_key}/models/{datasource_key}/params",
                params={"params": params},
            )

        if datasource_key is None:
            url = f"/projects/{project_key}/models"
        else:
            url = f"/projects/{project_key}/models/{datasource_key}"

        def construct_params(params_args: ParamsArgs):
            params = {
                "filename": params_args.file_name,
                "sha1Checksum": params_args.sha1hash,
                "datasourceKey": datasource_key,
            }
            if round is not None:
                params["round"] = round
            return params

        file_uploader = FileUploader(self.request)
        response = file_uploader.upload_file(
            file_path=path,
            presigned_endpoint_url=f"/projects/{project_key}/models/presigned-url",
            construct_params=construct_params,
            request_method="GET",
        )

        sha1_hash = response.sha1_hash
        params = {
            "sha1Checksum": sha1_hash,
        }

        if round is not None:
            params["round"] = round

        try:
            self.request._make_request("POST", url, params=params, print_error=False)
        except Exception as e:
            if str(e).find("Model will not be uploaded."):
                logger.error("Model not sampled.")
            else:
                raise e
