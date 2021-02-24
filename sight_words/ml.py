"""
Interfaces for ML-based customized testing. Views testing as multi-armed bandit problem,
relies on thomson-sampling to solve it.
"""
from typing import Tuple
from typing import Dict
import collections

import numpy as np

import sight_words.data_rep as data_rep

SUCCESS_KEY = "successes"
FAILURE_KEY = "failures"
PRIOR_FAILURES = 0.5
PRIOR_SUCCESSES = 0.5

rng = np.random.RandomState(13)


def get_beta_params_by_grade(
    dataset: Dict[str, data_rep.SightWordDatum]
) -> Dict[int, Dict[str, float]]:
    """Get the beta parameters for the grade"""
    successes = collections.defaultdict(lambda: PRIOR_SUCCESSES)
    failures = collections.defaultdict(lambda: PRIOR_FAILURES)
    for datum in dataset.values():
        successes[datum.grade] += datum.successes
        failures[datum.grade] += datum.failures
    params_by_grade = collections.defaultdict(dict)
    for grade, cnt in successes.items():
        params_by_grade[grade][SUCCESS_KEY] = cnt
    for grade, cnt in failures.items():
        params_by_grade[grade][FAILURE_KEY] = cnt
    return params_by_grade


def choose_grade(dataset, inv_temp=1):
    """Choose a grade by thomson sampling"""
    params_by_grade = get_beta_params_by_grade(dataset)
    draw_by_grade = {
        grade: rng.beta(a=inv_temp * p[FAILURE_KEY], b=inv_temp * p[SUCCESS_KEY])
        for grade, p in params_by_grade.items()
    }
    worst_grade = sorted(draw_by_grade.items(), key=lambda x: x[1])[-1][0]
    return worst_grade


def choose_word(
    dataset: Dict[str, data_rep.SightWordDatum], inv_grade_temp=1, inv_temp=1
) -> str:
    """Chooses a word based on thomson sampling"""
    # First choose the grade:
    grade = choose_grade(dataset, inv_temp=inv_grade_temp)
    draw_by_word = {
        word: rng.beta(a=inv_temp * datum.failures, b=inv_temp * datum.successes)
        for word, datum in dataset.items()
        if datum.grade == grade
    }
    worst_word = sorted(draw_by_word.items(), key=lambda x: x[1])[-1][0]
    return worst_word
