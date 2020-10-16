"""New Impressive Title - World API"""

import os
import xml.etree.ElementTree as etree

from kivy.logger import Logger, LOG_LEVELS
from panda3d.core import GeoMipTerrain, Texture, TextureStage

from utils import parse_vec


#Classes
#==============================================================================
class WorldManager(object):
    """A world manager for heightmapped worlds stored as XML."""
    def __init__(self):
        """Setup this world manager."""
        Logger.info("Initializing world manager...")
        Logger.info("World manager initialized.")

    def load_map(self, map):
        """Load a map."""
        #Unload the current map first
        self.unload_map()

        #Locate the XML file for the map
        Logger.info("Loading map '{}'...".format(map))
        map_file = os.path.join(map, os.path.basename(map) + ".xml")

        if not os.path.exists(map_file):
            Logger.error("Failed to load map file '{}'.".format(map_file))
            return False

        #Load the map XML file
        xml = etree.parse(map_file)
        root = xml.getroot()

        for child in root:
            #Terrain?
            if child.tag == "terrain":
                #Validate terrain
                if not ("size" in child.attrib and "spawnpos" in child.attrib
                    and "heightmap" in child.attrib):
                    Logger.error("Terrain section must define 'size', 'spawnpos', and 'heightmap'.")
                    return False

                #Load terrain
                self.size = parse_vec(child.attrib["size"], 2)
                self.spawnpos = parse_vec(child.attrib["spawnpos"], 2)
                heightmap = os.path.join(map, child.attrib["heightmap"])

                self.terrain = GeoMipTerrain("Terrain")
                self.terrain.set_block_size(64)
                self.terrain_node = self.terrain.get_root()
                
                if not self.terrain.set_heightfield(heightmap):
                    Logger.error("Failed to load heightmap for terrain.")
                    self.terrain = None
                    return False

                self.terrain.generate()
                self.terrain_node.set_scale(self.size[0] / 512, self.size[1] / 512, 300)
                tex = loader.load_texture("./data/textures/terrain/grass_tex.jpg")
                self.terrain_node.set_texture(tex)
                self.terrain_node.set_tex_scale(TextureStage.get_default(), 5000 / 512, 5000 / 512)
                tex.set_wrap_u(Texture.WM_repeat)
                tex.set_wrap_v(Texture.WM_repeat)
                self.terrain_node.reparent_to(render)

                #A small test
                panda = loader.load_model("panda")
                panda.set_pos(1643, 1479, 100)
                panda.reparent_to(render)

                base.camera.set_pos(1643, 1479, 100)

            #Unknown?
            else:
                Logger.warning(
                    "Unknown tag '{}' encountered in map '{}'.".format(
                        child.tag, map))

        #Map loaded
        Logger.info("Map '{}' loaded.".format(map))
        return True

    def unload_map(self):
        """Unload the current map."""
        self.terrain = None
        self.size = [0, 0]
        self.spawnpos = [0, 0, 0]
