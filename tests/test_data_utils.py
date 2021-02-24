"""Tests for the data utils"""
import pathlib

import hypothesis
import hypothesis.strategies as h_strats

import sight_words.data_utils as data_utils


def test_load_sight_words():
    """Validates the sight word data."""
    data = data_utils.load_sight_words()
    # Validate the data:
    assert isinstance(data, dict), "The sightwords should be a yaml dict of words."
    for grade, words in data.items():
        assert isinstance(
            grade, int
        ), f"The data should be indexed by grades, {grade} is invalid."
        assert isinstance(words, list), "Each grade should be a list of words."
        for word in words:
            assert isinstance(word, str), f"Each word should be a string, not {word}."
    min_grade, max_grade = min(data.keys()), max(data.keys())
    expected_grades = set(range(min_grade, max_grade + 1))
    actual_grades = set(data.keys())
    assert (
        actual_grades == expected_grades
    ), f"Grades should be contiguous; you are missing {expected_grades.difference(actual_grades)}."


@hypothesis.given(
    h_strats.integers(min_value=0, max_value=5),
    h_strats.integers(min_value=0, max_value=5),
)
def test_build_new_dataset(max_grade, past_grade_success_incr):
    """Tests building a new dataset"""
    dataset = data_utils.build_new_dataset(
        max_grade=max_grade, past_grade_success_incr=past_grade_success_incr
    )
    for datum in dataset.values():
        assert datum.grade <= max_grade
        assert datum.failures == data_utils.PRIOR_FAILURES
        assert (
            datum.successes
            == data_utils.PRIOR_SUCCESSES
            + past_grade_success_incr * (max_grade - datum.grade)
        )
    grades = {d.grade for d in dataset.values()}
    assert min(grades) == 0
    assert max(grades) == max_grade
    assert grades == set(range(max_grade + 1))


@hypothesis.given(
    h_strats.integers(min_value=0, max_value=5),
    h_strats.integers(min_value=0, max_value=5),
)
def test_dataset_serialization(tmp_path, max_grade, past_grade_success_incr):
    """Tests serialization"""
    dataset = data_utils.build_new_dataset(
        max_grade=max_grade, past_grade_success_incr=past_grade_success_incr
    )
    dataset = dict(list(dataset.items())[:10])  # <- keep things small
    data_utils.save_dataset(tmp_path / "dataset.yml", dataset)
    loaded_dataset = data_utils.load_dataset(tmp_path / "dataset.yml")
    assert loaded_dataset == dataset
