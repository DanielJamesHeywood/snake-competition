import random
from collections import deque
from snake.logic import GameState, Turn, Snake, Direction

"""
Your mission, should you choose to accept it, is to write the most cracked snake AI possible.

All the info you'll need to do this is in the GameState and Snake classes in snake/logic.py

Below is all of the data you'll need, and some small examples that you can uncomment and use if you want :)

"""


def myAI(state: GameState) -> Turn:
    safe = []
    enemy_bodies = set()
    for snake in state.enemies:
        enemy_bodies |= snake.body_set
    for turn in list(Turn):
        head = state.snake.get_next_head(turn)
        if (
            0 <= head[0] < state.width
            and 0 <= head[1] < state.height
            and head not in state.walls
            and head not in state.snake.body
            and head not in enemy_bodies
        ):
            safe.append(turn)
    return random.choice(safe)
