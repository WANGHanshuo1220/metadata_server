from blockpool import BlockPool
from typing import List

class CompNode:

    def __init__(self, num_gpu_blocks: int, block_size: int):
        self.gpu_pool = BlockPool(num_blocks=num_gpu_blocks, block_size=block_size)
        self.block_size = block_size
        self.request_count = 0

    def set_request_count(self, request_count: int):
        self.request_count = request_count

    def sync_status(self, gpu_blocks: List[int]):
        self.gpu_pool.sync_status(gpu_blocks)

    def get_free_blocks(self) -> int:
        return self.gpu_pool.get_free_blocks()

    def get_sequence_hits(self, seq: List[int]) -> int:
        return self.gpu_pool.get_sequence_hits(seq)
        
    def add_block(self, block: int):
        self.gpu_pool.add_block(block)
        
    def delete_block(self, block: int):
        self.gpu_pool.delete_block(block)
        
    def add_blocks(self, blocks: List[int]):
        self.gpu_pool.add_blocks(blocks)
        
    def delete_blocks(self, blocks: List[int]):
        self.gpu_pool.delete_blocks(blocks)