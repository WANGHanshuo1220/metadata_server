from typing import Dict, Optional
from abc import ABC, abstractmethod

from nodes.utils import MN2CNs
from common.utils import HostIP, GetMemNode


class MNBaseScheduler(ABC):
    
    def __init__(
        self, 
        prefill_nodes: Dict[HostIP, MN2CNs],
        decode_nodes: Dict[HostIP, MN2CNs],
    ) -> None:
        self.prefill_nodes = prefill_nodes
        self.decode_nodes = decode_nodes

    @abstractmethod
    def get_mn_for_prefix_sharing(self, request: GetMemNode) -> Optional[HostIP]:
        raise NotImplementedError
