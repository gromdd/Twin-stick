import arcade
import pathlib as p
import numpy as np
from numpy.random import choice, uniform
import pyglet.clock as clock


from backend import *
from enemies import *


class enemy_spawn(arcade.SpriteSolidColor):
    def __init__(self, width: int, height: int, pos_x, pos_y, available_enemies, spawn_ratios, game_controller, spawn_interval=1, spawn_offset=1.5):
        super().__init__(width, height, "black")
        self.center_x = pos_x
        self.center_y = pos_y

        sum_of_ratios = sum(spawn_ratios)
        self.spawn_ratios = np.asarray(spawn_ratios)/sum_of_ratios
        self.available_enemies = available_enemies
        self.game_controller = game_controller
        self.spawn_interval = spawn_interval
        self.spawn_offset = spawn_offset

        self.game_controller.physics_engine.add_sprite(self,
                                                       collision_type=collision_group.wall,
                                                       body_type=arcade.PymunkPhysicsEngine.STATIC)

    def enable(self):
        clock.schedule_once(self._spawn, self.spawn_offset)

    def _spawn(self, dt):
        x = uniform(self.left, self.right)
        y = uniform(self.bottom, self.top)
        spawned_enemy = choice(self.available_enemies, p=self.spawn_ratios)
        spawned_enemy(self.game_controller, center_x=x, center_y=y)
        clock.schedule_once(self._spawn, self.spawn_interval)


    def __del__(self):
        clock.unschedule(self._spawn)

