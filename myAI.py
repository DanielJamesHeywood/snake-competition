import random
from collections import deque
from snake.logic import GameState, Turn, Snake, Direction

from snake.logic import DIRECTIONS
from examples.smartAI import smartAI as enemyAI


def myAI(state: GameState) -> Turn:
    priorityQueue = deque()
    for turn in Turn:
        newState = copyGameState(state)
        if moveSnake(newState, turn):
            if newState.score > state.score:
                return turn
            insertIntoPriorityQueueForFoodFinding(
                priorityQueue,
                (newState, turn, 1, getDistanceToNearestFood(newState))
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
                    (newState, turn, newDistance, getDistanceToNearestFood(newState))
                )
    return Turn.STRAIGHT


def getDistanceToNearestFood(state):
    return getDistanceToNearestTarget(state, state.food)


def getDistanceToNearestTarget(state, targets):
    priorityQueue = deque()
    insertIntoPriorityQueueForDistanceFinding(
        priorityQueue,
        (state.snake.head, state.snake.direction, 0)
    )
    visited = {state.snake.head}
    while priorityQueue:
        position, direction, distance = priorityQueue.popleft()
        x, y = position
        newDistance = distance + 1
        for xOffset, yOffset in DIRECTIONS:
            newX, newY = x + xOffset, y + yOffset
            if 0 <= newX < state.width and 0 <= newY < state.height:
                newPosition = (newX, newY)
                if newPosition in targets:
                    return newDistance
                if newPosition not in state.walls and newPosition not in visited:
                    visited.add(newPosition)
                    insertIntoPriorityQueueForDistanceFinding(
                        priorityQueue,
                        (newPosition, None, newDistance)
                    )
    return None


def insertIntoPriorityQueueForFoodFinding(priorityQueue, newElement):
    def compare(lhs, rhs):
        lhState, lhTurn, lhDistance, lhDistanceToNearestFood = lhs
        lhTotalDistanceToNearestFood = lhDistance + lhDistanceToNearestFood
        rhState, rhTurn, rhDistance, rhDistanceToNearestFood = rhs
        rhTotalDistanceToNearestFood = rhDistance + rhDistanceToNearestFood
        if lhTotalDistanceToNearestFood != rhTotalDistanceToNearestFood:
            return -1 if lhTotalDistanceToNearestFood < rhTotalDistanceToNearestFood else 1
        return -1 if lhDistance > rhDistance else 0 if lhDistance == rhDistance else 1
    insertIntoPriorityQueue(priorityQueue, newElement, compare)


def insertIntoPriorityQueueForDistanceFinding(priorityQueue, newElement):
    def compare(lhs, rhs):
        lhPosition, lhDirection, lhDistance = lhs
        rhPosition, rhDirection, rhDistance = rhs
        return -1 if lhDistance < rhDistance else 0 if lhDistance == rhDistance else 1
    insertIntoPriorityQueue(priorityQueue, newElement, compare)


def insertIntoPriorityQueue(priorityQueue, newElement, compare):
    for index, element in enumerate(priorityQueue):
        if compare(newElement, element) <= 0:
            priorityQueue.insert(index, newElement)
            return
    priorityQueue.append(newElement)


def copyGameState(state):
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


def copySnake(snake):
    copy = Snake(0, 0, snake.id)
    copy.score = snake.score
    copy.isAlive = snake.isAlive
    copy.body = snake.body.copy()
    copy.direction = snake.direction
    return copy


def moveSnake(state, turn):
    state.snake.isAlive = moveAnySnake(state, state.snake, turn)
    if state.snake.isAlive:
        for index in range(len(state.enemies)):
            if state.enemies[index].isAlive:
                moveEnemy(state, index, enemyAI(getEnemyGameState(state, index)))
    return state.snake.isAlive


def moveEnemy(state, enemyIndex, turn):
    enemy = state.enemies[enemyIndex]
    enemy.isAlive = moveAnySnake(state, enemy, turn)
    if not enemy.isAlive:
        for position in enemy.body:
            state.food.add(position)
    return enemy.isAlive


def moveAnySnake(state, snake, turn):
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


def getEnemyGameState(state, enemyIndex):
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
