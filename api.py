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
    num_gpu_blocks: int
    api_base: str

class MemPoolCreate(BaseModel):
    num_blocks: int

class CompNodeSync(BaseModel):
    request_count: int
    gpu_blocks: Dict[int, int]

class MemPoolSync(BaseModel):
    blocks: Dict[int, int]

class ServerStats(BaseModel):
    compnode_count: int
    mempool_count: int

class TokenSequence(BaseModel):
    sequence: List[int]

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

@app.post("/compnode", response_model=int)
def add_compnode(node: CompNodeCreate, server: MetadataServer = Depends(get_metadata_server)):
    """Add a new compute node to the server."""
    compnode_id = server.add_compnode(node.num_gpu_blocks, node.api_base)
    print("Total compnodes: ", server.get_compnode_count())
    return compnode_id

@app.post("/mempool", response_model=int)
def add_mempool(pool: MemPoolCreate, server: MetadataServer = Depends(get_metadata_server)):
    """Add a new memory pool to the server."""
    mempool_id = server.add_mempool(pool.num_blocks)
    print("Total mempools: ", server.get_mempool_count())
    return mempool_id

@app.put("/compnode/{compnode_id}")
def sync_compnode(compnode_id: int, data: CompNodeSync, server: MetadataServer = Depends(get_metadata_server)):
    """Sync the status of a compute node."""
    if compnode_id >= server.get_compnode_count() or compnode_id < 0:
        raise HTTPException(status_code=404, detail="Compute node not found")
    
    server.sync_compnode(compnode_id, data.request_count, data.gpu_blocks)
    return {"status": "success"}

@app.put("/mempool/{mempool_id}")
def sync_mempool(mempool_id: int, data: MemPoolSync, server: MetadataServer = Depends(get_metadata_server)):
    """Sync the status of a memory pool."""
    if mempool_id >= server.get_mempool_count() or mempool_id < 0:
        raise HTTPException(status_code=404, detail="Memory pool not found")
    
    server.sync_mempool(mempool_id, data.blocks)
    return {"status": "success"}

@app.get("/mempool/{mempool_id}/unused_blocks", response_model=int)
def get_mempool_unused_blocks(mempool_id: int, server: MetadataServer = Depends(get_metadata_server)):
    """Get the number of unused blocks in a memory pool."""
    if mempool_id >= server.get_mempool_count() or mempool_id < 0:
        raise HTTPException(status_code=404, detail="Memory pool not found")
    
    return server.mempools[mempool_id].get_unused_blocks()

@app.get("/mempool/{mempool_id}/free_blocks", response_model=int)
def get_mempool_free_blocks(mempool_id: int, server: MetadataServer = Depends(get_metadata_server)):
    """Get the number of free blocks in a memory pool."""
    if mempool_id >= server.get_mempool_count() or mempool_id < 0:
        raise HTTPException(status_code=404, detail="Memory pool not found")
    
    return server.mempools[mempool_id].get_free_blocks()

@app.post("/mempool/{mempool_id}/hits", response_model=int)
def get_mempool_hits(mempool_id: int, token_seq: TokenSequence, server: MetadataServer = Depends(get_metadata_server)):
    """Get the number of hits for a token sequence in a memory pool."""
    if mempool_id >= server.get_mempool_count() or mempool_id < 0:
        raise HTTPException(status_code=404, detail="Memory pool not found")
    
    return server.mempools[mempool_id].get_hits(token_seq.sequence)

# vLLM API interaction endpoints
@app.post("/completions")
async def completions(request: CompletionRequest, server: MetadataServer = Depends(get_metadata_server)):
    """Process completions request, tokenize input, and forward to vLLM API."""
    try:
        # First tokenize the prompt
        prompt_text = request.prompt
        
        tokens = await server.tokenize(prompt_text)
        
        target_compnode = server.get_target_compnode(tokens)

        # Prepare the request payload
        request_payload = request.model_dump(exclude_unset=True)
        
        # Check if streaming is requested
        if request.stream:
            # Return a streaming response
            return StreamingResponse(
                server.stream_response(target_compnode, "/v1/completions", request_payload),
                media_type="text/event-stream"
            )
        else:
            # Make a non-streaming request
            response_data, status_code = await server.non_streaming_request(target_compnode, "/v1/completions", request_payload)
            return JSONResponse(content=response_data, status_code=status_code)
        
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )

# @app.post("/chat/completions")
# async def chat_completions(request: ChatCompletionRequest, server: MetadataServer = Depends(get_metadata_server)):
#     """Process chat completions request, tokenize input, and forward to vLLM API."""
#     try:
#         # First tokenize the messages
#         messages = [message.model_dump() for message in request.messages]
#         tokens = await server.tokenize(messages)
        
#         # Print the token IDs
#         print(f"Tokenized messages: {tokens}")
        
#         # Prepare the request payload
#         request_payload = request.model_dump(exclude_unset=True)
        
#         # Check if streaming is requested
#         if request.stream:
#             # Return a streaming response
#             return StreamingResponse(
#                 server.stream_response("/v1/chat/completions", request_payload),
#                 media_type="text/event-stream"
#             )
#         else:
#             # Make a non-streaming request
#             response_data, status_code = await server.non_streaming_request("/v1/chat/completions", request_payload)
#             return JSONResponse(content=response_data, status_code=status_code)
        
#     except Exception as e:
#         return JSONResponse(
#             content={"error": str(e)},
#             status_code=500
#         )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)