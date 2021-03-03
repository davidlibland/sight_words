"""Tests the IO module"""
from unittest import mock

from sight_words import io


@mock.patch("sight_words.io.pyttsx3")
def test_spoken_output(pyttsx3):
    """Tests that spoken output works"""
    engine_mock = mock.MagicMock()
    pyttsx3.init.return_value = engine_mock
    engine = io.OutputEngine(io.OutputType.SPOKEN)
    assert pyttsx3.init.called

    phrase = "hi there bob"
    engine.output(phrase)
    assert engine_mock.runAndWait.called
    engine_mock.say.assert_called_with(phrase)


@mock.patch("sight_words.io.click")
def test_silent_output(click):
    """Tests that spoken output works"""
    engine = io.OutputEngine(io.OutputType.SILENT)

    phrase = "hi there bob"
    engine.output(phrase)
    click.secho.assert_called_with(phrase)
