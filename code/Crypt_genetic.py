import pygame
import sys
import random
import numpy as np

points = 0
amount_of_moves = 0


# Screen dimensions
WIDTH, HEIGHT = 1000, 1000
GRID_SIZE = 100
ROWS = 10
COLS = 10
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("Crypt of the AIdancer")

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

background = pygame.transform.scale(pygame.image.load("../assets/sprites/floor.png"), (GRID_SIZE, GRID_SIZE))
background_lite = pygame.transform.scale(pygame.image.load("../assets/sprites/floor2.png"), (GRID_SIZE, GRID_SIZE))
grid = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]


class Player:
    def __init__(self, grid_pos, health):
        self.grid_pos = grid_pos
        self.image_idle = pygame.transform.scale(pygame.image.load("../assets/sprites/player.png"), (GRID_SIZE, GRID_SIZE))
        self.image_hurt = pygame.transform.scale(pygame.image.load("../assets/sprites/player_hurt.png"),
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
        super().__init__("../assets/sprites/bat_idle.png", "../assets/sprites/bat_attack.png", grid_pos, health)
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
        super().__init__("../assets/sprites/slime_idle.png", "../assets/sprites/slime_attack.png", grid_pos, health)
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
        super().__init__("../assets/sprites/wall.png", "../assets/sprites/wall.png", grid_pos, 1)
        grid[self.grid_pos[1]][self.grid_pos[0]] = WALL

    def take_dmg(self, amount):
        global points
        self.health -= amount
        if self.health <= 0:
            self.alive = False
            grid[self.grid_pos[1]][self.grid_pos[0]] = EMPTY


class Skeleton(Enemy):
    def __init__(self, grid_pos, health, direction):
        super().__init__("../assets/sprites/skeleton_idle.png", "../assets/sprites/skeleton_attack.png", grid_pos,
                         health)
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
                enemies.append(Skeleton([x, y], 1, False))
            elif value == BAT:
                enemies.append(Bat([x, y], 1))
            elif value == WALL:
                enemies.append(DestructibleWall([x, y]))
    return player, enemies


def isAlive(enemy):
    return enemy.alive


def get_entity_at_pos(pos, entities):
    for entity in entities:
        if entity.grid_pos == pos:
            return entity
    return None


def isNotWall(enemy):
    return not isinstance(enemy, DestructibleWall)


# Genetic Algorithm functions
def initialize_population(size, genome_length):
    return [np.random.choice(['LEFT', 'RIGHT', 'UP', 'DOWN'], genome_length) for _ in range(size)]


def evaluate_genome(genome):
    global grid, points, amount_of_moves
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
    grid = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
    points = 0
    amount_of_moves = 0
    player, enemies = create_entities(matrix)
    for move in genome:
        if not player[0].alive:
            break
        player[0].move(move, enemies)
        enemies = list(filter(isAlive, enemies))
        for enemy in enemies:
            enemy.move(player)
        enemies_without_walls = list(filter(isNotWall, enemies))
        if len(enemies_without_walls) == 0:
            break
    return points + player[0].health * 500 - len(enemies_without_walls) * 1000 - amount_of_moves * 100


def selection(population, fitnesses, num_parents):
    selected_indices = np.argsort(fitnesses)[-num_parents:]
    return [population[i] for i in selected_indices]


def crossover(parent1, parent2):
    point = random.randint(1, len(parent1) - 1)
    child1 = np.concatenate([parent1[:point], parent2[point:]])
    child2 = np.concatenate([parent2[:point], parent1[point:]])
    return child1, child2


def mutate(genome, mutation_rate=0.01):
    for i in range(len(genome)):
        if random.random() < mutation_rate:
            genome[i] = random.choice(['LEFT', 'RIGHT', 'UP', 'DOWN'])
    return genome


def genetic_algorithm():
    population_size = 300
    genome_length = 30
    num_generations = 50
    num_parents = 30
    mutation_rate = 0.2

    population = initialize_population(population_size, genome_length)

    for generation in range(num_generations):
        fitnesses = [evaluate_genome(genome) for genome in population]
        parents = selection(population, fitnesses, num_parents)
        next_population = []
        for i in range(population_size // 2):
            parent1, parent2 = random.sample(parents, 2)
            child1, child2 = crossover(parent1, parent2)
            next_population.append(mutate(child1, mutation_rate))
            next_population.append(mutate(child2, mutation_rate))
        population = next_population
        fitnesses = [evaluate_genome(genome) for genome in population]
        best_fitness = max(fitnesses)
        print(f'Generation {generation + 1}, Best Fitness: {best_fitness}')
        best_genome = population[np.argmax(fitnesses)]
        if best_fitness == 2000:
            print(population)
            break
    return best_genome



def main():
    best_genome = genetic_algorithm()
    print(f'Best Genome: {best_genome}')

if __name__ == "__main__":
    main()
