from backend import *
from weapons import crossbow
import pathlib as p

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



class dummy(enemy):
    point_value = 0
    health = 1000
    damage = 0

    def __init__(self, game_handler, **kwargs):
        super().__init__(game_handler,
                         mass=10**6,
                         friction=1,
                         max_velocity=0,
                         damping=1,
                         path=image_source/p.Path("dummy.png"),
                         move_force=0,
                         speed=0,
                         **kwargs
                         )

    def controller(self):
        pass


class zombie(enemy):
    point_value = 10
    health = 25
    damage = 5

    def __init__(self, game_handler, **kwargs):
        super().__init__(game_handler,
                         mass=5,
                         friction=10,
                         max_velocity=450,
                         damping=0.2,
                         path=image_source/p.Path("zombie.png"),
                         move_force=8000,
                         speed=450,
                         **kwargs
                         )

    def controller(self):

        tmp = (self.game_handler.player_sprite.position[0] - self.position[0],
               self.game_handler.player_sprite.position[1] - self.position[1])
        norm = np.sqrt(tmp[0]**2 + tmp[1]**2)
        self.change_x = tmp[0]/norm
        self.change_y = tmp[1]/norm


class hound(enemy):
    point_value = 25
    health = 15
    jump_circle = 450
    jump_impulse = 16000
    damage = 20

    def __init__(self, game_handler, **kwargs):
        super().__init__(game_handler,
                         mass=1.5,
                         friction=10,
                         max_velocity=650,
                         damping=0.2,
                         path=image_source/p.Path("hound.png"),
                         move_force=8000,
                         speed=650,
                         **kwargs
                         )
        self.can_jump = True

    def controller(self):
        if self.moves:

            tmp = (self.game_handler.player_sprite.position[0] - self.position[0],
                   self.game_handler.player_sprite.position[1] - self.position[1])
            norm = np.sqrt(tmp[0]**2 + tmp[1]**2)
            if norm < self.jump_circle and self.can_jump:
                self.moves = False
                self.can_jump = False
                clock.schedule_once(self._jump, 0.5, tmp, norm)
            else:
                self.change_x = tmp[0]/norm
                self.change_y = tmp[1]/norm

    def _jump(self, dt,  tmp, norm):
        self.pymunk.damping = 0.5
        self.pymunk.max_velocity = 950
        try:
            self.physics_engine.apply_impulse(
                self, (tmp[0]/norm*self.jump_impulse, tmp[1]/norm*self.jump_impulse))
        except Exception:
            print("jump exception")
            return
        clock.schedule_once(self._move, 1.35)
        clock.schedule_once(self._enable_jump, 2.85)

    def _move(self, dt):
        self.pymunk.damping = 0.2
        self.pymunk.max_velocity = 650
        self.moves = True

    def _enable_jump(self, dt):
        self.can_jump = True

    def __del__(self):
        clock.unschedule(self._jump)
        clock.unschedule(self._move)
        clock.unschedule(self._enable_jump)



class crossbowman(enemy):
    point_value = 25
    health = 15
    damage=15

    def __init__(self, game_handler, **kwargs):
        super().__init__(game_handler,
                         mass=6,
                         friction=10,
                         max_velocity=350,
                         damping=0.2,
                         path=image_source/p.Path("crossbowman.png"),
                         move_force=8000,
                         speed=650,
                         **kwargs
                         )
        self.crossbow = crossbow(self, game_handler)
        self.max_shooting_distance = 700
        self.min_shooting_distance = 550
        self.moving_backwards = False
        self.is_shooting = False

    def controller(self):
        x = self.game_handler.player_sprite.position[0]
        y = self.game_handler.player_sprite.position[1]
        tmp = (x - self.position[0],
               y - self.position[1])
        norm = np.sqrt(tmp[0]**2 + tmp[1]**2)

        self.change_x = tmp[0]/norm
        self.change_y = tmp[1]/norm

        if self.is_shooting:
            pass

        elif norm < self.min_shooting_distance:
            self.moving_backwards = True
            self.change_x = -self.change_x
            self.change_y = -self.change_y

        elif norm > self.max_shooting_distance:
            self.moving_backwards = False

        elif self.crossbow.is_ready:
            self.moving_backwards = False
            clock.schedule_once(self._shoot, 0.35)
            self.is_shooting =True


    
    def _shoot(self, dt):
        self.is_shooting = False
        self.crossbow.shoot(self.game_handler.player_sprite.position[0], self.game_handler.player_sprite.position[1])

    

    def rotate(self):
        angle = np.degrees(-np.arctan2(self.change_x, self.change_y))+180*self.moving_backwards
        self.turn_left(angle)

    
    def __del__(self):
        self.crossbow.__del__()






