from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn

from metadataserver import MetadataServer

# Create FastAPI app
app = FastAPI(title="Metadata Server API", description="API for managing compute nodes and memory pools")

# Create a global instance of MetadataServer
metadata_server = MetadataServer()

# Pydantic models for request/response validation
class CompNodeCreate(BaseModel):
    num_gpu_blocks: int

class MemPoolCreate(BaseModel):
    num_blocks: int
    num_gpus: int

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
    compnode_id = server.add_compnode(node.num_gpu_blocks)
    return compnode_id

@app.post("/mempool", response_model=int)
def add_mempool(pool: MemPoolCreate, server: MetadataServer = Depends(get_metadata_server)):
    """Add a new memory pool to the server."""
    mempool_id = server.add_mempool(pool.num_blocks, pool.num_gpus)
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)