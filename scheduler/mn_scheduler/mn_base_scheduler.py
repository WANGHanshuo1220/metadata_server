from typing import Dict
from abc import ABC, abstractmethod

from comp_node import CompNode
from mem_node import MemNode
from common.utils import CN_API_URL, HostIP


class MNBaseScheduler(ABC):
    
    def __init__(
        self, 
        comp_nodes: Dict[CN_API_URL, CompNode],
        mem_nodes: Dict[HostIP, MemNode]
    ) -> None:
        self.comp_nodes = comp_nodes
        self.mem_nodes = mem_nodes

    @abstractmethod
    def schedule_mn(self) -> HostIP:
        raise NotImplementedError
