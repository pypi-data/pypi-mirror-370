import pytest
from src.randomity.generate import prandom

def test_returntType():
    """Test that prandom returns a list."""
    result = prandom()
    assert isinstance(result, list)

def test_outputLength():
    """Test that prandom returns the correct number of outputs."""
    num_out = 5
    result = prandom(num_out=num_out)
    assert len(result) == num_out

def test_outputRange():
    """Test that generated numbers are within the specified range."""
    min_val = 5
    max_val = 15
    result = prandom(min_val=min_val, max_val=max_val, num_out=10)
    for num in result:
        assert min_val <= num <= max_val

def test_histogram():
    """Test that histogram is drawn when hist=True."""
    result = prandom(hist=True)
    assert isinstance(result, list)
    
def test_randSeed():
    """Test that not setting a seed uses the os.urandom method."""
    result1 = prandom(seed=None)
    result2 = prandom()
    result3 = prandom(seed=None)
    result4 = prandom()
    assert (result1 != result2) or (result3 != result4) or (result1 != result3) or (result2 != result4), "Random numbers should differ when no seed is set"

def test_setSeed():
    """Test that setting a seed produces consistent results."""
    seed = 100
    result1 = prandom(seed=seed)
    result2 = prandom(seed=seed)
    assert result1 == result2, "Random numbers should be the same when the same seed is used"

def test_algoSelection():
    """Test that the correct algorithm is selected based on input parameters."""
    valid_algos = ["MersenneTwister", "XORShift", "LCG", "MTNumpy", "BlumBlumShub"]
    for algo in valid_algos:
        result = prandom(algo=algo)
        assert isinstance(result, list), f"Invalid/unsupported algorithm. Should be in {valid_algos}"

def test_algoAbbriviation():
    """Test that algorithm abbreviations work correctly."""
    algo_abbrs = {
        "MersenneTwister": ["MT", "MersenneTwister"],
        "XORShift": ["XOR", "XORShift"],
        "LCG": ["LinearCongruentialGenerator", "LCG"],
        "MTNumpy": ["Numpy", "MTNumpy", "MersenneTwisterNumpy"],
        "BlumBlumShub": ["BBS", "BlumBlumShub"]
    }
    
    for _, abbrs in algo_abbrs.items():
        for abbr in abbrs:
            result = prandom(algo=abbr)
            assert isinstance(result, list), f"Invalid/unsupported algorithm: {abbr}. Should be in {abbrs}"

def test_defaultAlgo():
    """Test that the default algorithm is MersenneTwister."""
    result = prandom()
    assert isinstance(result, list), "Default algorithm should return a list"
    assert len(result) == 1, "Default algorithm should return one output"

def test_invalidAlgo():
    """Test fallback on MersenneTwister when invalid algorithm."""
    result = prandom(algo="InvalidAlgo")
    assert isinstance(result, list), "Expected a list when using an invalid algorithm"
    assert len(result) == 1, "Expected one output when using an invalid algorithm"

def test_invalidMinMax():
    """Test that ValueError is raised for invalid min_val and max_val."""
    with pytest.raises(ValueError):
        prandom(min_val=10, max_val=5)

def test_invalidNumOut():
    """Test that ValueError is raised for invalid num_out."""
    with pytest.raises(ValueError):
        prandom(num_out=-1)
    with pytest.raises(ValueError):
        prandom(num_out=0)
    with pytest.raises(ValueError):
        prandom(num_out="five")

def test_invalidHist():
    """Test that ValueError is raised for invalid hist."""
    with pytest.raises(ValueError):
        prandom(hist="yes")
    with pytest.raises(ValueError):
        prandom(hist=1)
    with pytest.raises(ValueError):
        prandom(hist=0.5)