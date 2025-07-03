import uvicorn
from fastapi import FastAPI, HTTPException, Depends

from common.utils import *
from metadata_server.metadata_server import MetadataServer

# Create FastAPI app
app = FastAPI(title="Metadata Server API", description="API for managing compute nodes and memory pools")

# Create a global instance of MetadataServer
metadata_server = MetadataServer()

# Dependency to get the metadata server instance
def get_metadata_server():
    return metadata_server

# Endpoints
@app.get("/", response_model=ServerStats)
def get_server_stats(server: MetadataServer = Depends(get_metadata_server)):
    """Get the current server statistics."""
    return {
        "compnode_count": server.total_cn_count,
        "mempool_count": server.mn_count
    }


##############################################################
#                      Add Nodes APIs                        #
##############################################################
@app.post("/compnode/add_node")
def add_compnode(cn_info: CompNodeCreate, server: MetadataServer = Depends(get_metadata_server)):
    """Add a new compute node to the server."""
    server.add_cn(cn_info)
    print("Total compnodes: ", server.total_cn_count)
    return {"status": "success"}

@app.post("/mempool/add_node")
def add_memnode(mn_info: MemNodeCreate, server: MetadataServer = Depends(get_metadata_server)):
    """Add a new memory pool to the server."""
    server.add_mn(mn_info)
    print("Total memnodes: ", server.mn_count)
    return {"status": "success"}


##############################################################
#                      Get Nodes APIs                        #
##############################################################
@app.get("/mempool/get_api")
def get_memnode(request: GetMemNode, server: MetadataServer = Depends(get_metadata_server)):
    """Schudule a mem node."""
    mn_addr = server.get_mn(request)
    return {"data": mn_addr}

@app.get("/get_disagg_pair_api")
def get_disagg_pair(request: GetDisaggNodePair, server: MetadataServer = Depends(get_metadata_server)):
    """Schudule a mem node."""
    disagg_pair_info = server.get_disagg_pair_api(request)
    return {"data": disagg_pair_info}


##############################################################
#                     Update Stats APIs                      #
##############################################################
@app.put("/compnode/sync")
def sync_compnode(data: CompNodeSync, server: MetadataServer = Depends(get_metadata_server)):
    """Sync the status of a compute node."""
    try:
        server.sync_compnode(data)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put("/mempool/sync")
def sync_memnode(data: MemNodeSync, server: MetadataServer = Depends(get_metadata_server)):
    """Sync the status of a memory pool."""
    try:
        server.sync_memnode(data)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/mempool/blocks")
def add_blocks_to_mempool(data: MemNodeSync, server: MetadataServer = Depends(get_metadata_server)):
    """Add multiple blocks to a memory pool."""
    try:
        server.add_blocks_to_mempool(data)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/mempool/hits")
def get_mempool_hits(server: MetadataServer = Depends(get_metadata_server)):
    """Get the number of hits for a list of blocks in a memory pool."""
    hit_rate = server.get_mempool_hit_rate()
    return {"ret": hit_rate}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6666)