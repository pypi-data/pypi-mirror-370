import pytest
from src.randomity.generate import qrandom

def test_returntType():
    """Test that qrandom returns a list."""
    result = qrandom()
    assert isinstance(result, list)

def test_outputLength():
    """Test that qrandom returns the correct number of outputs."""
    num_out = 5
    result = qrandom(num_out=num_out)
    assert len(result) == num_out

def test_outputRange():
    """Test that generated numbers are within the specified range."""
    min_val = 5
    max_val = 15
    result = qrandom(min_val=min_val, max_val=max_val, num_out=10)
    for num in result:
        assert min_val <= num <= max_val

def test_histogram():
    """Test that histogram is drawn when hist=True."""
    result = qrandom(hist=True)
    assert isinstance(result, list)

def test_invalid_range():
    """Test that an error is raised for invalid range."""
    with pytest.raises(ValueError):
        qrandom(min_val=10, max_val=5)
    with pytest.raises(ValueError):
        qrandom(min_val="five", max_val=10)

def test_invalid_num_out():
    """Test that an error is raised for invalid num_out."""
    with pytest.raises(ValueError):
        qrandom(num_out=0)
    with pytest.raises(ValueError):
        qrandom(num_out=-1)
    with pytest.raises(ValueError):
        qrandom(num_out="five")
    with pytest.raises(ValueError):
        qrandom(num_out=0.5)
    with pytest.raises(ValueError):
        qrandom(num_out=True)

def test_invalid_hist():
    """Test that an error is raised for invalid hist."""
    with pytest.raises(ValueError):
        qrandom(hist="yes")
    with pytest.raises(ValueError):
        qrandom(hist=1)
    with pytest.raises(ValueError):
        qrandom(hist=0.5)