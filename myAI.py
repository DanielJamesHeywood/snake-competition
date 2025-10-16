import random
from collections import deque
from snake.logic import GameState, Turn, Snake, Direction

from typing import Callable
from snake.logic import DIRECTIONS
from examples.smartAI import smartAI as enemyAI


def myAI(state: GameState) -> Turn:
    distancesToNearestFood = getDistancesToNearestTarget(state, state.food)
    priorityQueue = deque()
    for turn in Turn:
        newState = copyGameState(state)
        if moveSnake(newState, turn):
            if newState.score > state.score:
                return turn
            insertIntoPriorityQueueForFoodFinding(
                priorityQueue,
                (newState, turn, 1, distancesToNearestFood[newState.snake.head] + 1)
            )
    while priorityQueue and len(priorityQueue) < 256:
        state, turn, distance, distanceToNearestFood = priorityQueue.popleft()
        newDistance = distance + 1
        for newTurn in Turn:
            newState = state if newTurn == Turn.RIGHT else copyGameState(state)
            if moveSnake(newState, newTurn):
                if newState.score > state.score:
                    return turn
                insertIntoPriorityQueueForFoodFinding(
                    priorityQueue,
                    (newState, turn, newDistance, distancesToNearestFood[newState.snake.head] + newDistance)
                )
    return priorityQueue[-1][1] if priorityQueue else Turn.STRAIGHT


def getDistancesToNearestTarget(state: GameState, targets: set[tuple[int, int]]) -> dict[tuple[int, int], int]:
    distancesToNearestTarget = {
        target: 0 for target in targets
    }
    queue = deque(
        (target, 0) for target in targets
    )
    while queue:
        position, distanceToNearestTarget = queue.popleft()
        newDistanceToNearestTarget = distanceToNearestTarget + 1
        for xOffset, yOffset in DIRECTIONS:
            newX, newY = position[0] + xOffset, position[1] + yOffset
            if 0 <= newX < state.width and 0 <= newY < state.height:
                newPosition = (newX, newY)
                if newPosition not in state.walls and newPosition not in distancesToNearestTarget:
                    distancesToNearestTarget[newPosition] = newDistanceToNearestTarget
                    queue.append((newPosition, newDistanceToNearestTarget))
    return distancesToNearestTarget


def insertIntoPriorityQueueForFoodFinding(
    priorityQueue: deque[tuple[GameState, Turn, int, int]],
    newElement: tuple[GameState, Turn, int, int]
):
    def compare(lhs: tuple[GameState, Turn, int, int], rhs: tuple[GameState, Turn, int, int]) -> int:
        lhDistanceToNearestFood, rhDistanceToNearestFood = lhs[3], rhs[3]
        if lhDistanceToNearestFood != rhDistanceToNearestFood:
            return -1 if lhDistanceToNearestFood < rhDistanceToNearestFood else 1
        lhDistance, rhDistance = lhs[2], rhs[2]
        return -1 if lhDistance > rhDistance else 0 if lhDistance == rhDistance else 1
    insertIntoPriorityQueue(priorityQueue, newElement, compare)


def insertIntoPriorityQueue[E](priorityQueue: deque[E], newElement: E, compare: Callable[[E, E], int]):
    for index, element in enumerate(priorityQueue):
        if compare(newElement, element) <= 0:
            priorityQueue.insert(index, newElement)
            return
    priorityQueue.append(newElement)


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


def moveEnemy(state: GameState, enemyIndex: int, turn: Turn) -> bool:
    enemy = state.enemies[enemyIndex]
    enemy.isAlive = moveAnySnake(state, enemy, turn)
    if not enemy.isAlive:
        for position in enemy.body:
            state.food.add(position)
    return enemy.isAlive


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
