from dataclasses import dataclass
from typing import List, Optional
from pydantic import BaseModel


HostIP = str
PORT = int


# Pydantic models for request/response validation

# Node creation
class CompNodeCreate(BaseModel):
    host: HostIP
    port: PORT
    role: str # prefill or decode or cpu
    num_blocks: int

class MemNodeCreate(BaseModel):
    host: HostIP
    node_type: str # Prefill or Decode
    num_blocks: int

# Node get
class GetCompNode(BaseModel):
    block_hashes: List[int]
    # Used for schedule decode
    direct_hybrid: Optional[bool] = None

# Node sync
class CompNodeSync(BaseModel):
    host: HostIP
    port: PORT
    role: str # prefill or decode or cpu
    request_count: int
    gpu_blocks: List[int]

class MemNodeSync(BaseModel):
    host: HostIP
    node_type: str # Prefill or Decode
    block_hashes: List[int]


@dataclass
class SchedulePrefillOutput:
    cn_host_ip: HostIP
    mn_host_ip: Optional[HostIP]
    cn_port: int
    direct_hybrid_decode: bool

@dataclass
class ScheduleDecodeOutput:
    cn_host_ip: HostIP
    mn_host_ip: Optional[HostIP]
    cn_port: int


class Counter:

    def __init__(self, start: int = 0) -> None:
        self.counter = start

    def __next__(self) -> int:
        i = self.counter
        self.counter += 1
        return i

    def reset(self) -> None:
        self.counter = 0