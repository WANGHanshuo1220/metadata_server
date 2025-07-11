from typing import List, Union

from common.utils import MemNodeCreate, MemNodeSync, CompNodeCreate


class BlockPool:
    """ BlockPool could represent:
    1. CPU blocks of a memory node or
    2. GPU blocks of a compute engine
    """

    def __init__(self, mn_info: Union[MemNodeCreate, CompNodeCreate], block_size: int):
        self.num_blocks = mn_info.num_blocks
        self.block_size = block_size

        self.block_hashes = set()
    
    def _sync_block_hashes(self, block_hashes: List[int]) -> None:
        assert len(block_hashes) <= self.num_blocks
        self.block_hashes = set(block_hashes)

    def sync_status(self, data: MemNodeSync) -> int:
        self._sync_block_hashes(data.block_hashes)
        return len(self.block_hashes)

    def get_free_blocks(self) -> int:
        return self.num_blocks - len(self.block_hashes)

    def add_block_hashes(self, data: MemNodeSync) -> int:
        self.block_hashes.update(data.block_hashes)
        assert len(self.block_hashes) <= self.num_blocks
        return len(self.block_hashes)
