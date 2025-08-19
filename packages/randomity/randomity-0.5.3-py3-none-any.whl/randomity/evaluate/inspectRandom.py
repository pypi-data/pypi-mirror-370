from .._utils.compute_score import _getScore, _howUniform, _howPatterns, _howPeriodic
from .._utils.gen_test_vector import _gen_test_vector
from .._utils.check_param import _checkParam_inspectRandom

from .isRandom import SCORE_THRESHOLD

def inspectRandom(sequence):
    """
    Returns a report, scoring different aspects of the randomness of a given number sequence.
    """
    _checkParam_inspectRandom(sequence)

    vector = _gen_test_vector(sequence)
    
    score_uniform = _howUniform(vector)
    score_patterns = _howPatterns(vector)
    score_periodic = _howPeriodic(vector)
    score = _getScore(vector)

    report = {
        "Uniformity": score_uniform,
        "Patterns/Structures": score_patterns,
        "Periodicity": score_periodic,
        "Overall Score": score
    }

    report_keys = list(report.keys())

    output = f"Predictability report:\n\n{report_keys[0]}: {report['Uniformity']:.2f}\n{report_keys[1]}: {report['Patterns/Structures']:.2f}\n{report_keys[2]}: {report['Periodicity']:.2f}\n{report_keys[3]}: {report['Overall Score']:.2f}\n\n"

    if score >= SCORE_THRESHOLD:
        output += f"The sequence could be considered unpredicable ({score:.2f} >= {SCORE_THRESHOLD:.2f})."
    else:
        output += f"The sequence could be considered predictable ({score:.2f} < {SCORE_THRESHOLD:.2f})."

    print(output)