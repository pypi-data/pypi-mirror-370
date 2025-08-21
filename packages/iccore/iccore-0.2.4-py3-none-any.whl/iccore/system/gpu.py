"""
This module has elements of a GPU
"""

from pydantic import BaseModel


class Process(BaseModel, frozen=True):
    """Class representing a single process"""

    pid: int = 0
    name: str = ""


class GpuProcessor(BaseModel, frozen=True):
    """Class representing a physical GPU"""

    id: int
    model: str = ""
    serial: int
    bus_id: str = ""
    max_memory: int
    free_memory: int
    processes: list[Process] = []

    @property
    def num_processes(self) -> int:
        return len(self.processes)


class GpuInfo(BaseModel, frozen=True):
    """
    Information on a system's GPUs

    :param list[GpuProcessor] physical_procs: Collection of physical GPUs on the system
    """

    physical_procs: list[GpuProcessor]
