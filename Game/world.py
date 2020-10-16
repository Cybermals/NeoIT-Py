"""New Impressive Title - World API"""

import os
import xml.etree.ElementTree as etree

from kivy.logger import Logger, LOG_LEVELS
from panda3d.core import (
    CollisionNode,
    CollisionSphere,
    GeoMipTerrain,
    Texture,
    TextureStage
    )

from utils import parse_float, parse_vec


#Classes
#==============================================================================
class Portal(object):
    """A portal to another world."""
    def __init__(self, pos, radius, dest):
        """Setup this portal."""
        #Setup model
        self.model = loader.load_model("./data/models/scenery/portal/portal")
        self.model.set_pos(pos[0], pos[2], pos[1]) #Y is up in the map data
        self.model.set_scale(radius, radius, radius)

        try:
            texture = loader.load_texture(
                os.path.join("./data/maps", dest, "portal.png"))
            self.model.set_texture(texture, 1)

        except IOError:
            Logger.warning("No portal texture for map '{}'.".format(dest))

        self.model.reparent_to(render)

        #Setup collision detection
        cnode = CollisionNode("portal")
        cnode.add_solid(CollisionSphere(0, 0, 0, radius))
        collider = self.model.attach_new_node(cnode)
        base.cTrav.add_collider(collider, base.portal_handler)

        #Store desination
        self.dest = dest

    def __del__(self):
        """Cleanup this portal."""
        self.model.remove_node()


class Gate(Portal):
    """A gate to another world."""
    def __init__(self, pos, dest, destvec, material):
        """Setup this gate."""
        Portal.__init__(self, pos, 10, dest)

        #Change the name of the collision node
        self.model.ls()

        #Store destination vector


class WorldManager(object):
    """A world manager for heightmapped worlds stored as XML."""
    def __init__(self):
        """Setup this world manager."""
        Logger.info("Initializing world manager...")

        self.portals = []
        self.gates = []

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
                
                if not self.terrain.set_heightfield(heightmap):
                    Logger.error("Failed to load heightmap for terrain.")
                    self.terrain = None
                    return False

                self.terrain.generate()
                self.terrain_np = self.terrain.get_root()
                self.terrain_np.set_scale(self.size[0] / 512, self.size[1] / 512, 300)
                tex = loader.load_texture("./data/textures/terrain/grass_tex.jpg")
                self.terrain_np.set_texture(tex)
                self.terrain_np.set_tex_scale(TextureStage.get_default(), 5000 / 512, 5000 / 512)
                tex.set_wrap_u(Texture.WM_repeat)
                tex.set_wrap_v(Texture.WM_repeat)
                self.terrain_np.reparent_to(render)

                base.camera.set_pos(self.size[0] / 2, self.size[1] / 2, 100)

            #Portal?
            elif child.tag == "portal":
                #Validate portal
                if not ("pos" in child.attrib and "destmap" in child.attrib):
                    Logger.warning("Portal must define 'pos' and 'destmap'.")
                    continue

                #Load portal
                pos = parse_vec(child.attrib["pos"], 3)
                radius = parse_float(child.attrib["radius"]) if "radius" in child.attrib else 1
                destmap = child.attrib["destmap"]
                self.add_portal(pos, radius, destmap)

            #Gate?
            elif child.tag == "gate":
                #Validate gate
                if not ("pos" in child.attrib and "destmap" in child.attrib and
                    "destvec" in child.attrib):
                    Logger.warning("Gate must define 'pos', 'destmap', and 'destvec'.")
                    continue

                #Load gate
                pos = parse_vec(child.attrib["pos"])
                destmap = child.attrib["destmap"]
                destvec = parse_vec(child.attrib["destvec"])
                material = child.attrib["material"] if "material" in child.attrib else ""
                self.add_gate(pos, destmap, destvec, material)

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

        while len(self.portals) > 0:
            self.del_portal(self.portals[-1])

        while len(self.gates) > 0:
            self.del_gate(self.gates[-1])

    def add_portal(self, pos, radius, dest):
        """Add a portal to this world."""
        self.portals.append(Portal(pos, radius, dest))
        Logger.info("Added portal: pos = {}, radius = {}, dest = '{}'".format(
            pos, radius, dest))

    def del_portal(self, portal):
        """Remove a portal from this world."""
        self.portals.remove(portal)
        Logger.info("Removed portal {}".format(portal))

    def add_gate(self, pos, dest, destvec, material):
        """Add a gate to this world."""
        self.gates.append(Gate(pos, dest, destvec, material))
        Logger.info("Added gate: pos = {}, dest = '{}', destvec = {}, material = '{}'".format(pos, dest, destvec, material))

    def del_gate(self, gate):
        """Remove a gate from this world."""
        self.gates.remove(gate)
        Logger.info("Removed gate {}".format(gate))
