import pyglet.clock as clock
import arcade
from abc import ABC, ABCMeta
from numpy.random import choice, uniform
import pathlib as p

from backend import *



class modifier_spawn_field(arcade.SpriteSolidColor):
    def __init__(self, available_modifiers, spawn_ratios, game_controller, spawn_interval=10, spawn_offset=5):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "black")
        self.center_x = SCREEN_WIDTH/2
        self.center_y = SCREEN_HEIGHT/2

        sum_of_ratios = sum(spawn_ratios)
        self.spawn_ratios = np.asarray(spawn_ratios)/sum_of_ratios
        self.available_modifiers = available_modifiers
        self.game_controller = game_controller
        self.spawn_interval = spawn_interval
        self.spawn_offset = spawn_offset



    def enable(self):
        clock.schedule_once(self._spawn, self.spawn_offset)

    def _spawn(self, dt):
        x = uniform(self.left, self.right)
        y = uniform(self.bottom, self.top)
        spawned_modifier = choice(self.available_modifiers, p=self.spawn_ratios)
        spawned_modifier(self.game_controller, x, y)
        clock.schedule_once(self._spawn, self.spawn_interval)


    def __del__(self):
        clock.unschedule(self._spawn)

    def clear(self):
        for modifier in self.available_modifiers:
            modifier.clear()





class modifier(ABC, arcade.Sprite):


    def __init__(self, game_handler, center_x, center_y, scale=0.5, **kwargs):
        self.duration
        super().__init__(kwargs['path'], scale,  hit_box_algorithm="Simple")
        self.center_x=center_x
        self.center_y=center_y
        

        game_handler.modifier_list.append(self)
        game_handler.physics_engine.add_sprite(self,
            body_type=arcade.PymunkPhysicsEngine.STATIC,
            collision_type=collision_group.modifier)
        self.__class__.game_handler=game_handler

    @classmethod
    @abstractmethod
    def effect(cls, game_handler):
        pass

    @classmethod
    def on_pickup(cls):
        cls.effect(cls.game_handler)
        if cls.duration!=0:
            cls.is_on = True
            clock.schedule_once(cls.on_modifier_end, cls.duration, cls.game_handler)
            clock.schedule_once(cls.flip, cls.duration )
        

    @classmethod
    @abstractmethod
    def on_modifier_end(cls, dt, game_handler):
        pass
    
    @classmethod
    def clear(cls):
        clock.unschedule(cls.on_modifier_end)
        cls.is_on = False


    @classmethod
    def flip(cls, dt):
        cls.is_on = False

    


class turning_screen_red(modifier):
    is_on = False
    duration=1

    def __init__(self, game_controller, pos_x, pos_y):
        super().__init__( game_controller, pos_x, pos_y, path=image_source/p.Path("red.png"))

    @classmethod
    def effect(cls, game_handler):
        arcade.set_background_color(BACKGROUND_RED)

    @classmethod
    def on_modifier_end(cls, dt, game_handler):
        arcade.set_background_color(BACKGROUND_COLOR)



class railgun_weapons(modifier):
    is_on = False
    duration=5

    def __init__(self, game_controller, pos_x, pos_y):
        super().__init__( game_controller, pos_x, pos_y, path=image_source/p.Path("power_up2.png"))

    @classmethod
    def effect(cls, game_handler):
        for weapon in game_handler.player_sprite.weapons:
            weapon.is_penetraiting = True

    @classmethod
    def on_modifier_end(cls, dt, game_handler):
        for weapon in game_handler.player_sprite.weapons:
            weapon.is_penetraiting = weapon.__class__.is_penetraiting


class one_hp_for_enemies(modifier):
    is_on = False
    duration=0

    def __init__(self, game_controller, pos_x, pos_y):
        super().__init__( game_controller, pos_x, pos_y, path=image_source/p.Path("power_up.png"))

    @classmethod
    def effect(cls, game_handler):
        for enemy in game_handler.enemy_list:
            enemy.current_health = 1

    @classmethod
    def on_modifier_end(cls, dt, game_handler):
        pass

class cherry(modifier):
    is_on=False
    duration=0

    def __init__(self, game_controller, pos_x, pos_y):
        super().__init__( game_controller, pos_x, pos_y, path=image_source/p.Path("cherry.png"))

    @classmethod
    def effect(cls, game_handler):
        game_handler.points+=25

    @classmethod
    def on_modifier_end(cls, dt, game_handler):
        pass

    
