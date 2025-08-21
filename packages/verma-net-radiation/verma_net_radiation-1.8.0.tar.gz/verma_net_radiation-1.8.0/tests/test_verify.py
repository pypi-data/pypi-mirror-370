import pytest
from verma_net_radiation import verify

def test_verify():
    assert verify(), "Model verification failed: outputs do not match expected results."
