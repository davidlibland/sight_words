"""A simple stacking game"""
from typing import Optional
from typing import Union
from typing import List
import itertools

import blessed

from sight_words import game


class StackingGame(game.AbstractGame):
    def __init__(
        self,
        pass_words: Optional[List[str]] = None,
        fail_words: Optional[List[str]] = None,
    ):
        """A simple stacking game"""
        if pass_words is None:
            pass_words = []
        if fail_words is None:
            fail_words = []
        self.pass_words = pass_words
        self.fail_words = fail_words

    def play(self, ui: blessed.Terminal) -> Union[game.GameOver, game.ResumeGameHook]:
        left_rights = list(
            itertools.zip_longest(self.pass_words, self.fail_words, fillvalue="-")
        )
        if left_rights:
            with ui.fullscreen(), ui.cbreak(), ui.hidden_cursor():
                print(ui.home + ui.black_on_bright_cyan + ui.clear)
                for left, right in left_rights:
                    line = "  " + left
                    left_pad = ui.width // 2 - len(line)
                    line += " " * left_pad
                    line += ui.red
                    line += right
                    line += ui.black
                    print(line)

                while not ui.inkey(timeout=0.02):
                    pass
        if len(left_rights) >= ui.height:
            return game.GameOver(score=len(self.pass_words) - len(self.fail_words))

        def resume_hook(event: game.SightWordTestEvent):
            pass_words = self.pass_words.copy()
            fail_words = self.fail_words.copy()
            if event.result == game.TestQuestionResult.PASS:
                pass_words.append(event.word)
            elif event.result == game.TestQuestionResult.FAIL:
                fail_words.append(event.word)
            return StackingGame(pass_words, fail_words)

        return resume_hook
