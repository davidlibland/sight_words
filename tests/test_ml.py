"""Tests for ml"""
import collections

from sight_words import data_rep, data_utils, ml


def test_sampling():
    """Test Dataset"""
    dataset = {
        "a": data_rep.SightWordDatum(grade=0, successes=3, failures=0),
        "b": data_rep.SightWordDatum(grade=1, successes=3, failures=10000),
        "d": data_rep.SightWordDatum(grade=1, successes=3, failures=20_000),
        "c": data_rep.SightWordDatum(grade=2, successes=3, failures=5),
        "x": data_rep.SightWordDatum(grade=2, successes=3, failures=100),
    }
    chosen_grades = collections.Counter()
    for _ in range(100):
        grade = ml.choose_grade(dataset)
        chosen_grades[grade] += 1
    assert chosen_grades[1] >= chosen_grades[2] >= chosen_grades[0]
