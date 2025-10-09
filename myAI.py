import random
from collections import deque
from snake.logic import GameState, Turn, Snake, Direction

from examples.smartAI import smartAI as enemyAI


def myAI(state: GameState) -> Turn:
    possible_states = {
        turn: move_snake(state, turn) for turn in Turn
    }
    return enemyAI(state)


def move_snake(state: GameState, turn: Turn) -> GameState:
    for i in range(len(state.enemies)):
        enemy_state = getEnemyGameState(state, i)
        enemy_turn = enemyAI(enemy_state)
        state = move_enemy_snake(state, i, enemy_turn)
    return state

def getEnemyGameState(state: GameState, enemy_index: int) -> GameState:
    return GameState(
        width = state.width,
        height = state.height,
        snake = state.enemies[enemy_index],
        enemies = [state.snake] + [
            s for s in state.enemies if s != state.enemies[enemy_index]
        ],
        food = state.food,
        walls = state.walls,
        score = state.enemies[enemy_index].score
    )

def move_enemy_snake(state: GameState, enemy_index: int, turn: Turn) -> GameState:
    return state
