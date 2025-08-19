import numpy as np
from scipy.stats import chisquare

def chisqr_test(data):
    """
    Performs a chi-squared test for uniform distribution.
    """
    min_val, max_val = np.min(data), np.max(data)
    
    bins = np.arange(min_val, max_val + 2, 1)
    observed_freq, _ = np.histogram(data, bins=bins)
    
    expected_freq = np.full_like(observed_freq, len(data) / (max_val - min_val + 1), dtype=float)
    
    if not np.all(expected_freq > 0):
        return {'chisqr_p': np.nan, 'chisqr_X2': np.nan, 'chisqr_df': np.nan}
        
    chi2_stat, p_value = chisquare(observed_freq, f_exp=expected_freq)
    
    return {
        'chisqr_p': p_value,
        'chisqr_X2': chi2_stat,
        'chisqr_df': len(observed_freq) - 1
    }