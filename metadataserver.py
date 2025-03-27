from typing import Dict
from compnode import CompNode
from blockpool import BlockPool

class MetadataServer:

    def __init__(self, block_size: int=16):
        self.block_size = block_size
        self.compnodes = []
        self.mempools = []

    def add_compnode(self, num_gpu_blocks: int) -> int:
        compnode = CompNode(num_gpu_blocks, self.block_size)
        self.compnodes.append(compnode)
        return len(self.compnodes) - 1

    def add_mempool(self, num_blocks: int, num_gpus: int) -> int:
        mempool = BlockPool(num_blocks, self.block_size)
        self.mempools.append(mempool)
        return len(self.mempools) - 1

    def get_compnode_count(self):
        return len(self.compnodes)

    def get_mempool_count(self):
        return len(self.mempools)

    def sync_compnode(self, compnode_id: int, request_count: int, gpu_blocks: Dict[int, int]):
        self.compnodes[compnode_id].sync_status(request_count, gpu_blocks)

    def sync_mempool(self, mempool_id: int, blocks: Dict[int, int]):
        self.mempools[mempool_id].sync_status(blocks)