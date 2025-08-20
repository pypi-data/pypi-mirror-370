import logging

from dynamofl.Request import _Request


class _Attack:
    def __init__(self, request: _Request) -> None:
        self.request = request
        self.logger = logging.getLogger("_Attack")
        pass

    def attack(self, model_id: str, name: str, kwargs: any) -> None:
        params = {"model_id": model_id, "name": name, "parameters": kwargs}
        res = self.request._make_request("POST", "/attack", params=params)
        self.logger.info("Attack created: {}".format(res))
        pass
