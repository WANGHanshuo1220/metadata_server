from dataclasses import dataclass
from typing import List

from common.block_pool import BlockPool
from common.utils import CN_API_URL, CompNodeCreate, CompNodeSync


@dataclass
class CNBaseInfo:
    api_url: CN_API_URL
    engine_type: str
    pd_role: str

    @staticmethod
    def create(cn_info: CompNodeCreate) -> 'CNBaseInfo':
        return CNBaseInfo(
            cn_info.api_url, cn_info.engine_type, cn_info.pd_role)


class CompNode:

    def __init__(self, cn_info: CompNodeCreate, block_size: int) -> None:
        self.gpu_pool = BlockPool(num_blocks=cn_info.num_gpu_blocks, 
                                  block_size=block_size)
        self.block_size = block_size
        self.bash_info = CNBaseInfo.create(cn_info)
        
        self.request_count = 0

    def _sync_request_count(self, request_count: int) -> None:
        self.request_count = request_count
    
    def _sync_blocks(self, gpu_blocks) -> None:
        self.gpu_pool.sync_status(gpu_blocks)

    def sync_status(self, data: CompNodeSync) -> None:
        self._sync_blocks(data.gpu_blocks)
        self._sync_request_count(data.request_count)

    def get_free_blocks(self) -> int:
        return self.gpu_pool.get_free_blocks()

    def get_sequence_hits(self, seq: List[int]) -> int:
        return self.gpu_pool.get_sequence_hits(seq)

    def add_block(self, block: int) -> None:
        self.gpu_pool.add_block(block)
        
    def delete_block(self, block: int) -> None:
        self.gpu_pool.delete_block(block)
        
    def add_blocks(self, blocks: List[int]) -> None:
        self.gpu_pool.add_blocks(blocks)
        
    def delete_blocks(self, blocks: List[int]) -> None:
        self.gpu_pool.delete_blocks(blocks)