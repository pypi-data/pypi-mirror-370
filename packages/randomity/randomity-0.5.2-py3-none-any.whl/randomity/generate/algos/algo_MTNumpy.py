import numpy as np

class _MTNumpy:
    def __init__(self, seed: int):
        self.rng = np.random.RandomState(seed)

    def extract_number(self) -> int:
        return self.rng.randint(0, 2**32 - 1)