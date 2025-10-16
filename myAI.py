import random
from collections import deque
from snake.logic import GameState, Turn, Snake, Direction

from snake.logic import DIRECTIONS
from examples.smartAI import smartAI as enemyAI


def myAI(state: GameState) -> Turn:
    distancesToNearestFood = {
        food: 0 for food in state.food
    }
    queue = deque(state.food)
    while queue:
        position = queue.popleft()
        newDistanceToNearestFood = distancesToNearestFood[position] + 1
        for xOffset, yOffset in DIRECTIONS:
            newX, newY = position[0] + xOffset, position[1] + yOffset
            if 0 <= newX < state.width and 0 <= newY < state.height:
                newPosition = (newX, newY)
                if newPosition not in state.walls and newPosition not in distancesToNearestFood:
                    distancesToNearestFood[newPosition] = newDistanceToNearestFood
                    queue.append(newPosition)
    priorityQueue = deque()
    for turn in Turn:
        newState = copyGameState(state)
        if moveSnake(newState, turn):
            if newState.score > state.score:
                return turn
            insertInto((newState, turn, 1, distancesToNearestFood[newState.snake.head] + 1), priorityQueue)
    while priorityQueue and len(priorityQueue) < 256:
        state, firstTurn, distance, distanceToNearestFood = priorityQueue.popleft()
        newDistance = distance + 1
        for turn in Turn:
            newState = state if turn == Turn.RIGHT else copyGameState(state)
            if moveSnake(newState, turn):
                if newState.score > state.score:
                    return firstTurn
                insertInto((newState, firstTurn, newDistance, distancesToNearestFood[newState.snake.head] + newDistance), priorityQueue)
    return priorityQueue[-1][1] if priorityQueue else Turn.STRAIGHT


def insertInto(element: tuple[GameState, Turn, int, int], priorityQueue: deque[tuple[GameState, Turn, int, int]]):
    for index, otherElement in enumerate(priorityQueue):
        if element[3] < otherElement[3] or (element[3] == otherElement[3] and element[2] >= otherElement[2]):
            priorityQueue.insert(index, element)
            return
    priorityQueue.append(element)


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
        enemies = [state.snake] + [
            otherEnemy for otherEnemy in state.enemies if otherEnemy is not enemy and otherEnemy.isAlive
        ],
        food = state.food,
        walls = state.walls,
        score = enemy.score
    )
