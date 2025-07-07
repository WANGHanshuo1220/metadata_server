from typing import Tuple, Optional

from scheduler.base_scheduler import BaseScheduler
from common.utils import Counter, PORT, HostIP, GetCompNode
from nodes.utils import MN2CNs


class NaiveScheduler(BaseScheduler):
    """ Naive scheduler use round robin method and only consider prefix caching """
    
    def __init__(self, prefill_nodes, decode_nodes, cpu_nodes):
        super().__init__(prefill_nodes, decode_nodes, cpu_nodes)

        self.prefill_nodes_counter = Counter()
        self.decode_nodes_counter = Counter()

        self.direct_hybrid_counter = Counter()

    @property
    def name(self) -> str:
        return "Naive scheduler"
    
    def _schedule_prefill_host(self, request: GetCompNode) -> Tuple[HostIP, Optional[HostIP]]:
        """Schedule a physical host for prefill based on prefix caching.
        
        Return tulpe of (cn_host_ip, mn_host_ip). mn_host_ip may be None.
        We ONLY consider prefix caching, so if prefix cache hits, cn_host_ip == mn_host_ip.
        """
        block_hashes = request.block_hashes

        max_hits = 0
        mn_host_ip = None
        for host_ip, mn2cn in self.prefill_nodes.items():
            mem_node = mn2cn.mem_node
            num_hits = mem_node.check_hits(block_hashes)
            if num_hits > max_hits:
                max_hits = num_hits
                mn_host_ip = host_ip
        
        # No caching, use round robin
        if not mn_host_ip:
            idx = next(self.prefill_nodes_counter)%len(self.prefill_nodes)
            cn_host_ip = list(self.prefill_nodes.keys())[idx]
        else:
            cn_host_ip = mn_host_ip

        return (cn_host_ip, mn_host_ip)

    def _schedule_prefill_cn(self, mn2cns: MN2CNs) -> PORT:
        """Use round robin to choose a cn"""
        target_port = mn2cns.schedule_cn_rr()
        return target_port
    
    def _make_direct_hybrid(self, request: GetCompNode) -> bool:
        if next(self.direct_hybrid_counter)%100 == 0:
            return True
        
        return False

    def schedule_prefill(self, request: GetCompNode) -> Tuple[HostIP, Optional[HostIP], PORT, bool]:
        """ Schedule a prefill llm: only consider prefix caching, round robin otherwise.
        NOTE: node loads not considered

        Return:
            1. cn_host_ip and cn_port to form a prefill instance api_url
            2. mn_host_ip for fetch prefix caching, which may be None
            3. Direct hybrid decode or not
        """
        cn_host_ip, mn_host_ip = self._schedule_prefill_host(request)
        mn2cns = self.prefill_nodes[cn_host_ip]
        cn_port = self._schedule_prefill_cn(mn2cns)
        direct_hybrid_decode = self._make_direct_hybrid(request)
        return (cn_host_ip, mn_host_ip, cn_port, direct_hybrid_decode)

    def schedule_decode(self, request: GetCompNode) -> Tuple[HostIP, Optional[HostIP], PORT]:
        """ Schedule a docode llm """
        if request.direct_hybrid:
            return self._schedule_hybrid_decode(request)
        else:
            return self._schedule_gpu_decode(request)

    def _schedule_gpu_decode(self, request: GetCompNode) -> Tuple[HostIP, HostIP, PORT]:
        """ Use round robin method to choose a mn and a cn.
        
        Return:
            1. cn_host_ip and co_port to form a gpu decode llm api_url
            2. mn_host_ip to save PD intermediate fo decode instance
        """
        node_idx = next(self.decode_nodes_counter)%len(self.decode_nodes)
        mn_host_ip = list(self.decode_nodes.keys())[node_idx]
        cn_host_ip = mn_host_ip
        cn_port = self.decode_nodes[mn_host_ip].schedule_cn_rr()

        return (cn_host_ip, mn_host_ip, cn_port)

    def _schedule_hybrid_decode(self, request: GetCompNode) -> Tuple[HostIP, Optional[HostIP], PORT]:
        """ Use round robin method to choose a cn and save cache on local GPU host memory 
        NOTE: Let prefill llm save cache locally may lead to low aggregated network bandwidth
        and CPU computation
        
        Return: 
            1. cn_host_ip and co_port to form a cpu decode llm api_url
            2. mn_host_ip == None, which means prefill llm save cache locally
        """
        mn_host_ip = None
        cpu_node = self.cpu_nodes.schedule_rr()
        cn_host_ip = cpu_node.host_ip
        cn_port = cpu_node.port
        
        return (cn_host_ip, mn_host_ip, cn_port)
