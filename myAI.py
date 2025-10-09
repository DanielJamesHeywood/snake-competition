import random
from collections import deque
from snake.logic import GameState, Turn, Snake, Direction

from examples.smartAI import smartAI as enemyAI


def myAI(state: GameState) -> Turn:
    possibleStates = {turn: move_snake(state, turn) for turn in Turn}
    return Turn.STRAIGHT


def move_snake(state: GameState, turn: Turn) -> GameState:
    return state
