import importlib
import sys
import arcade
import pathlib as p
import numpy as np
import pyglet
import scipy.stats as stats

import pyglet.clock as clock


from abc import ABC, ABCMeta, abstractmethod

import enum
from copy import copy

image_source = p.Path("place_holder")


def modify_and_import(module_name, package, modification_func):
    spec = importlib.util.find_spec(module_name, package)
    source = spec.loader.get_source(module_name)
    new_source = modification_func(source)
    module = importlib.util.module_from_spec(spec)
    codeobj = compile(new_source, module.__spec__.origin, 'exec')
    exec(codeobj, module.__dict__)
    sys.modules[module_name] = module
    return module


physics = modify_and_import("arcade.pymunk_physics_engine", None, lambda src: src.replace("begin_handler(sprite_a, sprite_b, arbiter, space, data)", "return begin_handler(sprite_a, sprite_b, arbiter, space, data)").replace(
    "post_handler(sprite_a, sprite_b, arbiter, space, data)", "return post_handler(sprite_a, sprite_b, arbiter, space, data)").replace(
    "pre_handler(sprite_a, sprite_b, arbiter, space, data)", "return pre_handler(sprite_a, sprite_b, arbiter, space, data)").replace(
    "separate_handler(sprite_a, sprite_b, arbiter, space, data)", "return separate_handler(sprite_a, sprite_b, arbiter, space, data)")
)

"""Powyższa funkcja pozwala na ignorowanie kolizji, zwracając False w pre_handler, lub begin_handler."""


CHARACTER_SCALING = 0.5

PLAYER_MOVEMENT_SPEED = 5

PLAYER_DAMPING = 0.005
PLAYER_FRICTION = 0
PLAYER_MASS = 2.0
PLAYER_MOMENT = physics.PymunkPhysicsEngine.MOMENT_INF
PLAYER_MAX_SPEED = 700
PLAYER_MOVE_FORCE = 8000


BULLET_SPEED = 1800
BULLET_MASS = 0.01
BULLET_MOVE_FORCE = 800*4.5

PHYSICS_STEPS = 8
DELTA_TIME = 1/60


SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Twin stick"

HUD_HEIGHT = 150
HUD_WIDTH = 850


BOX_WIDTH = 64


class collision_group(enum.Enum):
    enemy = "enemy"
    player = "player"
    wall = "wall"
    bullet = "bullet"
    enemy_bullet = "enemy_bullet"


class BulletSprite(arcade.Sprite):

    """ Klasa ta sprawia, że pociski, które wyleciały poza planszę, zostaną usunięte."""

    def __init__(self, name, scale,  lim_x, lim_y, damage):
        super().__init__(name, scale)
        self.lim_x = lim_x
        self.lim_y = lim_y
        self.damage = damage

    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        boundary = 100
        if (self.center_y < -boundary or self.center_y > self.lim_y) or\
                (self.center_x < -boundary or self.center_x > self.lim_x):
            self.remove_from_sprite_lists()


def wall_hit_handler(bullet_sprite, _wall_sprite, _arbiter, _space, _data):
    """Gdy pocisk koliduje ze ścianami planszy, zignoruj kolizję. """
    return False


def enemy_hit_handler(bullet_sprite, _enemy_sprite, _arbiter, _space, _data):
    try:
        _enemy_sprite.take_damage(bullet_sprite.damage)
        bullet_sprite.remove_from_sprite_lists()
    except Exception:
        pass

    return False


def enemy_enemy_bullet_handler(enemy, bullet_sprite, _arbiter, _space, _data):
    return False


def player_enemy_bullet_handler(player, bullet_sprite, _arbiter, _space, _data):
    if player.take_damage(bullet_sprite.damage):
        bullet_sprite.remove_from_sprite_lists()
    return False


def bullet_bullet_handler(bullet1, bullet2, _arbiter, _space, _data):
    return False


def enemy_wall_handler(enemy, wall, _arbiter, _space, _data):
    return enemy.is_in_play_area()

def enemy_player_handler(enemy, player, _arbiter, _space, _data):
    return player.take_damage(enemy.damage)
    


class weapon(metaclass=ABCMeta):
    def __init__(self, shooter, game_controller):
        self.clip_size

        self.damage

        self.reload_time
        self.bullet_mass
        self.bullet_speed
        self.bullet_move_force
        self.angle_distribution
        self.shoot_interval

        self.projectile_path

        self.current_clip_size = self.clip_size
        self.collision_group = collision_group.bullet
        self.is_reloading = False
        self.shooter = shooter
        self.bullet_list = game_controller.bullet_list
        self.physics_engine = game_controller.physics_engine
        self.is_ready = True
        self.projectile_factory = lambda: BulletSprite(self.projectile_path,
                                                       CHARACTER_SCALING, *game_controller.screen_dimensions, self.damage
                                                       )

    def _reload_action(self, dt):
        self.current_clip_size = self.clip_size
        self.is_reloading = False
        print("weapon reloaded")

    def _ready_weapon(self, dt):
        self.is_ready = True

    def reload(self):
        if not self.is_reloading:
            print("reloading")
            self.current_clip_size = None
            self.is_reloading = True
            clock.schedule_once(self._reload_action, self.reload_time)


    def shoot(self, x, y):
        if not self.current_clip_size or not self.is_ready:
            return
        self.is_ready = False
        clock.schedule_once(self._ready_weapon, self.shoot_interval)
        bullet = self.projectile_factory()
        self.bullet_list.append(bullet)

        """Wygeneruj pocisk na granicy sprite'a gracza, a następnie nadaj mu prędkość """
        start_x = self.shooter.center_x
        start_y = self.shooter.center_y
        bullet.position = self.shooter.position
        x_diff = x - start_x
        y_diff = y - start_y
        angle = np.arctan2(y_diff, x_diff)+self.angle_distribution()
        size = self.shooter.width/2
        bullet.center_x += size * np.cos(angle)
        bullet.center_y += size * np.sin(angle)
        bullet.angle = np.degrees(angle)
        self.physics_engine.add_sprite(bullet,
                                       mass=self.bullet_mass,
                                       damping=1.0,
                                       friction=1.0,
                                       collision_type=self.collision_group,
                                       max_velocity=self.bullet_speed)
        force = (self.bullet_move_force, 0)
        self.physics_engine.apply_force(bullet, force)
        self.current_clip_size -= 1

    def __del__(self):
        clock.unschedule(self._reload_action)
        clock.unschedule(self._ready_weapon)


    def get_clip_size(self):
        return self.clip_size

    def get_current_clip_size(self):
        return self.current_clip_size


class entity(ABC, arcade.Sprite):
    def __init__(self, game_handler, scale=0.5, **kwargs):
        self.health
        self.current_health = self.health
        self.physics_engine = game_handler.physics_engine
        self.move_force = kwargs['move_force']
        self.moves = True

        super().__init__(kwargs['path'], scale, hit_box_algorithm="Detailed")
        self.change_x = 0
        self.change_y = 0

        if kwargs['center_x'] and kwargs['center_y']:
            self.center_x = kwargs['center_x']
            self.center_y = kwargs['center_y']

        moment = physics.PymunkPhysicsEngine.MOMENT_INF

        self.physics_engine.add_sprite(self,
                                       friction=kwargs['friction'],
                                       mass=kwargs['mass'],
                                       moment=moment,
                                       collision_type=kwargs['collision_type'],
                                       max_velocity=kwargs['max_velocity'],
                                       damping=kwargs['damping'],
                                       )

    @abstractmethod
    def die(self):
        pass

    def take_damage(self, damage):
        self.current_health -= damage
        if self.current_health <= 0:
            self.die()

    @abstractmethod
    def controller(self):
        pass

    @abstractmethod
    def rotate(self):
        pass


class enemy(entity):
    def __init__(self,  game_handler, **kwargs):
        kwargs["collision_type"] = collision_group.enemy
        self.point_value
        self.damage
        self.game_handler = game_handler
        self.move_force = kwargs["move_force"]
        self.speed = kwargs["speed"]
        super().__init__(game_handler, **kwargs)

        game_handler.enemy_list.append(self)

    def die(self):
        self.game_handler.on_enemy_death(self.point_value)
        self.remove_from_sprite_lists()

    def rotate(self):
        angle = np.degrees(-np.arctan2(self.change_x, self.change_y))
        self.turn_left(angle)

    def is_in_play_area(self):

        tmp_x = self.center_x <= self.game_handler.screen_dimensions[0] and self.center_x >= 0
        tmp_y = self.center_y <= self.game_handler.screen_dimensions[1] and self.center_y >= 0

        return tmp_x and tmp_y


class player(entity):
    def __init__(self, game_handler, weapons, **kwargs):
        kwargs["collision_type"] = collision_group.player

        self.weapons = weapons

        self.health = 100

        super().__init__(game_handler, **kwargs)
        game_handler.player_list.append(self)
        self.game_over_function=game_handler.end

        self.is_vulnerable = True
        self.invulnerability_time=0.5
        self.invulnerability_remaining_time = 0

    def die(self):
        print("you died")
        self.game_over_function()

    def controller(self):
        self.invulnerability_remaining_time=max(self.invulnerability_remaining_time-DELTA_TIME,0)
        self.alpha= 255 * (self.invulnerability_time-self.invulnerability_remaining_time)/self.invulnerability_time
    def rotate(self, mouse_x, mouse_y):
        x, y = self.position
        angle = np.degrees(np.arctan2(mouse_y-y, mouse_x-x))
        self.turn_left(angle)

    def _make_vurnerable(self, dt):
        self.is_vulnerable= True

    def take_damage(self, damage):

        if not self.is_vulnerable:
            return False

        self.is_vulnerable=False
        self.invulnerability_remaining_time=self.invulnerability_time
        clock.schedule_once(self._make_vurnerable, self.invulnerability_time)
        super().take_damage(damage)
        return False

    def __del__(self):
        clock.unschedule(self._make_vurnerable)
        


def movement_function(entity_sprite):
    try:
        if (entity_sprite.change_x or entity_sprite.change_y) and entity_sprite.moves:

            force = (entity_sprite.change_x * entity_sprite.move_force,
                    entity_sprite.change_y*entity_sprite.move_force)
            entity_sprite.physics_engine.apply_force(entity_sprite, force)

            entity_sprite.physics_engine.set_friction(entity_sprite, 0)
        elif entity_sprite is player:

            entity_sprite.physics_engine.set_friction(entity_sprite, 1.0)
    except:
        pass
