from collections import deque
import random

class Snake:
    def __init__(self, n=10):
        self.snake = deque([(0, 0)])
        self.snake_points = set([(0, 0)])
        self.remaining_points = set((i, j) for i in range(n) for j in range(n))
        self.remaining_points.remove((0, 0))
        self.apple = random.choice(list(self.remaining_points))
        self.n = n

    def map_direction(self, direction):
        assert direction in 'UDLR'

        if direction == 'U':
            delta = (-1, 0)
        elif direction == 'D':
            delta = (1, 0)
        elif direction == 'L':
            delta = (0, -1)
        elif direction == 'R':
            delta = (0, 1)

        return delta

    def move(self, direction):
        delta = self.map_direction(direction)

        prev_x, prev_y = self.snake[-1]
        delta_x, delta_y = delta
        new_x, new_y = prev_x + delta_x, prev_y + delta_y

        if 0 <= new_x < self.n and 0 <= new_y < self.n:
            if (new_x, new_y) == self.apple:
                self.snake.append((new_x, new_y))
                self.snake_points.add((new_x, new_y))
                self.remaining_points.remove(self.apple)
                self.apple = random.choice(list(self.remaining_points))
                return True, len(self.snake)

            snake_tail = self.snake.popleft()
            self.snake_points.remove(snake_tail)
            self.remaining_points.add(snake_tail)

            if (new_x, new_y) in self.snake_points:
                return False, len(self.snake)

            self.snake.append((new_x, new_y))
            self.snake_points.add((new_x, new_y))
            self.remaining_points.remove((new_x, new_y))

            return True, len(self.snake)
        else:
            return False, len(self.snake)

    def render(self):
        head = self.snake[-1]
        border = "+" + "-" * (2 * self.n + 1) + "+"
        lines = [border]

        for row in range(self.n):
            cells = []
            for column in range(self.n):
                point = (row, column)
                if point == head:
                    cells.append("@")
                elif point in self.snake_points:
                    cells.append("o")
                elif point == self.apple:
                    cells.append("*")
                else:
                    cells.append(".")
            lines.append("| " + " ".join(cells) + " |")

        lines.append(border)
        return "\n".join(lines)

    def get_state_str(self):
        points = 'Current points of snake: ' + ", ".join(str(point) for point in self.snake)
        curr_point = 'The head of the snake is currently at ' + str(points[-1])
        apple = 'Current apple location: ' + str(self.apple)
        board_size = 'Board size: ' + str(self.n) + " by " + str(self.n)
        instructions = '''
        This is a game of Snake, where we want to get the snake as large as possible. We fail if we hit ourselves or the walls of the board.
        We grow the snake by eating an apple, you want to do this.

        Positions are provided as (row, column) and are 0-indexed. U decreases row, D increases row, L decreases column, R increases column.
        The final snake coordiante is the head of the snake. This is where we will move from.

        First, avoid immediate collissions. Then avoid trapping the head in an enclosed area. If comparing safe moves, progress towards the apple.
        '''

        point_info = []

        curr_x, curr_y = self.snake[-1]
        for direction in 'ULDR':
            delta_x, delta_y = self.map_direction(direction)
            new_x, new_y = curr_x + delta_x, curr_y + delta_y
            if new_x < 0 or new_x >= self.n or new_y < 0 or new_y >= self.n or (new_x, new_y) in self.snake_points:
                point_info.append("You should not go in direction " + direction + " because that will cause you to hit a wall or yourself.")
            else:
                euclidean_distance = ((new_y - self.apple[1]) ** 2 + (new_x - self.apple[0]) ** 2) ** 0.5
                point_info.append("Going in direction " + direction + " will bring you " + str(euclidean_distance) + " units of distance from the current apple position")

        board_info = '\n'.join([points, curr_point, apple, board_size, instructions, ','.join(point_info)])
        return board_info
