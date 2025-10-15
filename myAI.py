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
    states = []
    queue = set()
    for turn in Turn:
        newState = copyGameState(state)
        if moveSnake(newState, turn):
            states.append(newState)
            queue.add((len(states) - 1, turn, 1))
    while queue and len(states) < 256:
        stateForMinimum, firstTurnForMinimum, distanceForMinimum = None, None, None
        minimumDistanceToNearestFood = None
        for stateIndex, firstTurn, distance in queue:
            state = states[stateIndex]
            distanceToNearestFood = distancesToNearestFood[state.snake.head]
            if distanceToNearestFood == 0:
                return firstTurn
            distanceToNearestFood += distance + 1
            if not stateForMinimum or distanceToNearestFood < minimumDistanceToNearestFood or (distanceToNearestFood == minimumDistanceToNearestFood and distance > distanceForMinimum):
                stateForMinimum, firstTurnForMinimum, distanceForMinimum = state, firstTurn, distance
                minimumDistanceToNearestFood = distanceToNearestFood
        newDistance = distanceForMinimum + 1
        for turn in Turn:
            newState = stateForMinimum if turn == Turn.RIGHT else copyGameState(stateForMinimum)
            if moveSnake(newState, turn):
                states.append(newState)
                queue.add((len(states) - 1, firstTurnForMinimum, newDistance))
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
