from typing import List, Optional, Union
from pydantic import BaseModel


HostIP = int
PORT = int


# Pydantic models for request/response validation

# Node creation
class CompNodeCreate(BaseModel):
    host: HostIP
    port: PORT
    role: str
    num_gpu_blocks: int

class MemNodeCreate(BaseModel):
    host: HostIP
    node_type: str
    num_blocks: int

# Node get
class GetCompNode(BaseModel):
    block_hashes: List[int]

class GetMemNode(BaseModel):
    block_hashes: List[int]

class GetDisaggNodePair(BaseModel):
    seq_length: int

# Node sync
class CompNodeSync(BaseModel):
    host: HostIP
    port: PORT
    role: str
    request_count: int
    gpu_blocks: List[int]

class MemNodeSync(BaseModel):
    host: HostIP
    port: PORT
    block_hashes: List[int]


class Counter:

    def __init__(self, start: int = 0) -> None:
        self.counter = start

    def __next__(self) -> int:
        i = self.counter
        self.counter += 1
        return i

    def reset(self) -> None:
        self.counter = 0