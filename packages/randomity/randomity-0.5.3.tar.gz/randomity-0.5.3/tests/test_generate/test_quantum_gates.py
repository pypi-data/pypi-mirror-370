import pytest
from src.randomity.generate import qrandom

def test_gates():
    """Test that different quantum gates can be used."""
    gates = ["h", "rx", "ry", "sx"]
    for gate in gates:
        result = qrandom(q_gate=gate)
        assert isinstance(result, list)

def test_invalid_gate():
    """Test fallback to "h" for an invalid quantum gate."""
    out1 = qrandom(q_gate="invalid_gate")
    out2 = qrandom(q_gate=5)
    out3 = qrandom(q_gate=None)
    out4 = qrandom(q_gate=True)
    
    assert isinstance(out1, list)
    assert isinstance(out2, list)
    assert isinstance(out3, list)
    assert isinstance(out4, list)