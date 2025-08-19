import warnings
warnings.filterwarnings("ignore")

from .._utils.check_param import _checkParam_prandom
from .._utils.check_param import _checkParam_pseudoFunc
from .._utils.gen_seed import _gen_seed_os
from .._utils.draw_histogram import _draw_histogram

from .algos import (
    _MersenneTwister,
    _XORShift,
    _LCG,
    _MTNumpy,
    _BlumBlumShub,
    _MiddleSquare
)

def prandom(min_val:int=0,
            max_val:int=10,
            num_out:int=1,
            algo:str="MersenneTwister",
            seed:int|None=None,
            hist=False) -> list[int]:
    """
    Generate a random number using a pseudo-random number generator (PRNG).

    Args:
        min_val (integer): Minimum value of the random number. Default is 0.
        max_val (integer): Maximum value of the random number. Default is 10.
        num_out (integer): Number of numbers to generate. Default is 1.
        algo (string): Algorithm to use for generating random numbers. Options are:
                        - "MersenneTwister" (or "MT"), 
                        - "XORShift" (or "XOR"), 
                        - "LCG" (or "LinearCongruentialGenerator"),
                        - "MTNumpy" (or "MersenneTwisterNumpy" or "Numpy"),
                        - "BlumBlumShub" (or "BBS").
                        - "MiddleSquare".
                    Default is "MersenneTwister".
        seed (integer): Seed for the random number generator. Default is current system's time.
        hist (boolean): Whether to display a histogram of the generated numbers. Default is False.

    Returns:
         A list of random integers.
    """
    if seed is None:
        seed = _gen_seed_os()

    algo = algo.lower()

    _checkParam_prandom(min_val, max_val, num_out, algo, seed, hist)

    if algo == "mersennetwister" or algo == "mt":
        random_numbers = mersenne_twister(min_val=min_val, max_val=max_val, num_out=num_out, seed=seed)
    elif algo == "xorshift" or algo == "xor":
        random_numbers = xor_shift(min_val=min_val, max_val=max_val, num_out=num_out, seed=seed)
    elif algo == "lcg" or algo == "linearcongruentialgenerator":
        random_numbers = lcg(min_val=min_val, max_val=max_val, num_out=num_out, seed=seed)
    elif algo == "mtnumpy" or algo == "mersennetwisternumpy" or algo == "numpy":
        random_numbers = mt_numpy(min_val=min_val, max_val=max_val, num_out=num_out, seed=seed)
    elif algo == "blumblumshub" or algo == "bbs":
        random_numbers = blum_blum_shub(min_val=min_val, max_val=max_val, num_out=num_out, seed=seed)
    elif algo == "midsquare" or algo == "midsquare":
        random_numbers = middle_square(min_val=min_val, max_val=max_val, num_out=num_out, seed=seed)
    else:
        random_numbers = mersenne_twister(min_val=min_val, max_val=max_val, num_out=num_out, seed=seed)

    if hist:
        _draw_histogram(random_numbers, 
             bins=10, 
             title='Histogram of Random Numbers', 
             xlabel='Value', 
             ylabel='Frequency', 
             color='tab:blue', 
             alpha=0.7, 
             edgecolor='black',
             grid=True)
        
    return random_numbers


def mersenne_twister(min_val:int=0, max_val:int=10, num_out:int=1, seed:int|None=None):
    if seed is None:
        seed = _gen_seed_os()

    _checkParam_pseudoFunc(min_val, max_val, num_out, seed)

    rng = _MersenneTwister(seed)
    random_numbers = []

    range_size = max_val - min_val + 1
    max_32bit = 2**32 - 1
    for _ in range(num_out):
        raw_number = rng.extract_number()
        scaled_number = min_val + int((raw_number / max_32bit) * range_size)
        random_numbers.append(scaled_number)

    return random_numbers

def xor_shift(min_val:int=0, max_val:int=10, num_out:int=1, seed:int|None=None):
    if seed is None:
        seed = _gen_seed_os()

    _checkParam_pseudoFunc(min_val, max_val, num_out, seed)

    rng = _XORShift(seed)
    random_numbers = []
    range_size = max_val - min_val + 1
    
    for _ in range(num_out):
        raw_number = rng.next_int()
        scaled_number = min_val + (raw_number % range_size)
        random_numbers.append(scaled_number)
        
    return random_numbers

def lcg(min_val:int=0, max_val:int=10, num_out:int=1, seed:int|None=None, a: int = 1664525, c: int = 1013904223, m: int = 2**32):
    if seed is None:
        seed = _gen_seed_os()

    _checkParam_pseudoFunc(min_val, max_val, num_out, seed)

    rng = _LCG(seed, a=a, c=c, m=m)
    random_numbers = []
    range_size = max_val - min_val + 1
    
    for _ in range(num_out):
        raw_number = rng.next_int()
        scaled_number = min_val + (raw_number % range_size)
        random_numbers.append(scaled_number)

    return random_numbers

def mt_numpy(min_val:int=0, max_val:int=10, num_out:int=1, seed:int|None=None):
    if seed is None:
        seed = _gen_seed_os()

    _checkParam_pseudoFunc(min_val, max_val, num_out, seed)

    rng = _MTNumpy(seed)
    random_numbers = [min_val + (rng.extract_number() % (max_val - min_val + 1)) for _ in range(num_out)]

    return random_numbers

def blum_blum_shub(min_val:int=0, max_val:int=10, num_out:int=1, seed:int|None=None):
    if seed is None:
        seed = _gen_seed_os()

    _checkParam_pseudoFunc(min_val, max_val, num_out, seed)

    try:
        rng = _BlumBlumShub(seed)
    except ValueError as e:
        print(f"Error initializing BlumBlumShub: {e}")
        return []

    random_numbers = []
    range_size = max_val - min_val + 1
    
    for _ in range(num_out):
        raw_number = rng.next_int()
        scaled_number = min_val + (raw_number % range_size)
        random_numbers.append(scaled_number)
        
    return random_numbers

def middle_square(min_val:int=0, max_val:int=10, num_out:int=1, seed:int|None=None):
    if seed is None:
        seed = _gen_seed_os()

    _checkParam_pseudoFunc(min_val, max_val, num_out, seed)

    rng = _MiddleSquare(seed)
    random_numbers = []
    
    for _ in range(num_out):
        raw_number = rng.next_int()
        scaled_number = min_val + (raw_number % (max_val - min_val + 1))
        random_numbers.append(scaled_number)

    return random_numbers