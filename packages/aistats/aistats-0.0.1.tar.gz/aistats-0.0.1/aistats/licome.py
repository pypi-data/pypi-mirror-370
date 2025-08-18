import numpy as np
def licome(a: int, c: int, x0: int, m: int, count: int):
    """
    Linear Congruential Method (LCM) to generate pseudo-random numbers.

    Parameters:
        a (int): Multiplier
        c (int): Increment
        x0 (int): Seed value (initial value)
        m (int): Modulus
        count (int): Number of pseudo-random numbers to generate

    Returns:
        tuple: A tuple (y, u)
            y (list): Generated sequence of integers
            u (ndarray): Sequence normalized to [0, 1)
    """
    y = [x0]
    for _ in range(count - 1):
        y.append((a * y[-1] + c) % m)
    u = np.divide(y, m)
    return y, u