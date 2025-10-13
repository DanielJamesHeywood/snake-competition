from collections import deque
from snake.logic import GameState, Turn, Snake
from examples.smartAI import smartAI as enemyAI


def myAI(state: GameState) -> Turn:
    states = {
        turn: set() for turn in Turn
    }
    for turn in Turn:
        newState = copyGameState(state)
        if moveSnake(newState, turn):
            if newState.score > state.score:
                return turn
            states[turn].add((newState, 1, getDistanceToNearestFood(newState) + 1))
    while any(states):
        turnForMinimum = None
        stateForMinimum, distanceForMinimum, minimumDistanceToNearestFood = None, None, None
        for turn in Turn:
            for state, distance, distanceToNearestFood in states[turn]:
                if minimumDistanceToNearestFood is None or distanceToNearestFood < minimumDistanceToNearestFood or (distanceToNearestFood == minimumDistanceToNearestFood and distance > distanceForMinimum):
                    turnForMinimum = turn
                    stateForMinimum, distanceForMinimum, minimumDistanceToNearestFood = state, distance, distanceToNearestFood
        for newTurn in Turn:
            newState = stateForMinimum if newTurn == Turn.RIGHT else copyGameState(stateForMinimum)
            if moveSnake(newState, newTurn):
                if newState.score > state.score:
                    return turnForMinimum
                newDistanceForMinimum = distanceForMinimum + 1
                states[turnForMinimum].add((newState, newDistanceForMinimum, getDistanceToNearestFood(newState) + newDistanceForMinimum))
    return Turn.STRAIGHT


def copyGameState(state: GameState) -> GameState:
    return GameState(
        width = state.width,
        height = state.height,
        snake = copySnake(state.snake),
        enemies = [
            copySnake(enemy) for enemy in state.enemies
        ],
        food = state.food.copy(),
        walls = state.walls.copy(),
        score = state.score
    )


def copySnake(snake: Snake) -> Snake:
    copy = Snake(0, 0, snake.id)
    copy.score = snake.score
    copy.isAlive = snake.isAlive
    copy.body = snake.body.copy()
    copy.direction = snake.direction
    return copy


def moveSnake(state: GameState, turn: Turn) -> bool:
    state.snake.isAlive = moveAnySnake(state, state.snake, turn)
    if state.snake.isAlive:
        for index in range(len(state.enemies)):
            if state.enemies[index].isAlive:
                moveEnemy(state, index, enemyAI(getEnemyGameState(state, index)))
    return state.snake.isAlive


def moveAnySnake(state: GameState, snake: Snake, turn: Turn) -> bool:
    nextHead = snake.get_next_head(turn)
    if nextHead in state.walls:
        return False
    if not (0 <= nextHead[0] < state.width and 0 <= nextHead[1] < state.height):
        return False
    if nextHead in snake.body and not nextHead == snake.body[-1]:
        return False
    if snake is not state.snake and nextHead in state.snake.body:
        return False
    for other_snake in state.enemies:
        if other_snake is not snake and other_snake.isAlive and nextHead in other_snake.body:
            return False
    growing = nextHead in state.food
    snake.move(turn, grow = growing)
    if growing:
        state.food.remove(nextHead)
        # if len(self.food) < self.num_food:
        #     self.spawn_food()
        snake.score += 1
        if snake is state.snake:
            state.score += 1
        # self.spawn_wall()
    return True

def moveEnemy(state: GameState, enemy_index: int, turn: Turn) -> bool:
    state.enemies[enemy_index].isAlive = moveAnySnake(state, state.enemies[enemy_index], turn)
    if not state.enemies[enemy_index].isAlive:
        for position in state.enemies[enemy_index].body:
            state.food.add(position)
    return state.enemies[enemy_index].isAlive


def getEnemyGameState(state: GameState, enemy_index: int) -> GameState:
    return GameState(
        width = state.width,
        height = state.height,
        snake = state.enemies[enemy_index],
        enemies = [state.snake] + [
            enemy for enemy in state.enemies if enemy is not state.enemies[enemy_index] and enemy.isAlive
        ],
        food = state.food,
        walls = state.walls,
        score = state.enemies[enemy_index].score
    )


def getDistanceToNearestFood(state: GameState) -> int | None:
    distanceToNearestFood = None
    for food in state.food:
        distanceToFood = abs(food[0] - state.snake.head[0]) + abs(food[1] - state.snake.head[1])
        if distanceToNearestFood is None or distanceToFood < distanceToNearestFood:
            distanceToNearestFood = distanceToFood
    return distanceToNearestFood
