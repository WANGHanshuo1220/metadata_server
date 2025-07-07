import uvicorn
from fastapi import FastAPI, HTTPException, Depends

from common.utils import *
from metadata_server import MetadataServer

# Create FastAPI app
app = FastAPI(title="Metadata Server API", description="API for managing compute nodes and memory pools")

# Create a global instance of MetadataServer
metadata_server = MetadataServer()

# Dependency to get the metadata server instance
def get_metadata_server():
    return metadata_server

##############################################################
#                      Add Nodes APIs                        #
##############################################################
@app.post("/compnode/add_node")
def add_compnode(cn_info: CompNodeCreate, server: MetadataServer = Depends(get_metadata_server)):
    """Add a new compute node to the server."""
    print(f"Add a cn")
    server.add_cn(cn_info)
    return {"status": f"Add cn success ({server.total_cn_count} CNs now)"}

@app.post("/mempool/add_node")
def add_memnode(mn_info: MemNodeCreate, server: MetadataServer = Depends(get_metadata_server)):
    """Add a new memory pool to the server."""
    print(f"Add a mn {mn_info.node_type}")
    server.add_mn(mn_info)
    return {"status": f"Add mn success ({server.mn_count} MNs now)"}


##############################################################
#                      Get Nodes APIs                        #
##############################################################
@app.post("/compnode/schedule_prefill")
def schedule_prefill(request: GetCompNode, server: MetadataServer = Depends(get_metadata_server)):
    """Schudule a comp node for prefilling stage."""
    print(f"Schedule a prefill")
    ret = server.schedule_prefill(request)
    return {"data": ret}

@app.post("/compnode/schedule_decode")
def schedule_decode(request: GetCompNode, server: MetadataServer = Depends(get_metadata_server)):
    """Schudule a comp node for prefilling stage."""
    print(f"Schedule a decode")
    ret = server.schedule_decode(request)
    return {"data": ret}


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
        num_cached_blocks = server.sync_memnode(data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"status": f"Sync mn {data.host} success ({num_cached_blocks} cached blocks now)"}

@app.post("/mempool/blocks")
def add_blocks_to_mempool(data: MemNodeSync, server: MetadataServer = Depends(get_metadata_server)):
    """Add multiple blocks to a memory pool."""
    try:
        num_cached_blocks = server.add_blocks_to_mempool(data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"status": f"Sync mn {data.host} success ({num_cached_blocks} cached blocks now)"}

@app.post("/mempool/hits")
def get_mempool_hits(server: MetadataServer = Depends(get_metadata_server)):
    """Get the number of hits for a list of blocks in a memory pool."""
    hit_rate = server.get_mempool_hit_rate()
    return {"ret": hit_rate}

@app.get("/save_time_metrics")
def save_time_metrics(server: MetadataServer = Depends(get_metadata_server)):
    print(f"Save time metrics not imple yet")
    return


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6666)