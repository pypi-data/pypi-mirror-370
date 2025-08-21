"""
This module has functionality to support running in
a distributed context
"""

from pydantic import BaseModel

from .network.info import NetworkInfo
from .cpu import CpuInfo
from .process import Process


class Environment(BaseModel):
    """
    This holds runtime information for the session, which is mostly
    useful in a distributed setting.
    """

    process: Process
    network: NetworkInfo
    cpu_info: CpuInfo
    node_id: int = 0
    num_nodes: int = 1
    gpus_per_node: int = 1
    platform: str = ""

    @property
    def is_multigpu(self) -> bool:
        return self.gpus_per_node > 1

    @property
    def world_size(self) -> int:
        return self.gpus_per_node * self.num_nodes

    @property
    def global_rank(self) -> int:
        return self.node_id * self.gpus_per_node + self.process.local_rank

    @property
    def is_master_process(self) -> bool:
        """
        Return true if this process has zero global rank
        """
        return self.global_rank == 0
