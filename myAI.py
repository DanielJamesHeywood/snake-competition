import random
from collections import deque
from snake.logic import GameState, Turn, Snake, Direction

from examples.smartAI import smartAI as enemyAI


def myAI(state: GameState) -> Turn:
    possibleStates = {turn: moveSnake(state, turn) for turn in Turn}
    return Turn.STRAIGHT

def moveSnake(state: GameState, turn: Turn) -> GameState:
    return state
