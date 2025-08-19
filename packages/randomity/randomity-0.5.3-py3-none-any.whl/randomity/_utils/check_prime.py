def _is_prime(n: int) -> bool:
    """Check if a number is prime."""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def _make_valid_prime(n: int, a: int, b: int) -> int:
    """Ensure n is a prime ≡ a mod b."""
    while not _is_prime(n) or n % b != a:
        n += 1
    return n


