from dataclasses import dataclass
from typing import Dict, Optional, Tuple, List

from nodes.comp_node import CompNode
from nodes.mem_node import MemNode
from nodes.utils import MN2CNs, CPUCNs
from common.utils import (HostIP, PORT,
                          GetCompNode, GetMemNode,
                          CompNodeCreate, MemNodeCreate,
                          MemNodeSync, CompNodeSync)
from scheduler.cn_scheduler.factory import CNSchedulerFactory
from scheduler.mn_scheduler.factory import MNSchedulerFactory


class MetadataServer:

    def __init__(self, block_size: int = 16) -> None:
        self.block_size = block_size

        # This node means physical node that contains memory nodes and GPU engines
        self.prefill_nodes: Dict[HostIP, MN2CNs] = {}
        self.decode_nodes: Dict[HostIP, MN2CNs] = {}
        self.cpu_nodes = CPUCNs()

        self.cn_scheduler = CNSchedulerFactory.create_scheduler(
            "Naive", self.prefill_nodes, self.decode_nodes, self.cpu_nodes)

        self.mn_scheduler = MNSchedulerFactory.create_scheduler(
            "Naive", self.prefill_nodes, self.decode_nodes)


    ##############################################################
    #                      Add Nodes APIs                        #
    ##############################################################
    def add_cn(self, cn_info: CompNodeCreate) -> None:
        compnode = CompNode(cn_info, self.block_size)

        if cn_info.role == "prefill":
            host = cn_info.host
            assert host in self.prefill_nodes
            self.prefill_nodes[host].comp_nodes[cn_info.port] = compnode

        elif cn_info.role == "decode":
            host = cn_info.host
            assert host in self.decode_nodes
            self.decode_nodes[host].comp_nodes[cn_info.port] = compnode

        else:
            assert cn_info.role == "cpu"
            self.cpu_nodes.append(cn_info.host, cn_info.port, compnode)

    def add_mn(self, mn_info: MemNodeCreate) -> None:
        mem_node = MemNode(mn_info, self.block_size)
        if mn_info.node_type == "prefill":
            assert mn_info.host not in self.prefill_nodes
            self.prefill_nodes[mn_info.host] = MN2CNs(
                host_ip=mn_info.host, mem_node=mem_node, comp_nodes={})
        else:
            assert mn_info.node_type == "decode"
            assert mn_info.host not in self.decode_nodes
            self.decode_nodes[mn_info.host] = MN2CNs(
                host_ip=mn_info.host, mem_node=mem_node, comp_nodes={})


    ##############################################################
    #                      Get Nodes APIs                        #
    ##############################################################
    # @property
    # def prefill_cn_count(self) -> int:
    #     return len(self.comp_nodes["prefill"])

    # @property
    # def decode_cn_count(self) -> int:
    #     return len(self.comp_nodes["decode"])

    # @property
    # def cpu_cn_count(self) -> int:
    #     return len(self.comp_nodes["cpu"])
    
    # @property
    # def total_cn_count(self) -> Tuple[int, int, int]:
    #     return (self.prefill_cn_count(), self.decode_cn_count(),
    #             self.cpu_cn_count())

    @property
    def mn_count(self) -> int:
        return len(self.prefill_nodes) + len(self.decode_nodes)

    def get_mn_for_prefix_sharing(self, request: GetMemNode) -> Optional[HostIP]:
        return self.mn_scheduler.get_mn_for_prefix_sharing(request)

    def schedule_prefill(self, request: GetCompNode) -> Tuple[HostIP, PORT]:
        return self.cn_scheduler.schedule_prefill(request)


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
