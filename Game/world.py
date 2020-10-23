"""New Impressive Title - World API"""

import os
import xml.etree.ElementTree as etree

from direct.task.Task import Task
from kivy.logger import Logger, LOG_LEVELS
from panda3d.core import (
    CollisionNode,
    CollisionSphere,
    GeoMipTerrain,
    Material,
    Texture,
    TextureStage,
    Vec4
    )

from utils import parse_float, parse_vec


#Constants
#==============================================================================
gate_mat_black = Material("GateMatBlack")
gate_mat_black.ambient = Vec4(0, 0, 0, 1)
gate_mat_black.diffuse = Vec4(0, 0, 0, 1)
gate_mat_black.specular = Vec4(0, 0, 0, 1)

gate_mat_white = Material("GateMatWhite")
gate_mat_white.ambient = Vec4(1, 1, 1, 1)
gate_mat_white.diffuse = Vec4(1, 1, 1, 1)
gate_mat_white.specular = Vec4(0, 0, 0, 1)
gate_mat_white.emission = Vec4(.5, .5, .5, 1)


#Classes
#==============================================================================
class Portal(object):
    """A portal to another world."""
    def __init__(self, pos, radius, dest):
        """Setup this portal."""
        #Setup model
        self.model = loader.load_model("./data/models/scenery/portal/portal")
        self.model.set_pos(*pos) #Y is up in the map data
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
        cnode.add_solid(CollisionSphere(0, 0, 0, 1))
        self.collider = self.model.attach_new_node(cnode)
        self.collider.set_python_tag("object", self)
        base.cTrav.add_collider(self.collider, base.portal_handler)

        #Store desination
        self.dest = dest

    def __del__(self):
        """Cleanup this portal."""
        base.cTrav.remove_collider(self.collider)
        self.model.remove_node()


class Gate(Portal):
    """A gate to another world."""
    def __init__(self, pos, dest, destvec, material):
        """Setup this gate."""
        Portal.__init__(self, pos, 40, dest)

        #Change the name of the collision node
        self.model.find("**/portal").set_name("gate")

        #Store destination vector
        self.destvec = destvec

        #Set the gate material
        self.model.set_texture_off(True)
        self.model.set_material(gate_mat_black, 1) #need to adjust this later


class Object(object):
    """A scenery object."""
    def __init__(self, mesh, pos, rot, scale, material, sound):
        """Setup this scenery object."""
        try:
            #Setup model
            self.model = loader.load_model(
                os.path.join("./data/models/scenery", mesh, mesh))
            self.model.set_pos(*pos)
            self.model.set_hpr(*rot)
            self.model.set_scale(*scale)
            self.model.reparent_to(render)

        except IOError:
            #Just set this to None if the model won't load
            self.model = None
            Logger.warning("Model '{}' failed to load.".format(mesh))

    def __del__(self):
        """Cleanup this scenery object."""
        if self.model is not None:
            self.model.remove_node()


class WorldManager(object):
    """A world manager for heightmapped worlds stored as XML."""
    def __init__(self):
        """Setup this world manager."""
        Logger.info("Initializing world manager...")

        self.terrain = None
        self.portals = []
        self.gates = []
        self.objects = []

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
                self.size = parse_vec(child.attrib["size"], 3)
                self.spawnpos = parse_vec(child.attrib["spawnpos"], 2)
                heightmap = os.path.join(map, child.attrib["heightmap"])

                self.terrain = GeoMipTerrain("Terrain")
                self.terrain.set_bruteforce(True)
                
                if not self.terrain.set_heightfield(heightmap):
                    Logger.error("Failed to load heightmap for terrain.")
                    self.terrain = None
                    return False

                self.terrain_np = self.terrain.get_root()
                self.terrain_np.set_scale(self.size[0] / 512, self.size[1] / 512, 
                    self.size[2])
                tex = loader.load_texture(
                    "./data/textures/terrain/grass_tex2.png")
                self.terrain_np.set_texture(tex)
                self.terrain_np.set_tex_scale(TextureStage.get_default(), 
                    self.size[0] / 512, self.size[1] / 512)
                tex.set_wrap_u(Texture.WM_repeat)
                tex.set_wrap_v(Texture.WM_repeat)
                self.terrain_np.reparent_to(render)
                self.terrain.generate()

                base.camera.set_pos(self.size[0] / 2, self.size[1] / 2, 
                    self.size[2])

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
                pos = parse_vec(child.attrib["pos"], 3)
                destmap = child.attrib["destmap"]
                destvec = parse_vec(child.attrib["destvec"], 3)
                material = child.attrib["material"] if "material" in child.attrib else ""
                self.add_gate(pos, destmap, destvec, material)

            #Object?
            elif child.tag == "object":
                #Validate object
                if not ("mesh" in child.attrib and "pos" in child.attrib):
                    Logger.warning("Object must define 'mesh' and 'pos'.")
                    continue

                #Load object
                mesh = child.attrib["mesh"]
                pos = parse_vec(child.attrib["pos"], 3)
                rot = parse_vec(child.attrib["rot"], 3) if "rot" in child.attrib else [0, 0, 0]
                scale = parse_vec(child.attrib["scale"], 3) if "scale" in child.attrib else [1, 1, 1]
                material = child.attrib["material"] if "material" in child.attrib else ""
                sound = child.attrib["sound"] if "sound" in child.attrib else ""
                self.add_object(mesh, pos, rot, scale, material, sound)

            #Object Group?
            elif child.tag == "objectgroup":
                #Validate object group
                if not ("mesh" in child.attrib):
                    Logger.warning("Object group must define 'mesh'.")
                    continue

                #Load object group
                mesh = child.attrib["mesh"]
                material = child.attrib["material"] if "material" in child.attrib else ""
                self.load_object_group(child, mesh, material)

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
        if self.terrain is not None:
            self.terrain.get_root().remove_node()

        self.terrain = None
        self.size = [0, 0]
        self.spawnpos = [0, 0, 0]

        while len(self.portals) > 0:
            self.del_portal(self.portals[-1])

        while len(self.gates) > 0:
            self.del_gate(self.gates[-1])

        while len(self.objects) > 0:
            self.del_object(self.objects[-1])

    def load_object_group(self, group, mesh, material):
        """Load a group of objects."""
        for object in group:
            #Validate object
            if not ("pos" in object.attrib):
                Logger.warning("Group object must define 'pos'.")
                continue

            #Load object
            pos = parse_vec(object.attrib["pos"], 2)
            rot = parse_vec(object.attrib["rot"], 1) if "rot" in object.attrib else [0, 0, 0]
            scale = parse_vec(object.attrib["scale"], 1) if "scale" in object.attrib else [1, 1, 1]
            self.add_object(mesh, pos, rot, scale, material, "")

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

    def add_object(self, mesh, pos, rot, scale, material, sound):
        """Add an object to this world."""
        #Handle 2 coordinate position
        if len(pos) == 2:
            pos = [pos[0], pos[1], self.get_terrain_height(pos)]

        #Handle single coordinate rotation
        if len(rot) == 1:
            rot = [rot[0], 0, 0]

        #Handle single or double coordinate scale
        if len(scale) == 1:
            scale = [scale[0], scale[0], scale[0]]

        elif len(scale) == 2:
            scale = [scale[0], scale[1], 1]

        #Add the object
        self.objects.append(Object(mesh, pos, rot, scale, material, sound))
        Logger.info("Added object: mesh = '{}', pos = {}, rot = {}, scale = {}, material = '{}', sound = '{}'".format(mesh, pos, rot, scale, material, sound))

    def del_object(self, object):
        """Delete an object from this world."""
        Logger.info("Removed object {}".format(object))

    def get_terrain_height(self, pos):
        """Get the height of the terrain at the given point."""
        #Is the position a list of 2 elements?
        if isinstance(pos, list) and len(pos) == 2:
            return self.terrain.get_elevation(
                pos[0] / (self.size[0] / 512), 
                pos[1] / (self.size[1] / 512)) * self.size[2]

        #Assume it is a point object
        else:
            return self.terrain.get_elevation(
                pos[0] / (self.size[0] / 512), 
                pos[1] / (self.size[1] / 512)) * self.size[2]
