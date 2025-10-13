from collections import deque
from snake.logic import GameState, Turn, Snake
from examples.smartAI import smartAI as enemyAI


def myAI(state: GameState) -> Turn:
    queue = deque()
    for turn in Turn:
        new_state = copyGameState(state)
        if move_snake(new_state, turn):
            if new_state.score > state.score:
                return turn
            queue.append((new_state, turn))
    while queue:
        state, turn = queue.popleft()
        for new_turn in Turn:
            new_state = copyGameState(state)
            if move_snake(new_state, new_turn):
                if new_state.score > state.score:
                    return turn
                queue.append((new_state, turn))
    return Turn.STRAIGHT


def copyGameState(state: GameState) -> GameState:
    return GameState(
        width = state.width,
        height = state.height,
        snake = copy_snake(state.snake),
        enemies = [copy_snake(enemy) for enemy in state.enemies],
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
    state.snake.isAlive = _move_snake(state, state.snake, turn)
    if state.snake.isAlive:
        for index in range(len(state.enemies)):
            if state.enemies[index].isAlive:
                move_enemy(state, index, enemyAI(getEnemyGameState(state, index)))
    return state.snake.isAlive


def _move_snake(state: GameState, snake: Snake, turn: Turn) -> bool:
    next_head = snake.get_next_head(turn)
    if next_head in state.walls:
        return False
    if not (0 <= next_head[0] < state.width and 0 <= next_head[1] < state.height):
        return False
    if next_head in snake.body and not next_head == -1:
        return False
    if snake is not state.snake and next_head in state.snake.body:
        return False
    for other_snake in state.enemies:
        if other_snake is not snake and other_snake.isAlive and next_head in other_snake.body:
            return False
    growing = next_head in state.food
    snake.move(turn, grow = growing)
    if growing:
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
        enemies = [state.snake] + [enemy for enemy in state.enemies if enemy is not state.enemies[enemy_index] and enemy.isAlive],
        food = state.food,
        walls = state.walls,
        score = state.enemies[enemy_index].score
    )


def move_enemy(state: GameState, enemy_index: int, turn: Turn) -> bool:
    state.enemies[enemy_index].isAlive = _move_snake(state, state.enemies[enemy_index], turn)
    if not state.enemies[enemy_index].isAlive:
        for position in state.enemies[enemy_index].body:
            state.food.add(position)
    return state.enemies[enemy_index].isAlive
