import numpy as np
from typing import Dict, Union
from .normalization_config import NORMALIZATION_PARAMS

_FEATURES = {
    'uniformity': ['chisqr_p', 'ks_p', 'freq_p', 'eqdist_diff'],
    'patterns': ['gap_p', 'serial_autocorrelation'],
    'periodicity': ['entropy_val', 'fft_max_magnitude']
}

def _get_normalized_score(value: float, feature_name: str) -> float:
    """
    Normalizes a single test result value to a 0-1 score.
    """
    if feature_name in ['chisqr_p', 'ks_p', 'freq_p', 'gap_p']:
        score = float(value)
    
    elif feature_name in NORMALIZATION_PARAMS:
        min_val = NORMALIZATION_PARAMS[feature_name]['min']
        max_val = NORMALIZATION_PARAMS[feature_name]['max']
        
        if min_val == max_val:
            score = 0.5
        else:
            normalized_value = (float(value) - min_val) / (max_val - min_val)
            
            if feature_name in ['eqdist_diff', 'serial_autocorrelation', 'fft_max_magnitude']:
                score = 1.0 - normalized_value
            else:
                score = normalized_value
    else:
        score = 0.0

    return np.clip(score, 0.0, 1.0)


def _howUniform(test_results: Dict[str, Union[float, int]]) -> float:
    """Computes the uniformity score from test results."""
    scores = [_get_normalized_score(test_results.get(feat, np.nan), feat) for feat in _FEATURES['uniformity']]
    return np.mean([s for s in scores if not np.isnan(s)])


def _howPatterns(test_results: Dict[str, Union[float, int]]) -> float:
    """Computes the patterns score from test results."""
    scores = [_get_normalized_score(test_results.get(feat, np.nan), feat) for feat in _FEATURES['patterns']]
    return np.mean([s for s in scores if not np.isnan(s)])


def _howPeriodic(test_results: Dict[str, Union[float, int]]) -> float:
    """Computes the periodicity score from test results."""
    scores = [_get_normalized_score(test_results.get(feat, np.nan), feat) for feat in _FEATURES['periodicity']]
    return np.mean([s for s in scores if not np.isnan(s)])


def _getScore(test_results: Dict[str, Union[float, int]]) -> float:
    """Computes the overall randomness score by averaging the sub-scores."""
    uniformity_score = _howUniform(test_results)
    patterns_score = _howPatterns(test_results)
    periodicity_score = _howPeriodic(test_results)

    all_scores = [uniformity_score, patterns_score, periodicity_score]
    return np.mean([s for s in all_scores if not np.isnan(s)])