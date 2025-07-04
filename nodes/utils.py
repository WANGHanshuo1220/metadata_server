from dataclasses import dataclass
from typing import Dict, List

from common.utils import HostIP, PORT, Counter
from nodes.comp_node import CompNode
from nodes.mem_node import MemNode


class MN2CNs:
    """ A mapping between MN and CN with the same host ip """
    host_ip: HostIP
    mem_node: MemNode
    comp_nodes: Dict[PORT, CompNode]

    def __init__(self, host_ip, mem_node, comp_nodes):
        self.host_ip = host_ip
        self.mem_node = mem_node
        self.comp_nodes = comp_nodes

        self.counter = Counter()
    
    def schedule_cn_rr(self) -> PORT:
        """Round robin schedule"""
        idx = next(self.counter)%len(self.comp_nodes)
        return list(self.comp_nodes.keys())[idx]


@dataclass
class CPUCN:
    host_ip: HostIP
    port: PORT
    comp_node: CompNode


class CPUCNs:
    cpu_cns: List[CPUCN]

    def __init__(self):
        self.cpu_cns = []
        self.counter = Counter()

    def append(self, host, port, comp_node) -> None:
        self.cpu_cns.append(CPUCNs(host, port, comp_node))

    def schedule_rr(self) -> CPUCN:
        """Round robin schedule"""
        idx = next(self.counter)%len(self.cpu_cns)
        return self.cpu_cns[idx]
