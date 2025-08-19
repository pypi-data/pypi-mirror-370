import math
import sys
import os

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', ))
sys.path.insert(0, src_dir)

from _utils import (
    _gen_seed_os,
    _make_valid_prime,
    _find_valid_seed
)

class _BlumBlumShub:
    def __init__(self, seed: int = None, p: int = 1009, q: int = 1013, max_attempts: int = 10):
        self.p = _make_valid_prime(p, 3, 4)
        self.q = _make_valid_prime(q, 3, 4)
        self.M = self.p * self.q

        self.seed = seed if seed is not None else _gen_seed_os()

        for _ in range(max_attempts):
            if math.gcd(self.seed, self.M) == 1:
                self.x = pow(self.seed, 2, self.M)
                if self.x not in (0, 1):
                    break
            self.seed = _gen_seed_os()
        else:
            self.seed = _find_valid_seed(self.M)
            self.x = pow(self.seed, 2, self.M)

        self._initial_x = self.x
        self._cycle_detected = False

    def next_int(self) -> int:
        self.x = pow(self.x, 2, self.M)
        if self.x == self._initial_x:
            self._cycle_detected = True
        return self.x

    def next_bit(self) -> int:
        return self.next_int() & 1

    def is_cycling(self) -> bool:
        return self._cycle_detected