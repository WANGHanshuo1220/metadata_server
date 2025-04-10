from typing import Dict, List, Optional, Union, Any, AsyncGenerator
import os
import httpx
import asyncio
from compnode import CompNode
from blockpool import BlockPool

class MetadataServer:

    def __init__(self, block_size: int=16):
        self.block_size = block_size
        self.compnodes = []
        self.mempools = []

    def add_compnode(self, num_gpu_blocks: int, api_base: str) -> int:
        compnode = CompNode(num_gpu_blocks, self.block_size, api_base)
        self.compnodes.append(compnode)
        return len(self.compnodes) - 1

    def add_mempool(self, num_blocks: int) -> int:
        mempool = BlockPool(num_blocks, self.block_size)
        self.mempools.append(mempool)
        return len(self.mempools) - 1

    def get_compnode_count(self):
        return len(self.compnodes)

    def get_mempool_count(self):
        return len(self.mempools)

    def sync_compnode(self, compnode_id: int, request_count: int, gpu_blocks: Dict[int, int]):
        print(f"Compnode {compnode_id} syncing")
        print(f"Request count: {request_count}")
        print(f"GPU blocks: {gpu_blocks}")
        self.compnodes[compnode_id].sync_status(request_count, gpu_blocks)

    def sync_mempool(self, mempool_id: int, blocks: Dict[int, int]):
        self.mempools[mempool_id].sync_status(blocks)

    def get_target_compnode(self, seq: List[int]):
        # Find compnode with most hits and most free blocks
        max_hits = -1
        max_free_blocks = -1
        target_compnode_id = 0

        for i, compnode in enumerate(self.compnodes):
            hits = compnode.get_hits(seq)
            free_blocks = compnode.get_free_blocks()
            
            if hits > max_hits or (hits == max_hits and free_blocks > max_free_blocks):
                max_hits = hits
                max_free_blocks = free_blocks
                target_compnode_id = i

        print(f"Sending to compnode {target_compnode_id} with hits {max_hits} and free blocks {max_free_blocks}")
                
        return target_compnode_id
        
        
    async def tokenize(self, content: Union[str, Dict[str, Any]]) -> List[int]:
        """Tokenize text using the vLLM API."""
        async with httpx.AsyncClient() as client:

            if isinstance(content, str):
                tokenize_payload = {"prompt": content}
            else:
                tokenize_payload = {"messages": content}
            
            response = await client.post(
                f"{self.compnodes[0].api_base}/tokenize", 
                json=tokenize_payload
            )
            
            if response.status_code != 200:
                raise Exception(f"Tokenization failed: {response.text}")
                
            tokenize_data = response.json()
            return tokenize_data.get("tokens", [])
    
    async def stream_response(self, compnode_id: int, endpoint: str, payload: Dict[str, Any]) -> AsyncGenerator[bytes, None]:
        """Stream response from vLLM API."""
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.compnodes[compnode_id].api_base}{endpoint}",
                json=payload,
                timeout=httpx.Timeout(timeout=None)  # No timeout for streaming
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    raise Exception(f"API request failed: {error_text.decode()}")
                    
                async for chunk in response.aiter_bytes():
                    yield chunk
                    await asyncio.sleep(0)  # Yield control back to event loop
    
    async def non_streaming_request(self, compnode_id: int, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make a non-streaming request to vLLM API."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.compnodes[compnode_id].api_base}{endpoint}",
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.text}")
                
            return response.json(), response.status_code