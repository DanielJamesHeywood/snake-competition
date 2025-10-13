import random
from collections import deque
from snake.logic import GameState, Turn, Snake, Direction

from snake.logic import DIRECTIONS
from examples.smartAI import smartAI as enemyAI


def myAI(state: GameState) -> Turn:
    minimumDistancesToNearestFood = {food: 0 for food in state.food}
    queue = deque([food for food in state.food])
    while queue:
        position = queue.popleft()
        minimumDistanceToNearestFood = minimumDistancesToNearestFood[position] + 1
        for xOffset, yOffset in DIRECTIONS:
            newX, newY = position[0] + xOffset, position[1] + yOffset
            if 0 <= newX < state.width and 0 <= newY < state.height:
                newPosition = (newX, newY)
                if newPosition not in state.walls and newPosition not in minimumDistancesToNearestFood:
                    minimumDistancesToNearestFood[newPosition] = minimumDistanceToNearestFood
                    queue.append(newPosition)
    queue = []
    for turn in Turn:
        newState = copyGameState(state)
        if moveSnake(newState, turn):
            if newState.score > state.score:
                tail = newState.snake.body[-1]
                minimumDistancesToTail = {tail: 0}
                otherQueue = deque([tail])
                while otherQueue:
                    position = otherQueue.popleft()
                    minimumDistanceToTail = minimumDistancesToTail[position] + 1
                    for xOffset, yOffset in DIRECTIONS:
                        newX, newY = position[0] + xOffset, position[1] + yOffset
                        if 0 <= newX < state.width and 0 <= newY < state.height:
                            newPosition = (newX, newY)
                            if newPosition not in newState.walls and newPosition not in minimumDistancesToTail:
                                minimumDistancesToTail[newPosition] = minimumDistanceToTail
                                otherQueue.append(newPosition)
                otherQueue = [(newState, minimumDistancesToTail[newState.snake.head])]
                while otherQueue and len(otherQueue) < 256:
                    otherState, minimumDistanceToTail = otherQueue.pop()
                    for otherTurn in Turn:
                        newOtherState = otherState if otherTurn == Turn.RIGHT else copyGameState(otherState)
                        if moveSnake(newOtherState, otherTurn):
                            minimumDistanceToTail = minimumDistancesToTail[newOtherState.snake.head]
                            if minimumDistanceToTail == 0:
                                return turn
                            inserted = False
                            for index in reversed(range(len(otherQueue))):
                                otherElement = otherQueue[index]
                                if minimumDistanceToTail <= otherElement[1]:
                                    otherQueue.insert(index + 1, (newOtherState, minimumDistanceToTail))
                                    inserted = True
                                    break
                            if not inserted:
                                otherQueue.insert(0, (newOtherState, minimumDistanceToTail))
                if otherQueue:
                    return turn
            insert(queue, (newState, turn, 1, minimumDistancesToNearestFood[newState.snake.head] + 1))
    while queue and len(queue) < 256:
        state, firstTurn, distance, minimumDistanceToNearestFood = queue.pop()
        newDistance = distance + 1
        for turn in Turn:
            newState = state if turn == Turn.RIGHT else copyGameState(state)
            if moveSnake(newState, turn):
                if newState.score > state.score:
                    tail = newState.snake.body[-1]
                    minimumDistancesToTail = {tail: 0}
                    otherQueue = deque([tail])
                    while otherQueue:
                        position = otherQueue.popleft()
                        minimumDistanceToTail = minimumDistancesToTail[position] + 1
                        for xOffset, yOffset in DIRECTIONS:
                            newX, newY = position[0] + xOffset, position[1] + yOffset
                            if 0 <= newX < state.width and 0 <= newY < state.height:
                                newPosition = (newX, newY)
                                if newPosition not in newState.walls and newPosition not in minimumDistancesToTail:
                                    minimumDistancesToTail[newPosition] = minimumDistanceToTail
                                    otherQueue.append(newPosition)
                    otherQueue = [(newState, minimumDistancesToTail[newState.snake.head])]
                    while otherQueue and len(otherQueue) < 256:
                        otherState, minimumDistanceToTail = otherQueue.pop()
                        for otherTurn in Turn:
                            newOtherState = otherState if otherTurn == Turn.RIGHT else copyGameState(otherState)
                            if moveSnake(newOtherState, otherTurn):
                                minimumDistanceToTail = minimumDistancesToTail[newOtherState.snake.head]
                                if minimumDistanceToTail == 0:
                                    return firstTurn
                                inserted = False
                                for index in reversed(range(len(otherQueue))):
                                    otherElement = otherQueue[index]
                                    if minimumDistanceToTail <= otherElement[1]:
                                        otherQueue.insert(index + 1, (newOtherState, minimumDistanceToTail))
                                        inserted = True
                                        break
                                if not inserted:
                                    otherQueue.insert(0, (newOtherState, minimumDistanceToTail))
                    if otherQueue:
                        return turn
                insert(queue, (newState, firstTurn, newDistance, minimumDistancesToNearestFood[newState.snake.head] + newDistance))
    return queue[-1][1] if queue else Turn.STRAIGHT


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
    moved = moveAnySnake(state, state.snake, turn)
    state.snake.isAlive = moved
    if moved:
        for index in range(len(state.enemies)):
            if state.enemies[index].isAlive:
                moveEnemy(state, index, enemyAI(getEnemyGameState(state, index)))
    return moved


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
        snake.score += 1
        if snake is state.snake:
            state.score += 1
    return True

def moveEnemy(state: GameState, enemyIndex: int, turn: Turn) -> bool:
    enemy = state.enemies[enemyIndex]
    moved = moveAnySnake(state, enemy, turn)
    enemy.isAlive = moved
    if not moved:
        for position in enemy.body:
            state.food.add(position)
    return moved


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
