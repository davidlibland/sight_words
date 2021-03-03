"""Tests for the data utils"""
import copy
import pathlib

import hypothesis
import hypothesis.strategies as h_strats

import sight_words.data_utils as data_utils
import sight_words.data_rep as data_rep


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
        assert len(datum.log) == 1
        assert datum.log[0].failure == data_utils.PRIOR_FAILURES
        assert datum.log[
            0
        ].success == data_utils.PRIOR_SUCCESSES + past_grade_success_incr * (
            max_grade - datum.grade
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


def test_update_dataset():
    """Tests that the dataset is updated correctly"""
    dataset_reading = data_utils.build_new_dataset(max_grade=3)
    dataset_spelling = data_utils.build_new_dataset(max_grade=2)
    dataset = data_rep.DataSet(
        reading_words=dataset_reading,
        spelling_words=dataset_spelling,
    )

    # Check reading words
    word = list(dataset_reading.keys())[0]
    old_dataset = copy.copy(dataset)
    new_dataset = data_utils.update_dataset(
        dataset, successes=1, failures=2, reading_word=word
    )
    assert dataset == old_dataset
    assert new_dataset != dataset
    assert new_dataset.spelling_words == dataset.spelling_words
    assert (
        new_dataset.reading_words[word].failures
        == dataset.reading_words[word].failures + 2
    )
    assert (
        new_dataset.reading_words[word].successes
        == dataset.reading_words[word].successes + 1
    )

    # Check spelling words
    word = list(dataset_spelling.keys())[0]
    old_dataset = copy.copy(dataset)
    new_dataset = data_utils.update_dataset(
        dataset, successes=1, failures=2, spelling_word=word
    )
    assert dataset == old_dataset
    assert new_dataset != dataset
    assert new_dataset.reading_words == dataset.reading_words
    assert (
        new_dataset.spelling_words[word].failures
        == dataset.spelling_words[word].failures + 2
    )
    assert (
        new_dataset.spelling_words[word].successes
        == dataset.spelling_words[word].successes + 1
    )


def test_sentence_index_object():
    """Tests the sentence index object"""
    index = data_utils.SentenceIndex(
        sentences=["hi there", "bob ate the cat"], index={"hi": [0], "bob": [1]}
    )

    assert index.get_sentence("hi") == "hi there"
    assert index.get_sentence("bob") == "bob ate the cat"
    assert index.get_sentence("jeff") == ""


def test_merged_index_object():
    """Tests the sentence index object"""
    index_1 = data_utils.SentenceIndex(
        sentences=["hi there", "bob ate the cat"],
        index={"hi": [0], "there": [0], "bob": [1]},
    )
    index_2 = data_utils.SentenceIndex(
        sentences=["there is a way", "cats are great"],
        index={"there": [0], "way": [0], "cats": [1]},
    )
    index = data_utils.MergedIndex([index_1, index_2])

    assert index.get_sentence("hi") == "hi there"
    assert index.get_sentence("bob") == "bob ate the cat"
    assert index.get_sentence("there") == "hi there"
    assert index.get_sentence("way") == "there is a way"
    assert index.get_sentence("cats") == "cats are great"
    assert index.get_sentence("jeff") == ""
