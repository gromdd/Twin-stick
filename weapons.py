from importlib import reload
from backend import *
import numpy as np
import scipy.stats as stats


class weapon_holder():

    def __init__(self, *args):
        self.weapon_list = []
        for arg in args:
            self.weapon_list += [arg]
        self.current_weapon = None
        if self.weapon_list:
            self.current_weapon = self.weapon_list[0]
        self.weapon_index = 0

    def shoot(self, *args):
        self.current_weapon.shoot(*args)

    def reload(self, *args):
        self.current_weapon.reload(*args)

    def set_weapon(self, index):
        if index > len(self.weapon_list):
            return
        self.weapon_index = index-1
        self.current_weapon = self.weapon_list[self.weapon_index]

    def next_weapon(self):
        self.weapon_index = (self.weapon_index+1) % len(self.weapon_list)
        self.current_weapon = self.weapon_list[self.weapon_index]

    def previous_weapon(self):
        self.weapon_index = (self.weapon_index-1) % len(self.weapon_list)
        self.current_weapon = self.weapon_list[self.weapon_index]

    def size(self):
        return len(self.weapon_list)

    def __iter__(self):
        return self.weapon_list.__iter__()


class player_weapon(weapon):
    def __init__(self, *args):
        super().__init__(*args)
        self.weapon_silhoutte


class pistol(player_weapon):
    clip_size = 9
    damage = 5
    reload_time = 2.5
    bullet_mass = 0.01
    bullet_speed = 1800
    bullet_move_force = 800*4.5
    shoot_interval = 0.3
    def angle_distribution(self): return stats.truncnorm.rvs(
        a=-6, b=6, scale=np.pi/35/6)
    projectile_path = image_source/p.Path("projectile.png")

    weapon_silhoutte = arcade.Sprite(
        image_source/p.Path("pistol_silhoutte.png"))


class ak47(player_weapon):
    clip_size = 30
    damage = 6
    reload_time = 4
    bullet_mass = 0.01
    bullet_speed = 2100
    bullet_move_force = 800*4.5
    shoot_interval = 0.05
    def angle_distribution(self): return stats.truncnorm.rvs(
        a=-6, b=6, scale=np.pi/28/6)
    projectile_path = image_source/p.Path("projectile.png")

    weapon_silhoutte = arcade.Sprite(image_source/p.Path("ak47_silhoutte.png"))


class crossbow(weapon):
    clip_size = 1
    damage = 15
    reload_time = 4.5
    bullet_mass = 0.01
    bullet_speed = 1500
    bullet_move_force = 80000
    shoot_interval = 0.05

    def angle_distribution(self): return stats.truncnorm.rvs(
        a=-6, b=6, scale=np.pi/40/6)
    projectile_path = image_source/p.Path("bolt.png")

    def shoot(self, x, y):
        super().shoot(x, y)
        self.reload()

    def __init__(self, shooter, game_controller):
        super().__init__(shooter, game_controller)
        self.collision_group = collision_group.enemy_bullet
        self.reload()


class shotgun(weapon):
    clip_size = 5
    damage = 5
    reload_time = 1.2
    bullet_mass = 0.01
    bullet_speed = 2000
    bullet_move_force = 800*4.5
    shoot_interval = 0.3

    def angle_distribution(self): return stats.truncnorm.rvs(
        a=-6, b=6, scale=np.pi/18/6)
    projectile_path = image_source/p.Path("shotgun_shell.png")

    shell_number = 5

    weapon_silhoutte = arcade.Sprite(
        image_source/p.Path("shotgun_silhoutte.png"))

    def shoot(self, x, y):
        if not self.is_ready:
            return
        for i in range(self.shell_number):
            self.is_ready = True
            super().shoot(x, y)
        clock.schedule_once(self._ready_shotgun, self.shoot_interval)

    def __init__(self, shooter, game_controller):
        super().__init__(shooter, game_controller)
        self.current_clip_size = self.clip_size*self.shell_number

    def reload(self):
        if not self.is_reloading:
            print("reloading")
            self.is_reloading = True
            clock.schedule_once(self._reload_action, self.reload_time)

    def _reload_action(self, dt):
        self.current_clip_size += self.shell_number
        if self.current_clip_size == self.clip_size*self.shell_number:
            self.is_reloading = False
            print("weapon reloaded")
        else:
            clock.schedule_once(self._reload_action, self.reload_time)

    def _ready_weapon(self, dt):
        pass

    def _ready_shotgun(self, dt):
        self.is_ready = True

    def __del__(self):
        clock.unschedule(self._ready_shotgun)
        return super().__del__()

    def get_current_clip_size(self):
        return int(self.current_clip_size//self.shell_number)
