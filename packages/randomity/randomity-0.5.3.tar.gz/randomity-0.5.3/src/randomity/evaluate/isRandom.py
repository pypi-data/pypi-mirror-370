from .._utils.compute_score import _getScore
from .._utils.gen_test_vector import _gen_test_vector
from .._utils.check_param import _checkParam_isRandom

SCORE_THRESHOLD = 0.6

def isRandom(sequence: list, threshold: float = SCORE_THRESHOLD) -> bool:
    """
    Returns a boolean based on if a sequence is scored higher than a threshold for the randomness score.
    """
    _checkParam_isRandom(sequence, threshold)
    
    vector = _gen_test_vector(sequence)
    score = _getScore(vector)
    if score > threshold:
        return True
    else:
        return False