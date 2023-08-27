import sys
import time
from abc import ABC, abstractmethod
import random
import pygame
import math


class Window:
    _instance = None
    _init_already = False
    menu_on = True

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            print("create_inst")
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._init_already:
            self.__class__._init_already = True
            pygame.init()
            pygame.font.init()
            self.resolution = (720, 480)
            self.background_color = "black"
            self.clock = pygame.time.Clock()
            self.fps = 30
            self.screen = pygame.display.set_mode(self.resolution)
            pygame.display.set_caption("Pong")
            self.screen.fill(self.background_color)
            self.score_font = pygame.sysfont.SysFont("Arial", 30)
            self.menu_font = pygame.sysfont.SysFont("Georgia", 20)
            self.friend_score = 0
            self.enemy_score = 0
            self.button_size = (200, 25)
            self.play_with_AI = pygame.Surface(self.button_size)
            self.play_with_AI.fill("white")
            self.play_with_human = pygame.Surface(self.button_size)
            self.play_with_human.fill("white")
            self.AI_on = None

    def run(self, running=False):
        friend_label = FriendLabel()
        enemy_label = EnemyLabel()
        ball = Ball()
        while running:
            if self.menu_on:
                self.screen.fill(self.background_color)
                self.play_with_AI.blit(self.menu_font.render("Play with AI", False, "black"), (50, 0))
                self.play_with_human.blit(self.menu_font.render("Play with Human", False, "black"), (25, 0))
                self.screen.blit(self.play_with_AI, (260, 200))
                self.screen.blit(self.play_with_human, (260, 300))
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        if 260<mouse_pos[0]<400 and 200<mouse_pos[1]<225:
                            self.AI_on = True
                            self.menu_on = False
                pygame.display.update()

            else:
                self.screen.fill(self.background_color)
                self.screen.blit(friend_label.figure, friend_label.coords)
                self.screen.blit(enemy_label.figure, enemy_label.coords)
                score = self.score_font.render(f"{self.friend_score}:{self.enemy_score}", True, "white")
                self.screen.blit(score, (340, 30))
                ball.ball_move()
                self.screen.blit(ball.shape, ball.position)
                pygame.display.update()
                # self.screen.fill(self.background_color)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        friend_label.controller(event, True)
                        enemy_label.controller(event, True)
                    if event.type == pygame.KEYUP:
                        friend_label.controller(event, False)
                        enemy_label.controller(event, False)
                    friend_label.controller(event, True)
                    enemy_label.controller(event, True)
                enemy_label.AI_controller()

            self.clock.tick(self.fps)


class Ball:
    _instance = None
    _inited = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            print("create_inst")
            cls._instance = object.__new__(cls)
        return cls._instance
    def __init__(self):
        if not self.__class__._inited:
            self.__class__._inited = True
            size = (25, 25)
            self.position = [360, 240]
            self.shape = pygame.Surface(size)
            self.window = Window()
            self.shape.fill("black")
            self.direction_angle = self.angle_gen()
            # self.direction_angle = math.pi * 1/4
            self.movespeed = 4
            pygame.draw.circle(self.shape, "red", (12.5, 12.5), 12.5)
            self.friend_label = FriendLabel()
            self.enemy_label = EnemyLabel()

    def ball_move(self):
        self.position[0] = self.position[0] + self.movespeed * math.cos(self.direction_angle)
        self.position[1] = self.position[1] + self.movespeed * math.sin(self.direction_angle)
        self.wall_collision()
        self.score_checking()
        self.ball_collide_with_label()

    def wall_collision(self):
        if self.position[1] <= 15 or self.position[1] >= 465:
            self.direction_angle = -self.direction_angle
            self.position[0] = self.position[0] + self.movespeed * math.cos(self.direction_angle)
            self.position[1] = self.position[1] + self.movespeed * math.sin(self.direction_angle)

    def score_checking(self):
        if self.position[0] <= 15:
            Window().enemy_score += 1
            self.pause_after_goal()
        if self.position[0] >= 705:
            Window().friend_score += 1
            self.pause_after_goal()

    def pause_after_goal(self):
        self.position = [360, 240]
        self.direction_angle = self.angle_gen()
        self.movespeed = 4
        time.sleep(3)

    def ball_collide_with_label(self):
        if self.friend_label.coords[0] < self.position[0] < self.friend_label.coords[0] + self.friend_label.size[0] and \
           self.friend_label.coords[1] < self.position[1] < self.friend_label.coords[1] + self.friend_label.size[1]:
            print("left")
            print(self.direction_angle)
            label_center_y = self.friend_label.coords[1] + self.friend_label.size[1] / 2
            arccos_ball_direction = math.acos(math.cos(math.pi / 2 + abs(self.position[1] - label_center_y)))
            self.direction_angle = 0
            self.direction_angle += random.choice([1,-1])*math.pi/2/random.randint(5,9)
            self.movespeed+=0.5
        if self.enemy_label.coords[0]-self.enemy_label.size[0] < self.position[0] and \
           self.enemy_label.coords[1] < self.position[1] < self.enemy_label.coords[1] + self.enemy_label.size[1]:
            print("right")
            print(self.direction_angle)
            label_center_y = self.enemy_label.coords[1] + self.enemy_label.size[1] / 2
            arccos_ball_direction = math.acos(math.cos(math.pi / 2 + abs(self.position[1] - label_center_y)))
            self.direction_angle = math.pi
            self.direction_angle += random.choice([1,-1])*math.pi/2/random.randint(5,9)
            self.movespeed+=0.5
    def angle_gen(self):
        angle = random.random() * 2 * math.pi
        if math.pi/3<angle<2*math.pi/3 or 4*math.pi/3<angle<5*math.pi/3:
            return self.angle_gen()
        return angle

class Label(ABC):
    _instance = None
    _inited = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            print("create_inst")
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        if not self.__class__._inited:
            self._inited = True
            self.size = (25, 100)
            self.speed = 5
            self.color = "white"
            self.figure = pygame.Surface(self.size)
            self.figure.fill(self.color)
            self.window = Window()
            self.moving = False
            self.friend_key = None
            self.enemy_key = None

    @abstractmethod
    def controller(self, event, move):
        pass


class EnemyLabel(Label):
    def __init__(self):
        super().__init__()
        self.coords = [700, 190]
        self.figure.fill("red")
        self.window.screen.blit(self.figure, self.coords)

    def controller(self, event, move):
        if not Window().AI_on:
            if event.type == pygame.KEYDOWN and move:
                self.moving = True
                self.enemy_key = event.key
            if event.type == pygame.KEYUP and not move:
                self.moving = False
            if self.enemy_key == pygame.K_p and move:
                self.coords[1] -= 5
            if self.enemy_key == pygame.K_l and move:
                self.coords[1] += 5
    def AI_controller(self):
        if Window().AI_on:
            print("ai_moving")
            if self.coords[1]+self.size[1]/2 < Ball().position[1]:
                self.coords[1]+=5
            if self.coords[1]+self.size[1]/2 > Ball().position[1]:
                self.coords[1]-=5
class FriendLabel(Label):
    def __init__(self):
        super().__init__()
        self.coords = [0, 190]
        self.figure.fill("green")
        self.window.screen.blit(self.figure, self.coords)

    def controller(self, event, move):
        if event.type == pygame.KEYDOWN and move:
            self.moving = True
            self.friend_key = event.key
        if event.type == pygame.KEYUP and not move:
            self.moving = False
        if self.friend_key == pygame.K_w and move:
            self.coords[1] -= 5
        if self.friend_key == pygame.K_s and move:
            self.coords[1] += 5


class Wall(ABC):
    pass


game = Window()
game.run(True)
