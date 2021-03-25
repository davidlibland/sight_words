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


def test_target_accuracy_sampling():
    """Test Dataset"""
    dataset = {
        "a": data_rep.SightWordDatum(
            grade=0, log=[data_rep.Event(success=10_000, failure=0)]
        ),
        "b": data_rep.SightWordDatum(
            grade=1, log=[data_rep.Event(success=10_000 * 2, failure=10_000)]
        ),
        "bp": data_rep.SightWordDatum(
            grade=1, log=[data_rep.Event(success=10_000 * 3, failure=10_000)]
        ),
        "d": data_rep.SightWordDatum(
            grade=1, log=[data_rep.Event(success=10_000 * 4, failure=10_000)]
        ),
        "c": data_rep.SightWordDatum(
            grade=2, log=[data_rep.Event(success=3, failure=10_000)]
        ),
        "x": data_rep.SightWordDatum(
            grade=2, log=[data_rep.Event(success=3, failure=100)]
        ),
    }

    # Choose grade under assumption that it is the first word in session
    chosen_grades = collections.Counter()
    chosen_word = collections.Counter()
    for _ in range(100):
        grade = ml.choose_grade_for_target_accuracy(
            dataset, target_accuracy=0.75, session_successes=0, session_failures=0
        )
        chosen_grades[grade] += 1

        word = ml.choose_word_for_target_accuracy(
            dataset, target_accuracy=0.75, session_successes=0, session_failures=0
        )
        chosen_word[word] += 1
    assert chosen_grades[2] <= chosen_grades[1]
    assert chosen_grades[0] <= chosen_grades[1]
    assert chosen_word.most_common()[0][0] == "bp"

    # Choose grade under assumption that we've had a string of failures:
    chosen_grades = collections.Counter()
    chosen_word = collections.Counter()
    for _ in range(100):
        grade = ml.choose_grade_for_target_accuracy(
            dataset, target_accuracy=0.75, session_successes=0, session_failures=10_000
        )
        chosen_grades[grade] += 1

        word = ml.choose_word_for_target_accuracy(
            dataset, target_accuracy=0.75, session_successes=0, session_failures=10_000
        )
        chosen_word[word] += 1
    assert chosen_grades[0] >= chosen_grades[1] >= chosen_grades[2]
    assert chosen_word.most_common()[0][0] == "a"

    # Choose grade under assumption that we've had a string of successes:
    chosen_grades = collections.Counter()
    chosen_word = collections.Counter()
    for _ in range(100):
        grade = ml.choose_grade_for_target_accuracy(
            dataset, target_accuracy=0.75, session_successes=10_000, session_failures=0
        )
        chosen_grades[grade] += 1

        word = ml.choose_word_for_target_accuracy(
            dataset, target_accuracy=0.75, session_successes=10_000, session_failures=0
        )
        chosen_word[word] += 1
    assert chosen_grades[0] <= chosen_grades[1] <= chosen_grades[2]
    assert chosen_word.most_common()[0][0] == "c"
