from snake import Snake
import sys
from dotenv import load_dotenv

load_dotenv()

from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

MAX_ATTEMPTS = 200

def render_board(snake, status):
    clear = "\033[2J\033[H" if sys.stdout.isatty() else ""
    print(
        f"{clear}Snake | Length: {len(snake.snake)}\n"
        f"{snake.render()}\n"
        f"@ head   o body   * apple   . empty\n"
        f"{status}\n",
        flush=True,
    )


snake = Snake()
render_board(snake, "Waiting for the model's first move...")

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
        status = f"Move {i + 1}/{MAX_ATTEMPTS}: {direction}"

        if not keep_going:
            render_board(snake, f"{status} | Game over! Final length: {length}")
            break

        if i == MAX_ATTEMPTS - 1:
            status += f" | Move limit reached. Final length: {length}"
        else:
            status += " | Waiting for the model's next move..."
        render_board(snake, status)
