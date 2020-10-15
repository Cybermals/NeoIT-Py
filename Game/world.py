"""New Impressive Title - World API"""

import os
import xml.etree.ElementTree as etree

from kivy.logger import Logger, LOG_LEVELS
from panda3d.core import GeoMipTerrain


#Classes
#==============================================================================
class WorldManager(object):
    """A world manager for heightmapped worlds stored as XML."""
    def __init__(self):
        """Setup this world manager."""
        Logger.info("Initializing world manager...")

        self.terrain = None

        Logger.info("World manager initialized.")

    def load_map(self, map):
        """Load a map."""
        #Locate the XML file for the map
        Logger.info("Loading map '{}'...".format(map))
        map_file = os.path.join(map, os.path.basename(map) + ".xml")

        if not os.path.exists(map_file):
            Logger.error("Failed to load map file '{}'.".format(map_file))
            return False

        #Load the map XML file
        xml = etree.parse(map_file)
        root = xml.getroot()

        #Map loaded
        Logger.info("Map '{}' loaded.".format(map))
        return True

    def unload_map(self):
        """Unload the current map."""
