import random
from collections import deque
from snake.logic import GameState, Turn, Snake, Direction

from snake.logic import DIRECTIONS
from examples.smartAI import smartAI as enemyAI


def myAI(state: GameState) -> Turn:
    possible_states = {turn: [] for turn in Turn}
    for turn in Turn:
        possible_state = copyGameState(state)
        if move_snake(possible_state, turn):
            possible_states[turn].append(possible_state)
    best_turn = None
    best__3 = None
    best_score = None
    for turn in Turn:
        for possible_state in possible_states[turn]:
            head = get_head(possible_state.snake)
            tail = get_tail(possible_state.snake)
            empty_cells = get_empty_cells(possible_state)
            _1 = {head}
            _2 = deque([head])
            _3 = False
            while _2 and not _3:
                pos = _2.popleft()
                for dx, dy in DIRECTIONS:
                    next_pos = (pos[0] + dx, pos[1] + dy)
                    if (next_pos in empty_cells | possible_state.food) and next_pos not in _1:
                        _1.add(next_pos)
                        _2.append(next_pos)
                    if next_pos == tail:
                        _3 = True
            if not best_turn or (_3 and not best__3) or (_3 == best__3 and possible_state.score > best_score):
                best_turn = turn
                best__3 = _3
                best_score = possible_state.score
    return best_turn if best_turn else Turn.LEFT


def copyGameState(state: GameState) -> GameState:
    return GameState(
        width = state.width,
        height = state.height,
        snake = copy_snake(state.snake),
        enemies = [
            copy_snake(s) for s in state.enemies
        ],
        food = state.food.copy(),
        walls = state.walls.copy(),
        score = state.score
    )


def copy_snake(snake: Snake) -> Snake:
    copy = Snake(0, 0, snake.id)
    copy.score = snake.score
    copy.isAlive = snake.isAlive
    copy.body = snake.body.copy()
    copy.direction = snake.direction
    return copy


def move_snake(state: GameState, turn: Turn) -> bool:
    moved = _move_snake(state, state.snake, turn)
    state.snake.isAlive = moved
    if moved:
        for i in range(len(state.enemies)):
            if state.enemies[i].isAlive:
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
        if other_snake.isAlive:
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
            s for s in state.enemies if s != state.enemies[enemy_index] and s.isAlive
        ],
        food = state.food,
        walls = state.walls,
        score = state.enemies[enemy_index].score
    )


def move_enemy(state: GameState, enemy_index: int, turn: Turn) -> bool:
    moved = _move_snake(state, state.enemies[enemy_index], turn)
    state.enemies[enemy_index].isAlive = moved
    if not moved:
        for pos in list(state.enemies[enemy_index].body):
            state.food.add(pos)
    return moved


def get_head(snake: Snake) -> (int, int):
    return snake.body[0]


def get_tail(snake: Snake) -> (int, int):
    return snake.body[-1]


def get_empty_cells(state: GameState) -> set[(int, int)]:
    all_cells = {(x, y) for x in range(state.width) for y in range(state.height)}
    occupied = state.walls | state.food | state.snake.body_set
    for s in state.enemies:
        if s.isAlive:
            occupied |= s.body_set
    return all_cells - occupied
