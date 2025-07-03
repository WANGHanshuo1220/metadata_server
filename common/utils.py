from typing import List, Optional, Union
from pydantic import BaseModel


HostIP = int
PORT = int
NODE_TYPE = str


# Pydantic models for request/response validation

# Node creation
class CompNodeCreate(BaseModel):
    host: HostIP
    port: PORT
    engine_type: str
    role: str
    num_gpu_blocks: int

class MemNodeCreate(BaseModel):
    host: HostIP
    num_blocks: int

# Node get
class GetCompNode(BaseModel):
    seq_length: int

class GetMemNode(BaseModel):
    seq_length: int

class GetDisaggNodePair(BaseModel):
    seq_length: int

# Node sync
class CompNodeSync(BaseModel):
    api_url: CN_API_URL
    role: str
    request_count: int
    gpu_blocks: List[int]

class MemNodeSync(BaseModel):
    address: HostIP
    block_hashes: List[int]

# metadata server stats
class ServerStats(BaseModel):
    compnode_count: int
    mempool_count: int
