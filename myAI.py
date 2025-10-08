import random
from collections import deque
from snake.logic import GameState, Turn, Snake, Direction

"""
Your mission, should you choose to accept it, is to write the most cracked snake AI possible.

All the info you'll need to do this is in the GameState and Snake classes in snake/logic.py

Below is all of the data you'll need, and some small examples that you can uncomment and use if you want :)

"""


def myAI(state: GameState) -> Turn:
    from examples.smartAI import smartAI
    return smartAI(state)
