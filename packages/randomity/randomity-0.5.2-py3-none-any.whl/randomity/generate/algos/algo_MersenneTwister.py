class _MersenneTwister:
    def __init__(self, seed: int):
        # MT19937 constants
        self.w = 32
        self.n = 624
        self.m = 397
        self.r = 31
        self.a = 0x9908B0DF
        self.u = 11
        self.d = 0xFFFFFFFF
        self.s = 7
        self.b = 0x9D2C5680
        self.t = 15
        self.c = 0xEFC60000
        self.l = 18
        self.f = 1812433253

        self.mt = [0] * self.n
        self.index = self.n + 1

        self.seed_mt(seed)

    def seed_mt(self, seed: int):
        self.mt[0] = seed & 0xFFFFFFFF
        for i in range(1, self.n):
            self.mt[i] = (self.f * (self.mt[i-1] ^ (self.mt[i-1] >> (self.w-2))) + i) & 0xFFFFFFFF
        self.index = self.n

    def twist(self):
        for i in range(self.n):
            x = (self.mt[i] & (1 << self.w)) + (self.mt[(i+1) % self.n] & ((1 << self.w) - 1))
            xA = x >> 1
            if (x % 2) != 0:
                xA = xA ^ self.a

            self.mt[i] = self.mt[(i + self.m) % self.n] ^ xA

    def extract_number(self):
        if self.index >= self.n:
            self.twist()
            self.index = 0

        y = self.mt[self.index]
        self.index += 1

        y = y ^ (y >> self.u)
        y = y ^ ((y << self.s) & self.b)
        y = y ^ ((y << self.t) & self.c)
        y = y ^ (y >> self.l)

        return y & 0xFFFFFFFF