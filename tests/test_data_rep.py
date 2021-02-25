"""Tests for the data reps"""
import yaml

import sight_words.data_rep as data_rep


def test_serialization():
    """Tests that serialization works as expected."""
    test_data = data_rep.SightWordDatum(1, [data_rep.Event(1, 3)])
    blob = yaml.dump(test_data)
    expected_blob = (
        "!SightWordDatum\ngrade: 1\nlog:\n- !Event\n  failure: 3\n  success: 1\n"
    )

    assert blob == expected_blob


def test_deserialization():
    """Tests that serialization works as expected."""
    blob = "!SightWordDatum\ngrade: 1\nlog:\n- !Event\n  failure: 3\n  success: 1\n"
    expected_data = data_rep.SightWordDatum(1, [data_rep.Event(1, 3)])
    data = yaml.load(blob)

    assert data == expected_data
