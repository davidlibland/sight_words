"""This module helps handle io."""
import enum

import click
import pyttsx3


##############################
# Method to flush the input  #
# buffer is system-dependent #
##############################
try:
    import sys, termios

    def flush_input():
        """Flushes the input buffer on unix systems"""
        termios.tcflush(sys.stdin, termios.TCIFLUSH)


except ImportError:
    import msvcrt

    def flush_input():
        """Flushes the input buffer on windows systems"""
        while msvcrt.kbhit():
            msvcrt.getch()


class OutputType(enum.Enum):
    SPOKEN = "SPOKEN"
    SILENT = "SILENT"


class OutputEngine:
    """A small io class which abstracts the output mechanism (spoken vs written)"""

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
