"""New Impressive Title - GUI API"""

import os

from direct.showbase.ShowBase import ShowBase
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.factory import Factory
from kivy.graphics import Color, Rectangle
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import NoTransition, ScreenManager, SlideTransition
from kivy.uix.widget import Widget
from panda3d_kivy.app import App


#Classes
#===============================================================================
class AnimatedLogo(Widget):
    """An animated logo for the logo screen."""
    def __init__(self, **kwargs):
        """Setup this animated logo."""
        super(AnimatedLogo, self).__init__(**kwargs)

        with self.canvas:
            Color(1, 1, 1, 1)
            self.bg = Rectangle(
                pos = self.pos,
                size = self.size, 
                source = "./data/textures/GUI/logo.jpg"
                )

            texture = CoreImage("./data/textures/GUI/logowaves.png").texture
            texture.wrap = "repeat"
            self.fg = Rectangle(
                pos = self.pos,
                size = self.size,
                texture = texture
                )

        self.bind(pos = self.update, size = self.update)
        Clock.schedule_interval(self.update_anim, 1 / 60)

    def update(self, sender, value):
        """Update the content when the size or position changes."""
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.fg.pos = self.pos
        self.fg.size = self.size

    def update_anim(self, dt):
        """Update the animation for this logo."""
        t = Clock.get_boottime() * .1
        self.fg.tex_coords = (
            -t, t + 1,
            -t + 1, t + 1,
            -t + 1, t,
            -t, t
        )


class GameFrame(BoxLayout):
    """A frame that has a background"""
    bg_source = StringProperty(None)

    def __init__(self, **kwargs):
        """Setup this frame."""
        if "bg_source" in kwargs:
            self.bg_source = kwargs["bg_source"]
            del kwargs["bg_source"]

        super(GameFrame, self).__init__(**kwargs)
        print("bg_source = {}".format(self.bg_source))

        with self.canvas:
            Color(1, 1, 1, 1)
            self.bg = Rectangle(
                pos = self.pos,
                size = self.size,
                source = self.bg_source
                )

        self.bind(
            pos = self.update, 
            size = self.update, 
            bg_source = self.update_bg_source
            )

    def update(self, sender, value):
        """Update the content when the position or size changes."""
        self.bg.pos = self.pos
        self.bg.size = self.size

    def update_bg_source(self, sender, value):
        """Update the bg image."""
        self.bg.source = value


class GameButton(ButtonBehavior, Label):
    """A special button that uses a custom set of images."""
    def __init__(self, **kwargs):
        """Setup this button."""
        super(GameButton, self).__init__(**kwargs)
        self.images = [
            "./data/textures/GUI/buttonUp.png",
            "./data/textures/GUI/buttonOver.png",
            "./data/textures/GUI/buttonDown.png"
        ]

        with self.canvas:
            Color(1, 1, 1, 1)
            self.bg = Rectangle(pos = self.pos, size = self.size, 
                source = self.images[0])

        self.bind(
            pos = self.update, 
            size = self.update, 
            state = self.on_state
            )

    def update(self, sender, value):
        """Update the content when the position or size changes."""
        self.bg.pos = self.pos
        self.bg.size = self.size

    def on_state(self, sender, value):
        """Update button appearance based on current state."""
        if value == "normal":
            self.bg.source = self.images[0]

        else:
            self.bg.source = self.images[2]


class GameListButton(ButtonBehavior, Label):
    """A game button designed for use in RecycleView widgets."""
    def __init__(self, **kwargs):
        """Setup this button."""
        super(GameListButton, self).__init__(**kwargs)
        self.images = [
            "./data/textures/GUI/buttonUp.png",
            "./data/textures/GUI/buttonOver.png",
            "./data/textures/GUI/buttonDown.png"
        ]

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg = Rectangle(pos = self.pos, size = self.size, 
                source = self.images[0])

        self.bind(
            pos = self.update, 
            size = self.update, 
            state = self.on_state
            )

    def update(self, sender, value):
        """Update the content when the position or size changes."""
        self.bg.pos = self.pos
        self.bg.size = self.size

    def on_state(self, sender, value):
        """Update button appearance based on current state."""
        if value == "normal":
            self.bg.source = self.images[0]

        else:
            self.bg.source = self.images[2]


class HPBar(Widget):
    """An HP bar."""
    hp = NumericProperty(100)
    max_hp = NumericProperty(100)

    def __init__(self, **kwargs):
        """Setup this HP bar."""
        super(HPBar, self).__init__(**kwargs)

        with self.canvas:
            Color(1, 1, 1, .5)
            self.bg = Rectangle(pos = self.pos, size = self.size)
            Color(1, 1, 1, 1)
            self.fg = Rectangle(
                pos = self.pos, 
                size = self.size, 
                source = "./data/textures/GUI/hpbar.png"
                )

        self.bind(
            pos = self.update, 
            size = self.update, 
            hp = self.update, 
            max_hp = self.update
            )

    def update(self, *args):
        """Update this widget when its position or size changes."""
        self.bg.pos = self.pos
        self.bg.size = self.size

        self.fg.pos = self.pos
        ratio = self.hp / self.max_hp
        self.fg.size = (self.width * abs(ratio), self.height)

        if ratio < 0:
            self.fg.source = "./data/textures/GUI/woundbar.png"

        else:
            self.fg.source = "./data/textures/GUI/hpbar.png"


class MainScreen(ScreenManager):
    """The main screen of this app. It manages all the other screens."""


class GUI(App):
    """The GUI component for this app."""
    def build(self):
        """Build the GUI for this app."""
        self.root = MainScreen()
        base.task_mgr.add(base.run_logic)
        return self.root

    def switch_to_screen(self, name, transition):
        """Switch to the given screen."""
        self.root.transition = transition
        self.root.current = name

    def start_title_anim(self):
        """Start the title animation."""
        anim = Animation(
            pos_hint = {"x": .125, "y": .65}, 
            size_hint = (.75, .2)
            )
        anim.bind(on_complete = self.stop_anims)
        anim.start(self.root.title)

    def stop_anims(self, sender, widget):
        """Stop all animations."""
        Animation.stop_all(widget)

    def get_selected_campaign(self):
        """Return the currently selected campaign."""
        if len(self.root.campaign_list.selection):
            return self.root.campaign_list.selection[0]

        else:
            return None

    def show_chat_box(self, show):
        """Show or hide the chat box."""
        if show:
            self.root.chat_box.transition = SlideTransition(direction = "up")
            self.root.chat_box.current = "Show"

        else:
            self.root.chat_box.transition = SlideTransition(direction = "down")
            self.root.chat_box.current = "Hide"

    def switch_chat_mode(self):
        """Switch to the next chat mode."""
        next = self.root.chat_text.next()
        self.root.chat_mode.text = next
        self.root.chat_text.current = next

    def show_multiplayer_hud(self, show):
        """Show or hide the multiplayer HUD."""
        self.root.multiplayer_hud.transition = NoTransition()

        if show:
            self.root.multiplayer_hud.current = "Show"

        else:
            self.root.multiplayer_hud.current = "Hide"


#Register custom widget classes
#===============================================================================
Factory.register("AnimatedLogo", AnimatedLogo)
Factory.register("GameFrame", GameFrame)
Factory.register("GameButton", GameButton)
Factory.register("HPBar", HPBar)
