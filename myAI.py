import random
from collections import deque
from snake.logic import GameState, Turn, Snake, Direction

from snake.logic import DIRECTIONS
from examples.smartAI import smartAI as enemyAI


def myAI(state: GameState) -> Turn:
    minimumDistancesToNearestFood = getMinimumDistancesToNearestFood(state)
    queue = []
    for turn in Turn:
        newState = copyGameState(state)
        if moveSnake(newState, turn):
            if newState.score > state.score:
                return turn
            insert(queue, (newState, turn, 1, minimumDistancesToNearestFood[newState.snake.head] + 1))
    while queue and len(queue) < 256:
        state, firstTurn, distance, minimumDistanceToNearestFood = queue.pop()
        newDistance = distance + 1
        for turn in Turn:
            newState = state if turn == Turn.RIGHT else copyGameState(state)
            if moveSnake(newState, turn):
                if newState.score > state.score:
                    return firstTurn
                insert(queue, (newState, firstTurn, newDistance, minimumDistancesToNearestFood[newState.snake.head] + newDistance))
    return queue[-1][1] if queue else Turn.STRAIGHT


def getMinimumDistancesToNearestFood(state: GameState) -> dict[tuple[int, int], int]:
    minimumDistancesToNearestFood = {food: 0 for food in state.food}
    queue = deque(state.food)
    while queue:
        position = queue.popleft()
        newMinimumDistanceToNearestFood = minimumDistancesToNearestFood[position] + 1
        for xOffset, yOffset in DIRECTIONS:
            newX, newY = position[0] + xOffset, position[1] + yOffset
            if 0 <= newX < state.width and 0 <= newY < state.height:
                newPosition = (newX, newY)
                if newPosition not in state.walls and newPosition not in minimumDistancesToNearestFood:
                    minimumDistancesToNearestFood[newPosition] = newMinimumDistanceToNearestFood
                    queue.append(newPosition)
    return minimumDistancesToNearestFood


def copyGameState(state: GameState) -> GameState:
    return GameState(
        width = state.width,
        height = state.height,
        snake = copySnake(state.snake),
        enemies = [copySnake(enemy) for enemy in state.enemies],
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
    if nextHead in snake.body and nextHead != snake.body[-1]:
        return False
    if snake is not state.snake and nextHead in state.snake.body:
        return False
    for enemy in state.enemies:
        if enemy is not snake and enemy.isAlive and nextHead in enemy.body:
            return False
    willEat = nextHead in state.food
    snake.move(turn, grow = willEat)
    if willEat:
        state.food.remove(nextHead)
        snake.score += 1
        if snake is state.snake:
            state.score += 1
    return True

def moveEnemy(state: GameState, enemyIndex: int, turn: Turn) -> bool:
    enemy = state.enemies[enemyIndex]
    enemy.isAlive = moveAnySnake(state, enemy, turn)
    if not enemy.isAlive:
        for position in enemy.body:
            state.food.add(position)
    return enemy.isAlive


def getEnemyGameState(state: GameState, enemyIndex: int) -> GameState:
    enemy = state.enemies[enemyIndex]
    return GameState(
        width = state.width,
        height = state.height,
        snake = enemy,
        enemies = [state.snake] + [otherEnemy for otherEnemy in state.enemies if otherEnemy is not enemy and otherEnemy.isAlive],
        food = state.food,
        walls = state.walls,
        score = enemy.score
    )


def insert(queue: list[tuple[GameState, Turn, int, int]], element: tuple[GameState, Turn, int, int]):
    for index in reversed(range(len(queue))):
        otherElement = queue[index]
        if element[3] < otherElement[3] or (element[3] == otherElement[3] and element[2] >= otherElement[2]):
            queue.insert(index + 1, element)
            return
    queue.insert(0, element)
