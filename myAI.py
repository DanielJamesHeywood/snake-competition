import random
from collections import deque
from snake.logic import GameState, Turn, Snake, Direction

from examples.smartAI import smartAI as enemyAI


def myAI(state: GameState) -> Turn:
    leftStates = set()
    straightStates = set()
    rightStates = set()
    return Turn.STRAIGHT
