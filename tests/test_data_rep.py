"""Tests for the data reps"""
import yaml

import sight_words.data_rep as data_rep


def test_serialization():
    """Tests that serialization works as expected."""
    test_data = data_rep.SightWordDatum(1, 2, 3)
    blob = yaml.dump(test_data)
    expected_blob = "!SightWordDatum\nfailures: 3\ngrade: 1\nsuccesses: 2\n"

    assert blob == expected_blob


def test_deserialization():
    """Tests that serialization works as expected."""
    blob = "!SightWordDatum\nfailures: 3\ngrade: 1\nsuccesses: 2\n"
    expected_data = data_rep.SightWordDatum(1, 2, 3)
    data = yaml.load(blob)

    assert data == expected_data
