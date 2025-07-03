from typing import Tuple

from scheduler.cn_scheduler.cn_base_scheduler import CNBaseScheduler
from common.utils import Counter, PORT, HostIP, GetCompNode
from nodes.utils import MN2CNs
from nodes.comp_node import CompNode


class CNNaiveScheduler(CNBaseScheduler):
    """ Naive scheduler use round robin method """
    
    def __init__(self, prefill_nodes, decode_nodes, cpu_nodes):
        super().__init__(prefill_nodes, decode_nodes, cpu_nodes)

        self.prefill_counter = Counter()
        self.decode_counter = Counter()
        self.cpu_counter = Counter()

        self.direct_hybrid_counter = Counter()
    
    def _schedule_prefill_host(self, request: GetCompNode) -> HostIP:
        """Schedule a host for prefill based on prefix caching."""
        block_hashes = request.block_hashes

        max_hits = 0
        target_host_ip = None
        for host_ip, mn2cn in self.prefill_nodes.items():
            mem_node = mn2cn.mem_node
            num_hits = mem_node.check_hits(block_hashes)
            if num_hits > max_hits:
                max_hits = num_hits
                target_host_ip = host_ip
        
        # No caching, use round robin
        if not target_host_ip:
            idx = next(self.prefill_counter)%len(self.prefill_nodes)
            target_host_ip = list(self.prefill_nodes.keys())[idx]

        return target_host_ip

    def _schedule_prefill_cn(self, mn2cns: MN2CNs) -> PORT:
        """Use round robin to choose a cn"""
        target_port = mn2cns.schedule_cn_rr()
        return target_port

    def schedule_prefill(self, request: GetCompNode) -> Tuple[HostIP, PORT]:
        target_host_ip = self._schedule_prefill_host(request)
        mn2cns = self.prefill_nodes[target_host_ip]
        target_port = self._schedule_prefill_cn(mn2cns)
        return (target_host_ip, target_port)

    def schedule_decode(self) -> Tuple[HostIP, PORT]:
        idx = next(self.decode_counter)%len(self.comp_nodes["decode"])
        return self.comp_nodes["decode"][idx]

    def schedule_cpu(self) -> Tuple[HostIP, PORT]:
        idx = next(self.cpu_counter)%len(self.comp_nodes["cpu"])
        return self.comp_nodes["cpu"][idx]

