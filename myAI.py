import random
from collections import deque
from snake.logic import GameState, Turn, Snake, Direction

from examples.smartAI import smartAI as enemyAI


def myAI(state: GameState) -> Turn:
    possibleStates = {Turn.LEFT: {moveSnake(state, Turn.LEFT)}, Turn.STRAIGHT: {moveSnake(state, Turn.STRAIGHT)}, Turn.RIGHT: {moveSnake(state, Turn.RIGHT)}}
    return Turn.STRAIGHT

def moveSnake(state: GameState, turn: Turn) -> GameState:
    return state
