import pygame
import os
from sys import exit
import argparse
from data.code_dop import constants
from pygame.math import Vector2
import sqlite3

parser = argparse.ArgumentParser()
parser.add_argument("map", type=str, nargs="?", default="map.map")
args = parser.parse_args()
map_file = args.map

con = sqlite3.connect("data/data_base/Game_on_Pygame.sqlite")
CUR = con.cursor()


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
    'bot_on_grass': load_image('sprites/bot_on_grass.png')
}
player_image = load_image('sprites/Jacob_pewpew.png').convert_alpha()
bot_image = load_image('sprites/HT.png')

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

    def move(self, x, y):
        camera.dx -= tile_width * (x - self.pos[0])
        camera.dy -= tile_height * (y - self.pos[1])
        self.pos = (x, y)
        for sprite in sprite_group:
            camera.apply(sprite)

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
            elif level[y][x] == 'Q':
                Tile('bot_on_grass', x, y)
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

    def __init__(self, x, y, width, height, buttonText='Button', onclickFunction=None, onclickFunction2=None,
                 onePress=False):
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


def pressButton2():
    global button_exit
    if pygame.mouse.get_pressed(num_buttons=5)[0]:
        button_exit = True


Button(275, 275, 190, 65, 'Start', pressButton)
Button(275, 400, 190, 65, 'Quit', pressButton2)


def switch_scene(scene):
    global current_scene
    current_scene = scene


lst = [0, 0]
flag1 = True
flag2 = True
flag3 = True


# Стрельба для уровней
def shoot(mouse_x, mouse_y, lst):
    global flag1, flag2, flag3, CUR
    pygame.draw.line(screen, (255, 0, 0), (408, 456), (mouse_x, mouse_y), 5)

    # изменение X мыши для хода в лево
    if lst[0] < 0:
        mouse_x = mouse_x + lst[0] * 48

    # изменение Y мыши для хода в верх
    if lst[1] > 0:
        mouse_y = mouse_y - lst[1] * 48

    # изменение X мыши для хода в право
    if lst[0] > 0:
        mouse_x = mouse_x + lst[0] * 48

    # изменение Y мыши для хода в низ
    if lst[1] < 0:
        mouse_y = mouse_y - lst[1] * 48

    if 624 <= mouse_x <= 672 and 48 <= mouse_y <= 96 and flag1:
        count = 0
        for i in sprite_group:
            if count == 34:
                i.kill()
                flag1 = False
                result = CUR.execute("""UPDATE score_for_levels SET kills = kills + 1""").fetchall()
                con.commit()
            count += 1

    if 144 <= mouse_x <= 192 and 627 <= mouse_y <= 720 and flag2:
        count = 0
        for i in sprite_group:
            if not flag1:
                if count == 296:
                    i.kill()
                    flag2 = False
                    result = CUR.execute("""UPDATE score_for_levels SET kills = kills + 1""").fetchall()
                    con.commit()
                count += 1
            else:
                if count == 297:
                    i.kill()
                    flag2 = False
                    result = CUR.execute("""UPDATE score_for_levels SET kills = kills + 1""").fetchall()
                    con.commit()
                count += 1

    if 768 <= mouse_x <= 816 and 816 <= mouse_y <= 864 and flag3:
        count = 0
        for i in sprite_group:
            if not flag2 and not flag1:
                if count == 371:
                    i.kill()
                    flag3 = False
                    result = CUR.execute("""UPDATE score_for_levels SET kills = kills + 1""").fetchall()
                    con.commit()
                count += 1
            elif not flag2 and flag1:
                if count == 372:
                    i.kill()
                    flag3 = False
                    result = CUR.execute("""UPDATE score_for_levels SET kills = kills + 1""").fetchall()
                    con.commit()
                count += 1
            elif flag2 and not flag1:
                if count == 372:
                    i.kill()
                    flag3 = False
                    result = CUR.execute("""UPDATE score_for_levels SET kills = kills + 1""").fetchall()
                    con.commit()
                count += 1
            else:
                if count == 373:
                    i.kill()
                    flag3 = False
                    result = CUR.execute("""UPDATE score_for_levels SET kills = kills + 1""").fetchall()
                    con.commit()
                count += 1


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


def score():
    num = CUR.execute("""SELECT kills FROM score_for_levels""").fetchall()
    intro_text = f"score: {num[0][0]}"

    fon = pygame.transform.scale(load_image('sprites/box.png'), (1, 1))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 10
    string_rendered = font.render(intro_text, 1, pygame.Color((0, 0, 255)))
    intro_rect = string_rendered.get_rect()
    text_coord += 10
    intro_rect.top = text_coord
    intro_rect.x = 10
    text_coord += intro_rect.height
    screen.blit(string_rendered, intro_rect)
    return num[0][0]


def game_end():
    result = CUR.execute("""UPDATE score_for_levels SET kills = 0""").fetchall()
    con.commit()
    return True


def level_scene1():
    global cursorPX, cursorPY, level_map, hero, max_x, max_y, camera, flPause2, music_on_lvl2, player_image, lst
    for i in sprite_group:
        i.kill()
    for i in bot_group:
        i.kill()
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
        if score() == 3:
            switch_scene(level_scene2)
            return
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.mixer.music.stop()
                switch_scene(None)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    old_pos = hero.pos
                    move(hero, "up")
                    if old_pos != hero.pos:
                        lst[1] += 1

                elif event.key == pygame.K_s:
                    old_pos = hero.pos
                    move(hero, "down")
                    if old_pos != hero.pos:
                        lst[1] -= 1

                elif event.key == pygame.K_a:
                    old_pos = hero.pos
                    move(hero, "left")
                    if old_pos != hero.pos:
                        lst[0] -= 1

                elif event.key == pygame.K_d:
                    old_pos = hero.pos
                    move(hero, "right")
                    if old_pos != hero.pos:
                        lst[0] += 1

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

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                shoot(mouse_x, mouse_y, lst)

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
        bot_group.draw(screen)
        clock.tick(FPS)
        pygame.display.flip()


def level_scene2():
    global cursorPX, cursorPY, level_map, hero, max_x, max_y, camera, flPause2, music_on_lvl2, player_image, lst
    for i in sprite_group:
        i.kill()
    for i in bot_group:
        i.kill()
    level_map = load_level("levels/the_map2.txt")
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
        if score() == 6:
            if game_end():
                for i in sprite_group:
                    i.kill()
                for i in bot_group:
                    i.kill()
                for i in hero_group:
                    i.kill()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.mixer.music.stop()
                switch_scene(None)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    old_pos = hero.pos
                    move(hero, "up")
                    if old_pos != hero.pos:
                        lst[1] += 1

                elif event.key == pygame.K_s:
                    old_pos = hero.pos
                    move(hero, "down")
                    if old_pos != hero.pos:
                        lst[1] -= 1

                elif event.key == pygame.K_a:
                    old_pos = hero.pos
                    move(hero, "left")
                    if old_pos != hero.pos:
                        lst[0] -= 1

                elif event.key == pygame.K_d:
                    old_pos = hero.pos
                    move(hero, "right")
                    if old_pos != hero.pos:
                        lst[0] += 1

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

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                shoot(mouse_x, mouse_y, lst)

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
        bot_group.draw(screen)
        clock.tick(FPS)
        pygame.display.flip()


switch_scene(scene1)
while current_scene is not None:
    current_scene()
pygame.quit()
