import numpy as np
from scipy.stats import chisquare

def gap_test(data):
    """
    Performs a chi-squared test on the gaps between numbers in each bin.
    """
    min_val, max_val = np.min(data), np.max(data)
    num_bins = int(max_val - min_val + 1)

    bins = np.linspace(min_val, max_val + 1, num=num_bins + 1)
    binned = np.digitize(data, bins)
    
    gaps = []
    for bin_label in np.unique(binned):
        indices = np.where(binned == bin_label)[0]
        if len(indices) > 1:
            gaps.extend(np.diff(indices))
            
    if not gaps:
        return {'gap_p': np.nan, 'gap_X2': np.nan, 'gap_df': np.nan}
        
    gap_freq = np.bincount(gaps)
    gap_freq = gap_freq[1:]
    
    if len(gap_freq) == 0:
        return {'gap_p': np.nan, 'gap_X2': np.nan, 'gap_df': np.nan}
    
    expected_freq = np.full_like(gap_freq, len(gaps) / len(gap_freq), dtype=float)
    
    if not np.all(expected_freq > 0):
        return {'gap_p': np.nan, 'gap_X2': np.nan, 'gap_df': np.nan}
        
    chi2_stat, p_value = chisquare(gap_freq, f_exp=expected_freq)
    
    return {
        'gap_p': p_value,
        'gap_X2': chi2_stat,
        'gap_df': len(gap_freq) - 1
    }