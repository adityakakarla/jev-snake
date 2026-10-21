"""Terminal presentation only: no changes to game state or model requests."""

import os
import shutil
import sys
import textwrap


class TerminalUI:
    def __init__(self, stream=None):
        self.stream = stream if stream is not None else sys.stdout
        self.interactive = self.stream.isatty() and os.environ.get("TERM") != "dumb"
        self.color = self.interactive and "NO_COLOR" not in os.environ
        try:
            "╭─╮│╰╯●◆↑↓←→░━".encode(self.stream.encoding or "utf-8")
            self.unicode = True
        except UnicodeEncodeError:
            self.unicode = False

    def __enter__(self):
        if self.interactive:
            self.stream.write("\033[2J\033[H\033[?25l")
            self.stream.flush()
        return self

    def __exit__(self, *_):
        if self.interactive:
            self.stream.write("\033[0m\033[?25h")
            self.stream.flush()

    def paint(self, text, style):
        return f"\033[{style}m{text}\033[0m" if self.color else text

    def _board(self, snake, direction):
        horizontal = "─" if self.unicode else "-"
        vertical = "│" if self.unicode else "|"
        corners = "╭╮╰╯" if self.unicode else "++++"
        lines = [self.paint(corners[0] + horizontal * (3 * snake.n) + corners[1], "38;5;240")]
        head = snake.snake[-1]
        arrows = {"U": "↑", "D": "↓", "L": "←", "R": "→"}
        for row in range(snake.n):
            cells = []
            for column in range(snake.n):
                point = (row, column)
                background = 234 if (row + column) % 2 == 0 else 235
                if point == head:
                    symbol = arrows.get(direction, "●") if self.unicode else "@"
                    style = "1;38;5;232;48;5;120"
                elif point in snake.snake_points:
                    symbol = " " if self.color else ("●" if self.unicode else "o")
                    style = "48;5;120"
                elif point == snake.apple:
                    symbol = "◆" if self.unicode else "*"
                    style = f"1;38;5;203;48;5;{background}"
                else:
                    symbol = " " if self.color else "."
                    style = f"48;5;{background}"
                cells.append(self.paint(f" {symbol} ", style))
            edge = self.paint(vertical, "38;5;240")
            lines.append(edge + "".join(cells) + edge)
        lines.append(self.paint(corners[2] + horizontal * (3 * snake.n) + corners[3], "38;5;240"))
        return lines

    def frame(self, snake, *, step, limit, direction=None, outcome=None):
        width = shutil.get_terminal_size((80, 24)).columns
        board_width = 3 * snake.n + 2
        wide = width >= board_width + 30
        content_width = board_width + 26 if wide else max(board_width, 26)
        dot = "●" if self.unicode else "*"
        title = self.paint("JEV", "1;38;5;120") + self.paint(" / SNAKE", "1;97")
        label, accent = {
            None: ("PLAYING", "38;5;120"),
            "game_over": ("GAME OVER", "38;5;203"),
            "limit": ("COMPLETE", "38;5;222"),
        }[outcome]
        rule = "─" if self.unicode else "-"
        header = title + " " * max(2, content_width - 11 - len(label) - 2)
        header += self.paint(f"{dot} {label}", accent)

        arrows = {"U": "↑  UP", "D": "↓  DOWN", "L": "←  LEFT", "R": "→  RIGHT"}
        names = {"U": "UP", "D": "DOWN", "L": "LEFT", "R": "RIGHT"}
        move = (arrows if self.unicode else names).get(direction, "--")
        filled = min(18, int(18 * step / max(1, limit)))
        bar = self.paint(("━" if self.unicode else "#") * filled, "38;5;120")
        bar += self.paint(("░" if self.unicode else "-") * (18 - filled), "38;5;238")
        sidebar = [
            self.paint("LENGTH", "38;5;245"),
            self.paint(f"{len(snake.snake):02d}", "1;38;5;120"),
            "",
            self.paint("TURN", "38;5;245"),
            self.paint(f"{step:03d} / {limit}", "1;97"),
            bar,
            "",
            self.paint("LAST MOVE", "38;5;245"),
            self.paint(move, "1;97"),
            "",
            self.paint(f"{snake.n} x {snake.n} BOARD", "38;5;245"),
        ]

        lines = ["", header, self.paint(rule * content_width, "38;5;238")]
        board = self._board(snake, direction)
        if wide:
            for index in range(max(len(board), len(sidebar))):
                left = board[index] if index < len(board) else " " * board_width
                right = sidebar[index] if index < len(sidebar) else ""
                lines.append(left + "    " + right)
        else:
            lines.extend(board)
            lines.extend(["", f"LENGTH {len(snake.snake):02d}   TURN {step}/{limit}   MOVE {move}"])

        head_mark = "↑" if self.unicode else "@"
        body_mark = "●" if self.unicode else "o"
        body_legend = (self.paint("   ", "48;5;120") + self.paint(" body", "38;5;120")
                       if self.color else f"{body_mark} body")
        apple_mark = "◆" if self.unicode else "*"
        lines.extend([
            "",
            self.paint(f"{head_mark} head", "38;5;120") + "    "
            + body_legend + "    "
            + self.paint(f"{apple_mark} apple", "38;5;203"),
            self.paint(rule * content_width, "38;5;238"),
        ])
        message = {
            None: "Waiting for the model's first move..." if step == 0 else "Waiting for the model's next move...",
            "game_over": f"Collision. Final length: {len(snake.snake)}.",
            "limit": f"Move limit reached. Final length: {len(snake.snake)}.",
        }[outcome]
        lines.extend(self.paint(line, accent if outcome else "38;5;245")
                     for line in textwrap.wrap(message, content_width))
        return "\n".join("  " + line for line in lines) + "\n"

    def render(self, snake, **kwargs):
        frame = self.frame(snake, **kwargs)
        if self.interactive:
            # Move home and erase only the remainder, avoiding a full-screen flash.
            frame = "\033[H" + frame + "\033[J"
        self.stream.write(frame)
        self.stream.flush()
