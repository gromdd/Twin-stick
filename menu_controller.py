import arcade
import os
import pathlib as p
from arcade.arcade_types import Color
import pymunk
import numpy as np
import pickle


import arcade.gui
from arcade.gui import UIManager


from levels import *
from prototyp import *


SCORE_TEXT_GAP_HEIGHT= SCREEN_HEIGHT/20

class test_view(arcade.View):
    def __init__(self):
        """ This is run once when we switch to this view """
        super().__init__()


    def setup(self):
        pass

    def on_show(self):
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)

    def on_draw(self):
        """ Draw this view """
        arcade.start_render()
        arcade.draw_text("Kraaaaaaa",
                         SCREEN_WIDTH/2, SCREEN_HEIGHT/2, (0, 0, 0, 196), 48, align="center",
                         anchor_x="center", anchor_y="center")


class Game_over_view(arcade.View):

    def __init__(self, score=0, highscore=0):
        """ This is run once when we switch to this view """
        super().__init__()
        self.score = score
        self.highscore = highscore
        self.header="Game Over"
    def setup(self):
        pass

    def on_show(self):
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)

    def on_draw(self):
        """ Draw this view """
        arcade.start_render()
        text_sprite=arcade.draw_text("Score: {}".format(self.score), SCREEN_WIDTH / 2, SCREEN_HEIGHT/2,
                                       (0, 0, 0, 196), 128, align="center", anchor_x="center", anchor_y="top")
        arcade.draw_text(self.header,
                                    SCREEN_WIDTH/2, text_sprite.top+SCORE_TEXT_GAP_HEIGHT, (0, 0, 0, 196), 196, align="center",
                                    anchor_x="center", anchor_y="bottom")

        

        text_sprite=arcade.draw_text("Highscore: {}".format(self.highscore), SCREEN_WIDTH / 2, text_sprite.bottom-SCORE_TEXT_GAP_HEIGHT,
                                       (0, 0, 0, 196), 128, align="center", anchor_x="center", anchor_y="top")
    def on_hide_view(self):
        self.score = 0
        self.highscore = 0
        self.header="Game Over"
        return super().on_hide_view()



class new_game_button(arcade.gui.UIFlatButton):

    def __init__(self, *args,**kwargs):
        super().__init__( *args,**kwargs)
        self.set_style_attrs(font_size=48, vmargin=0)


    def on_click(self):
        #arcade.get_window().show_view(MyGame(level_list[0], end_screen))
        arcade.get_window().show_view(level_selection_screen)

class highscores_button(arcade.gui.UIFlatButton):

    def __init__(self, *args,**kwargs):
        super().__init__( *args,**kwargs)
        self.set_style_attrs(font_size=48, vmargin=0)

    def on_click(self):
        arcade.get_window().show_view(highscores_screen)



class level_selection_button(arcade.gui.UIFlatButton):
    def __init__(self, level, *args,**kwargs):
        super().__init__(level.name, *args,**kwargs)
        self.set_style_attrs(font_size=48, vmargin=0)
        self.level=level

    def on_click(self):
        arcade.get_window().show_view(MyGame(self.level, end_screen, data))

class Main_menu(arcade.View):
    def __init__(self):
        super().__init__()

        self.ui_manager = UIManager()



    def on_draw(self):
        """ Draw this view. GUI elements are automatically drawn. """
        arcade.start_render()


    def on_show_view(self):
        """ Called once when view is activated. """
        self.setup()
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)

    def on_hide_view(self):
       self.ui_manager.unregister_handlers()
       #self.ui_manager.purge_ui_elements()

    def setup(self):
        """ Set up this view. """
        self.ui_manager.purge_ui_elements()
        button = new_game_button(
            'New Game',
            center_x=SCREEN_WIDTH/2,
            center_y=SCREEN_HEIGHT/2,
            width=SCREEN_WIDTH//3,
            height=SCREEN_HEIGHT//8,
            )
        
        self.ui_manager.add_ui_element(button)



        text=arcade.gui.UILabel(
            'Twin Stick',
            center_x=SCREEN_WIDTH/2,
            center_y=button.top+SCORE_TEXT_GAP_HEIGHT, 
        )
        text.set_style_attrs(font_size=196, font_color=(0, 0, 0, 196), font_color_hover=(0, 0, 0, 196), font_color_press=(0, 0, 0, 196))
        text.center_y+=text.height/2
        self.ui_manager.add_ui_element(text)


        button = highscores_button(
            'Highscores',
            center_x=SCREEN_WIDTH/2,
            center_y=button.bottom -SCREEN_HEIGHT//8,
            width=SCREEN_WIDTH//3,
            height=SCREEN_HEIGHT//8,
            )

        self.ui_manager.add_ui_element(button)



class level_selection(arcade.View):
    def __init__(self):
        super().__init__()

        self.ui_manager = UIManager()



    def on_draw(self):
        """ Draw this view. GUI elements are automatically drawn. """
        arcade.start_render()


    def on_show_view(self):
        """ Called once when view is activated. """
        self.setup()
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)

    def on_hide_view(self):
       self.ui_manager.unregister_handlers()
       #self.ui_manager.purge_ui_elements()

    def setup(self):
        """ Set up this view. """
        self.ui_manager.purge_ui_elements()
        for i,level in enumerate(level_list):
            
            button = level_selection_button(
                level,
                center_x=SCREEN_WIDTH/2,
                center_y=SCREEN_HEIGHT/2-i*SCREEN_HEIGHT*3//(8*2),
                width=SCREEN_WIDTH//3,
                height=SCREEN_HEIGHT//8,
                )
            
            self.ui_manager.add_ui_element(button)



        text=arcade.gui.UILabel(
            'Level Selection',
            center_x=SCREEN_WIDTH/2,
            center_y=SCREEN_HEIGHT/2+SCREEN_HEIGHT*3//(8*2)+SCORE_TEXT_GAP_HEIGHT, 
        )
        text.set_style_attrs(font_size=196, font_color=(0, 0, 0, 196), font_color_hover=(0, 0, 0, 196), font_color_press=(0, 0, 0, 196))
        text.center_y+=text.height/2
        self.ui_manager.add_ui_element(text)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.get_window().show_view(menu_screen)


        

class highscores(arcade.View):
    def __init__(self):
        super().__init__()

        self.ui_manager = UIManager()



    def on_draw(self):
        """ Draw this view. GUI elements are automatically drawn. """
        arcade.start_render()


    def on_show_view(self):
        """ Called once when view is activated. """
        self.setup()
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)

    def on_hide_view(self):
       self.ui_manager.unregister_handlers()
       #self.ui_manager.purge_ui_elements()

    def setup(self):
        """ Set up this view. """
        self.ui_manager.purge_ui_elements()
        for i, (key, value) in enumerate(data["highscores"].items()):
            print(key, value)
            
            text = arcade.gui.UILabel(
                "{}: {}".format(key, value),
                center_x=SCREEN_WIDTH/2,
                center_y=SCREEN_HEIGHT/2-i*SCREEN_HEIGHT*3//(8*2),
                )
            text.set_style_attrs(font_size=128, font_color=(0, 0, 0, 196),
                font_color_hover=(0, 0, 0, 196), font_color_press=(0, 0, 0, 196))
            
            self.ui_manager.add_ui_element(text)



        text=arcade.gui.UILabel(
            'Highscores',
            center_x=SCREEN_WIDTH/2,
            center_y=SCREEN_HEIGHT/2+SCREEN_HEIGHT*3//(8*2)+SCORE_TEXT_GAP_HEIGHT, 
        )
        text.set_style_attrs(font_size=196, font_color=(0, 0, 0, 196), font_color_hover=(0, 0, 0, 196), font_color_press=(0, 0, 0, 196))
        text.center_y+=text.height/2
        self.ui_manager.add_ui_element(text)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.get_window().show_view(menu_screen)
            






if __name__ == "__main__":
    with open("data.txt", "rb") as file:
        try:
            data=pickle.load(file)
        except:
            data={
                "highscores" : dict()
            }

    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=False)
    window.set_update_rate(DELTA_TIME)

    menu_screen = Main_menu()
    end_screen = Game_over_view()
    level_selection_screen = level_selection()
    highscores_screen = highscores()


    window.show_view(menu_screen)
    arcade.run()
    with open("data.txt", "wb") as file:
        pickle.dump(data, file)
