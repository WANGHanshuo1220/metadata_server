from typing import Dict, Tuple
from abc import ABC, abstractmethod

from comp_node import CompNode
from mem_node import MemNode
from common.utils import CN_API_URL, HostIP


class CNBaseScheduler(ABC):
    
    def __init__(
        self, 
        comp_nodes: Dict[CN_API_URL, CompNode],
        mem_nodes: Dict[HostIP, MemNode]
    ) -> None:
        self.comp_nodes = comp_nodes
        self.mem_nodes = mem_nodes

    @abstractmethod
    def schedule_prefill(self) -> CN_API_URL:
        raise NotImplementedError

    @abstractmethod
    def schedule_decode(self) -> CN_API_URL:
        raise NotImplementedError

    @abstractmethod
    def schedule_cpu(self) -> CN_API_URL:
        raise NotImplementedError

    @abstractmethod
    def schedule_disagg_pair(self) -> Tuple[CN_API_URL, CN_API_URL, bool]:
        raise NotImplementedError
