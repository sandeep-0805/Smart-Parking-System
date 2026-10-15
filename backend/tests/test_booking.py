from datetime import datetime, timedelta
import pytest
from app.utils import generate_blocks, round_down_to_block, round_up_to_block

def test_generate_blocks_15_mins():
    start = datetime(2026, 10, 15, 10, 0, 0)
    end = datetime(2026, 10, 15, 11, 0, 0)
    blocks = generate_blocks(start, end, granularity_mins=15)
    
    # 1 hour with 15-min blocks = 4 blocks
    assert len(blocks) == 4
    assert blocks[0] == datetime(2026, 10, 15, 10, 0, 0)
    assert blocks[1] == datetime(2026, 10, 15, 10, 15, 0)
    assert blocks[2] == datetime(2026, 10, 15, 10, 30, 0)
    assert blocks[3] == datetime(2026, 10, 15, 10, 45, 0)

def test_generate_blocks_unaligned():
    start = datetime(2026, 10, 15, 10, 5, 0)
    end = datetime(2026, 10, 15, 10, 40, 0)
    blocks = generate_blocks(start, end, granularity_mins=15)
    # Starts at 10:00 (rounded down), ends at 10:45 (rounded up)
    # [10:00, 10:15, 10:30]
    assert len(blocks) == 3
    assert blocks[0] == datetime(2026, 10, 15, 10, 0, 0)
