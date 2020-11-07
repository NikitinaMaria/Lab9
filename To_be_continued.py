from random import randrange as rnd, choice
import pygame
from pygame.draw import *
import math
import time

pygame.init()

screen_size_x = 800
screen_size_y = 600
FPS = 50

# Colors and list of the colors
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
MAGENTA = (255, 0, 255)
CYAN = (0, 255, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIL = (190, 0, 255)

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
        Initializing a new goal
        """
        self.target_x = rnd(600, 780)
        self.target_y = rnd(300, 550)
        self.target_r = rnd(10, 50)
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
        self.color = BLACK
        self.gun_x = gun_x
        self.gun_y = gun_y
        self.id = line(screen, self.color, [self.gun_x, self.gun_y], [self.gun_x + 20, self.gun_y + 20], 7)

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
            self.color = BLACK
        self.id = line(screen, self.color, [self.gun_x, self.gun_y],
                       [self.gun_x + max(self.gun_power, 20) * math.cos(self.gun_angle),
                        self.gun_y + max(self.gun_power, 20) * math.sin(self.gun_angle)], 7)

    def power_up(self):
        """
        Gun reinforcement
        """
        if self.gun_on:
            if self.gun_power < 100:
                self.gun_power += 1
            self.color = RED
        else:
            self.color = BLACK


class Target_1(Targets):
    def __init__(self, parent):
        """
        Constructor of the target class
        """
        super().__init__(RED)
        self.parent = parent

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
            self.id = circle(screen, self.color, (self.target_x, self.target_y), self.target_r)
            circle(screen, BLACK, (self.target_x, self.target_y), self.target_r, 1)

class Target_2(Targets):
    def __init__(self, parent):
        """
        Constructor of the target class
        """
        super().__init__(LIL)
        self.parent = parent
        self.target_r //= 2
        self.show_time = 60
        self.hide_time = 50
        self.invisible = False

    def move_target(self):
        """
        Moving a target
        """
        if not self.hitted:
            if self.show_time > 0:
                if self.show_time % 3 == 0:
                    self.target_r += 1
                self.show_time -= 1
                self.id = circle(screen, self.color, (self.target_x, self.target_y), self.target_r)
                circle(screen, BLACK, (self.target_x, self.target_y), self.target_r, 1)
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


class Solyanka:
    def __init__(self):
        self.gun = Gun(self)
        self.balls = []
        self.targets_1 = []
        self.targets_2 = []
        for i in range(3):
            self.targets_1.append(Target_1(self))
            self.targets_1[i].new_target()
        for i in range(3):
            self.targets_2.append(Target_2(self))
            self.targets_2[i].new_target()
        self.points = 0
        self.count_of_shoots = 0
        self.congrats_time = 100
        self.text = font.render(str(self.points), True, BLACK)
        self.screen_id_points = screen.blit(self.text, self.text.get_rect())

    def draw(self):
        self.gun.draw()
        for ball in self.balls:
            ball.move()
        for target in self.targets_1:
            target.move_target()
        for target in self.targets_2:
            target.move_target()
        self.text = font.render(str(self.points), True, BLACK)
        self.screen_id_points = screen.blit(self.text, self.text.get_rect())

    def shoot(self, angle, power, start_x, start_y, button):
        if button == 1:
            self.balls.append(Common_ball(angle, power, start_x, start_y, self))
        if button == 3:
            self.balls.append(Bomb_ball(angle, power, start_x, start_y, self))
        self.count_of_shoots += 1

    def delete_ball(self, color):
        for i in range(len(self.balls)):
            if self.balls[i].color == color:
                del self.balls[i]
                break

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


clock = pygame.time.Clock()
finished = False
solyanka = Solyanka()

while not finished:
    clock.tick(FPS)
    pygame.display.update()
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            solyanka.gun.fire_start()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                solyanka.gun.fire_end(1)
            if event.button == 3:
                solyanka.gun.fire_end(3)
        elif event.type == pygame.MOUSEMOTION:
            solyanka.gun.targetting(event)
    solyanka.gun.power_up()
    solyanka.hitting()
    solyanka.draw()
    solyanka.all_hitted()

pygame.quit()
