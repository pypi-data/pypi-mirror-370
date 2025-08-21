from pydantic import BaseModel

from .node import ComputeNode


class ClusterAllocation(BaseModel, frozen=True):

    nodes: list[ComputeNode] = []
