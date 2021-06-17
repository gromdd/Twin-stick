import arcade
import pathlib as p
import numpy as np
from numpy.random import choice, uniform
import pyglet.clock as clock

from enemy_spawns import *
from modifier import *

class level(metaclass=ABCMeta):
    enemy_spawns=[]
    number_of_enemies=-1
    name=""
    modifier_field=[]

        
    def begin(self):
        for spawn in self.enemy_spawns:
            spawn.enable()
        for spawn in self.modifier_field:
            spawn.enable()
        

    def __del__(self):
        for spawn in self.enemy_spawns:
            spawn.__del__()
        for spawn in self.modifier_field:
            spawn.clear()

    

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
        self.modifier_field=[
            modifier_spawn_field(
                available_modifiers = [one_hp_for_enemies],
                spawn_ratios = [1],
                game_controller = game_controller, 
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
        self.modifier_field=[
            modifier_spawn_field(
                available_modifiers = [railgun_weapons],
                spawn_ratios = [1],
                game_controller = game_controller, 
            )
        ]


class final_level(level):
    number_of_enemies = 50
    name="All elements"
    def setup(self, game_controller):
        self.enemy_spawns=[
            enemy_spawn(
                width=BOX_WIDTH//2,
                height=game_controller.screen_dimensions[1]//4,
                pos_x=game_controller.screen_dimensions[0]+BOX_WIDTH//2,
                pos_y=game_controller.screen_dimensions[1]//2,
                available_enemies=[zombie,crossbowman],
                spawn_ratios=[2,1],
                game_controller=game_controller,
                spawn_interval=3,
                spawn_offset=0.5
            ),

            enemy_spawn(
                width=BOX_WIDTH//2,
                height=game_controller.screen_dimensions[1]//4,
                pos_x=-BOX_WIDTH//2,
                pos_y=game_controller.screen_dimensions[1]//2,
                available_enemies=[zombie,crossbowman],
                spawn_ratios=[2,1],
                game_controller=game_controller,
                spawn_interval=3,
                spawn_offset=1
            ),

            enemy_spawn(
                width=game_controller.screen_dimensions[0]//4,
                height=BOX_WIDTH//2,
                pos_x=game_controller.screen_dimensions[0]//2,
                pos_y=game_controller.screen_dimensions[1]+BOX_WIDTH//2,
                available_enemies=[zombie, hound],
                spawn_ratios=[1.25,1],
                game_controller=game_controller,
                spawn_interval=3,
                spawn_offset=1.5
            ),

            enemy_spawn(
                width=game_controller.screen_dimensions[0]//4,
                height=BOX_WIDTH//2,
                pos_x=game_controller.screen_dimensions[0]//2,
                pos_y=-BOX_WIDTH//2,
                available_enemies=[zombie, hound],
                spawn_ratios=[1.5,1],
                game_controller=game_controller,
                spawn_interval=3,
                spawn_offset=2
            ),
            
        ]
        self.modifier_field=[
            modifier_spawn_field(
                available_modifiers = [cherry, one_hp_for_enemies,railgun_weapons],
                spawn_ratios = [5,1,1],
                game_controller = game_controller, 
                spawn_interval=5
            )
        ]




class mod_level(level):
    number_of_enemies = 1
    name="TEST"
    def setup(self, game_controller):
        self.modifier_field=[
            modifier_spawn_field(
                available_modifiers = [cherry, turning_screen_red],
                spawn_ratios = [1,1],
                game_controller = game_controller, 
            )
        ]



level_list=[
    zombie_level,
    crossbowman_level,
    final_level,
    ]