from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union, Any, Literal, AsyncGenerator
import uvicorn
import json
import traceback

from metadataserver import MetadataServer

# Create FastAPI app
app = FastAPI(title="Metadata Server API", description="API for managing compute nodes and memory pools")

# Create a global instance of MetadataServer
metadata_server = MetadataServer()

# Pydantic models for request/response validation
class CompNodeCreate(BaseModel):
    address: str
    num_gpu_blocks: int

class MemPoolCreate(BaseModel):
    address: str
    num_blocks: int

class CompNodeSync(BaseModel):
    request_count: int
    gpu_blocks: List[int]

class MemPoolSync(BaseModel):
    blocks: List[int]

class ServerStats(BaseModel):
    compnode_count: int
    mempool_count: int

class TokenSequence(BaseModel):
    sequence: List[int]

class BlockData(BaseModel):
    block: int

class BlocksData(BaseModel):
    blocks: List[int]

# OpenAI API compatible models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = None
    messages: List[ChatMessage]
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    max_tokens: Optional[int] = None
    stop: Optional[Union[str, List[str]]] = None
    stream: Optional[bool] = True
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    user: Optional[str] = None

class CompletionRequest(BaseModel):
    model: Optional[str] = None
    prompt: Union[str, List[str]]
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    max_tokens: Optional[int] = 16
    stop: Optional[Union[str, List[str]]] = None
    stream: Optional[bool] = True
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    user: Optional[str] = None

class TokenizeRequest(BaseModel):
    model: Optional[str] = None
    prompt: Optional[str] = None
    messages: Optional[List[ChatMessage]] = None
    add_special_tokens: Optional[bool] = True
    add_generation_prompt: Optional[bool] = True

# Dependency to get the metadata server instance
def get_metadata_server():
    return metadata_server

# Endpoints
@app.get("/", response_model=ServerStats)
def get_server_stats(server: MetadataServer = Depends(get_metadata_server)):
    """Get the current server statistics."""
    return {
        "compnode_count": server.get_compnode_count(),
        "mempool_count": server.get_mempool_count()
    }

@app.post("/compnode")
def add_compnode(node: CompNodeCreate, server: MetadataServer = Depends(get_metadata_server)):
    """Add a new compute node to the server."""
    server.add_compnode(node.address, node.num_gpu_blocks)
    print("Total compnodes: ", server.get_compnode_count())
    return {"status": "success"}

@app.post("/mempool")
def add_mempool(pool: MemPoolCreate, server: MetadataServer = Depends(get_metadata_server)):
    """Add a new memory pool to the server."""
    server.add_mempool(pool.address, pool.num_blocks)
    print("Total mempools: ", server.get_mempool_count())
    return {"status": "success"}

@app.put("/compnode/sync")
def sync_compnode(address: str, data: CompNodeSync, server: MetadataServer = Depends(get_metadata_server)):
    """Sync the status of a compute node."""
    try:
        server.sync_compnode(address, data.request_count, data.gpu_blocks)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put("/mempool/sync")
def sync_mempool(address: str, data: MemPoolSync, server: MetadataServer = Depends(get_metadata_server)):
    """Sync the status of a memory pool."""
    try:
        server.sync_mempool(address, data.blocks)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/compnode/block")
def add_block_to_compnode(address: str, data: BlockData, server: MetadataServer = Depends(get_metadata_server)):
    """Add a single block to a compute node."""
    try:
        server.add_block_to_compnode(address, data.block)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/compnode/block")
def delete_block_from_compnode(address: str, data: BlockData, server: MetadataServer = Depends(get_metadata_server)):
    """Delete a single block from a compute node."""
    try:
        server.delete_block_from_compnode(address, data.block)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/compnode/blocks")
def add_blocks_to_compnode(address: str, data: BlocksData, server: MetadataServer = Depends(get_metadata_server)):
    """Add multiple blocks to a compute node."""
    try:
        server.add_blocks_to_compnode(address, data.blocks)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/compnode/blocks")
def delete_blocks_from_compnode(address: str, data: BlocksData, server: MetadataServer = Depends(get_metadata_server)):
    """Delete multiple blocks from a compute node."""
    try:
        server.delete_blocks_from_compnode(address, data.blocks)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/mempool/block")
def add_block_to_mempool(address: str, data: BlockData, server: MetadataServer = Depends(get_metadata_server)):
    """Add a single block to a memory pool."""
    try:
        server.add_block_to_mempool(address, data.block)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/mempool/block")
def delete_block_from_mempool(address: str, data: BlockData, server: MetadataServer = Depends(get_metadata_server)):
    """Delete a single block from a memory pool."""
    try:
        server.delete_block_from_mempool(address, data.block)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/mempool/blocks")
def add_blocks_to_mempool(address: str, data: BlocksData, server: MetadataServer = Depends(get_metadata_server)):
    """Add multiple blocks to a memory pool."""
    try:
        server.add_blocks_to_mempool(address, data.blocks)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/mempool/blocks")
def delete_blocks_from_mempool(address: str, data: BlocksData, server: MetadataServer = Depends(get_metadata_server)):
    """Delete multiple blocks from a memory pool."""
    try:
        server.delete_blocks_from_mempool(address, data.blocks)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/mempool/free_blocks")
def get_mempool_free_blocks(address: str, server: MetadataServer = Depends(get_metadata_server)):
    """Get the number of free blocks in a memory pool."""
    try:
        return server.mempools[address].get_free_blocks()
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Memory pool with address {address} not found")

@app.post("/mempool/hits")
def get_mempool_hits(address: str, data: BlocksData, server: MetadataServer = Depends(get_metadata_server)):
    """Get the number of hits for a list of blocks in a memory pool."""
    try:
        return server.mempools[address].get_block_hits(data.blocks)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Memory pool with address {address} not found")

# vLLM API interaction endpoints
@app.post("/completions")
async def completions(request: CompletionRequest, server: MetadataServer = Depends(get_metadata_server)):
    """Process completions request, tokenize input, and forward to vLLM API."""
    try:
        # Tokenize the prompt
        if isinstance(request.prompt, str):
            tokens = await server.tokenize(request.prompt)
        else:
            # Handle list of prompts - just use the first one for now
            tokens = await server.tokenize(request.prompt[0])
            
        # Find the best compute node for this request
        target_address = server.get_target_compnode(tokens)
        
        # Forward the request to the target compute node
        if request.stream:
            return StreamingResponse(
                server.stream_response(target_address, "/v1/completions", request.model_dump()),
                media_type="text/event-stream"
            )
        else:
            response, status_code = await server.non_streaming_request(target_address, "/v1/completions", request.model_dump())
            return JSONResponse(content=response, status_code=status_code)
            
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# @app.post("/chat/completions")
# async def chat_completions(request: ChatCompletionRequest, server: MetadataServer = Depends(get_metadata_server)):
#     """Process chat completions request, tokenize input, and forward to vLLM API."""
#     try:
#         # Tokenize the messages
#         tokens = await server.tokenize(request.messages)
            
#         # Find the best compute node for this request
#         target_compnode_id = server.get_target_compnode(tokens)
        
#         # Forward the request to the target compute node
#         if request.stream:
#             return StreamingResponse(
#                 server.stream_response(target_compnode_id, "/v1/chat/completions", request.model_dump()),
#                 media_type="text/event-stream"
#             )
#         else:
#             response, status_code = await server.non_streaming_request(target_compnode_id, "/v1/chat/completions", request.model_dump())
#             return JSONResponse(content=response, status_code=status_code)
            
#     except Exception as e:
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)