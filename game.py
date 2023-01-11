import pygame
import os
from sys import exit
import argparse
import math


parser = argparse.ArgumentParser()
parser.add_argument("map", type=str, nargs="?", default="map.map")
args = parser.parse_args()
map_file = args.map
all_sprites = pygame.sprite.Group()
Moveble_items = pygame.sprite.Group()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


pygame.init()
screen_size = (550, 550)
screen = pygame.display.set_mode(screen_size)
FPS = 50

tile_images = {
    'wall': load_image('bs1.jpg'),
    'empty': load_image('grass_2.png'),
    'road': load_image('box.png')
}
player_image = load_image('Jacob_up.png')

tile_width = tile_height = 50


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


class MoveObject(pygame.sprite.Sprite):
    def __init__(self, sheet, x=0, y=0):
        super().__init__(all_sprites)
        self.image = sheet
        self.original_image = self.image
        Moveble_items.add(self)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

    def rotate(self, x, y):
        rel_x, rel_y = x - self.rect.x, y - self.rect.y
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        self.image = pygame.transform.rotate(self.original_image, int(angle))
        self.rect = self.image.get_rect(center=(self.rect.centerx, self.rect.centery))


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(hero_group)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.pos = (pos_x, pos_y)

    def move(self, x, y):
        camera.dx -= tile_width * (x - self.pos[0])
        camera.dy -= tile_height * (y - self.pos[1])
        self.pos = (x, y)
        for sprite in sprite_group:
            camera.apply(sprite)


# def drawCursor(x, y):
   #  pygame.draw.circle(screen, (255, 255, 255), (x, y), 20, 1)
    # pygame.draw.circle(screen, (255, 255, 255), (x, y), 1)
    # pygame.draw.line(screen, (255, 255, 255), (x - 24, y), (x - 16, y))
   #  pygame.draw.line(screen, (255, 255, 255), (x + 24, y), (x + 16, y))
   #  pygame.draw.line(screen, (255, 255, 255), (x, y - 24), (x, y - 16))
   #  pygame.draw.line(screen, (255, 255, 255), (x, y + 24), (x, y + 16))

class Cursor(pygame.sprite.Sprite):  # Курсор
    image = load_image("crosshair.png")
    cursor = pygame.transform.scale(image, (15, 15))
    all_sprites.add()

    def init(self, *group):
        super().__init__(*group)
        self.image = Cursor.cursor
        self.rect = self.image.get_rect()

    def update(self, *args):
        self.rect.x = args[0][0] - self.rect.width // 2
        self.rect.y = args[0][1] - self.rect.height // 2


cursorPX, cursorPY = 500 // 3, 500 // 2 - 200
pygame.mouse.set_visible(False)
player = None
clock = pygame.time.Clock()
sprite_group = SpriteGroup()
hero_group = SpriteGroup()


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
    return new_player, x, y


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
cursor = Cursor()
level_map = load_level("the_map1.txt")
hero, max_x, max_y = generate_level(level_map)
current_scene = None
FONT = 'font2.ttf'
BUTTON_FONT_SIZE = 24
LOGO_FONT_SIZE = 250


def switch_scene(scene):
    global current_scene
    current_scene = scene


def scene1():
    global flPause, music_on
    intro_text = ["                                        ",

                  "                    Name first game on pygame               ",
                  "                                        ",
                  "                                        ",
                  "                            Start{Press Enter}",
                  "                                        ",
                  "                             Exit[Press Esc]",
                  "                                        ",
                  "                                         v1.0",
                  "                                        ",
                  "                                        ",
                  "                                        ",
                  "                                                 Game developers:",
                  "                                             S1notik and Stevenson",]
    fon = pygame.transform.scale(load_image('fon2.jpg'), screen_size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(FONT, BUTTON_FONT_SIZE)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color(72, 83, 84))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    running = True
    pygame.mixer.music.load("HM2-Dust.mp3")
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
        pygame.display.flip()


def level_scene1():
    global cursorPX, cursorPY, level_map, hero, max_x, max_y, camera, flPause2, music_on_lvl2, cursor
    camera.update(hero)
    pygame.mixer.music.load("Kaito Shoma - Hotline.mp3")
    vol = 1.0
    pygame.mixer.music.play(-1)
    running = True
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
        screen.fill(pygame.Color(153, 19, 186))
        sprite_group.draw(screen)
        cursorPX, cursorPY = pygame.mouse.get_pos()
        hero_group.draw(screen)
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
