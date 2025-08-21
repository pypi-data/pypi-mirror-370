"""
This module has elements of a CPU
"""

from pydantic import BaseModel


class ProcessorThread(BaseModel, frozen=True):
    """Class representing a logical thread on a processor core"""

    id: int


class ProcessorCore(BaseModel, frozen=True):
    """Class representing a core on a processor"""

    id: int
    threads: list[ProcessorThread]

    @property
    def num_threads(self) -> int:
        return len(self.threads)


class PhysicalProcessor(BaseModel, frozen=True):
    """Class representing a real (physical) processor"""

    id: int
    cores: list[ProcessorCore]
    core_count: int = 0
    model: str = ""
    cache_size: int = 0
    sibling: int = 1

    @property
    def num_cores(self) -> int:
        return len(self.cores)


class CpuInfo(BaseModel, frozen=True):
    """Information on a system's CPUs

    :param list[PhysicalProcessor] physical_procs: Collection of physical processors
    :param int threads_per_core: Number of threads available per processor core
    :param int cores_per_node: Number of cores per compute node (network location)
    """

    physical_procs: list[PhysicalProcessor]
    threads_per_core: int = 1
    cores_per_node: int = 1
