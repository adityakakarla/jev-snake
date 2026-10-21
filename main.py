from snake import Snake
from terminal_ui import TerminalUI
from dotenv import load_dotenv

load_dotenv()

from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

MAX_ATTEMPTS = 200

snake = Snake()
with TerminalUI() as ui:
    ui.render(snake, step=0, limit=MAX_ATTEMPTS)
    with TypeSafeClient(model="jev-latest") as client:
        for i in range(MAX_ATTEMPTS):
            response = client.system_one(
                state=snake.get_state_str(),
                questions={
                    "direction": Choice(
                        instructions="Which direction should the snake move in?",
                        criteria={
                            "U": "The snake should move up",
                            "D": "The snake should move down",
                            "L": "The snake should move left",
                            "R": "The snake should move right"
                        },
                    ),
                },
            )

            direction = response.choices["direction"].choice
            keep_going, length = snake.move(direction)
            outcome = "game_over" if not keep_going else "limit" if i == MAX_ATTEMPTS - 1 else None
            ui.render(snake, step=i + 1, limit=MAX_ATTEMPTS,
                      direction=direction, outcome=outcome)
            if not keep_going:
                break
