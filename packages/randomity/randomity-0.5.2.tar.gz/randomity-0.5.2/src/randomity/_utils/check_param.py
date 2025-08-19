def _checkParam_prandom(min_val, max_val, num_out, algo, seed, hist):
    """
    Checks for the validity of parameters in prandom().
    """
    if not isinstance(max_val, int) or not isinstance(min_val, int) or min_val >= max_val:
        raise ValueError("min_val must be less than max_val and both must be integers")
    
    if not isinstance(hist, bool):
        raise ValueError("hist must be a boolean value")
    
    if not isinstance(num_out, int) or num_out <= 0 or isinstance(num_out, bool):
        raise ValueError("num_out must be a positive integer")
    
    algos = {
        "MersenneTwister": ["mt", "mersennetwister"],
        "XORShift": ["xor", "xorshift"],
        "LCG": ["linearcongruentialgenerator", "lcg"],
        "MTNumpy": ["numpy", "mtnumpy", "mersennetwisternumpy"],
        "BlumBlumShub": ["bbs", "blumblumshub"],
        "MiddleSquare": ["middlesquare", "midsquare"]
    }

    if not(any(algo in aliases for aliases in algos.values())):
        print(f"Unsupported algorithm: '{algo}'. Defaulting to MersenneTwister instead.")

    if not isinstance(seed, (int, type(None))):
        raise ValueError("seed must be an integer or None")
    
    if seed is not None and (not isinstance(seed, int) or seed < 0):
        raise ValueError("seed must be a non-negative integer or left as None")

def _checkParam_pseudoFunc(min_val, max_val, num_out, seed):
    """
    Checks for the validity of parameters in pseudo functions.
    """
    if not isinstance(max_val, int) or not isinstance(min_val, int) or min_val >= max_val:
        raise ValueError("min_val must be less than max_val and both must be integers")
    
    if not isinstance(num_out, int) or num_out <= 0 or isinstance(num_out, bool):
        raise ValueError("num_out must be a positive integer")
    
    if not isinstance(seed, (int, type(None))):
        raise ValueError("seed must be an integer or None")
    
    if seed is not None and (not isinstance(seed, int) or seed < 0):
        raise ValueError("seed must be a non-negative integer or left as None")

def _checkParam_qrandom(min_val, max_val, num_out, q_gate, hist):
    """
    Checks for the validity of parameters in qrandom().
    """
    if not isinstance(max_val, int) or not isinstance(min_val, int) or min_val >= max_val:
        raise ValueError("min_val must be less than max_val and both must be integers")
    
    if not isinstance(hist, bool):
        raise ValueError("hist must be a boolean value")
    
    if not isinstance(num_out, int) or num_out <= 0 or isinstance(num_out, bool):
        raise ValueError("num_out must be a positive integer")
    
    if q_gate not in ["h", "rx", "ry", "sx"]:
        print("Gate not available. Using Hadamard gate instead.")

def _checkParam_histogram(data, bins, title, xlabel, ylabel, color, alpha, edgecolor, grid):
    """
    Checks for the validity of parameters in histogram utility function.
    """
    if not isinstance(data, list) or len(data) == 0:
        raise ValueError("data must be a non-empty list")
    
    if not (isinstance(bins, int) and bins > 0) and not (isinstance(bins, list) and all(isinstance(b, (int, float)) for b in bins)):
        raise ValueError("bins must be a positive integer or a list of numbers")
    
    if not isinstance(title, str):
        raise ValueError("title must be a string")
    
    if not isinstance(xlabel, str):
        raise ValueError("xlabel must be a string")
    
    if not isinstance(ylabel, str):
        raise ValueError("ylabel must be a string")
    
    if not isinstance(color, str):
        raise ValueError("color must be a supported color string")
    
    if not isinstance(alpha, (int, float)) or not (0.0 <= alpha <= 1.0):
        raise ValueError("alpha must be a float between 0.0 and 1.0")
    
    if not isinstance(edgecolor, str):
        raise ValueError("edgecolor must be a supported color string")
    
    if not isinstance(grid, bool):
        raise ValueError("grid must be a boolean value")
    
def _checkParam_isRandom(sequence, threshold):
    """
    Checks for the validity of parameters in isRandom().
    """
    if not isinstance(sequence, list) or len(sequence) == 0:
        raise ValueError("sequence must be a non-empty list")
    
    if len(sequence) < 2:
        raise ValueError("sequence must contain at least two elements to evaluate randomness")

    if not all(isinstance(item, int) for item in sequence):
        raise ValueError("All items in sequence must be integers")

    if not isinstance(threshold, float) or not (0.0 <= threshold <= 1.0):
        raise ValueError("threshold must be a value between 0.0 and 1.0")
    
def _checkParam_inspectRandom(sequence):
    """
    Checks for the validity of parameters in inspectRandom().
    """
    if not isinstance(sequence, list) or len(sequence) == 0:
        raise ValueError("sequence must be a non-empty list")
    
    if len(sequence) < 2:
        raise ValueError("sequence must contain at least two elements to evaluate randomness")

    if not all(isinstance(item, int) for item in sequence):
        raise ValueError("All items in sequence must be integers")