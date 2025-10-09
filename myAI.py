import random
from collections import deque
from snake.logic import GameState, Turn, Snake, Direction

from examples.smartAI import smartAI as enemyAI


def myAI(state: GameState) -> Turn:
    possibleStates = {Turn.LEFT: set(), Turn.STRAIGHT: set(), Turn.RIGHT: set()}
    return Turn.STRAIGHT

# Maintain set of states achievable by immediatly turning left, right and straight.
# Iteratively evaluate all positions in each set in turn.
# Data structures are sets to prevent evaluating identical states twice.
# Before adding a state to straightStates we should check that state isn't present in leftStates.
# Before adding a state to rightStates we should check that state isn't present in straightStates or leftStates.
