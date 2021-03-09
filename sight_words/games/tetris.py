"""A tetris game"""
from typing import List
from typing import Union
import dataclasses

import blessed

from sight_words import game


@dataclasses.dataclass
class RowData:
    """The data for a row"""

    blocks_filled: List[bool]
    word: str = ""


# TETRIS_BG_COLOR = blessed.Terminal.black_on_bright_cyan
TOP_OFFSET = 2
BOTTOM_OFFSET = 2


@dataclasses.dataclass
class Tetris(game.AbstractGame):
    """The tetris game"""

    width: int = 10
    rows: List[RowData] = dataclasses.field(default_factory=list)
    score: int = 0
    piece = (5, 0)
    inv_speed: float = 0.5

    def adjust_rows(self, height):
        """Adjusts the state to the correct height."""
        i = 0
        while i < len(self.rows):
            # Check if any rows are full:
            row = self.rows[i]
            if not row.word and all(row.blocks_filled):
                # Delete the row.
                self.rows.pop(i)
                self.score += self.width
            else:
                i += 1
        if len(self.rows) < height:
            new_rows = [
                RowData([False] * self.width) for _ in range(height - len(self.rows))
            ]
            self.rows = new_rows + self.rows
        self.rows = self.rows[-height:]

    def render_board(self, ui: blessed.Terminal):
        """Renders the game board"""
        text = ui.home + ui.black_on_bright_cyan + ui.clear
        text += " " * 2 * self.width + f"Score: {self.score}\n"
        for row in self.rows:
            assert len(row.blocks_filled) == self.width
            if row.word:
                missing = self.width - len(row.word)
                row_txt = (
                    ui.white_on_black
                    + row.word
                    + " " * missing
                    + ui.black_on_bright_cyan
                )
            else:
                row_txt = "".join(
                    "█" if filled else " " for filled in row.blocks_filled
                )
            text += row_txt + ui.move_down()
        print(text, end="")

    def is_game_over(self) -> bool:
        """Checks if the game is over"""
        return any(self.rows[0].blocks_filled)

    def render_game_over(self, ui):
        """Renders the game over message"""
        print(ui.home + ui.black_on_bright_cyan + ui.clear, end="")
        msg = "Game Over!"
        print(ui.move_xy(ui.width // 2 - 5, ui.height // 2) + msg)
        msg = f"Score: {self.score}"
        print(ui.move_xy((ui.width - len(msg)) // 2, ui.height // 2 + 1) + msg)

    def render_piece(self, ui):
        """Renders the piece"""
        with ui.location(self.piece[0], self.piece[1] + TOP_OFFSET - 1):
            print("█", end="")

    def is_piece_blocked(self):
        """Checks if the piece is blocked"""
        x, y = self.piece
        if y >= len(self.rows) - 1:
            return True
        if self.rows[y + 1].blocks_filled[x]:
            return True
        return False

    def reset_piece(self):
        self.piece = (5, 0)

    def move_piece(self, inp) -> bool:
        """
        Move the piece according to the keystroke
        Returns True if the piece could move

        Args:
            inp: The keystroke

        Returns:
            Whether the piece could move
        """
        # Constrain the piece
        x, y = self.piece
        self.piece = (x, y)

        if self.is_piece_blocked():
            self.rows[y].blocks_filled[x] = True
            return False
        else:
            if inp.code == 260:
                x -= 1
            if inp.code == 261:
                x += 1
            y += 1
            y = max(0, min(y, len(self.rows) - 1))
            x = max(0, min(x, self.width - 1))
            self.piece = (x, y)
        return True

    def play(self, ui: blessed.Terminal) -> Union[game.GameOver, game.ResumeGameHook]:
        """The core game play loop"""

        def resume_hook(event: game.SightWordTestEvent):
            if event.result == game.TestQuestionResult.PASS:
                return dataclasses.replace(
                    self, score=self.score + 1, inv_speed=self.inv_speed * 0.9
                )
            elif event.result == game.TestQuestionResult.FAIL:
                new_row = RowData(blocks_filled=[True] * self.width, word=event.word)
                return dataclasses.replace(self, rows=self.rows + [new_row])

        with ui.fullscreen(), ui.cbreak(), ui.hidden_cursor():
            while (inp := ui.inkey(timeout=self.inv_speed)) != "q":
                self.adjust_rows(ui.height - TOP_OFFSET - BOTTOM_OFFSET)
                if self.is_game_over():
                    self.render_game_over(ui)
                    while not ui.inkey(timeout=0.02):
                        pass
                    return game.GameOver(score=self.score)
                self.render_board(ui)
                self.render_piece(ui)
                if not self.move_piece(inp):
                    self.reset_piece()
                    return resume_hook

        return resume_hook
