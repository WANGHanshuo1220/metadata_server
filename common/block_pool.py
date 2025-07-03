import hashlib
from typing import List, Tuple

from utils import MemNodeCreate, MemNodeSync


class BlockPool:
    """ BlockPool could represent:
    1. CPU blocks of a memory node or
    2. GPU blocks of a compute engine
    """

    def __init__(self, mn_info: MemNodeCreate, block_size: int):
        self.num_blocks = mn_info.num_blocks
        self.block_size = block_size

        self.block_hashes = set()
    
    def _sync_block_hashes(self, block_hashes: List[int]) -> None:
        assert len(block_hashes) <= self.num_blocks
        self.block_hashes = set(block_hashes)

    def sync_status(self, data: MemNodeSync) -> None:
        self._sync_block_hashes(data.block_hashes)

    def get_free_blocks(self) -> int:
        return self.num_blocks - len(self.block_hashes)

    def add_block_hashes(self, block_hashes: List[int]) -> None:
        self.block_hashes.update(block_hashes)
        assert len(self.block_hashes) <= self.num_blocks


    def get_block_hits(self, blocks: List[int]) -> int:
        for i in range(len(blocks)):
            if blocks[i] not in self.blocks:
                return i
        return len(blocks)

    def get_sequence_hits(self, seq: List[int]) -> int:
        hashes = generate_block_hashes(seq, self.block_size)
        return self.get_block_hits(hashes)
        