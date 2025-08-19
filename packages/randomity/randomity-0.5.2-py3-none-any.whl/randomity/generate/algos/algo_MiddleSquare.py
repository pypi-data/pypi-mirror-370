class _MiddleSquare:
    def __init__(self, seed:int):
        self.seed = seed

    def next_int(self) -> int:
        x = self.seed
        num_digits = len(str(x))
        x_squared = x ** 2
        x_str = str(x_squared).zfill(2 * num_digits)
        start_index = (len(x_str) - num_digits) // 2
        middle = x_str[start_index:start_index + num_digits]
        self.seed = int(middle)
        return self.seed