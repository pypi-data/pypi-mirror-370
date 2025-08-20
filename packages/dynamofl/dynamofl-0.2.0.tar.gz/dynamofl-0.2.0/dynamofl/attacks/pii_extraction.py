from dynamofl.models.model import Model

from .attack import _Attack


class PIIExtraction(_Attack):
    def __init__(self, request) -> None:
        super().__init__(request)
        pass

    def attack(self, model: Model, name: str, kwargs: any) -> None:
        print("PII Extraction initiated")
        return super().attack(model_id=model["_id"], name=name, kwargs=kwargs)
