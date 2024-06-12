import pygame
import sys
import random

points = 0
amount_of_moves = 0

class Player:
    def __init__(self, grid_pos, health):
        self.grid_pos = grid_pos
        self.image_idle = pygame.transform.scale(pygame.image.load("assets/sprites/player.png"), (GRID_SIZE, GRID_SIZE))
        self.image_hurt = pygame.transform.scale(pygame.image.load("assets/sprites/player_hurt.png"),
                                                 (GRID_SIZE, GRID_SIZE))
        self.image = self.image_idle
        self.health = health
        self.iframes = False
        self.alive = True
        grid[self.grid_pos[1]][self.grid_pos[0]] = PLAYER

    def draw(self, surface):
        rect = self.image.get_rect()
        rect.topleft = (self.grid_pos[0] * GRID_SIZE, self.grid_pos[1] * GRID_SIZE)
        surface.blit(self.image, rect)

    def move(self, direction, enemies):
        global amount_of_moves
        amount_of_moves += 1
        self.image = self.image_idle
        next_pos = self.grid_pos.copy()
        if direction == "LEFT":
            next_pos[0] -= 1
        elif direction == "RIGHT":
            next_pos[0] += 1
        elif direction == "UP":
            next_pos[1] -= 1
        elif direction == "DOWN":
            next_pos[1] += 1

        if 0 <= next_pos[0] < COLS and 0 <= next_pos[1] < ROWS:
            if grid[next_pos[1]][next_pos[0]] >= 2:
                get_entity_at_pos(next_pos, enemies).take_dmg(1)
            else:
                grid[self.grid_pos[1]][self.grid_pos[0]] = EMPTY
                self.grid_pos = next_pos
                grid[self.grid_pos[1]][self.grid_pos[0]] = PLAYER

    def take_dmg(self, amount):
        if not self.iframes:
            self.image = self.image_hurt
            self.health -= amount
            if self.health <= 0:
                grid[self.grid_pos[1]][self.grid_pos[0]] = EMPTY
                self.alive = False
            print(self.health)
            self.iframes = True


class Enemy:
    def __init__(self, image_idle_path, image_attack_path, grid_pos, health):
        self.grid_pos = grid_pos
        self.image_idle = pygame.transform.scale(pygame.image.load(image_idle_path), (GRID_SIZE, GRID_SIZE))
        self.image_attack = pygame.transform.scale(pygame.image.load(image_attack_path), (GRID_SIZE, GRID_SIZE))
        self.image = self.image_idle
        self.alive = True
        self.health = health
        self.parity = False

    def draw(self, surface):
        rect = self.image.get_rect()
        rect.topleft = (self.grid_pos[0] * GRID_SIZE, self.grid_pos[1] * GRID_SIZE)
        surface.blit(self.image, rect)

    def move(self, player):
        return

    def take_dmg(self, amount):
        global points
        self.health -= amount
        if self.health <= 0:
            self.alive = False
            grid[self.grid_pos[1]][self.grid_pos[0]] = EMPTY
            points += 100


class Bat(Enemy):
    def __init__(self, grid_pos, health):
        super().__init__("assets/sprites/bat_idle.png", "assets/sprites/bat_attack.png", grid_pos, health)
        grid[self.grid_pos[1]][self.grid_pos[0]] = BAT

    def move(self, player):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random.shuffle(directions)
        if self.parity:
            for dx, dy in directions:
                next_pos = [self.grid_pos[0] + dx, self.grid_pos[1] + dy]
                if 0 <= next_pos[0] < COLS and 0 <= next_pos[1] < ROWS:
                    if grid[next_pos[1]][next_pos[0]] == EMPTY:
                        self.parity = False
                        self.image = self.image_idle
                        grid[self.grid_pos[1]][self.grid_pos[0]] = EMPTY
                        self.grid_pos = next_pos
                        grid[self.grid_pos[1]][self.grid_pos[0]] = BAT
                        return
                    if grid[next_pos[1]][next_pos[0]] == PLAYER:
                        self.parity = False
                        self.image = self.image_idle
                        get_entity_at_pos(next_pos, player).take_dmg(1)
                        return
        else:
            self.parity = True
            grid[self.grid_pos[1]][self.grid_pos[0]] = BAT_ATTACKING
            self.image = self.image_attack


class Slime(Enemy):
    def __init__(self, grid_pos, health):
        super().__init__("assets/sprites/slime_idle.png", "assets/sprites/slime_attack.png", grid_pos, health)
        grid[self.grid_pos[1]][self.grid_pos[0]] = SLIME
        self.up = True

    def move(self, player):
        if self.up:
            direction = 1
        else:
            direction = -1
        if self.parity:
            next_pos = [self.grid_pos[0], self.grid_pos[1] + direction]
            if 0 <= next_pos[0] < COLS and 0 <= next_pos[1] < ROWS and grid[next_pos[1]][next_pos[0]] != WALL:
                if grid[next_pos[1]][next_pos[0]] == EMPTY:
                    self.up = not self.up
                    self.parity = False
                    self.image = self.image_idle
                    grid[self.grid_pos[1]][self.grid_pos[0]] = EMPTY
                    self.grid_pos = next_pos
                    grid[self.grid_pos[1]][self.grid_pos[0]] = SLIME
                    return
                if grid[next_pos[1]][next_pos[0]] == PLAYER:
                    self.parity = False
                    self.image = self.image_idle
                    get_entity_at_pos(next_pos, player).take_dmg(2)
        else:
            self.parity = True
            self.image = self.image_attack
            grid[self.grid_pos[1]][self.grid_pos[0]] = SLIME_ATTACKING


class DestructibleWall(Enemy):
    def __init__(self, grid_pos):
        super().__init__("assets/sprites/wall.png", "assets/sprites/wall.png", grid_pos, 1)
        grid[self.grid_pos[1]][self.grid_pos[0]] = WALL

    def take_dmg(self, amount):
        global points
        self.health -= amount
        if self.health <= 0:
            self.alive = False
            grid[self.grid_pos[1]][self.grid_pos[0]] = EMPTY


class Skeleton(Enemy):
    def __init__(self, grid_pos, health, direction):
        super().__init__("assets/sprites/skeleton_idle.png", "assets/sprites/skeleton_attack.png", grid_pos, health)
        self.direction = direction  # true - vertical false - "horizontal"

    def move(self, player):
        if self.parity:
            player_pos = player[0].grid_pos
            if self.direction:
                if self.grid_pos[1] != player_pos[1]:
                    next_pos = [self.grid_pos[0], self.grid_pos[1] + (1 if player_pos[1] > self.grid_pos[1] else -1)]
                else:
                    self.direction = False
                    next_pos = [self.grid_pos[0] + (1 if player_pos[0] > self.grid_pos[0] else -1), self.grid_pos[1]]
            else:  # horizontal
                if self.grid_pos[0] != player_pos[0]:
                    next_pos = [self.grid_pos[0] + (1 if player_pos[0] > self.grid_pos[0] else -1), self.grid_pos[1]]
                else:
                    self.direction = True
                    next_pos = [self.grid_pos[0], self.grid_pos[1] + (1 if player_pos[1] > self.grid_pos[1] else -1)]

            if 0 <= next_pos[0] < COLS and 0 <= next_pos[1] < ROWS:
                if grid[next_pos[1]][next_pos[0]] == EMPTY:
                    self.parity = False
                    self.image = self.image_idle
                    grid[self.grid_pos[1]][self.grid_pos[0]] = EMPTY
                    self.grid_pos = next_pos
                    grid[self.grid_pos[1]][self.grid_pos[0]] = SKELETON
                    return
                if grid[next_pos[1]][next_pos[0]] == PLAYER:
                    self.parity = False
                    self.image = self.image_idle
                    get_entity_at_pos(next_pos, player).take_dmg(1)
        else:
            self.parity = True
            grid[self.grid_pos[1]][self.grid_pos[0]] = SKELETON_ATTACKING
            self.image = self.image_attack


def isAlive(enemy):
    return enemy.alive


def get_entity_at_pos(pos, entities):
    for entity in entities:
        if entity.grid_pos == pos:
            return entity
    return None


# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 1000
GRID_SIZE = 100
ROWS = 10
COLS = 10
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Crypt of the AIdancer")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Define the grid
EMPTY = 0
PLAYER = 1
WALL = 2
BAT = 3
BAT_ATTACKING = 4
SLIME = 5
SLIME_ATTACKING = 6
SKELETON = 7
SKELETON_ATTACKING = 8

background = pygame.transform.scale(pygame.image.load("assets/sprites/floor.png"), (GRID_SIZE, GRID_SIZE))
background_lite = pygame.transform.scale(pygame.image.load("assets/sprites/floor2.png"), (GRID_SIZE, GRID_SIZE))
grid = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

def create_entities(matrix):
    player = []
    enemies = []

    for y, row in enumerate(matrix):
        for x, value in enumerate(row):
            if value == PLAYER:
                player = [Player([x, y], 6)]
            elif value == SLIME:
                enemies.append(Slime([x, y], 2))
            elif value == SKELETON:
                enemies.append(Skeleton([x, y], 1, random.choice([True, False])))
            elif value == BAT:
                enemies.append(Bat([x, y], 1))
            elif value == WALL:
                enemies.append(DestructibleWall([x, y]))
    return player, enemies


def isNotWall(enemy):
    return not isinstance(enemy, DestructibleWall)
# PLAYER = 1
# WALL = 2
# BAT = 3
# SLIME = 5
# SKELETON = 7
def main():
    matrix = [
        [2, 2, 2, 1, 2, 2, 2, 2, 2, 2],
        [2, 2, 2, 0, 2, 2, 2, 2, 2, 2],
        [2, 2, 2, 7, 2, 2, 2, 2, 2, 2],
        [2, 2, 0, 0, 0, 0, 0, 2, 2, 2],
        [2, 2, 0, 0, 0, 0, 5, 2, 2, 2],
        [2, 2, 0, 0, 0, 5, 0, 2, 2, 2],
        [2, 2, 7, 0, 0, 0, 0, 2, 2, 2],
        [2, 2, 0, 0, 0, 0, 0, 2, 2, 2],
        [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
        [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    ]
    player, enemies = create_entities(matrix)
    prev_turn_iframes = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    player[0].move("LEFT", enemies)
                elif event.key == pygame.K_RIGHT:
                    player[0].move("RIGHT", enemies)
                elif event.key == pygame.K_UP:
                    player[0].move("UP", enemies)
                elif event.key == pygame.K_DOWN:
                    player[0].move("DOWN", enemies)
                enemies = list(filter(isAlive, enemies))
                for enemy in enemies:
                    enemy.move(player)
                if player[0].iframes and not prev_turn_iframes:
                    prev_turn_iframes = True
                else:
                    player[0].iframes = False
                    prev_turn_iframes = False
        if not player[0].alive:
            running = False

        # Draw everything
        for y in range(0, ROWS):
            for x in range(0, COLS):
                if (x + y) % 2 == 0:
                    screen.blit(background, (x * GRID_SIZE, y * GRID_SIZE))
                else:
                    screen.blit(background_lite, (x * GRID_SIZE, y * GRID_SIZE))
        player[0].draw(screen)
        for enemy in enemies:
            enemy.draw(screen)

        pygame.display.flip()
    global points
    enemies_without_walls = list(filter(isNotWall, enemies))
    print(points + player[0].health * 500 + len(enemies_without_walls) * -250 + amount_of_moves * -100)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
