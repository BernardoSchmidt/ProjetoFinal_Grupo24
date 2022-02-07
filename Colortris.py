from ast import While
import pygame
import random
from operator import itemgetter
from itertools import groupby

# Variaveis globais
color_red = (255,0,0)
color_yellow = (255,255,0)
color_blue = (0,0,255)
color_green = (0,128,0)

colors = [
    (0,0,0),
    color_red,
    color_yellow,
    color_blue,
    color_green,
]

class Figure:
    x = 0
    y = 0

    figures = [
        [[1, 1, 1]], 
    ]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.randint(0, len(self.figures) - 1)
        self.color = random.randint(1, len(colors) - 1)
        figure_color = ""

        #Id dado a peças com certa cor
        if(self.color == 1):
            figure_color = "red"
        elif(self.color == 2):
            figure_color = "yellow"
        elif(self.color == 3):
            figure_color = "blue"
        elif(self.color == 4):
            figure_color = "green"

        self.identificator = figure_color
        self.rotation = 0

    def image(self):
        return self.figures[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.figures[self.type])

class Colortris:
    # Variaveis locais
    level = 2
    score = 0
    state = "start"
    field = []
    height = 0
    width = 0
    x = 80
    y = 60
    zoom = 30
    figure = None

    # Desenha janela do jogo
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.field = []
        self.score = 0
        self.state = "start"
        for i in range(height):
            new_line = []
            for j in range(width):
                new_line.append(0)
            self.field.append(new_line)

    # Desenha peça
    def new_figure(self):
        self.figure = Figure(2, 0)

    # Valida se a peça tocou no topo do ecrã
    def intersects(self):
        intersection = False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if i + self.figure.y > self.height - 1 or \
                            j + self.figure.x > self.width - 1 or \
                            j + self.figure.x < 0 or \
                            self.field[i + self.figure.y][j + self.figure.x] > 0:
                        intersection = True
        return intersection
    
    # Limpa peças e atribiu pontos
    def break_lines(self):
        horizontal_list = self.field
        vertical_list = [list(tup) for tup in zip(*self.field)]
        value_a = -1
        value_b = -1

        for b in horizontal_list:
            value_a += 1
            ignore_zero = [value for value in b if value != 0]
            if (any(i==j for i,j in zip(ignore_zero, ignore_zero[2:]))):
                c = [v for k, g in groupby(b) for v in [k] + [0] * (len(list(g))-1)]
                self.score += 1
                horizontal_list[value_a] = c

        for b in vertical_list:
            value_b += 1
            ignore_zero = [value for value in b if value != 0]
            if (any(i==j for i,j in zip(ignore_zero, ignore_zero[2:]))):
                c = [v for k, g in groupby(b) for v in [k] + [0] * (len(list(g))-1)]
                self.score += 1
                vertical_list[value_b] = c
                self.field = [list(tup) for tup in zip(*vertical_list)]

    def go_space(self):
        while not self.intersects():
            self.figure.y += 1
        self.figure.y -= 1
        self.freeze()

    def go_down(self):
        self.figure.y += 1
        if self.intersects():
            self.figure.y -= 1
            self.freeze()

    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
        self.break_lines()
        self.new_figure()
        if self.intersects():
            self.state = "gameover"

    def go_side(self, dx):
        old_x = self.figure.x
        self.figure.x += dx
        if self.intersects():
            self.figure.x = old_x

    def rotate(self):
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects():
            self.figure.rotation = old_rotation

# Inicia a game engine
pygame.init()

# Define cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

size = (360, 640)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Colotris")

# Loop
done = False
clock = pygame.time.Clock()
fps = 10
game = Colortris(10, 7)
counter = 0

pressing_down = False

while not done:
    # Desenha a primeira peça
    if game.figure is None:
        game.new_figure()
    counter += 1
    if counter > 100000:
        counter = 0

    # Velocidade das peças
    if counter % (fps // game.level // 2) == 0 or pressing_down:
        if game.state == "start":
            game.go_down()

    # Controlos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                pressing_down = True
            if event.key == pygame.K_LEFT:
                game.go_side(-1)
            if event.key == pygame.K_RIGHT:
                game.go_side(1)
            if event.key == pygame.K_SPACE:
                game.go_space()
            if event.key == pygame.K_ESCAPE:
                game.__init__(10, 7)

    if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                pressing_down = False

    # Cor de fundo
    screen.fill(BLACK)

    # Desenha grelha de jogo
    for i in range(game.height):
        for j in range(game.width):
            pygame.draw.rect(screen, GRAY, [game.x + game.zoom * j, game.y + game.zoom * i, game.zoom, game.zoom], 1)
            if game.field[i][j] > 0:
                pygame.draw.rect(screen, colors[game.field[i][j]],
                                 [game.x + game.zoom * j + 1, game.y + game.zoom * i + 1, game.zoom - 2, game.zoom - 1])

    # Desenha queda da peça
    if game.figure is not None:
        for i in range(4):
            for j in range(4):
                p = i * 4 + j
                if p in game.figure.image():
                    pygame.draw.rect(screen, colors[game.figure.color],
                                     [game.x + game.zoom * (j + game.figure.x) + 1,
                                      game.y + game.zoom * (i + game.figure.y) + 1,
                                      game.zoom - 2, game.zoom - 2])

    # Texto do jogo
    font = pygame.font.SysFont('Times_New_Roman', 25, True, False)
    font1 = pygame.font.SysFont('Times_New_Roman', 25, True, False)
    text = font.render("Score: " + str(game.score), True, WHITE)
    text_game_over = font1.render("YOU DIED", True, (250, 20, 20))
    text_game_over1 = font1.render("Press ESC to try again", True, (139,134,130))

    screen.blit(text, [0, 0])

    # Apresenta se chegar ao estado de game over
    if game.state == "gameover":
        screen.blit(text_game_over, [125, 450])
        screen.blit(text_game_over1, [65, 500])

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()