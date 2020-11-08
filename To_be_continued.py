from random import randrange as rnd, choice
import pygame
from pygame.draw import *
import math
import time

pygame.init()

screen_size_x = 800
screen_size_y = 600
FPS = 50

# Colors
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
MAGENTA = (255, 0, 255)
CYAN = (0, 255, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIL = (190, 0, 255)
DARK_GREEN = (0, 128, 0)
GREY = (128, 128, 128)

# The main screen
screen = pygame.display.set_mode((screen_size_x, screen_size_y))
screen.fill(WHITE)

# Font and text size
font = pygame.font.Font('freesansbold.ttf', 32)


class Targets:
    def __init__(self, color):
        self.target_x = 10
        self.target_y = 10
        self.target_r = 10
        self.target_speed_x = 10
        self.target_speed_y = 10
        self.color = color
        self.id = circle(screen, self.color, (self.target_x, self.target_y), self.target_r)
        self.hitted = False

    def new_target(self):
        """
        Initializing a new target
        """
        self.target_x = rnd(600, 780)
        self.target_y = rnd(300, 550)
        self.target_r = rnd(10, 35)
        self.target_speed_x = rnd(-5, 5)
        self.target_speed_y = rnd(-5, 5)
        self.id = circle(screen, self.color, (self.target_x, self.target_y), self.target_r)

    def hit(self):
        """
        The ball hits the target
        """
        self.hitted = True


class Balls:
    def __init__(self, angle, power, start_x, start_y, color, parent):
        """ Constructor of the ball class

        Args:
        baal_x - Starting position of the ball horizontally
        ball_y - Starting position of the ball vertically
        angle - Angle of rotation of the gun
        power - The force of the flight of the ball
        """
        self.parent = parent
        self.ball_x = start_x
        self.ball_y = start_y
        self.color = color

        # Radius of the ball
        self.ball_r = 13

        # Speed of the ball
        self.speed_x = 0.8 * power * math.cos(angle)
        self.speed_y = - 0.8 * power * math.sin(angle)

        self.id = circle(screen, self.color,
                         (self.ball_x, self.ball_y,), self.ball_r)
        self.live = 200

    def move(self):
        """
        Moving the ball
        """
        self.ball_x += self.speed_x
        self.ball_y -= self.speed_y

        # Taking into account the reflection from the walls and slowing down the ball
        if self.ball_x <= self.ball_r:
            self.ball_x = self.ball_r
            self.speed_x = - self.speed_x * 0.8
        if self.ball_y <= 0:
            self.ball_y = 0
            self.speed_y = - self.speed_y
            self.speed_x = self.speed_x * 0.8
        if self.ball_x >= screen_size_x - self.ball_r:
            self.ball_x = screen_size_x - self.ball_r
            self.speed_x = - self.speed_x * 0.8
        if self.ball_y >= screen_size_y - self.ball_r:
            self.ball_y = screen_size_y - self.ball_r
            self.speed_y = - self.speed_y * 0.9
            self.speed_x = self.speed_x * 0.9

        self.live -= 1
        if self.live <= 0:
            self.parent.delete_ball(self.color)
        self.id = circle(screen,
                         self.color,
                         (round(self.ball_x), round(self.ball_y)), self.ball_r)

    def check(self, target_x, target_y, target_r):
        """
        Checking whether the ball hit the target
        """
        distance = math.sqrt((self.ball_x - target_x) * (self.ball_x - target_x) + \
                             (self.ball_y - target_y) * (self.ball_y - target_y))
        if distance <= self.ball_r + target_r:
            return True
        return False


class Common_ball(Balls):
    def __init__(self, angle, power, start_x, start_y, parent):
        """
        Constructor of the Common_ball class
        """
        super().__init__(angle, power, start_x, start_y, BLUE, parent)


class Bomb_ball(Balls):
    def __init__(self, angle, power, start_x, start_y, parent):
        """
        Constructor of the Bomb_ball class
        """
        super().__init__(angle, power, start_x, start_y, MAGENTA, parent)
        self.ball_r = 10
        self.speed_x *= 0.5
        self.speed_y *= 0.5


class Mini_ball(Balls):
    def __init__(self, angle, power, start_x, start_y, parent):
        """
        Constructor of the Mini_ball class
        """
        super().__init__(angle, power, start_x, start_y, GREEN, parent)
        self.ball_r = 5
        self.live = 50


class Gun:
    def __init__(self, parent, gun_power=10, gun_on=0, gun_angle=0, gun_x=100, gun_y=450):
        """ Constructor of the gun class
        Args:
        gun_power - Power of the gun
        gun_on - Is the gun turned on
        gun_angel - Angle of rotation of the gun
        """
        self.parent = parent
        self.gun_power = gun_power
        self.gun_on = gun_on
        self.gun_angle = gun_angle
        self.color = GREY
        self.gun_x = gun_x
        self.gun_y = gun_y
        self.gun_move = False
        self.direction = 'stop'

    def fire_start(self):
        """
        Turning on the gun
        """
        self.gun_on = 1

    def fire_end(self, button):
        """
        Turning off the gun
        """
        self.gun_on = 0
        self.parent.shoot(self.gun_angle, self.gun_power, self.gun_x, self.gun_y, button)
        self.gun_power = 10

    def targetting(self, event):
        """
        Aiming. Depends on the mouse position
        """
        mouse_x, mouse_y = event.pos
        if mouse_x != self.gun_x:
            if mouse_x > self.gun_x:
                self.gun_angle = math.atan((mouse_y - self.gun_y) / (mouse_x - self.gun_x))
            else:
                self.gun_angle = math.pi + math.atan((mouse_y - self.gun_y) / (mouse_x - self.gun_x))

    def draw(self):
        """
        Drawing a gun
        """
        if self.gun_on:
            self.color = RED
        else:
            self.color = GREY
        if self.direction == 'left':
            rect(screen, BLACK, (self.gun_x - 13, self.gun_y - 15, 40, 30))
            rect(screen, GREY, (self.gun_x - 16, self.gun_y - 20, 46, 5))
            rect(screen, GREY, (self.gun_x - 16, self.gun_y + 15, 46, 5))
        elif self.direction == 'up':
            rect(screen, BLACK, (self.gun_x - 15, self.gun_y - 13, 30, 40))
            rect(screen, GREY, (self.gun_x - 20, self.gun_y - 16, 5, 46))
            rect(screen, GREY, (self.gun_x + 15, self.gun_y - 16, 5, 46))
        elif self.direction == 'down':
            rect(screen, BLACK, (self.gun_x - 15, self.gun_y - 27, 30, 40))
            rect(screen, GREY, (self.gun_x - 20, self.gun_y - 30, 5, 46))
            rect(screen, GREY, (self.gun_x + 15, self.gun_y - 30, 5, 46))
        else:
            rect(screen, BLACK, (self.gun_x - 27, self.gun_y - 15, 40, 30))
            rect(screen, GREY, (self.gun_x - 30, self.gun_y - 20, 46, 5))
            rect(screen, GREY, (self.gun_x - 30, self.gun_y + 15, 46, 5))
        circle(screen, DARK_GREEN, (self.gun_x, self.gun_y), 10)
        line(screen, self.color, [self.gun_x, self.gun_y],
             [self.gun_x + max(self.gun_power, 20) * math.cos(self.gun_angle),
              self.gun_y + max(self.gun_power, 20) * math.sin(self.gun_angle)], 7)

    def move_start(self, direction):
        """
        The gun starts moving
        :param direction: Direction of movement
        """
        self.direction = direction
        self.gun_move = True

    def move_end(self):
        """
        The cannon finishes moving
        """
        self.direction = 'stop'
        self.gun_move = False

    def move(self):
        '''
        The function sets the new coordinates of the tank
        '''
        if self.gun_move == True:
            if (self.direction == 'right') and (self.gun_x <= screen_size_x - 20):
                self.gun_x += 5
            if (self.direction == 'left') and (self.gun_x >= 35):
                self.gun_x -= 5
            if (self.direction == 'up') and (self.gun_y >= 25):
                self.gun_y -= 5
            if (self.direction == 'down') and (self.gun_y <= screen_size_y - 25):
                self.gun_y += 5

    def power_up(self):
        """
        Gun reinforcement
        """
        if self.gun_on:
            if self.gun_power < 100:
                self.gun_power += 1
            self.color = RED
        else:
            self.color = GREY


class Target_1(Targets):
    def __init__(self, parent):
        """
        Constructor of the target class
        """
        super().__init__(RED)
        self.parent = parent
        self.target_surf = pygame.image.load('angry.png')

    def move_target(self):
        """
        Moving a target
        """
        if not self.hitted:
            self.target_x += self.target_speed_x
            self.target_y -= self.target_speed_y

            # Taking into account the reflection from the walls and slowing down the ball
            if self.target_x <= self.target_r:
                self.target_x = self.target_r
                self.target_speed_x = - self.target_speed_x
            if self.target_y <= self.target_r:
                self.target_y = self.target_r
                self.target_speed_y = - self.target_speed_y
            if self.target_x >= screen_size_x - self.target_r:
                self.target_x = screen_size_x - self.target_r
                self.target_speed_x = - self.target_speed_x
            if self.target_y >= screen_size_y - self.target_r:
                self.target_y = screen_size_y - self.target_r
                self.target_speed_y = - self.target_speed_y
            self.scale = pygame.transform.scale(self.target_surf, (2 * self.target_r, 2 * self.target_r))
            screen.blit(self.scale, (self.target_x - self.target_r, self.target_y - self.target_r))


class Target_2(Targets):
    def __init__(self, parent):
        """
        Constructor of the target class
        """
        super().__init__(LIL)
        self.parent = parent
        self.target_r //= 3
        self.show_time = 60
        self.hide_time = 50
        self.invisible = False
        self.target_surf = pygame.image.load('bomb.png')

    def move_target(self):
        """
        Moving a target
        """
        if not self.hitted:
            if self.show_time > 0:
                if self.show_time % 3 == 0:
                    self.target_r += 1
                self.show_time -= 1
                self.scale = pygame.transform.scale(self.target_surf, (2 * self.target_r, 2 * self.target_r))
                screen.blit(self.scale, (self.target_x - self.target_r, self.target_y - self.target_r))
            else:
                self.invisible = True
                if self.hide_time > 0:
                    self.hide_time -= 1
                    self.target_x += self.target_speed_x * 5
                    self.target_y -= self.target_speed_y * 5

                    # Taking into account the reflection from the walls and slowing down the ball
                    if self.target_x <= self.target_r:
                        self.target_x = self.target_r
                        self.target_speed_x = - self.target_speed_x
                    if self.target_y <= self.target_r:
                        self.target_y = self.target_r
                        self.target_speed_y = - self.target_speed_y
                    if self.target_x >= screen_size_x - self.target_r:
                        self.target_x = screen_size_x - self.target_r
                        self.target_speed_x = - self.target_speed_x
                    if self.target_y >= screen_size_y - self.target_r:
                        self.target_y = screen_size_y - self.target_r
                        self.target_speed_y = - self.target_speed_y
                else:
                    self.invisible = False
                    self.show_time = 60
                    self.target_r -= 20
                    self.hide_time = 50


class Bomb:
    def __init__(self, target_x, target_y, gun_x, gun_y, parent):
        self.parent = parent
        self.angle = 0
        self.bomb_x = target_x
        self.bomb_y = target_y
        self.bomb_r = 15
        if gun_x != target_x:
            if gun_x > target_x:
                self.angle = math.atan((gun_y - target_y) / (gun_x - target_x))
            else:
                self.angle = math.pi + math.atan((gun_y - target_y) / (gun_x - target_x))
        self.speed_x = 5 * math.cos(self.angle)
        self.speed_y = - 5 * math.sin(self.angle)
        self.live = 100
        self.bomb_surf = pygame.image.load('star.png')
        self.scale = pygame.transform.scale(self.bomb_surf, (30, 30))

    def move(self):
        """
        Moving the bomb
        """
        self.bomb_x += self.speed_x
        self.bomb_y -= self.speed_y

        # Taking into account the reflection from the walls and slowing down the bomb
        if self.bomb_x <= self.bomb_r:
            self.bomb_x = self.bomb_r
            self.speed_x = - self.speed_x * 0.8
        if self.bomb_y <= 0:
            self.bomb_y = 0
            self.bomb_y = - self.speed_y
            self.speed_x = self.speed_x * 0.8
        if self.bomb_x >= screen_size_x - self.bomb_r:
            self.bomb_x = screen_size_x - self.bomb_r
            self.speed_x = - self.speed_x * 0.8
        if self.bomb_y >= screen_size_y - self.bomb_r:
            self.bomb_y = screen_size_y - self.bomb_r
            self.speed_y = - self.speed_y * 0.9
            self.speed_x = self.speed_x * 0.9

        self.live -= 1
        if self.live <= 0:
            self.parent.delete_bomb()

        screen.blit(self.scale, (self.bomb_x - 15, self.bomb_y - 15))

    def check(self, gun_x, gun_y):
        """
        Checking whether the bomb hit the gun
        """
        if ((self.bomb_x - 15) <= (gun_x + 15)) and ((self.bomb_x + 15) >= (gun_x - 15)) and \
                ((self.bomb_y - 15) <= (gun_y + 15)) and ((self.bomb_y + 15) >= (gun_y - 15)):
            return True
        else:
            return False


class Hp:
    def __init__(self, place, parent):
        self.parent = parent
        self.place = place * 50
        self.hp_surf = pygame.image.load('heart.png')
        self.scale = pygame.transform.scale(self.hp_surf, (50, 50))

    def draw(self):
        screen.blit(self.scale, (650 + self.place, 0))


class Solyanka:
    def __init__(self):
        self.gun = Gun(self)
        self.balls = []
        self.targets_1 = []
        self.targets_2 = []
        self.bombs = []
        self.hp = []
        self.attack_time = 200
        for i in range(3):
            self.targets_1.append(Target_1(self))
            self.targets_1[i].new_target()
        for i in range(3):
            self.targets_2.append(Target_2(self))
            self.targets_2[i].new_target()
        for i in range(3):
            self.hp.append(Hp(i, self))
        self.points = 0
        self.hit_points = 3
        self.count_of_shoots = 0
        self.congrats_time = 100
        self.text = font.render(str(self.points), True, BLACK)
        self.screen_id_points = screen.blit(self.text, self.text.get_rect())

    def draw(self):
        """
        Draw everything
        """
        self.gun.draw()
        for ball in self.balls:
            ball.move()
        for target in self.targets_1:
            target.move_target()
        for target in self.targets_2:
            target.move_target()
        for bomb in self.bombs:
            bomb.move()
        for heart in self.hp:
            heart.draw()
        self.text = font.render(str(self.points), True, BLACK)
        self.screen_id_points = screen.blit(self.text, self.text.get_rect())

    def shoot(self, angle, power, start_x, start_y, button):
        """
        Shot out of a gun and the creation of bullets
        baal_x - Starting position of the ball horizontally
        ball_y - Starting position of the ball vertically
        angle - Angle of rotation of the gun
        power - The force of the flight of the ball
        button - The type of the bullet
        """
        if button == 1:
            self.balls.append(Common_ball(angle, power, start_x, start_y, self))
        if button == 3:
            self.balls.append(Bomb_ball(angle, power, start_x, start_y, self))
        self.count_of_shoots += 1

    def attack(self):
        """
        Targets attack the gun
        """
        self.attack_time -= 1
        if self.attack_time <= 0:
            for target in self.targets_1:
                if not target.hitted:
                    self.bombs.append(Bomb(target.target_x, target.target_y, self.gun.gun_x, self.gun.gun_y, self))
            self.attack_time = 200

    def attack_check(self):
        f = False
        for bomb in self.bombs:
            if bomb.check(self.gun.gun_x, self.gun.gun_y):
                self.hit_points -= 1
                self.bombs.remove(bomb)
                if self.hit_points >= 0:
                    del self.hp[0]
        if self.hit_points <= 0:
            f = True
        return f


    def delete_ball(self, color):
        """
        Removed a dead ball at the end of its life time
        """
        for i in range(len(self.balls)):
            if self.balls[i].color == color:
                del self.balls[i]
                break

    def delete_bomb(self):
        """
        Removed a dead bomb at the end of its life time
        """
        del self.bombs[0]

    def hitting_actions(self, target, points):
        for ball in self.balls:
            if ball.check(target.target_x, target.target_y, target.target_r):
                if isinstance(ball, Bomb_ball):
                    for i in range(6):
                        self.balls.append(Mini_ball(i, 2, int(ball.ball_x), int(ball.ball_y), self))
                self.balls.remove(ball)
                target.hit()
                self.points += points

    def hitting(self):
        for target in self.targets_1:
            if not target.hitted:
                self.hitting_actions(target, 1)
        for target in self.targets_2:
            if not target.hitted and not target.invisible:
                self.hitting_actions(target, 5)

    def all_hitted(self):
        """
        If all targets are hit, complete the round
        """
        if self.targets_1[0].hitted and self.targets_1[1].hitted and self.targets_1[2].hitted and \
                self.targets_2[0].hitted and self.targets_2[1].hitted and self.targets_2[2].hitted:
            self.congrats_time -= 1
            if self.congrats_time < 0:
                for target in self.targets_1:
                    target.new_target()
                    target.hitted = False
                for target in self.targets_2:
                    target.new_target()
                    target.show_time = 60
                    target.hide_time = 50
                    target.hitted = False
                self.congrats_time = 100
                self.count_of_shoots = 0
            else:
                text = font.render('You hit the targets in ' + str(self.count_of_shoots) + ' turns', True, BLACK)
                screen.blit(text, (screen_size_x // 4, screen_size_y // 2))


def keydown_actions():
    """
    The movement of the gun
    """
    if event.key == pygame.K_d:
        solyanka.gun.move_start('right')
    if event.key == pygame.K_a:
        solyanka.gun.move_start('left')
    if event.key == pygame.K_w:
        solyanka.gun.move_start('up')
    if event.key == pygame.K_s:
        solyanka.gun.move_start('down')


def keyup_actions():
    """
    The end of the movement of the gun
    """
    if (event.key == pygame.K_d) and (solyanka.gun.direction == 'right'):
        solyanka.gun.move_end()
    if (event.key == pygame.K_a) and (solyanka.gun.direction == 'left'):
        solyanka.gun.move_end()
    if (event.key == pygame.K_w) and (solyanka.gun.direction == 'up'):
        solyanka.gun.move_end()
    if (event.key == pygame.K_s) and (solyanka.gun.direction == 'down'):
        solyanka.gun.move_end()


def button(font, text, x, y, color):
    """
    The function adds a field with text
    """
    textrun = font.render(text, True, RED, color)
    textRect = textrun.get_rect()
    textRect.center = (x, y)
    screen.blit(textrun, textRect)


clock = pygame.time.Clock()
finished = False
finished_game = False
solyanka = Solyanka()

while (not finished) and (not finished_game):
    clock.tick(FPS)
    pygame.display.update()
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
            finished_game = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            solyanka.gun.fire_start()
        elif event.type == pygame.MOUSEBUTTONUP:
            solyanka.gun.fire_end(event.button)
        elif event.type == pygame.KEYDOWN:
            keydown_actions()
        elif event.type == pygame.KEYUP:
            keyup_actions()
        elif event.type == pygame.MOUSEMOTION:
            solyanka.gun.targetting(event)
    solyanka.gun.move()
    solyanka.gun.power_up()
    solyanka.hitting()
    solyanka.draw()
    solyanka.all_hitted()
    solyanka.attack()
    finished = solyanka.attack_check()

if not finished_game:
    finished = False
    while not finished:
        clock.tick(FPS)
        pygame.display.update()
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finished = True
        button(font, 'GAME OVER', screen_size_x // 2, screen_size_y // 2, BLACK)

pygame.quit()
