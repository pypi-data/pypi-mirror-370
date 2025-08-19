import math
import os

def _gen_seed_os():
    """
    Generate a seed using the operating system source.
    """
    return int.from_bytes(os.urandom(4), byteorder='big')

def _find_valid_seed(M: int) -> int:
    """Find a seed that is coprime with M and avoids trivial cycles."""
    while True:
        candidate = _gen_seed_os()
        if math.gcd(candidate, M) == 1:
            x = pow(candidate, 2, M)
            if x not in (0, 1):
                return candidate