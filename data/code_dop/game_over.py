import os
import sys
import pygame


def load_image(name, colorkey=None):
    fullname = os.path.join('', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Car(pygame.sprite.Sprite):
    image_right = None
    image_left = None

    def __init__(self, group, size):
        # НЕОБХОДИМО вызвать конструктор родительского класса Sprite
        super().__init__(group)
        if Car.image_right is None:
            Car.image_right = load_image("../sprites/gameover.png")
            Car.image_left = pygame.transform.flip(Car.image_right, True, False)
        self.width, self.height = size
        self.image = Car.image_right
        self.rect = self.image.get_rect()
        self.vx = 1
        # считаем количество тиков для замедления
        self.ticks = 10
        self.rect.left = -600

    def update(self):
        if self.rect.left <= -1:
            self.rect.left += 5
        else:
            return False


def main():
    size = 600, 300
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Машинка')
    clock = pygame.time.Clock()
    # группа, содержащая все спрайты
    all_sprites = pygame.sprite.Group()

    _ = Car(all_sprites, size)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill(pygame.Color("blue"))
        all_sprites.draw(screen)
        if running:
            all_sprites.update()
        else:
            running = False
        pygame.display.flip()
        clock.tick(30)
    pygame.quit()


if __name__ == '__main__':
    main()
