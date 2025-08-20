"""
This file contains the GPUConfig dataclass.
Defines the various GPU configurations that can be used in the system.
"""
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Union


# ENUM for GPU configuration
class GPUType(Enum):
    """
    Enum for GPU types.
    These are all the GPU types that are supported by the system.
    Note: We need to make a distinction between A100_40GB and A100_80GB.
    """

    A100 = "a100"
    A10G = "a10g"
    H100 = "h100"
    M60 = "m60"
    T4 = "t4"
    V100 = "v100"

    def __str__(self):
        return self.value


# Step 1: Base Dataclass
@dataclass
class BaseDataClass:
    kind: str = field(init=False)

    def __post_init__(self):
        self.kind = self.__class__.__name__

    def as_dict(self):
        return asdict(self)


@dataclass
class GPUConfig(BaseDataClass):
    gpu_type: GPUType
    gpu_count: int

    def as_dict(self):
        value = super().as_dict()
        value["gpu_type"] = str(value["gpu_type"])
        return value


@dataclass
class VRAMConfig(BaseDataClass):
    vramGB: int  # pylint: disable=invalid-name


GPUSpecification = Union[GPUConfig, VRAMConfig]
