from .api.ProjectAPI import ProjectAPI


class _Project:
    def __init__(self, key: str, api: ProjectAPI):
        """
        Creates a new project with params or connects to an existing project with key.

        Throws exception if neither key nor params is given.
        """
        self._api = api
        self.key = key

    def get_info(self):
        return self._api.get_info(self.key)

    def complete(self):
        return self._api.complete(self.key)

    def update_rounds(self, rounds):
        return self._api.update_rounds(self.key, rounds)

    def update_schedule(self, schedule):
        return self._api.update_schedule(self.key, schedule)

    def update_paused(self, paused):
        return self._api.update_paused(self.key, paused)

    def update_auto_increment(self, auto_increment):
        return self._api.update_auto_increment(self.key, auto_increment)

    def update_optimizer_params(self, optimizer_params):
        return self._api.update_optimizer_params(self.key, optimizer_params)

    def update_contributor(self, email, role):
        return self._api.update_contributor(self.key, email, role)

    def set_dynamic_trainer(self, dynamic_trainer_key):
        return self._api.set_dynamic_trainer(self.key, dynamic_trainer_key)

    def delete_project(self):
        return self._api.delete_project(self.key)

    def add_contributor(self, email, role="member"):
        return self._api.add_contributor(self.key, email, role)

    def delete_contributor(self, email):
        return self._api.delete_contributor(self.key, email)

    def get_next_schedule(self):
        return self._api.get_next_schedule(self.key)

    def increment_round(self):
        return self._api.increment_round(self.key)

    def get_rounds(self):
        return self._api.get_rounds(self.key)

    def get_round(self, round):
        return self._api.get_round(self.key, round)

    def get_stats(self, round=None, datasource_key=None, owned=None):
        params = {}
        if round is not None:
            params["round"] = round
        if datasource_key is not None:
            params["datasource"] = datasource_key
        if owned is not None:
            params["owned"] = owned
        return self._api.get_stats(self.key, params)

    def get_stats_avg(self):
        return self._api.get_stats_avg(self.key)

    def get_submissions(self, datasource_key=None, round=None, owned=None):
        params = {}
        if round is not None:
            params["round"] = round
        if datasource_key is not None:
            params["datasource"] = datasource_key
        if owned is not None:
            params["owned"] = owned
        return self._api.get_submissions(self.key, params)

    def upload_optimizer(self, path):
        self._api.upload_optimizer(self.key, path)

    def upload_file(self, path):
        self._api.upload_file(self.key, path)

    def upload_dynamic_trainer(self, path):
        self._api.upload_dynamic_trainer(self.key, path)

    def report_stats(self, scores, num_samples, round, datasource_key):
        stats = {
            "round": round,
            "scores": scores,
            "numPoints": num_samples,
            "datasource": datasource_key,
        }
        return self._api.report_stats(self.key, stats)

    def push_model(self, path, datasource_key, round=None, params=None):
        self._api.push_model(
            project_key=self.key,
            path=path,
            datasource_key=datasource_key,
            round=round,
            params=params,
        )

    def pull_model(
        self, filepath, datasource_key=None, round=None, federated_model=None
    ):
        self._api.pull_model(
            project_key=self.key,
            filepath=filepath,
            datasource_key=datasource_key,
            round=round,
            federated_model=federated_model,
        )

    def add_datasource_and_trainer(
        self, datasource_key, trainer_key, hyper_param_values={}, labeled=True
    ):
        params = {
            "datasourceKey": datasource_key,
            "trainerKey": trainer_key,
            "hyperParamValues": hyper_param_values,
            "labeled": labeled,
        }
        return self._api.create_bridge(self.key, params)

    def log(self, datasource_key, round, model_path=None, metrics=None):
        if model_path:
            self.push_model(model_path, datasource_key, round=round)

        if metrics:
            self.report_stats(metrics, 1, round, datasource_key)
