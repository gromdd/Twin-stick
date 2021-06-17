import arcade
import pathlib as p
import numpy as np
from numpy.random import choice, uniform
import pyglet.clock as clock

from enemy_spawns import *

class level(metaclass=ABCMeta):
    enemy_spawns=None
    number_of_enemies=-1
    name=""

        
    def begin(self):
        for spawn in self.enemy_spawns:
            spawn.enable()

    def __del__(self):
        for spawn in self.enemy_spawns:
            spawn.__del__()
    

class zombie_level(level):
    number_of_enemies = 10
    name="Zombies only"
    def setup(self, game_controller):
        self.enemy_spawns=[
            enemy_spawn(
                width=BOX_WIDTH//2,
                height=game_controller.screen_dimensions[1],
                pos_x=game_controller.screen_dimensions[0]+BOX_WIDTH/2,
                pos_y=game_controller.screen_dimensions[1]/2,
                available_enemies=[zombie],
                spawn_ratios=[1],
                game_controller=game_controller
            )
        ]


class crossbowman_level(level):
    number_of_enemies = 10
    name="Crossbows"
    def setup(self, game_controller):
        self.enemy_spawns=[
            enemy_spawn(
                width=BOX_WIDTH//2,
                height=game_controller.screen_dimensions[1]//4,
                pos_x=game_controller.screen_dimensions[0]+BOX_WIDTH//2,
                pos_y=game_controller.screen_dimensions[1]//8,
                available_enemies=[crossbowman],
                spawn_ratios=[1],
                game_controller=game_controller,
                spawn_interval=2.5,
                spawn_offset=0.5
            ),

            enemy_spawn(
                width=BOX_WIDTH//2,
                height=game_controller.screen_dimensions[1]//4,
                pos_x=-BOX_WIDTH//2,
                pos_y=game_controller.screen_dimensions[1]*7//8,
                available_enemies=[crossbowman],
                spawn_ratios=[1],
                game_controller=game_controller,
                spawn_interval=2.5,
                spawn_offset=1
            ),

            enemy_spawn(
                width=game_controller.screen_dimensions[0]//4,
                height=BOX_WIDTH//2,
                pos_x=game_controller.screen_dimensions[0]//8,
                pos_y=game_controller.screen_dimensions[1]+BOX_WIDTH//2,
                available_enemies=[crossbowman],
                spawn_ratios=[1],
                game_controller=game_controller,
                spawn_interval=2.5,
                spawn_offset=1.5
            ),

            enemy_spawn(
                width=game_controller.screen_dimensions[0]//4,
                height=BOX_WIDTH//2,
                pos_x=game_controller.screen_dimensions[0]*7//8,
                pos_y=-BOX_WIDTH//2,
                available_enemies=[crossbowman],
                spawn_ratios=[1],
                game_controller=game_controller,
                spawn_interval=2.5,
                spawn_offset=2
            ),
            
        ]







level_list=[
    zombie_level,
    crossbowman_level,
    ]