from dataclasses import dataclass
from typing import List

from common.block_pool import BlockPool
from common.utils import HostIP, PORT, CompNodeCreate, CompNodeSync


@dataclass
class CNBaseInfo:
    host: HostIP
    port: PORT
    role: str

    @staticmethod
    def create(cn_info: CompNodeCreate) -> 'CNBaseInfo':
        return CNBaseInfo(
            cn_info.host, cn_info.port, cn_info.role)


class CompNode:

    def __init__(self, cn_info: CompNodeCreate, block_size: int) -> None:
        self.gpu_pool = BlockPool(cn_info, block_size)
        self.block_size = block_size
        self.base_info = CNBaseInfo.create(cn_info)
        
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
