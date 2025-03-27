from blockpool import BlockPool
from typing import List, Dict

class CompNode:

    def __init__(self, num_gpu_blocks: int, block_size: int):
        self.gpu_pool = BlockPool(num_blocks=num_gpu_blocks, block_size=block_size)
        self.block_size = block_size
        self.request_count = 0

    def sync_status(self, request_count: int, gpu_blocks: Dict[int, int]):
        self.request_count = request_count
        self.gpu_pool.sync_status(gpu_blocks)

    def get_unused_blocks(self) -> int:
        return self.gpu_pool.get_unused_blocks()

    def get_free_blocks(self) -> int:
        return self.gpu_pool.get_free_blocks()

    def get_hits(self, seq: List[int]) -> int:
        return self.gpu_pool.get_hits(seq)