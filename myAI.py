import random
from collections import deque
from snake.logic import GameState, Turn, Snake, Direction

from examples.smartAI import smartAI as enemyAI


def myAI(state: GameState) -> Turn:
    state.snake.score = 1 # Testing whether we're passed a shallow or deep copy.
    return enemyAI(state)


def move_snake(state: GameState, turn: Turn) -> bool:
    moved = _move_snake(state, state.snake, turn)
    state.snake.isAlive = moved
    if moved:
        for i in range(len(state.enemies)):
            enemy_state = getEnemyGameState(state, i)
            enemy_turn = enemyAI(enemy_state)
            move_enemy(state, i, enemy_turn)
    return moved


def _move_snake(state: GameState, snake: Snake, turn: Turn) -> bool:
    next_head = snake.get_next_head(turn)
    if next_head in state.walls:
        return False
    if not (0 <= next_head[0] < state.width and 0 <= next_head[1] < state.height):
        return False
    body_without_tail = list(snake.body)[:-1]
    if next_head in body_without_tail:
        return False
    all_other_bodies = set()
    if snake is not state.snake:
        all_other_bodies |= state.snake.body_set
    for other_snake in state.enemies:
        if other_snake is snake:
            continue
        all_other_bodies |= other_snake.body_set
    if next_head in all_other_bodies:
        return False
    will_eat = next_head in state.food
    snake.move(turn, grow = will_eat)
    if will_eat:
        state.food.remove(next_head)
        # if len(self.food) < self.num_food:
        #     self.spawn_food()
        snake.score += 1
        if snake is state.snake:
            state.score += 1
        # self.spawn_wall()
    return True


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


def move_enemy(state: GameState, enemy_index: int, turn: Turn) -> bool:
    moved = _move_snake(state, state.enemies[enemy_index], turn)
    if not moved:
        for pos in list(state.enemies[enemy_index].body):
            state.food.add(pos)
        del state.enemies[enemy_index]
    return moved
