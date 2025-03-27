import hashlib
from typing import List, Dict

def generate_block_hashes(token_sequence: List[int], block_size: int) -> List[int]:
    """
    Generate block hashes for a sequence of tokens.
    
    Args:
        token_sequence (List[int]): A list of tokens to process
        block_size (int): The size of each block
        
    Returns:
        List[int]: A list of block hashes for full blocks only
    """
    # Calculate how many full blocks we have
    num_full_blocks = len(token_sequence) // block_size
    
    # Initialize the list to store block hashes
    block_hashes = []
    
    # Process each full block
    prev_block_hash = None
    for i in range(num_full_blocks):
        # Get tokens for the current block
        start_idx = i * block_size
        end_idx = start_idx + block_size
        cur_block_tokens = token_sequence[start_idx:end_idx]
        
        # Determine if this is the first block
        is_first_block = (i == 0)
        
        # Compute the hash for this block
        input_str = str(is_first_block) + str(prev_block_hash)
        for token_id in cur_block_tokens:
            input_str = input_str + str(token_id)
        
        _hash_str = hashlib.sha256(input_str.encode())
        _hash = int.from_bytes(_hash_str.digest(), byteorder='big')
        _hash_32bit = _hash & 0xFFFFFFFF  # Masking: keep only the lower 32 bits
        
        # Add the hash to our list
        block_hashes.append(_hash_32bit)
        
        # Update prev_block_hash for the next iteration
        prev_block_hash = _hash_32bit
    
    return block_hashes

class BlockPool:

    def __init__(self, num_blocks: int, block_size: int):
        self.num_blocks = num_blocks
        self.block_size = block_size
        self.blocks = []
        self.active_blocks = []

    def sync_status(self, blocks: Dict[int, int]) -> None:
        assert len(self.blocks) <= len(blocks) <= self.num_blocks

        self.blocks = list(blocks.keys())
        self.active_blocks = [block_id for block_id, status in blocks.items() if status != 0]

    def get_unused_blocks(self) -> int:
        return self.num_blocks - len(self.blocks)

    def get_free_blocks(self) -> int:
        return self.num_blocks - len(self.active_blocks)

    def get_hits(self, seq: List[int]) -> int:
        hashes = generate_block_hashes(seq, self.block_size)
        for i in range(len(hashes)):
            if hashes[i] not in self.blocks:
                return i
        return len(hashes)