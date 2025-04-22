from typing import Dict, List, Optional, Union, Any, AsyncGenerator
import os
import httpx
import asyncio
from compnode import CompNode
from blockpool import BlockPool

class MetadataServer:

    def __init__(self, block_size: int=16):
        self.block_size = block_size
        self.compnodes = {}
        self.mempools = {}

    def add_compnode(self, address: str, num_gpu_blocks: int):
        compnode = CompNode(num_gpu_blocks, self.block_size)
        self.compnodes[address] = compnode

    def add_mempool(self, address: str, num_blocks: int):
        mempool = BlockPool(num_blocks, self.block_size)
        self.mempools[address] = mempool

    def get_compnode_count(self):
        return len(self.compnodes)

    def get_mempool_count(self):
        return len(self.mempools)

    def sync_compnode(self, address: str, request_count: int, gpu_blocks: List[int]):
        if address not in self.compnodes:
            raise ValueError(f"Compute node with address {address} not found")
        self.compnodes[address].set_request_count(request_count)
        self.compnodes[address].sync_status(gpu_blocks)

    def sync_mempool(self, address: str, blocks: List[int]):
        if address not in self.mempools:
            raise ValueError(f"Memory pool with address {address} not found")
        self.mempools[address].sync_status(blocks)

    def add_block_to_compnode(self, address: str, block: int):
        if address not in self.compnodes:
            raise ValueError(f"Compute node with address {address} not found")
        self.compnodes[address].add_block(block)
        
    def delete_block_from_compnode(self, address: str, block: int):
        if address not in self.compnodes:
            raise ValueError(f"Compute node with address {address} not found")
        self.compnodes[address].delete_block(block)
        
    def add_blocks_to_compnode(self, address: str, blocks: List[int]):
        if address not in self.compnodes:
            raise ValueError(f"Compute node with address {address} not found")
        self.compnodes[address].add_blocks(blocks)
        
    def delete_blocks_from_compnode(self, address: str, blocks: List[int]):
        if address not in self.compnodes:
            raise ValueError(f"Compute node with address {address} not found")
        self.compnodes[address].delete_blocks(blocks)
        
    def add_block_to_mempool(self, address: str, block: int):
        if address not in self.mempools:
            raise ValueError(f"Memory pool with address {address} not found")
        self.mempools[address].add_block(block)
        
    def delete_block_from_mempool(self, address: str, block: int):
        if address not in self.mempools:
            raise ValueError(f"Memory pool with address {address} not found")
        self.mempools[address].delete_block(block)
        
    def add_blocks_to_mempool(self, address: str, blocks: List[int]):
        if address not in self.mempools:
            raise ValueError(f"Memory pool with address {address} not found")
        self.mempools[address].add_blocks(blocks)
        
    def delete_blocks_from_mempool(self, address: str, blocks: List[int]):
        if address not in self.mempools:
            raise ValueError(f"Memory pool with address {address} not found")
        self.mempools[address].delete_blocks(blocks)

    def get_target_compnode(self, seq: List[int]):
        # Find compnode with most hits and most free blocks
        max_hits = -1
        max_free_blocks = -1
        target_address = None

        for address, compnode in self.compnodes.items():
            hits = compnode.get_sequence_hits(seq)
            free_blocks = compnode.get_free_blocks()
            
            if hits > max_hits or (hits == max_hits and free_blocks > max_free_blocks):
                max_hits = hits
                max_free_blocks = free_blocks
                target_address = address

        print(f"Sending to compnode {target_address} with hits {max_hits} and free blocks {max_free_blocks}")
                
        return target_address
        
        
    async def tokenize(self, content: Union[str, Dict[str, Any]]) -> List[int]:
        """Tokenize text using the vLLM API."""
        if not self.compnodes:
            raise ValueError("No compute nodes available for tokenization")
            
        # Get the first compnode address
        first_address = next(iter(self.compnodes))
        
        async with httpx.AsyncClient() as client:

            if isinstance(content, str):
                tokenize_payload = {"prompt": content}
            else:
                tokenize_payload = {"messages": content}
            
            response = await client.post(
                f"{first_address}/tokenize", 
                json=tokenize_payload
            )
            
            if response.status_code != 200:
                raise Exception(f"Tokenization failed: {response.text}")
                
            tokenize_data = response.json()
            return tokenize_data.get("tokens", [])
    
    async def stream_response(self, address: str, endpoint: str, payload: Dict[str, Any]) -> AsyncGenerator[bytes, None]:
        """Stream response from vLLM API."""
        if address not in self.compnodes:
            raise ValueError(f"Compute node with address {address} not found")
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{address}{endpoint}",
                json=payload,
                timeout=httpx.Timeout(timeout=None)  # No timeout for streaming
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    raise Exception(f"API request failed: {error_text.decode()}")
                    
                async for chunk in response.aiter_bytes():
                    yield chunk
                    await asyncio.sleep(0)  # Yield control back to event loop
    
    async def non_streaming_request(self, address: str, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make a non-streaming request to vLLM API."""
        if address not in self.compnodes:
            raise ValueError(f"Compute node with address {address} not found")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{address}{endpoint}",
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.text}")
                
            return response.json(), response.status_code