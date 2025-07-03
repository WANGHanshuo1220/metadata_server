from dataclasses import dataclass
from typing import List

from common.block_pool import BlockPool


@dataclass
class HitStatistics:
    num_fetch: int = 0
    fetch_hits: int = 0

    def update(self, num_fetch: int, fetch_hits: int) -> None:
        self.num_fetch += num_fetch
        self.fetch_hits += fetch_hits


class MemNode(BlockPool):

    def __init__(self, mn_info, block_size):
        super().__init__(mn_info, block_size)

        self.hit_statistics = HitStatistics()

    def check_hits(self, block_hashes: List[int]) -> int:
        hit_count = len(set(block_hashes) & self.block_hashes)
        self.hit_statistics.update(len(block_hashes), hit_count)
        return hit_count
