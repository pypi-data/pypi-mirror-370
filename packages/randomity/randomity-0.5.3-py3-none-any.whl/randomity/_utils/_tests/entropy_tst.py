import numpy as np

def entropy_test(data):
    """
    Calculates the Shannon entropy.
    """
    min_val, max_val = np.min(data), np.max(data)
    num_bins = int(max_val - min_val + 1)
    
    bins = np.linspace(min_val, max_val + 1, num=num_bins + 1)
    hist, _ = np.histogram(data, bins=bins)
    probabilities = hist / np.sum(hist)
    
    probabilities = probabilities[probabilities > 0]
    
    entropy_value = -np.sum(probabilities * np.log2(probabilities))
    
    return {'entropy_val': entropy_value}