class _LCG:
    def __init__(self, 
                 seed: int, 
                 a: int, c: int, m: int):
        self.a = a
        self.c = c
        self.m = m

        self.x = seed

    def next_int(self) -> int:
        self.x = (self.a * self.x + self.c) % self.m
        return self.x