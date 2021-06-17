from importlib import reload
from backend import *
import numpy as np
import scipy.stats as stats


class weapon(metaclass=ABCMeta):
    is_penetraiting = False
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
        self.to_reload_time = 0

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
        if not self.is_reloading and self.get_current_clip_size()!= self.clip_size:
            print("reloading")
            self.current_clip_size = None
            self.is_reloading = True
            self.to_reload_time = self.reload_time
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
        bullet.is_penetraiting = self.is_penetraiting
        bullet.last_enemy = None
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


class shotgun(player_weapon):
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
        if not self.is_reloading and self.get_current_clip_size()!= self.clip_size:
            print("reloading")
            self.is_reloading = True
            self.to_reload_time= self.reload_time
            clock.schedule_once(self._reload_action, self.reload_time)

    def _reload_action(self, dt):
        self.current_clip_size += self.shell_number
        if self.current_clip_size == self.clip_size*self.shell_number:
            self.is_reloading = False
            print("weapon reloaded")
        else:
            self.to_reload_time= self.reload_time
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
