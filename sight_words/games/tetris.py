"""A tetris game"""
import random
import time
from typing import List
from typing import Tuple
from typing import Union
import dataclasses

import blessed

from sight_words import game


@dataclasses.dataclass
class RowData:
    """The data for a row"""

    blocks_filled: List[bool]
    word: str = ""


@dataclasses.dataclass
class TetrisPiece:
    """A tetris piece"""

    squares: List[Tuple[int, int]]
    center: Tuple[float, float]

    def rotate(self, n_quarter_turns: int) -> "TetrisPiece":
        """Returns a rotated tetris piece"""
        n_quarter_turns = n_quarter_turns % 4
        if n_quarter_turns == 0:
            # No rotation
            return self
        if n_quarter_turns == 2:
            # Flip the piece
            def rotate(x, y):
                x_centered = x - self.center[0]
                y_centered = y - self.center[1]
                x_rot_centered = -x_centered
                y_rot_centered = -y_centered
                x_rot = x_rot_centered + self.center[0]
                y_rot = y_rot_centered + self.center[1]
                return int(2 * x_rot) // 2, int(2 * y_rot) // 2

        elif n_quarter_turns == 1:
            # Rotate the piece
            def rotate(x, y):
                x_centered = x - self.center[0]
                y_centered = y - self.center[1]
                x_rot_centered = -y_centered
                y_rot_centered = x_centered
                x_rot = x_rot_centered + self.center[0]
                y_rot = y_rot_centered + self.center[1]
                return int(2 * x_rot) // 2, int(2 * y_rot) // 2

        elif n_quarter_turns == 3:
            # Rotate the piece
            def rotate(x, y):
                x_centered = x - self.center[0]
                y_centered = y - self.center[1]
                x_rot_centered = y_centered
                y_rot_centered = -x_centered
                x_rot = x_rot_centered + self.center[0]
                y_rot = y_rot_centered + self.center[1]
                return int(2 * x_rot) // 2, int(2 * y_rot) // 2

        else:
            raise RuntimeError("Invalid rotation number")
        new_squares = [rotate(x, y) for x, y in self.squares]
        return dataclasses.replace(self, squares=new_squares)

    def shift(self, x, y):
        """Shift the piece"""
        new_squares = [(x + x_, y + y_) for x_, y_ in self.squares]
        return dataclasses.replace(
            self, squares=new_squares, center=(self.center[0] + x, self.center[1] + y)
        )

    @staticmethod
    def box(x, y):
        """Get a box"""
        return TetrisPiece(
            squares=[(0, 0), (0, 1), (1, 0), (1, 1)], center=(0.5, 0.5)
        ).shift(x, y)

    @staticmethod
    def line(x, y):
        """Get a line"""
        return TetrisPiece(
            squares=[(0, 2), (0, 1), (0, 0), (0, -1)], center=(0, 0.5)
        ).shift(x, y)

    @staticmethod
    def ell(x, y):
        """Get a ell"""
        return TetrisPiece(
            squares=[(0, 2), (0, 1), (0, 0), (1, 0)], center=(0, 0.5)
        ).shift(x, y)

    @staticmethod
    def lle(x, y):
        """Get a lle"""
        return TetrisPiece(
            squares=[(0, 2), (0, 1), (0, 0), (-1, 0)], center=(0, 0.5)
        ).shift(x, y)

    @staticmethod
    def zig(x, y):
        """Get a zig"""
        return TetrisPiece(
            squares=[(0, 0), (0, 1), (1, 0), (1, -1)], center=(0.5, 0)
        ).shift(x, y)

    @staticmethod
    def zag(x, y):
        """Get a zag"""
        return TetrisPiece(
            squares=[(0, 0), (0, -1), (1, 0), (1, 1)], center=(0.5, 0)
        ).shift(x, y)

    @staticmethod
    def random_piece(x, y) -> "TetrisPiece":
        """Get a random piece"""
        method = random.choice(
            [
                TetrisPiece.box,
                TetrisPiece.line,
                TetrisPiece.ell,
                TetrisPiece.lle,
                TetrisPiece.zag,
                TetrisPiece.zig,
            ]
        )
        return method(x, y)


# TETRIS_BG_COLOR = blessed.Terminal.black_on_bright_cyan
TOP_OFFSET = 2
BOTTOM_OFFSET = 2


@dataclasses.dataclass
class Tetris(game.AbstractGame):
    """The tetris game"""

    width: int = 10
    rows: List[RowData] = dataclasses.field(default_factory=list)
    score: int = 0
    piece: TetrisPiece = dataclasses.field(
        default_factory=lambda: TetrisPiece.random_piece(5, 0)
    )
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
        text += " " * 2 * (self.width + 2) + f"Score: {self.score}\n"
        for row in self.rows:
            assert len(row.blocks_filled) == self.width
            if row.word:
                missing = self.width - len(row.word)
                row_txt = (
                    ui.white_on_black
                    + "▒"
                    + row.word
                    + " " * missing
                    + "▒"
                    + ui.black_on_bright_cyan
                )
            else:
                row_txt = (
                    "▒"
                    + "".join("█" if filled else " " for filled in row.blocks_filled)
                    + "▒"
                )
            text += row_txt + ui.move_down()
        text += "▒" * (self.width + 2)
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

    def clear_piece(self, ui):
        """Renders the piece"""
        for x, y in self.piece.squares:
            with ui.location(x + 1, y + TOP_OFFSET - 1):
                print(" ", end="")

    def render_piece(self, ui):
        """Renders the piece"""
        for x, y in self.piece.squares:
            with ui.location(x + 1, y + TOP_OFFSET - 1):
                print("█", end="")

    def is_piece_blocked(self, piece):
        """Checks if the piece is blocked"""
        for x, y in piece.squares:
            if y >= len(self.rows):
                return True
            if x > self.width - 1:
                return True
            if x < 0:
                return True
            if y < 0:
                continue
            if self.rows[y].blocks_filled[x]:
                return True
        return False

    def reset_piece(self):
        """Resets to a new piece"""
        self.piece = TetrisPiece.random_piece(5, 0)

    def drop_piece(self) -> bool:
        """
        Drop the piece one unit to the keystroke
        Returns True if the piece could move


        Returns:
            Whether the piece could move
        """
        if self.is_piece_blocked(self.piece.shift(0, 1)):
            for x, y in self.piece.squares:
                self.rows[y].blocks_filled[x] = True
            return False
        else:
            # y += 1
            # y = max(0, min(y, len(self.rows) - 1))
            # x = max(0, min(x, self.width - 1))
            # self.piece = (x, y)
            new_piece = self.piece.shift(0, 1)
            if not self.is_piece_blocked(new_piece):
                self.piece = new_piece
        return True

    def move_piece(self, inp) -> bool:
        """
        Move the piece according to the keystroke
        Returns True if the piece could move

        Args:
            inp: The keystroke

        Returns:
            Whether the piece could move
        """

        if inp.code == 260:
            new_piece = self.piece.shift(-1, 0)
            if not self.is_piece_blocked(new_piece):
                self.piece = new_piece
        elif inp.code == 261:
            new_piece = self.piece.shift(1, 0)
            if not self.is_piece_blocked(new_piece):
                self.piece = new_piece
        elif inp.code == 258:
            new_piece = self.piece.rotate(-1)
            if not self.is_piece_blocked(new_piece):
                self.piece = new_piece
        elif inp.code == 259:
            new_piece = self.piece.rotate(1)
            if not self.is_piece_blocked(new_piece):
                self.piece = new_piece
        elif inp == " ":
            new_piece = self.piece.shift(0, 1)
            if not self.is_piece_blocked(new_piece):
                self.piece = new_piece

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
            while True:
                stime = time.time()
                self.adjust_rows(ui.height - TOP_OFFSET - BOTTOM_OFFSET)
                if self.is_game_over():
                    self.render_game_over(ui)
                    while not ui.inkey(timeout=2):
                        pass
                    return game.GameOver(score=self.score)
                self.render_board(ui)
                while time.time() - stime < self.inv_speed:
                    inp = ui.inkey(timeout=0.02)
                    if inp == "q":
                        return resume_hook
                    self.clear_piece(ui)
                    self.move_piece(inp)
                    self.render_piece(ui)
                if not self.drop_piece():
                    time.sleep(0.5)
                    self.reset_piece()
                    return resume_hook
