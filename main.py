from snake import Snake
import os
from dotenv import load_dotenv

load_dotenv()

from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

snake = Snake()

for i in range(20):
    with TypeSafeClient(model="jev-latest") as client:
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
    print(direction)
    keep_going, length = snake.move(direction)

    if not keep_going:
        print("finished at length " + str(length))
        break
