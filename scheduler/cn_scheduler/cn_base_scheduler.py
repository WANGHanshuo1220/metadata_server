from typing import Dict, Tuple, List
from abc import ABC, abstractmethod

from nodes.utils import MN2CNs, CPUCNs
from common.utils import PORT, HostIP


class CNBaseScheduler(ABC):
    
    def __init__(
        self, 
        prefill_nodes: Dict[HostIP, MN2CNs],
        decode_nodes: Dict[HostIP, MN2CNs],
        cpu_nodes: List[CPUCNs]
    ) -> None:
        self.prefill_nodes = prefill_nodes
        self.decode_nodes = decode_nodes
        self.cpu_nodes = cpu_nodes

    @abstractmethod
    def schedule_prefill(self) -> Tuple[HostIP, PORT]:
        raise NotImplementedError

    @abstractmethod
    def schedule_decode(self) -> Tuple[HostIP, PORT]:
        raise NotImplementedError

    @abstractmethod
    def schedule_cpu(self) -> Tuple[HostIP, PORT]:
        raise NotImplementedError
