from typing import Tuple

from scheduler.cn_scheduler.cn_base_scheduler import CNBaseScheduler
from common.utils import CN_API_URL
from scheduler.utils import Counter


class CNNaiveScheduler(CNBaseScheduler):
    """ Naive scheduler use round robin method """
    
    def __init__(self, comp_nodes, mem_nodes):
        super().__init__(comp_nodes, mem_nodes)

        self.prefill_counter = Counter()
        self.decode_counter = Counter()
        self.cpu_counter = Counter()

        self.direct_hybrid_counter = Counter()

    def schedule_prefill(self) -> CN_API_URL:
        idx = next(self.prefill_counter)%len(self.comp_nodes["prefill"])
        return self.comp_nodes["prefill"][idx]

    def schedule_decode(self) -> CN_API_URL:
        idx = next(self.decode_counter)%len(self.comp_nodes["decode"])
        return self.comp_nodes["decode"][idx]

    def schedule_cpu(self) -> CN_API_URL:
        idx = next(self.cpu_counter)%len(self.comp_nodes["cpu"])
        return self.comp_nodes["cpu"][idx]

    def schedule_disagg_pair(self) -> Tuple[CN_API_URL, CN_API_URL, bool]:
        prefill_api_url = self.schedule_prefill()

        if next(self.direct_hybrid_counter)%100 == 0:
            decode_api_url = self.schedule_cpu()
            direct_hybrid = True
        else:
            decode_api_url = self.schedule_decode()
            direct_hybrid = False

        return (prefill_api_url, decode_api_url, direct_hybrid)
