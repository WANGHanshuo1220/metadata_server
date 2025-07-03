from typing import Optional

from scheduler.mn_scheduler.mn_base_scheduler import MNBaseScheduler
from common.utils import HostIP, GetMemNode


class MNNaiveScheduler(MNBaseScheduler):
    """ Naive scheduler use round robin method """
    
    def __init__(self, prefill_nodes, decode_nodes):
        super().__init__(prefill_nodes, decode_nodes)

    def get_mn_for_prefix_sharing(self, request: GetMemNode) -> Optional[HostIP]:
        target_host = None
        max_hits = 0

        for host, mn2cns in self.prefill_nodes.items():
            hits = mn2cns.mem_node.check_hits(request.block_hashes)
            if hits > max_hits:
                max_hits = hits
                target_host = host
        
        return target_host
