import numpy as np

from ._tests import (
    chisqr_test, 
    ks_test, 
    freq_test, 
    eqdist_test, 
    gap_test, 
    serial_test, 
    permute_test, 
    entropy_test, 
    ftt_test
)

def _gen_test_vector(sequence: list) -> dict:
    """
    Generate a result vector from the given sequence of numbers.

    Args:
        sequence (list): A list of integers representing the sequence to be tested.

    Returns:
        dict: A dictionary containing the results of various statistical tests.
    """
    seq_numbers = np.array(sequence)

    test_results = {}
    test_results.update(chisqr_test(seq_numbers))
    test_results.update(ks_test(seq_numbers))
    test_results.update(freq_test(seq_numbers))
    test_results.update(eqdist_test(seq_numbers))
    test_results.update(gap_test(seq_numbers))
    test_results.update(serial_test(seq_numbers))
    test_results.update(permute_test(seq_numbers))
    test_results.update(entropy_test(seq_numbers))
    test_results.update(ftt_test(seq_numbers))

    return test_results