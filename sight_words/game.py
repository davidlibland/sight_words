"""An abstraction for a game"""
from typing import Union
from typing import Callable
import dataclasses
import enum
import abc

import blessed


class TestQuestionResult(enum.Enum):
    """The result of a user's test question"""

    PASS = "PASS"
    FAIL = "FAIL"


@dataclasses.dataclass
class SightWordTestEvent:
    """
    An event involving spelling or reading. The user can either pass or fail
    """

    word: str
    """The word being """
    pass_probability: float
    """The estimated probability of passing"""
    result: TestQuestionResult
    """Whether the user passed or failed"""


ResumeGameHook = Callable[[SightWordTestEvent], "AbstractGame"]


@dataclasses.dataclass
class GameOver:
    """
    The end result of playing the game
    """

    score: int


class AbstractGame(abc.ABC):
    @abc.abstractmethod
    def play(self, ui: blessed.Terminal) -> Union[GameOver, ResumeGameHook]:
        """
        Play the game. If the game is not over, it returns a hook to continue
        the game following a SightWordTestEvent.

        Args:
            ui: The UI needed to play. (A blessed terminal)

        Returns:
            Either a game over result or a resume game hook.
        """
        raise NotImplementedError
