"""Tests for ml"""
import collections

from sight_words import data_rep, ml


def test_sampling():
    """Test Dataset"""
    dataset = {
        "a": data_rep.SightWordDatum(
            grade=0, log=[data_rep.Event(success=3, failure=0)]
        ),
        "b": data_rep.SightWordDatum(
            grade=1, log=[data_rep.Event(success=3, failure=10000)]
        ),
        "d": data_rep.SightWordDatum(
            grade=1, log=[data_rep.Event(success=3, failure=20_000)]
        ),
        "c": data_rep.SightWordDatum(
            grade=2, log=[data_rep.Event(success=3, failure=5)]
        ),
        "x": data_rep.SightWordDatum(
            grade=2, log=[data_rep.Event(success=3, failure=100)]
        ),
    }
    chosen_grades = collections.Counter()
    for _ in range(100):
        grade = ml.choose_grade(dataset)
        chosen_grades[grade] += 1
    assert chosen_grades[1] >= chosen_grades[2] >= chosen_grades[0]
