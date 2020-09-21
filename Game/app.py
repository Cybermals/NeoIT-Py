"""New Impressive Title - App API"""

from queue import Queue

from direct.showbase.ShowBase import ShowBase
from direct.task.Task import Task
from kivy.uix.screenmanager import FadeTransition, SlideTransition
from panda3d.core import WindowProperties

from gui import GUI


#Constants
#===============================================================================
APP_STATE_LOGO = 0
APP_STATE_TITLE = 1
APP_STATE_CAMPAIGN_SELECT = 2
APP_STATE_CAMPAIGN = 3
APP_STATE_LOGIN = 4
APP_STATE_NEW_ACCOUNT = 5


#Classes
#===============================================================================
class NeoITPyApp(ShowBase):
    """The NeoITPy app."""
    def __init__(self):
        """Setup this app."""
        ShowBase.__init__(self)

        #Set window size
        wnd_props = WindowProperties()
        wnd_props.set_title("Neo Impressive Title")
        wnd_props.set_origin(0, 0)
        wnd_props.set_size(1280, 960)
        self.win.request_properties(wnd_props)

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
        print("Change password...")

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

        #Update campaign mode screen
        elif self.state == APP_STATE_CAMPAIGN:
            pass

        #Update new account screen
        elif self.state == APP_STATE_NEW_ACCOUNT:
            pass

        #This task continues infinitely
        return Task.cont

    user_exit = ShowBase.userExit
