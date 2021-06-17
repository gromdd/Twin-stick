import arcade
import os
import pathlib as p
from arcade.arcade_types import Color
import pymunk
import numpy as np



from backend import *
from weapons import *
from enemies import *
from levels import *


LOCAL_DIR = p.Path(os.getcwd())

image_source = p.Path("place_holder")

number_keys = {arcade.key.KEY_0, arcade.key.KEY_1, arcade.key.KEY_2, arcade.key.KEY_3, arcade.key.KEY_4,
               arcade.key.KEY_5, arcade.key.KEY_6, arcade.key.KEY_7, arcade.key.KEY_8, arcade.key.KEY_9}


class MyGame(arcade.View):

    def __init__(self, level, game_over_screen, data):
        """Inicjalizacja zmiennych"""


        super().__init__()
        # self.set_exclusive_mouse()

        arcade.set_background_color(BACKGROUND_COLOR)
        self.player_sprite = None
        self.player_list = None
        self.weapon_silhoutte_list = None

        self.bullet_list = None
        self.bullet_sprite = None
        self.enemy_list = None
        self.modifier_list = None

        self.space = pymunk.Space()
        self.space.iterations = 35
        self.space.gravity = (0.0, 0.0)
        self.confinement_box = None

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.mouse_pressed = False

        self.physics_engine = None
        self.mouse_x = 0
        self.mouse_y = 0

        self.screen_dimensions = (SCREEN_WIDTH, SCREEN_HEIGHT)

        self.level=level()

        self.enemies_max = -1
        self.enemies_left = -1

        self.game_over_screen=game_over_screen
        self.data=data
        

    def setup(self):

        self.physics_engine = physics.PymunkPhysicsEngine()
        """ Bariery, które utrzymują gracza na planszy"""
        box_width = BOX_WIDTH
        self.confinement_box = arcade.SpriteList()
        self.confinement_box.append(arcade.SpriteSolidColor(
            BOX_WIDTH, self.screen_dimensions[1], "black"))
        self.confinement_box[-1].center_x = self.screen_dimensions[0]+BOX_WIDTH/2
        self.confinement_box[-1].center_y = self.screen_dimensions[1]/2

        self.confinement_box.append(arcade.SpriteSolidColor(
            BOX_WIDTH, self.screen_dimensions[1], "black"))
        self.confinement_box[-1].center_x = -BOX_WIDTH/2
        self.confinement_box[-1].center_y = self.screen_dimensions[1]/2

        self.confinement_box.append(arcade.SpriteSolidColor(
            self.screen_dimensions[0], BOX_WIDTH, "black"))
        self.confinement_box[-1].center_x = self.screen_dimensions[0]/2
        self.confinement_box[-1].center_y = self.screen_dimensions[1]+BOX_WIDTH/2

        self.confinement_box.append(arcade.SpriteSolidColor(
            self.screen_dimensions[0], BOX_WIDTH, "black"))
        self.confinement_box[-1].center_x = self.screen_dimensions[0]/2
        self.confinement_box[-1].center_y = -BOX_WIDTH/2

        """Dodaj obiekty reprezentowane przez sprite'y do silnika fizycznego."""
        self.physics_engine.add_sprite_list(self.confinement_box,
                                            collision_type=collision_group.wall,
                                            body_type=arcade.PymunkPhysicsEngine.STATIC)

        self.player_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.weapon_silhoutte_list = arcade.SpriteList()
        self.modifier_list = arcade.SpriteList()

        self.player_sprite = player(self,
                                    weapons=None,
                                    path=image_source/p.Path("player.png"),
                                    friction=PLAYER_FRICTION,
                                    mass=PLAYER_MASS,
                                    max_velocity=PLAYER_MAX_SPEED,
                                    damping=PLAYER_DAMPING,
                                    velocity=PLAYER_MOVEMENT_SPEED,
                                    move_force=PLAYER_MOVE_FORCE,
                                    center_x=64,
                                    center_y=128
                                    )

        #self.bullet_sprite = arcade.Sprite( image_source/p.Path("projectile.png"), CHARACTER_SCALING)


        self.physics_engine.add_collision_handler(
            collision_group.bullet, collision_group.wall, begin_handler=wall_hit_handler)
        self.physics_engine.add_collision_handler(
            collision_group.bullet, collision_group.enemy, pre_handler=enemy_hit_handler)

        self.physics_engine.add_collision_handler(
            collision_group.enemy_bullet, collision_group.wall, begin_handler=wall_hit_handler)
        self.physics_engine.add_collision_handler(
            collision_group.enemy, collision_group.enemy_bullet, begin_handler=enemy_enemy_bullet_handler)
        self.physics_engine.add_collision_handler(
            collision_group.player, collision_group.enemy_bullet, begin_handler=player_enemy_bullet_handler)

        self.physics_engine.add_collision_handler(
            collision_group.enemy_bullet, collision_group.enemy_bullet, begin_handler=bullet_bullet_handler)
        self.physics_engine.add_collision_handler(
            collision_group.bullet, collision_group.enemy_bullet, begin_handler=bullet_bullet_handler)
        self.physics_engine.add_collision_handler(
            collision_group.bullet, collision_group.bullet, begin_handler=bullet_bullet_handler)

        self.physics_engine.add_collision_handler(
            collision_group.enemy, collision_group.wall, begin_handler=enemy_wall_handler)
        self.physics_engine.add_collision_handler(
            collision_group.enemy, collision_group.player, begin_handler=enemy_player_handler)


        self.physics_engine.add_collision_handler(
            collision_group.modifier, collision_group.enemy, begin_handler=modifier_enemy_handler)
        self.physics_engine.add_collision_handler(
            collision_group.modifier, collision_group.player, begin_handler=modifier_player_handler)
        self.physics_engine.add_collision_handler(
            collision_group.modifier, collision_group.enemy_bullet, begin_handler=modifier_enemy_bullet_handler)
        self.physics_engine.add_collision_handler(
            collision_group.modifier, collision_group.bullet, begin_handler=modifier_bullet_handler)

        self.points = 0
        self.player_sprite.weapons = weapon_holder(
            pistol(self.player_sprite, self),
            ak47(self.player_sprite, self),
            shotgun(self.player_sprite, self)
        )


        self.weapon_hud_width = (self.screen_dimensions[0]-HUD_WIDTH)/2
        self.weapon_hud_height = HUD_HEIGHT*4/5

        self.weapon_hud_offset = self.weapon_hud_width-self.player_sprite.weapons.size() * \
            self.weapon_hud_height/(5/4)

        for i, weapon in enumerate(self.player_sprite.weapons):
            weapon.weapon_silhoutte.center_x=self.weapon_hud_width/2 +\
                (i-self.player_sprite.weapons.size()+2)* \
                (self.weapon_hud_width-self.weapon_hud_offset)/self.player_sprite.weapons.size()


            weapon.weapon_silhoutte.center_y=self.weapon_hud_height*(4/5)/2 +self.weapon_hud_height/5
            weapon.weapon_silhoutte.scale=self.weapon_hud_height*(4/5)/weapon.weapon_silhoutte.width*weapon.weapon_silhoutte.scale
            self.weapon_silhoutte_list.append(weapon.weapon_silhoutte)

        self.level.setup(self)
        self.enemies_max = self.level.number_of_enemies
        self.enemies_left = self.enemies_max
        self.level.begin()
        


    def on_show_view(self):
        """ Called once when view is activated. """
        self.setup()
        arcade.set_background_color(BACKGROUND_COLOR)


    def on_draw(self):

        arcade.start_render()
        self.player_list.draw()
        self.bullet_list.draw()
        self.enemy_list.draw()
        self.modifier_list.draw()
        # self.confinement_box.draw()

        arcade.draw_rectangle_filled(
            self.screen_dimensions[0]/2, HUD_HEIGHT/2, HUD_WIDTH, HUD_HEIGHT, GUI_COLOR)
        arcade.draw_text("Score\n{}".format(self.points),
                         self.screen_dimensions[0]/2-1/3*HUD_WIDTH, HUD_HEIGHT/2, FONT_COLOR, AUX_FONT_SIZE, align="center",
                         anchor_x="center", anchor_y="center")

        arcade.draw_text("Health\n{}/{}".format(self.player_sprite.current_health, self.player_sprite.health),
                         self.screen_dimensions[0]/2, HUD_HEIGHT/2, FONT_COLOR, AUX_FONT_SIZE, align="center",
                         anchor_x="center", anchor_y="center")

        arcade.draw_text("Enemies\n{}/{}".format(self.enemies_left, self.enemies_max),
                         self.screen_dimensions[0]/2+1/3*HUD_WIDTH, HUD_HEIGHT/2, FONT_COLOR, AUX_FONT_SIZE, align="center",
                         anchor_x="center", anchor_y="center")


        tmp_y= self.weapon_hud_height/5/2
        for i, weapon in enumerate(self.player_sprite.weapons):
            tmp_x=self.weapon_hud_width/2 +\
                (i-self.player_sprite.weapons.size()+2)* \
                (self.weapon_hud_width-self.weapon_hud_offset)/self.player_sprite.weapons.size()

            arcade.draw_rectangle_filled(
                tmp_x,
                self.weapon_hud_height /2,
                (self.weapon_hud_width-self.weapon_hud_offset)/self.player_sprite.weapons.size(),
                self.weapon_hud_height,
                ( GUI_COLOR if i != self.player_sprite.weapons.weapon_index else GUI_GREEN)-\
                    GUI_ALPHA*weapon.to_reload_time/weapon.reload_time
                )
            
            arcade.draw_text("{}/{}".format(weapon.get_current_clip_size() or "-",
                weapon.get_clip_size()),
                tmp_x, tmp_y, (0, 0, 0, 196), 16, align="center",
                anchor_x="center", anchor_y="center")


        self.weapon_silhoutte_list.draw()

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

        elif key in number_keys:
            self.player_sprite.weapons.set_weapon(key-48)

        elif key == arcade.key.ESCAPE:
            """Wyjście z gry"""
            arcade.close_window()

        elif key == arcade.key.R:
            self.player_sprite.weapons.reload()

    def on_key_release(self, key, modifiers):

        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y -= PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y -= -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x -= -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x -= PLAYER_MOVEMENT_SPEED

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.mouse_pressed = True
            self.player_sprite.weapons.shoot(x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.mouse_pressed = False

    def on_update(self, delta_time):

        for enemy in self.enemy_list:
            enemy.controller()

        if self.mouse_pressed:
            self.player_sprite.weapons.shoot(self.mouse_x, self.mouse_y)

        self.player_sprite.controller()

        """Ta sekcja odpowiada za poruszanię się. Pętla sprawia, że częściej sprawdzamy kolizje"""
        for step in range(PHYSICS_STEPS-1):
            movement_function(self.player_sprite)
            for i, enemy in enumerate(self.enemy_list):
                movement_function(enemy)

            self.physics_engine.step(
                delta_time=DELTA_TIME/PHYSICS_STEPS, resync_sprites=False)

        movement_function(self.player_sprite)
        for i, enemy in enumerate(self.enemy_list):
            try:
                movement_function(enemy)
            except Exception:
                pass
        self.physics_engine.step(
            delta_time=DELTA_TIME/PHYSICS_STEPS, resync_sprites=True)

        """Obrót sprite'a gracza. """
        self.player_sprite.rotate(self.mouse_x, self.mouse_y)
        for i, enemy in enumerate(self.enemy_list):
            try:
                enemy.rotate()
            except Exception:
                pass

        """ ile czasu zostało do przeładowania"""
        for weapon in self.player_sprite.weapons:
            weapon.to_reload_time = max(0, weapon.to_reload_time-delta_time)


    def on_enemy_death(self,points):
        self.points += points
        if self.enemies_left == 1:
            self.game_over_screen.header= "Level Cleared!"
            self.end()
        self.enemies_left-=1

    def end(self):
        self.game_over_screen.score=self.points
        self.window.show_view(self.game_over_screen)
        try:
            self.game_over_screen.highscore=self.data["highscores"][self.level.name]
            if self.data["highscores"][self.level.name]<self.points:
                self.data["highscores"][self.level.name]=self.points
        except:
            self.game_over_screen.highscore=0
            self.data["highscores"][self.level.name]=self.points
        self.__del__()
        
    def __del__(self):
        print("game del")
        for sprite in self.enemy_list:
            sprite.kill()
        for sprite in self.bullet_list:
            sprite.kill()
        for sprite in self.modifier_list:
            sprite.kill()
        self.player_sprite.kill()
        self.level.__del__()




def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
