"""Test class for Dynamofl API"""
import logging
from typing import Dict, List, Union

from ..entities.test import TestEntity
from ..Helpers import Helpers
from ..Request import _Request
from .gpu_config import GPUConfig, GPUSpecification, VRAMConfig


class Test:
    """Test class for Dynamofl API"""

    @staticmethod
    def create_test(
        request: _Request,
        name: str,
        model_key: str,
        dataset_id: Union[str, None],
        test_type: str,
        gpu: GPUSpecification,
        config: list,
        guardrail_model_key="",
        target_model_key="",
        api_key=None,
    ) -> TestEntity:
        logger = logging.getLogger("Test")
        if gpu is None:
            raise Exception("GPU is not set.")  # pylint: disable=broad-exception-raised

        if isinstance(gpu, VRAMConfig):
            if gpu.vramGB is None or gpu.vramGB <= 0:
                raise Exception("VRAM is not set.")  # pylint: disable=broad-exception-raised

        if isinstance(gpu, GPUConfig):
            if gpu.gpu_count is None or gpu.gpu_type is None:
                raise Exception(  # pylint: disable=broad-exception-raised
                    "GPU is not set. You need to set gpu_count and gpu_type."
                )

        params = {
            "name": name,
            "modelKey": model_key,
            "datasetId": dataset_id,
            "type": test_type,
            "guardrailModelKey": guardrail_model_key,
            "targetModelKey": target_model_key,
            "gpu": gpu.as_dict(),
            "config": config,
        }
        if api_key:
            params["apiKey"] = api_key
        # TODO: Uncomment and remove the below call when endpoint is shipped to the customers
        # res = request._make_request(  # pylint: disable=protected-access
        #     "POST", f"/attack/model/key/{model_key}/test", params=params
        # )
        res = request._make_request(  # pylint: disable=protected-access
            "POST", "/attack/test", params=params
        )
        test_id = res["id"]
        attacks = res["attacks"]
        logger.info("Test created: %s", str(res))
        return TestEntity(
            id=test_id,
            name=name,
            model_key=model_key,
            dataset_id=dataset_id,
            test_type=test_type,
            guardrail_model_key=guardrail_model_key,
            target_model_key=target_model_key,
            attacks=attacks,
            config=config,
            api_host=request.host,
        )

    @staticmethod
    def generate_test_config_from_grid(
        common_attack_config: Dict, grid: List[Dict[str, List[Union[str, float, int]]]]
    ) -> List[Dict[str, Dict]]:
        """Generate test config given grid of hyper parameters"""
        test_config = []
        hyper_parameters_combinations = Helpers.expand_grid_search(grid)
        if len(hyper_parameters_combinations) == 0:
            hyper_parameters_combinations = [{}]

        for hyper_parameters in hyper_parameters_combinations:
            test_config.append({**common_attack_config, "hyper_parameters": hyper_parameters})
        return test_config

    @staticmethod
    def create_test_with_grid(
        request: _Request,
        name: str,
        model_key: str,
        dataset_id: Union[str, None],
        test_type: str,
        gpu: GPUSpecification,
        common_attack_config: Dict,
        grid: List[Dict[str, List[Union[str, float, int]]]],
        guardrail_model_key: str = "",
        target_model_key: str = "",
        api_key=None,
    ) -> TestEntity:
        """Create test with grid of hyper parameters"""
        test_config = Test.generate_test_config_from_grid(common_attack_config, grid)
        return Test.create_test(
            request,
            name,
            model_key,
            dataset_id,
            test_type,
            gpu,
            test_config,
            guardrail_model_key=guardrail_model_key,
            target_model_key=target_model_key,
            api_key=api_key,
        )
