import pygame as pg
from pygame import sprite
from collections import namedtuple
from random import choice

SCREEN_SIZE = namedtuple('SCREEN_SIZE', ("WIDTH", "HEIGHT"))
SCREEN_SIZE = SCREEN_SIZE(900, 600)
FPS = 60

pause = False


class Rocket(sprite.Sprite):
    SPACE_BEFORE_ROCKET = 30
    X_CORDS = iter((("right", SPACE_BEFORE_ROCKET), ("left", SCREEN_SIZE.WIDTH - SPACE_BEFORE_ROCKET)))

    def __init__(self):
        super().__init__()
        self.image = pg.Surface((20, 60))
        self.image.fill("green")
        self.rect = self.image.get_rect()
        data = next(Rocket.X_CORDS)
        exec(f"self.rect.{data[0]} = {data[1]}")
        self.rect.y = SCREEN_SIZE.HEIGHT // 2
        self.speedy = 0


class PlayerRocket(Rocket):
    def __init__(self, up_key, down_key):
        super().__init__()
        self.down_key = down_key
        self.up_key = up_key
        self.abs_speed = 8

    def update(self):
        self.speedy = 0
        keystate = pg.key.get_pressed()
        if keystate[self.up_key]:
            self.speedy = -self.abs_speed
        elif keystate[self.down_key]:
            self.speedy = self.abs_speed
        self.rect.y += self.speedy
        if self.rect.bottom > SCREEN_SIZE.HEIGHT:
            self.rect.bottom = SCREEN_SIZE.HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0


class BotRocket(Rocket):
    def __init__(self, ball):
        super().__init__()
        self.ball = ball

    def update(self):
        self.rect.y = self.ball.rect.y
        if self.rect.bottom > SCREEN_SIZE.HEIGHT:
            self.rect.bottom = SCREEN_SIZE.HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0


class Ball(sprite.Sprite):
    def __init__(self, text):
        super().__init__()
        self.image = pg.transform.scale(pg.image.load("ball.png"), (50, 50))
        self.image.set_colorkey("white")

        self.rect = self.image.get_rect()
        self.rect.centerx = self.image.get_width() / 2
        self.rect.centery = self.image.get_height() / 2

        self.abs_speed = 8
        self.speedx = self.abs_speed * choice((1, -1))
        self.speedy = self.abs_speed * choice((1, -1))
        self.rect.x = SCREEN_SIZE.WIDTH // 2
        self.rect.y = SCREEN_SIZE.HEIGHT // 2

        self.text = text

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        if self.rect.top < 0 or self.rect.bottom > SCREEN_SIZE.HEIGHT:
            self.speedy *= -1

        if self.rect.left < 0:
            self.rand_spawn()
            self.text.update((0, 1))

        if self.rect.right > SCREEN_SIZE.WIDTH:
            self.rand_spawn()
            self.text.update((1, 0))

    def rand_spawn(self):
        pg.time.wait(100)
        self.rect.x = SCREEN_SIZE.WIDTH // 2
        self.rect.y = SCREEN_SIZE.HEIGHT // 2
        self.speedx = self.abs_speed * choice((1, -1))
        self.speedy = self.abs_speed * choice((1, -1))


class ScoreBar:
    def __init__(self):
        self.font = pg.font.SysFont("Arial", 36)
        self.left = 0
        self.right = 0
        self.text = "0 - 0"
        self.render()

    def update(self, add):
        global pause
        self.left += add[0]
        self.right += add[1]
        if 10 in (self.left, self.right):
            pause = True
        self.render()

    def render(self):
        if pause:
            self.text = self.font.render('Игра окончена', True, (255, 255, 255))
        else:
            self.text = self.font.render(f"{self.left} - {self.right}", True, (255, 255, 255))
        self.rect = self.text.get_rect()
        self.rect.centerx = SCREEN_SIZE.WIDTH // 2

    def blit(self):
        screen.blit(self.text, self.rect)


def make_rockets(bots=0):
    player = 2 - bots
    keys = iter(((pg.K_w, pg.K_s), (pg.K_UP, pg.K_DOWN)))
    return [PlayerRocket(*next(keys)) for _ in range(player)] + [BotRocket(ball) for _ in range(bots)]


pg.init()
screen = pg.display.set_mode(SCREEN_SIZE)

all_sprites = sprite.Group()
rockets_sprites = sprite.Group()

score = ScoreBar()
ball = Ball(score)

rockets = make_rockets(bots=0)

all_sprites.add(ball, *rockets)
rockets_sprites.add(*rockets)

running = True
while running:

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False

    if pause:
        running = False
        pg.time.wait(500)

    if pg.sprite.spritecollide(ball, rockets_sprites, dokill=False):
        ball.speedx *= -1

    if not pause:
        all_sprites.update()
        pg.time.Clock().tick(FPS)
        screen.fill("black")
        all_sprites.draw(screen)
        score.blit()
        pg.display.update()
        pg.display.flip()
