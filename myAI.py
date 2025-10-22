import random
from collections import deque
from snake.logic import GameState, Turn, Snake, Direction

import time
from snake.logic import DIRECTIONS
from examples.smartAI import smartAI as enemyAI


def myAI(state: GameState) -> Turn:
    priorityQueue = deque()
    for turn in Turn:
        newState = copyGameState(state)
        if moveSnake(newState, turn):
            if newState.score > state.score:
                if headIsRereachable(newState):
                    return turn
            else:
                newDistanceToNearestFood = getDistanceToNearestFood(newState)
                if newDistanceToNearestFood:
                    insertIntoPriorityQueueForFoodFinding(
                        priorityQueue,
                        (newState, turn, 1, newDistanceToNearestFood)
                    )
    while priorityQueue:
        state, turn, distance, _ = priorityQueue.popleft()
        newDistance = distance + 1
        for newTurn in Turn:
            newState = state if newTurn == Turn.RIGHT else copyGameState(state)
            if moveSnake(newState, newTurn):
                if newState.score > state.score:
                    if headIsRereachable(newState):
                        return turn
                else:
                    newDistanceToNearestFood = getDistanceToNearestFood(newState)
                    if newDistanceToNearestFood:
                        insertIntoPriorityQueueForFoodFinding(
                            priorityQueue,
                            (newState, turn, newDistance, newDistanceToNearestFood)
                        )
    return Turn.STRAIGHT


def headIsRereachable(state):

    head = state.snake.head

    priorityQueue = deque()
    insertIntoPriorityQueueForHeadFinding(
        priorityQueue,
        (state, getDistanceToTarget(state, head))
    )

    while priorityQueue:

        state, _ = priorityQueue.popleft()

        for turn in Turn:
            newState = state if turn == Turn.RIGHT else copyGameState(state)
            if moveSnake(newState, turn):

                newDistanceToHead = getDistanceToTarget(newState, head)

                if newDistanceToHead == 0:
                    return True

                insertIntoPriorityQueueForHeadFinding(
                    priorityQueue,
                    (newState, newDistanceToHead)
                )

    return False


def getDistanceToNearestFood(state):
    return getDistanceToNearestTarget(state, state.food)


def getDistanceToTarget(state, target):
    return getDistanceToNearestTarget(state, {target})


def getDistanceToNearestTarget(state, targets):

    minimumDistancesToCellsInBodies = {}

    for index, position in enumerate(state.snake.body):

        minimumDistanceToHead = len(state.snake.body) - 1

        if minimumDistanceToHead % 2 != 0:
            minimumDistanceToHead += 1

        minimumDistancesToCellsInBodies[position] = minimumDistanceToHead - index

    for enemy in state.enemies:
        if enemy.isAlive:

            minimumDistanceToHead = len(enemy.body)

            x, y = state.snake.head
            enemyX, enemyY = enemy.head
            if minimumDistanceToHead % 2 != (abs(x - enemyX) + abs(y - enemyY)) % 2:
                minimumDistanceToHead += 1

            for index, position in enumerate(enemy.body):
                minimumDistancesToCellsInBodies[position] = minimumDistanceToHead - index

    priorityQueue = deque()
    insertIntoPriorityQueueForDistanceFinding(
        priorityQueue,
        (state.snake.head, 0)
    )

    visited = {state.snake.head}

    while priorityQueue:

        position, distance = priorityQueue.popleft()

        if position in targets:
            return distance

        x, y = position
        for xOffset, yOffset in DIRECTIONS:
            newX, newY = x + xOffset, y + yOffset
            if 0 <= newX < state.width and 0 <= newY < state.height:
                newPosition = (newX, newY)
                if newPosition not in state.walls and newPosition not in visited:

                    visited.add(newPosition)

                    newDistance = distance + 1

                    if newPosition in minimumDistancesToCellsInBodies:
                        minimumDistance = minimumDistancesToCellsInBodies[newPosition]
                        if newDistance < minimumDistance:
                            newDistance = minimumDistance

                    insertIntoPriorityQueueForDistanceFinding(
                        priorityQueue,
                        (newPosition, newDistance)
                    )

    return None


def insertIntoPriorityQueueForFoodFinding(priorityQueue, newElement):

    def compare(lhs, rhs):

        _, _, lhDistance, lhDistanceToNearestFood = lhs
        lhTotalDistanceToNearestFood = lhDistance + lhDistanceToNearestFood

        _, _, rhDistance, rhDistanceToNearestFood = rhs
        rhTotalDistanceToNearestFood = rhDistance + rhDistanceToNearestFood

        if lhTotalDistanceToNearestFood != rhTotalDistanceToNearestFood:
            return -1 if lhTotalDistanceToNearestFood < rhTotalDistanceToNearestFood else 1

        return -1 if lhDistance > rhDistance else 0 if lhDistance == rhDistance else 1

    insertIntoPriorityQueue(priorityQueue, newElement, compare)


def insertIntoPriorityQueueForHeadFinding(priorityQueue, newElement):

    def compare(lhs, rhs):

        _, lhDistanceToHead = lhs

        _, rhDistanceToHead = rhs

        return -1 if lhDistanceToHead < rhDistanceToHead else 0 if lhDistanceToHead == rhDistanceToHead else 1

    insertIntoPriorityQueue(priorityQueue, newElement, compare)


def insertIntoPriorityQueueForDistanceFinding(priorityQueue, newElement):

    def compare(lhs, rhs):

        _, lhDistance = lhs

        _, rhDistance = rhs

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
