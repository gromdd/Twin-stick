import arcade
import os
import pathlib as p
import pymunk
import numpy as np
import re
from copy import copy


import importlib
import sys

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


SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Twin stick"

CHARACTER_SCALING = 0.5

PLAYER_MOVEMENT_SPEED = 5
LOCAL_DIR=p.Path(os.getcwd() )

PLAYER_DAMPING = 0.005
PLAYER_FRICTION = 0
PLAYER_MASS = 2.0
PLAYER_MOMENT = physics.PymunkPhysicsEngine.MOMENT_INF
PLAYER_MAX_SPEED = 700
PLAYER_MOVE_FORCE = 8000


BULLET_SPEED=1800
BULLET_MASS=0.01
BULLET_MOVE_FORCE = 800*4.5

PHYSICS_STEPS=4
DELTA_TIME=1/60

image_source=p.Path("place_holder")



class BulletSprite(arcade.Sprite):
    """ Klasa ta sprawia, że pociski, które wyleciały poza planszę, zostaną usunięte."""
    def __init__(self,name,scale,  lim_x, lim_y):
        super().__init__(name,scale)
        self.lim_x=lim_x
        self.lim_y=lim_y
    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        boundary=100
        if (self.center_y < -boundary or self.center_y> self.lim_y) or\
            (self.center_x < -boundary or self.center_x> self.lim_x) :
            self.remove_from_sprite_lists()



class MyGame(arcade.Window):


    def __init__(self):
        """Inicjalizacja zmiennych"""

        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=True)
        self.set_update_rate(DELTA_TIME)

        #self.set_exclusive_mouse()

        arcade.set_background_color(arcade.csscolor.GREY)
        self.player_sprite = None
        self.player_list = None

        self.bullet_list = None
        self.bullet_sprite = None

        self.space = pymunk.Space()
        self.space.iterations = 35
        self.space.gravity = (0.0, 0.0)
        self.confinement_box=None
        


        
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.physics_engine = None
        self.mouse_x = 0
        self.mouse_y = 0
        
        self.screen_dimensions=arcade.get_display_size()


    def setup(self):
        """ Bariery, które utrzymują gracza na planszy"""
        box_width=64
        self.confinement_box=arcade.SpriteList()
        self.confinement_box.append(arcade.SpriteSolidColor(box_width, self.screen_dimensions[1], "black"))
        self.confinement_box[-1].center_x=self.screen_dimensions[0]+box_width/2
        self.confinement_box[-1].center_y=self.screen_dimensions[1]/2

        self.confinement_box.append(arcade.SpriteSolidColor(box_width, self.screen_dimensions[1], "black"))
        self.confinement_box[-1].center_x=-box_width/2
        self.confinement_box[-1].center_y=self.screen_dimensions[1]/2

        self.confinement_box.append(arcade.SpriteSolidColor(self.screen_dimensions[0],box_width , "black"))
        self.confinement_box[-1].center_x=self.screen_dimensions[0]/2
        self.confinement_box[-1].center_y=self.screen_dimensions[1]+box_width/2

        self.confinement_box.append(arcade.SpriteSolidColor(self.screen_dimensions[0],box_width , "black"))
        self.confinement_box[-1].center_x=self.screen_dimensions[0]/2
        self.confinement_box[-1].center_y=-box_width/2



        self.player_sprite = arcade.Sprite( image_source/p.Path("player.png"), CHARACTER_SCALING, hit_box_algorithm="Detailed")
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)
        self.physics_engine = physics.PymunkPhysicsEngine()

        self.bullet_sprite = arcade.Sprite( image_source/p.Path("projectile.png"), CHARACTER_SCALING)
        self.bullet_list=arcade.SpriteList()

        def wall_hit_handler(bullet_sprite, _wall_sprite, _arbiter, _space, _data):
            """Gdy pocisk koliduje ze ścianami planszy, zignoruj kolizję. """
            return False
        self.physics_engine.add_collision_handler("bullet", "wall", begin_handler=wall_hit_handler)


        """Dodaj obiekty reprezentowane przez sprite'y do silnika fizycznego."""
        self.physics_engine.add_sprite(self.player_sprite,
                                       friction=PLAYER_FRICTION,
                                       mass=PLAYER_MASS,
                                       moment=PLAYER_MOMENT,
                                       collision_type="player",
                                       max_velocity=PLAYER_MAX_SPEED,
                                       damping=PLAYER_DAMPING)

        self.physics_engine.add_sprite_list(self.confinement_box,
                                        collision_type="wall",
                                        body_type=arcade.PymunkPhysicsEngine.STATIC)

    	




    def on_draw(self):


        arcade.start_render()
        self.player_list.draw()
        self.bullet_list.draw()
        #self.confinement_box.draw()

    	

    def on_key_press(self, key, modifiers):
        """Poruszanie się"""

        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y += PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y += -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x += -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x += PLAYER_MOVEMENT_SPEED

        
        elif key == arcade.key.ESCAPE:
            """Wyjście z gry"""
            self.close()
            

    	

    def on_key_release(self, key, modifiers):

        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y -= PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y -= -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x  -= -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x -= PLAYER_MOVEMENT_SPEED


    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_press(self, x, y, button, modifiers):
        bullet = BulletSprite( image_source/p.Path("projectile.png"), CHARACTER_SCALING , *self.screen_dimensions)

        self.bullet_list.append(bullet)

        """Wygeneruj pocisk na granicy sprite'a gracza, a następnie nadaj mu prędkość """
        start_x = self.player_sprite.center_x
        start_y = self.player_sprite.center_y
        bullet.position = self.player_sprite.position
        x_diff = x - start_x
        y_diff = y - start_y
        angle = np.arctan2(y_diff, x_diff)
        size=self.player_sprite.width/2
        bullet.center_x += size * np.cos(angle)
        bullet.center_y += size * np.sin(angle)
        bullet.angle = np.degrees(angle)
        self.physics_engine.add_sprite(bullet,
                                        mass=BULLET_MASS,
                                        damping=1.0,
                                        friction=1.0,
                                        collision_type="bullet",
                                        max_velocity=BULLET_SPEED)
        force = (BULLET_MOVE_FORCE, 0)
        self.physics_engine.apply_force(bullet, force)



    def on_update(self, delta_time):

        """Ta sekcja odpowiada za poruszanię się. Pętla sprawia, że częściej sprawdzamy kolizje"""
        for step in range(PHYSICS_STEPS-1):
            if self.player_sprite.change_x or self.player_sprite.change_y:

                force = (self.player_sprite.change_x *PLAYER_MOVE_FORCE,  self.player_sprite.change_y*PLAYER_MOVE_FORCE)
                self.physics_engine.apply_force(self.player_sprite, force)

                self.physics_engine.set_friction(self.player_sprite, 0)
            else:

                self.physics_engine.set_friction(self.player_sprite, 1.0)
            self.physics_engine.step(delta_time=DELTA_TIME/PHYSICS_STEPS, resync_sprites=False)

        if self.player_sprite.change_x or self.player_sprite.change_y:

            force = (self.player_sprite.change_x *PLAYER_MOVE_FORCE,  self.player_sprite.change_y*PLAYER_MOVE_FORCE)
            self.physics_engine.apply_force(self.player_sprite, force)

            self.physics_engine.set_friction(self.player_sprite, 0)
        else:

            self.physics_engine.set_friction(self.player_sprite, 1.0)
        self.physics_engine.step(delta_time=DELTA_TIME/PHYSICS_STEPS, resync_sprites=True)
        
        """Obrót sprite'a gracza. """
        x,y=self.player_sprite.position
        angle=np.degrees( np.arctan2(self.mouse_y-y, self.mouse_x-x ) )
        self.player_sprite.turn_left(angle)


    


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()