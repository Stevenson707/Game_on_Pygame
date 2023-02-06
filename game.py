import pygame
import os
from sys import exit
import argparse
from data.code_dop import constants
from pygame.math import Vector2
from pygame import K_a, K_s, K_d, K_w

parser = argparse.ArgumentParser()
parser.add_argument("map", type=str, nargs="?", default="map.map")
args = parser.parse_args()
map_file = args.map


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


pygame.init()
screen_size = (750, 750)
screen = pygame.display.set_mode(screen_size)
FPS = 50

tile_images = {
    'wall': load_image('sprites/bs1.jpg'),
    'empty': load_image('sprites/cover'),
    'road': load_image('sprites/box.png'),
    # 'bot': load_image('sprites/HT.png')
}
player_image = load_image('sprites/Jacob_pewpew.png').convert_alpha()
bot_image = load_image('sprites/HT.png')
# bullet_image = load_image("sprites/bullet.png")

tile_width = tile_height = 48


class ScreenFrame(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.rect = (0, 0, 500, 500)


class SpriteGroup(pygame.sprite.Group):

    def __init__(self):
        super().__init__()

    def get_event(self, event):
        for sprite in self:
            sprite.get_event(event)


class Sprite(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.rect = None

    def get_event(self, event):
        pass


class Tile(Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(sprite_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.abs_pos = (self.rect.x, self.rect.y)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 20))
        self.image.fill(pygame.Color("yellow"))
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        # убить, если он заходит за верхнюю часть экрана
        if self.rect.bottom < 0:
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(hero_group)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 10, tile_height * pos_y + 15)
        self.pos = (pos_x, pos_y)
        self.orig = self.image
       # self.og_surf = pygame.transform.smoothscale(pygame.image.load("data/sprites/bullet.png").convert(), (100, 100))
        #self.surf = self.og_surf
        #self.rect = self.surf.get_rect(center=(400, 400))
        #self.pos = (pos_x, pos_y)

    def move(self, x, y):
        camera.dx -= tile_width * (x - self.pos[0])
        camera.dy -= tile_height * (y - self.pos[1])
        self.pos = (x, y)
        for sprite in sprite_group:
            camera.apply(sprite)

    # def update(self, keys):
        #if keys[K_a]:
        #    self.rect.x -= self.speed
        #if keys[K_d]:
         #   self.rect.x += self.speed
        #if keys[K_s]:
          #  self.rect.y += self.speed
        #if keys[K_w]:
         #   self.rect.y -= self.speed

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        constants.all_sprites.add(bullet)
        constants.bullets.add(bullet)

    def rotate(self):
        x, y, w, h = self.rect
        direction = pygame.mouse.get_pos() - Vector2(x + w // 2, y + h // 2)
        radius, angle = direction.as_polar()
        self.image = pygame.transform.rotate(self.orig, -angle - 360)
        self.rect = self.image.get_rect(center=self.rect.center)


class Bot(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(bot_group)
        self.image = bot_image
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.pos = (pos_x, pos_y)



def drawCursor(x, y):
    pygame.draw.circle(screen, (255, 255, 255), (x, y), 20, 1)
    pygame.draw.circle(screen, (255, 255, 255), (x, y), 1)
    pygame.draw.line(screen, (255, 255, 255), (x - 24, y), (x - 16, y))
    pygame.draw.line(screen, (255, 255, 255), (x + 24, y), (x + 16, y))
    pygame.draw.line(screen, (255, 255, 255), (x, y - 24), (x, y - 16))
    pygame.draw.line(screen, (255, 255, 255), (x, y + 24), (x, y + 16))



cursorPX, cursorPY = 500 // 3, 500 // 2 - 200
pygame.mouse.set_visible(True)
player = None
clock = pygame.time.Clock()
sprite_group = SpriteGroup()
hero_group = SpriteGroup()
bot_group = SpriteGroup()


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x = obj.abs_pos[0] + self.dx
        obj.rect.y = obj.abs_pos[1] + self.dy

    def update(self, target):
        self.dx = 0
        self.dy = 0


def terminate():
    pygame.quit()
    exit


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
                level[y][x] = "."
            elif level[y][x] == '+':
                Tile('road', x, y)
            elif level[y][x] == 'B':
                Tile('empty', x, y)
                Bot(x, y)
                level[y][x] = "."
    return new_player, x, y,


def move(hero, movement):
    x, y = hero.pos

    if movement == "up":
        if y > 0 and level_map[y - 1][x] == ".":
            hero.move(x, y - 1)
    elif movement == "down":
        if y < max_y - 1 and level_map[y + 1][x] == ".":
            hero.move(x, y + 1)
    elif movement == "left":
        if x > 0 and level_map[y][x - 1] == ".":
            hero.move(x - 1, y)
    elif movement == "right":
        if x < max_x - 1 and level_map[y][x + 1] == ".":
            hero.move(x + 1, y)


flPause = False
flPause2 = False

music_on = True
music_on_lvl2 = True

camera = Camera()

current_scene = None
FONT = 'data/sprites/font2.ttf'
BUTTON_FONT_SIZE = 30
objects = []
font = pygame.font.Font(FONT, BUTTON_FONT_SIZE)

button_start = False
button_exit = False

fps = 60
fpsClock = pygame.time.Clock()
player_coords = Player(8, 9)


class Button():
    global button_start, button_exit

    def __init__(self, x, y, width, height, buttonText='Button', onclickFunction=None, onclickFunction2=None, onePress=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.onclickFunction = onclickFunction
        self.onePress = onePress
        self.alreadyPressed = False
        self.onclickFunction2 = onclickFunction2

        self.fillColors = {
            'normal': '#f70a98c0',
            'hover': '#73184ec0',
            'pressed': '#333333',
        }

        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.buttonSurf = font.render(buttonText, True, (47, 10, 194, 0.66))

        objects.append(self)

    def process(self):
        global button_start, button_exit
        mousePos = pygame.mouse.get_pos()
        self.buttonSurface.fill(self.fillColors['normal'])
        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill(self.fillColors['hover'])
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])
                if self.onePress:
                    self.onclickFunction()
                elif not self.alreadyPressed:
                    self.onclickFunction()
                    self.alreadyPressed = True
            if pygame.mouse.get_pressed(num_buttons=5)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])
                if self.onePress:
                    self.onclickFunction2()
                elif not self.alreadyPressed:
                    self.onclickFunction2()
                    self.alreadyPressed = True
            else:
                self.alreadyPressed = False

        self.buttonSurface.blit(self.buttonSurf, [
            self.buttonRect.width / 2 - self.buttonSurf.get_rect().width / 2,
            self.buttonRect.height / 2 - self.buttonSurf.get_rect().height / 2
        ])
        screen.blit(self.buttonSurface, self.buttonRect)


def pressButton():
    global button_start, button_exit
    if pygame.mouse.get_pressed(num_buttons=3)[0]:
        button_start = True
    print(button_start)


def pressButton2():
    global button_exit
    if pygame.mouse.get_pressed(num_buttons=5)[0]:
        button_exit = True
    print(button_exit)


Button(275, 275, 190, 65, 'Start', pressButton)
Button(275, 400, 190, 65, 'Quit', pressButton2)


def switch_scene(scene):
    global current_scene
    current_scene = scene


def scene1():
    global flPause, music_on, button_start, button_exit
    intro_text = ["                                        ",
                  "                                        ",
                  "                             Name first game on pygame               ",
                  "                                        ",
                  "                                    ",
                  "                                        ",
                  "                                     ",
                  "                                        ",
                  "                                       ",
                  "                                        ",
                  "                                                       v1.0",
                  "                                        ",
                  "                                        ",
                  "                                        ",
                  "                                                                Game developers:",
                  "                                                           S1notik and Stevenson", ]
    fon = pygame.transform.scale(load_image('sprites/background'), screen_size)
    screen.blit(fon, (0, 0))
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color(47, 10, 194))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    running = True
    pygame.mixer.music.load("data/music/HM2-Dust.mp3")
    vol = 1.0
    pygame.mixer.music.play(-1)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.mixer.music.stop()
                switch_scene(None)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    switch_scene(level_scene1)
                    running = False
                    pygame.mixer.music.stop()
                elif event.key == pygame.K_ESCAPE:
                    running = False
                    pygame.mixer.music.stop()
                    switch_scene(None)
                elif event.key == pygame.K_SPACE:
                    flPause = not flPause
                    if flPause:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                elif event.key == pygame.K_DOWN:
                    vol -= 0.1
                    pygame.mixer.music.set_volume(vol)
                elif event.key == pygame.K_UP:
                    vol += 0.1
                    pygame.mixer.music.set_volume(vol)
                elif event.key == pygame.K_F10:
                    music_on = False
                    pygame.mixer.music.stop()
                elif event.key == pygame.K_F9 and not music_on:
                    music_on = True
                    pygame.mixer.music.play(-1)
        try:
            if button_start:
                button_exit = False
                switch_scene(level_scene1)
                running = False
                pygame.mixer.music.stop()
            elif button_exit:
                exit(1)
                running = False
                pygame.mixer.music.stop()
                switch_scene(None)
        except:
            button_start = False
            exit(1)
        for object in objects:
            pygame.display.flip()
            object.process()
        pygame.display.flip()
        fpsClock.tick(fps)


def level_scene1():
    global cursorPX, cursorPY, level_map, hero, max_x, max_y, camera, flPause2, music_on_lvl2, player_image
    level_map = load_level("levels/the_map1.txt")
    hero, max_x, max_y = generate_level(level_map)
    camera.update(hero)
    pygame.mixer.music.load("data/music/Kaito Shoma - Hotline.mp3")
    vol = 1.0
    pygame.mixer.music.play(-1)
    running = True
    presses = pygame.key.get_pressed()
    pygame.mouse.set_visible(False)

    # Удаление неподвижного спрайта персонажа
    count = 0
    for i in hero_group:
        if count > 0:
            i.kill()
            count += 1
        count += 1

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.mixer.music.stop()
                switch_scene(None)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    move(hero, "up")
                elif event.key == pygame.K_s:
                    move(hero, "down")
                elif event.key == pygame.K_a:
                    move(hero, "left")
                elif event.key == pygame.K_d:
                    move(hero, "right")
                elif event.key == pygame.K_DOWN:
                    vol -= 0.1
                    pygame.mixer.music.set_volume(vol)
                elif event.key == pygame.K_UP:
                    vol += 0.1
                    pygame.mixer.music.set_volume(vol)
                elif event.key == pygame.K_F10:
                    music_on_lvl2 = False
                    pygame.mixer.music.stop()
                elif event.key == pygame.K_F9 and not music_on_lvl2:
                    music_on_lvl2 = True
                    pygame.mixer.music.play(-1)

        for x in constants.all_sprites:
            x.move(presses)
            screen.blit(x.surf, x.rect)
        constants.all_sprites.update()

        player_coords.rotate()

        constants.all_sprites.draw(screen)
        cursorPX, cursorPY = pygame.mouse.get_pos()
        drawCursor(cursorPX, cursorPY)
        pygame.display.update()

        screen.fill(pygame.Color(153, 19, 186))
        constants.all_sprites.update()
        sprite_group.draw(screen)
        hero_group.draw(screen)
        # bot_group.draw(screen)
        clock.tick(FPS)
        pygame.display.flip()


def level_scene2():
    global cursorPX, cursorPY, level_map2, hero, max_x, max_y, camera, flPause2
    camera.update(hero)
    pass


def level_scene3():
    global cursorPX, cursorPY, level_map3, hero, max_x, max_y, camera, flPause2
    camera.update(hero)
    pass


switch_scene(scene1)
while current_scene is not None:
    current_scene()
pygame.quit()