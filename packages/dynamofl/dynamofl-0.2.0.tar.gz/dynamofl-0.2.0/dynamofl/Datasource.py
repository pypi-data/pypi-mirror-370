from .api.DatasourceAPI import DatasourceAPI


class _Datasource:
    def __init__(self, key, api: DatasourceAPI):
        self._api = api
        self.key: str = key
        self.trainers = {}

    def add_trainer(
        self,
        key,
        train=None,
        test=None,
        default_hyper_params=None,
        description=None,
        model_path=None,
    ):
        params = {"key": key}
        if default_hyper_params is not None:
            params["defaultHyperParams"] = default_hyper_params
        if description is not None:
            params["description"] = description

        self._api.create_trainers(self.key, params=params)

        self.trainers[key] = params
        if train:
            self.trainers[key]["train"] = train
        if test:
            self.trainers[key]["test"] = test

        if model_path is not None:
            self.trainers[key]["model_path"] = model_path

    def add_existing_trainers(self):
        for trainer in self.trainers.values():
            self.add_trainer(self.add_trainer(**trainer))

    def get_datasource(self):
        return self._api.get_datasource(key=self.key)
