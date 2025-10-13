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
            newPosition = (newX, newY)
            if 0 <= newX < state.width and 0 <= newY < state.height:
                newPosition = (newX, newY)
                if newPosition not in state.walls and newPosition not in minimumDistancesToNearestFood:
                    minimumDistancesToNearestFood[newPosition] = minimumDistanceToNearestFood
                    queue.append(newPosition)
    
    states = {
        turn: [] for turn in Turn
    }
    for turn in Turn:
        newState = copyGameState(state)
        if moveSnake(newState, turn):
            if newState.score > state.score:
                return turn
            states[turn].append((newState, 1, minimumDistancesToNearestFood[newState.snake.head] + 1, turn))
    while any(states.values()):
        turnForMinimum = None
        stateForMinimum, distanceForMinimum, minimumDistanceToNearestFood, ldForMinimum = None, None, None, None
        for turn in Turn:
            for state, distance, distanceToNearestFood, ld in states[turn]:
                if minimumDistanceToNearestFood is None or distanceToNearestFood < minimumDistanceToNearestFood or (distanceToNearestFood == minimumDistanceToNearestFood and distance > distanceForMinimum) or (distanceToNearestFood == minimumDistanceToNearestFood and distance == distanceForMinimum and ld != Turn.STRAIGHT):
                    turnForMinimum = turn
                    stateForMinimum, distanceForMinimum, minimumDistanceToNearestFood, ldForMinimum = state, distance, distanceToNearestFood, ld
        states[turnForMinimum].remove((stateForMinimum, distanceForMinimum, minimumDistanceToNearestFood, ldForMinimum))
        for newTurn in Turn:
            newState = stateForMinimum if newTurn == Turn.RIGHT else copyGameState(stateForMinimum)
            if moveSnake(newState, newTurn):
                if newState.score > state.score:
                    return turnForMinimum
                newDistanceForMinimum = distanceForMinimum + 1
                states[turnForMinimum].append((newState, newDistanceForMinimum, minimumDistancesToNearestFood[newState.snake.head] + newDistanceForMinimum, newTurn))
    return Turn.STRAIGHT


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
        # if len(self.food) < self.num_food:
        #     self.spawn_food()
        snake.score += 1
        if snake is state.snake:
            state.score += 1
        # self.spawn_wall()
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
