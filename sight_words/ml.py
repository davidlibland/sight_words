"""
Interfaces for ML-based customized testing. Views testing as multi-armed bandit problem,
relies on thomson-sampling to solve it.
"""
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
    dataset: Dict[str, data_rep.SightWordDatum],
    inv_grade_temp=1,
    inv_temp=1,
) -> str:
    """Chooses a word based on thomson sampling"""
    # First choose the grade:
    grade = choose_grade(dataset, inv_temp=inv_grade_temp)

    def clean_param(v):
        return max(v * inv_temp, 0.1)

    draw_by_word = {
        word: rng.beta(a=clean_param(datum.failures), b=clean_param(datum.successes))
        for word, datum in dataset.items()
        if datum.grade == grade
    }
    worst_word = sorted(draw_by_word.items(), key=lambda x: x[1])[-1][0]
    return worst_word


def choose_grade_for_target_accuracy(
    dataset,
    inv_temp=1,
    target_accuracy=0.75,
    session_successes=0.5,
    session_failures=0.5,
):
    """Choose a grade by thomson sampling to target an overall target accuracy"""
    params_by_grade = get_beta_params_by_grade(dataset)

    def expected_new_accuracy(params):
        expected_accuracy = rng.beta(
            a=max(params[SUCCESS_KEY] * inv_temp, 0.1),
            b=max(params[FAILURE_KEY] * inv_temp, 0.1),
        )
        new_successes = session_successes + expected_accuracy
        new_failures = session_failures + 1 - expected_accuracy
        return new_successes / (new_successes + new_failures)

    draw_by_grade = {
        grade: abs(expected_new_accuracy(p) - target_accuracy)
        for grade, p in params_by_grade.items()
    }
    target_grade = sorted(draw_by_grade.items(), key=lambda x: x[1])[0][0]
    return target_grade


def choose_word_for_target_accuracy(
    dataset: Dict[str, data_rep.SightWordDatum],
    inv_grade_temp=1,
    inv_temp=1,
    target_accuracy=0.75,
    session_successes=0.5,
    session_failures=0.5,
) -> str:
    """Chooses a word based on thomson sampling to target an overall target accuracy"""
    # First choose the grade:
    grade = choose_grade_for_target_accuracy(
        dataset,
        inv_temp=inv_grade_temp,
        target_accuracy=target_accuracy,
        session_successes=session_successes,
        session_failures=session_failures,
    )

    def expected_new_accuracy(datum):
        expected_accuracy = rng.beta(
            a=max(datum.successes * inv_temp, 0.1),
            b=max(datum.failures * inv_temp, 0.1),
        )
        new_successes = session_successes + expected_accuracy
        new_failures = session_failures + 1 - expected_accuracy
        return new_successes / (new_successes + new_failures)

    draw_by_word = {
        word: abs(expected_new_accuracy(datum) - target_accuracy)
        for word, datum in dataset.items()
        if datum.grade == grade
    }
    best_word = sorted(draw_by_word.items(), key=lambda x: x[1])[0][0]
    return best_word
