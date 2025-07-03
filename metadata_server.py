from typing import Dict, Optional, Tuple

from comp_node import CompNode
from mem_node import MemNode
from common.utils import (HostIP, NODE_TYPE,
                          CompNodeCreate, MemNodeCreate,
                          MemNodeSync, CompNodeSync)
from scheduler.cn_scheduler.factory import CNSchedulerFactory
from scheduler.mn_scheduler.factory import MNSchedulerFactory


class MN2CNs:
    """ A mapping between MN and CN with same host ip """
    


class MetadataServer:

    def __init__(self, block_size: int = 16) -> None:
        self.block_size = block_size
        self.comp_nodes: Dict[NODE_TYPE, Dict[HostIP, CompNode]] = {}
        self.mem_nodes: Dict[HostIP, MemNode] = {}

        self.cn_scheduler = CNSchedulerFactory.create_scheduler(
            "Naive", self.comp_nodes, self.mem_nodes)

        self.mn_scheduler = MNSchedulerFactory.create_scheduler(
            "Naive", self.comp_nodes, self.mem_nodes)

        self.__post_init__()
    
    def __post_init__(self) -> None:
        self.comp_nodes["prefill"] = {}
        self.comp_nodes["decode"] = {}
        self.comp_nodes["cpu"] = {}


    ##############################################################
    #                      Add Nodes APIs                        #
    ##############################################################
    def add_cn(self, cn_info: CompNodeCreate) -> None:
        compnode = CompNode(cn_info, self.block_size)
        self.comp_nodes[cn_info.role][cn_info.api_url] = compnode

    def add_mn(self, mn_info: MemNodeCreate) -> None:
        mem_node = MemNode(mn_info, self.block_size)
        self.mem_nodes[mn_info.host] = mem_node


    ##############################################################
    #                      Get Nodes APIs                        #
    ##############################################################
    @property
    def prefill_cn_count(self) -> int:
        return len(self.comp_nodes["prefill"])

    @property
    def decode_cn_count(self) -> int:
        return len(self.comp_nodes["decode"])

    @property
    def cpu_cn_count(self) -> int:
        return len(self.comp_nodes["cpu"])
    
    @property
    def total_cn_count(self) -> Tuple[int, int, int]:
        return (self.prefill_cn_count(), self.decode_cn_count(),
                self.cpu_cn_count())

    @property
    def mn_count(self) -> int:
        return len(self.mem_nodes)

    def get_mn(self) -> Optional[HostIP]:
        return self.mn_scheduler.schedule_mn()

    def get_disagg_pair_api(self) -> Tuple[HostIP, HostIP, bool]:
        return self.cn_scheduler.schedule_disagg_pair()


    ##############################################################
    #                     Update Stats APIs                      #
    ##############################################################
    def sync_compnode(self, data: CompNodeSync):
        address = data.api_url
        if address not in self.comp_nodes[data.role]:
            raise ValueError(f"Compute node with address {address} not found")
        self.comp_nodes[data.role][address].sync_status(data)

    def sync_memnode(self, data: MemNodeSync):
        address = data.address
        if address not in self.mem_nodes:
            raise ValueError(f"Memory pool with address {address} not found")
        self.mem_nodes[address].sync_status(data)

    def add_blocks_to_mempool(self, data: MemNodeSync):
        address = data.address
        if address not in self.mem_nodes:
            raise ValueError(f"Memory pool with address {address} not found")
        self.mem_nodes[address].add_block_hashes(data.block_hashes)
        

    ##############################################################
    #                     Statistics APIs                      #
    ##############################################################
    def get_mempool_hit_rate(self) -> float:
        return 0.0
