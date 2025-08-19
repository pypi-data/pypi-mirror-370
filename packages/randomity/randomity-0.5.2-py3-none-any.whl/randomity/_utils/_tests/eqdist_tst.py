import numpy as np

def eqdist_test(data):
    """
    Calculates the difference between empirical and expected mean.
    """
    min_val, max_val = np.min(data), np.max(data)

    if max_val == min_val:
        data_scaled = np.zeros_like(data, dtype=float)
    else:
        data_scaled = (data - min_val) / (max_val - min_val)
        
    empirical_mean_val = np.mean(data_scaled)
    expected_mean = 0.5
    diff = abs(empirical_mean_val - expected_mean)
    
    return {
        'eqdist_empiricalMean': empirical_mean_val,
        'eqdist_diff': diff
    }