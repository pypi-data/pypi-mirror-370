from pydantic import BaseModel

from iccore.system.cpu import PhysicalProcessor
from iccore.system.gpu import GpuProcessor


class ComputeNode(BaseModel, frozen=True):

    address: str
    cpus: list[PhysicalProcessor] = []
    gpus: list[GpuProcessor] = []
