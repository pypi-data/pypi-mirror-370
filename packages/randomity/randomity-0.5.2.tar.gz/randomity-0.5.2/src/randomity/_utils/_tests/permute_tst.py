import numpy as np
from itertools import permutations

def permute_test(data, block_size=5, num_permutations=1000):
    """
    Performs a permutation test.
    """
    def calculate_statistic(data, block_size):
        num_blocks = len(data) // block_size
        data_trimmed = data[:num_blocks * block_size]
        blocks = data_trimmed.reshape(num_blocks, block_size)
        block_means = np.mean(blocks, axis=1)
        return np.mean(block_means)

    observed_stat = calculate_statistic(data, block_size)
    
    permuted_stats = []
    for _ in range(num_permutations):
        permuted_data = np.random.permutation(data)
        permuted_stats.append(calculate_statistic(permuted_data, block_size))
        
    permuted_stats = np.array(permuted_stats)
    p_value = np.mean(np.abs(permuted_stats - np.mean(permuted_stats)) >= 
                      np.abs(observed_stat - np.mean(permuted_stats)))

    return {
        'perm_observed_stat': observed_stat,
        'perm_p': p_value
    }