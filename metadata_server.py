from typing import Dict, Tuple

from nodes.comp_node import CompNode
from nodes.mem_node import MemNode
from nodes.utils import MN2CNs, CPUCNs
from common.utils import (HostIP, PORT, GetCompNode,
                          CompNodeCreate, MemNodeCreate,
                          MemNodeSync, CompNodeSync)
from scheduler.factory import SchedulerFactory


class MetadataServer:

    def __init__(self, block_size: int = 16) -> None:
        self.block_size = block_size

        # This node means physical node that contains memory nodes and GPU engines
        self.prefill_nodes: Dict[HostIP, MN2CNs] = {}
        self.decode_nodes: Dict[HostIP, MN2CNs] = {}
        self.cpu_nodes = CPUCNs()

        self.scheduler = SchedulerFactory.create_scheduler(
            "Naive", self.prefill_nodes, self.decode_nodes, self.cpu_nodes)


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
    @property
    def prefill_cn_count(self) -> int:
        num_prefill_cn = 0
        for _, mn2cns in self.prefill_nodes.items():
            num_prefill_cn += len(mn2cns.comp_nodes)
        return num_prefill_cn

    @property
    def decode_cn_count(self) -> int:
        num_decode_cn = 0
        for _, mn2cns in self.decode_nodes.items():
            num_decode_cn += len(mn2cns.comp_nodes)
        return num_decode_cn

    @property
    def cpu_cn_count(self) -> int:
        return len(self.cpu_nodes.cpu_cns)
    
    @property
    def total_cn_count(self) -> Tuple[int, int, int]:
        return (self.prefill_cn_count(), self.decode_cn_count(),
                self.cpu_cn_count())

    @property
    def mn_count(self) -> int:
        return len(self.prefill_nodes) + len(self.decode_nodes)

    def schedule_prefill(self, request: GetCompNode) -> Tuple[HostIP, PORT]:
        return self.scheduler.schedule_prefill(request)

    def schedule_decode(self, request: GetCompNode) -> Tuple[HostIP, PORT]:
        return self.scheduler.schedule_decode(request)


    ##############################################################
    #                     Update Stats APIs                      #
    ##############################################################
    def sync_compnode(self, data: CompNodeSync):
        host = data.host
        port = data.port
        role = data.role
        if role == "prefill":
            if host not in self.prefill_nodes.keys():
                raise ValueError(f"Compute node {role} with {host}:{port} not found")
            self.prefill_nodes[host].comp_nodes[port].sync_status(data)
        elif role == "decode":
            if host not in self.decode_nodes.keys():
                raise ValueError(f"Compute node {role} with {host}:{port} not found")
            self.decode_nodes[host].comp_nodes[port].sync_status(data)

        else:
            assert role == "cpu"
            for cpu_cn in self.cpu_nodes.cpu_cns:
                if host == cpu_cn.host_ip and port == cpu_cn.port:
                    cpu_cn.comp_node.sync_status(data)
                    return

            raise ValueError(f"Compute node {role} with {host}:{port} not found")

    def sync_memnode(self, data: MemNodeSync) -> int:
        host = data.host
        node_type = data.node_type

        if node_type == "prefill":
            if host not in self.prefill_nodes.keys():
                raise ValueError(f"Memory node {node_type} with {host} not found")
            return self.prefill_nodes[host].mem_node.sync_status(data)
        else:
            assert node_type == "decode"
            if host not in self.decode_nodes.keys():
                raise ValueError(f"Memory node {node_type} with {host} not found")
            return self.decode_nodes[host].mem_node.sync_status(data)

    def add_blocks_to_mempool(self, data: MemNodeSync) -> int:
        host = data.host
        node_type = data.node_type

        if node_type == "prefill":
            if host not in self.prefill_nodes.keys():
                raise ValueError(f"Memory node {node_type} with {host} not found")
            return self.prefill_nodes[host].mem_node.add_block_hashes(data)
        else:
            assert node_type == "decode"
            if host not in self.decode_nodes.keys():
                raise ValueError(f"Memory node {node_type} with {host} not found")
            return self.decode_nodes[host].mem_node.add_block_hashes(data)
        

    ##############################################################
    #                     Statistics APIs                      #
    ##############################################################
    def get_mempool_hit_rate(self) -> float:
        return 0.0
