"""New Impressive Title - App API"""

from queue import Queue

from direct.showbase.ShowBase import ShowBase
from direct.task.Task import Task
from kivy.uix.screenmanager import FadeTransition, SlideTransition
from panda3d.core import (
    AmbientLight,
    CollisionHandlerEvent,
    CollisionTraverser,
    DirectionalLight,
    load_prc_file_data,
    PStatClient,
    Vec3,
    Vec4,
    WindowProperties
    )
load_prc_file_data("", "stencil-bits 8")

from camera import CameraManager, CAM_MODE_FREE
from gui import GUI
from world import WorldManager


#Constants
#===============================================================================
APP_STATE_LOGO = 0
APP_STATE_TITLE = 1
APP_STATE_CAMPAIGN_SELECT = 2
APP_STATE_CAMPAIGN = 3
APP_STATE_LOGIN = 4
APP_STATE_NEW_ACCOUNT = 5
APP_STATE_CHANGE_PASSWORD = 6


#Classes
#===============================================================================
class NeoITPyApp(ShowBase):
    """The NeoITPy app."""
    def __init__(self):
        """Setup this app."""
        ShowBase.__init__(self)

        #Setup window
        wnd_props = WindowProperties()
        wnd_props.set_title("Neo Impressive Title")
        wnd_props.set_origin(0, 0)
        wnd_props.set_size(1280, 960)
        self.win.request_properties(wnd_props)

        self.set_background_color(0, .5, 1, 1)

        #Init GUI sub-system
        self.gui = GUI(self)
        self.gui.run()

        #Init app state
        self.state = APP_STATE_LOGO
        self.logo_delay = 600

        #Start title music
        self.title_music = loader.loadMusic("./data/sounds/title.ogg")
        self.title_music.set_loop(True)
        self.title_music.play()

        #Setup collision detection
        self.cTrav = CollisionTraverser()

        self.portal_handler = CollisionHandlerEvent()
        self.portal_handler.add_in_pattern("%fn-entered-%in")

        #Init other sub-systems
        self.cam_mgr = CameraManager()
        self.world_mgr = WorldManager()

        #Setup lighting
        self.ambient = AmbientLight("Ambient Light")
        self.ambient.set_color(Vec4(.2, .2, .2, 1))
        self.ambient_np = self.render.attach_new_node(self.ambient)
        self.render.set_light(self.ambient_np)

        self.sun = DirectionalLight("Sun")
        self.sun_np = self.render.attach_new_node(self.sun)
        self.sun_np.set_p(-135)
        self.render.set_light(self.sun_np)

        #Setup auto-shaders
        self.render.set_shader_auto()

        #Debug stats
        #self.messenger.toggle_verbose()
        PStatClient.connect()

    def new_game(self):
        """Start a new game."""
        self.gui.switch_to_screen("CampaignSelectScreen", 
            SlideTransition(direction = "left"))
        self.state = APP_STATE_CAMPAIGN_SELECT

    def multiplayer(self):
        """Start multiplayer mode."""
        self.gui.switch_to_screen("LoginScreen",
            SlideTransition(direction = "left"))
        self.state = APP_STATE_LOGIN

    def quit(self):
        """Close the app."""
        self.user_exit()

    def start_campaign(self, name):
        """Start the given campaign."""
        print("Starting campaign '{}'...".format(name))
        self.gui.show_multiplayer_hud(False)
        self.gui.show_target_info(False)
        self.gui.switch_to_screen("HUD", FadeTransition())
        self.cam_mgr.change_mode(CAM_MODE_FREE)
        self.world_mgr.load_map("./data/maps/Default")

    def leave_campaign_select(self):
        """Leave the campaign select screen and return to the title screen."""
        self.gui.switch_to_screen("TitleScreen", 
            SlideTransition(direction = "right"))
        self.state = APP_STATE_TITLE

    def login(self):
        """Begin login process."""
        print("Logging in...")

    def new_account(self):
        """Enter the account creation screen."""
        self.gui.switch_to_screen("NewAccountScreen",
            SlideTransition(direction = "left"))
        self.state = APP_STATE_NEW_ACCOUNT

    def change_password(self):
        """Enter the password change screen."""
        self.gui.switch_to_screen("ChangePasswordScreen",
            SlideTransition(direction = "left"))
        self.state = APP_STATE_CHANGE_PASSWORD

    def leave_login_screen(self):
        """Leave the login screen and return to the title screen."""
        self.gui.switch_to_screen("TitleScreen",
            SlideTransition(direction = "right"))
        self.state = APP_STATE_TITLE

    def create_new_account(self):
        """Create a new account."""
        print("Creating new account...")

    def leave_new_account_screen(self):
        """Leave the new account screen and return to the login screen."""
        self.gui.switch_to_screen("LoginScreen",
            SlideTransition(direction = "right"))
        self.state = APP_STATE_LOGIN

    def do_password_change(self):
        """Change the user's current password."""
        print("Changing password...")

    def leave_change_password_screen(self):
        """Leave the change password screen and return to the login screen."""
        self.gui.switch_to_screen("LoginScreen",
            SlideTransition(direction = "right"))
        self.state = APP_STATE_LOGIN

    def run_logic(self, task):
        """Run the game logic for each frame."""
        #Update logo screen
        if self.state == APP_STATE_LOGO:
            #Is the logo delay over?
            if self.logo_delay == 0:
                self.gui.switch_to_screen("TitleScreen", FadeTransition())
                self.gui.start_title_anim()
                self.state = APP_STATE_TITLE

            #If not, update the delay timer
            else:
                self.logo_delay -= 1

        #Update title screen
        elif self.state == APP_STATE_TITLE:
            pass

        #Update campaign select screen
        elif self.state == APP_STATE_CAMPAIGN_SELECT:
            pass

        #Update login screen
        elif self.state == APP_STATE_LOGIN:
            pass

        #Update campaign mode screen
        elif self.state == APP_STATE_CAMPAIGN:
            pass

        #Update new account screen
        elif self.state == APP_STATE_NEW_ACCOUNT:
            pass

        #Update change password screen
        elif self.state == APP_STATE_CHANGE_PASSWORD:
            pass

        #This task continues infinitely
        return Task.cont

    user_exit = ShowBase.userExit
