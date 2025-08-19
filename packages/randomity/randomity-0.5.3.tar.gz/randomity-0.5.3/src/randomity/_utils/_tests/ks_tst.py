import numpy as np
from scipy.stats import kstest

def ks_test(data):
    """
    Performs a Kolmogorov-Smirnov test for uniform distribution.
    """
    min_val, max_val = np.min(data), np.max(data)
    if max_val == min_val:
        data_scaled = np.zeros_like(data, dtype=float)
    else:
        data_scaled = (data - min_val) / (max_val - min_val)
    
    stat, p_value = kstest(data_scaled, 'uniform')
    
    return {
        'ks_p': p_value,
        'ks_D': stat
    }