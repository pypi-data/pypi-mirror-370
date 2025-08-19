import numpy as np
from scipy.stats import chisquare

def freq_test(data):
    """
    Performs a chi-squared frequency test.
    """
    min_val, max_val = np.min(data), np.max(data)
    num_bins = int(max_val - min_val + 1)
    
    breaks = np.linspace(min_val, max_val + 1, num=num_bins + 1)
    observed_freq, _ = np.histogram(data, bins=breaks)
    
    expected_freq = np.full_like(observed_freq, len(data) / num_bins, dtype=float)
    
    if not np.all(expected_freq > 0):
        return {'freq_p': np.nan, 'freq_X2': np.nan, 'freq_df': np.nan}

    chi2_stat, p_value = chisquare(observed_freq, f_exp=expected_freq)
    
    return {
        'freq_p': p_value,
        'freq_X2': chi2_stat,
        'freq_df': len(observed_freq) - 1
    }