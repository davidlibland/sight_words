"""This module helps handle io."""
import enum

import click
import pyttsx3


class OutputType(enum.Enum):
    SPOKEN = "SPOKEN"
    SILENT = "SILENT"


class OutputEngine:
    def __init__(self, output_type: OutputType):
        """Initializes the output type."""
        if output_type == OutputType.SPOKEN:
            self.engine = pyttsx3.init()
        else:
            self.engine = None

    def output(self, phrase: str):
        """Outputs the str."""
        if self.engine:
            self.engine.say(phrase)
            self.engine.runAndWait()
        else:
            click.secho(phrase)
