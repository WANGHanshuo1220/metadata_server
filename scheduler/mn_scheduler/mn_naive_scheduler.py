from typing import Optional

from scheduler.cn_scheduler.cn_base_scheduler import CNBaseScheduler
from common.utils import HostIP


class CNNaiveScheduler(CNBaseScheduler):
    """ Naive scheduler use round robin method """
    
    def __init__(self, comp_nodes, mem_nodes):
        super().__init__(comp_nodes, mem_nodes)

    def schedule_mn(self) -> Optional[HostIP]:
        target_addr = None
        max_hits = 0

        for mn_addr, mn in self.mem_nodes.items():
            hits = mn.check_hits()
            if hits > max_hits:
                max_hits = hits
                target_addr = mn_addr
        
        return target_addr
