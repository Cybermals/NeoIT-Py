#!/usr/bin/python3
"""IT to NeoIT-Py map upgrader."""

import argparse
import os
import sys
from xml.dom import minidom
import xml.etree.ElementTree as etree

#Constants
#==============================================================================
__author__ = "DylanCheetah"
__copyright__ = "(c) 2020 by DylanCheetah"
__license__ = "MIT"
__version__ = "1.0.0"


#Classes
#==============================================================================
class MapUpgrader(object):
    """A basic app class."""
    def load_ogre_terrain(self, terrain_file):
        """Load an Ogre terrain config file."""
        #Open the terrain config file
        heightmap = ""
        material = ""

        with open(terrain_file, "r") as f:
            #Find the heightmap and material file entries
            for line in f:
                #Heightmap?
                if line.startswith("Heightmap.image"):
                    heightmap = line.split("=")[1].strip()

                #Material?
                elif line.startswith("CustomMaterialName"):
                    material = line.split("=")[1].strip()

        return (heightmap, material)

    def load_it_cfg(self, world_file):
        """Load an IT config file.
        
        Note: The normal config parser is unable to load IT config files like
        .world due to duplicate sections and lack of keys. The Ogre terrain files
        can however be loaded with the normal config parser.
        """
        #Read the map data
        with open(world_file, "r") as f:
            data = f.read()

        #Parse the map data
        sections = [[line for line in section.replace("]", "").split("\n") if line != "" and line != "#"] for section in data.split("[") if section != ""]
        return sections

    def load_it_trees(self, tree_file, elm):
        """Load an IT tree file and add the trees as children of the given XML 
        element.
        """
        #Load the trees
        sections = self.load_it_cfg(tree_file)

        for section in sections:
            #Separate the mesh and material
            tree = section[0].split(";")
            mesh = os.path.splitext(tree[0])[0]
            material = tree[1] if len(tree) > 1 else ""

            #Add a new tree group to the XML
            tree_group = etree.SubElement(elm, "treegroup", {
                "mesh": mesh,
                "material": material
                })
            print("TreeGroup: {}".format(tree_group.attrib))

            #Parse the tree data
            skip = True

            for inst in section:
                #Skip over the section header
                if skip:
                    skip = False

                #Next tree
                else:
                    #Parse instance data
                    inst_data = inst.split(";")
                    pos = inst_data[0]
                    scale = inst_data[1] if len(inst_data) > 1 else ""
                    rot = inst_data[2] if len(inst_data) > 2 else ""

                    #Add the tree to the XML
                    tree_inst = etree.SubElement(tree_group, "tree", {
                        "pos": pos,
                        "scale": scale,
                        "rot": rot
                        })
                    print("    Tree: {}".format(tree_inst.attrib))

    def load_it_bushes(self, bush_file, elm):
        """Load an IT bush file and add the bushes as children of the given XML 
        element.
        """
        #Load the bush
        sections = self.load_it_cfg(bush_file)

        for section in sections:
            #Separate the mesh and material
            bush = section[0].split(";")
            mesh = os.path.splitext(bush[0])[0]
            material = bush[1] if len(bush) > 1 else ""

            #Add a new bush group to the XML
            bush_group = etree.SubElement(elm, "bushgroup", {
                "mesh": mesh,
                "material": material
                })
            print("BushGroup: {}".format(bush_group.attrib))

            #Parse the bush data
            skip = True

            for inst in section:
                #Skip over the section header
                if skip:
                    skip = False

                #Next bush
                else:
                    #Parse instance data
                    inst_data = inst.split(";")
                    pos = inst_data[0]
                    scale = inst_data[1] if len(inst_data) > 1 else ""
                    rot = inst_data[2] if len(inst_data) > 2 else ""

                    #Add the bush to the XML
                    bush_inst = etree.SubElement(bush_group, "bush", {
                        "pos": pos,
                        "scale": scale,
                        "rot": rot
                        })
                    print("    Bush: {}".format(bush_inst.attrib))

    def load_it_critters(self, critter_file, elm):
        """Load an IT critter file and add the data as children of the given XML 
        element.
        """
        #Parse the critter file
        sections = self.load_it_cfg(critter_file)

        for section in sections:
            #Limit Section
            if section[0] == "Limit":
                #Parse the limit data
                limit = section[1]

                #Add the limit to the XML data
                critters = etree.SubElement(elm, "critters", {
                    "limit": limit
                    })
                print("Critters: {}".format(critters.attrib))

            #Critter Section
            elif section[0] == "Critter":
                #Parse the critter data
                type = section[1].split("=")[1]
                rate = section[2].split("=")[1]
                roam_area = section[3].split("=")[1]

                #Add the critter to the XML
                critter = etree.SubElement(elm, "critter", {
                    "type": type,
                    "rate": rate,
                    "roamarea": roam_area
                    })
                print("    Critter: {}".format(critter.attrib))

            #RoamArea Section
            elif section[0] == "RoamArea":
                #Parse the roam area data
                start = section[1].split("=")[1]
                range = section[2].split("=")[1]

                #Add the roam area to the XML
                roam_area = etree.SubElement(elm, "roamarea", {
                    "start": start,
                    "range": range
                    })
                print("    RoamArea: {}".format(roam_area.attrib))

            #Unknown Section
            else:
                print("WARNING: Unknown critter section '{}' encountered.".format(
                    section[0]))

    def upgrade_map(self, world_file):
        """Upgrade an IT map to NeoIT-Py format."""
        print("Upgrading '{}'...".format(world_file))

        #Upgrade the old map
        map_dir = os.path.dirname(world_file)
        sections = self.load_it_cfg(world_file)
        xml = etree.ElementTree()
        xml._setroot(etree.Element("world"))
        root = xml.getroot()

        for section in sections:
            #Initialize Section
            if section[0] == "Initialize":
                #Parse terrain data
                config = section[1]
                width = section[2]
                height = section[3]
                spawn_pos = section[4]

                #Load the heightmap and material data
                heightmap, material = self.load_ogre_terrain(
                    os.path.join(map_dir, config))

                #Add terrain to XML
                terrain = etree.SubElement(root, "terrain", {
                    "size": width + " " + height,
                    "spawnpos": spawn_pos,
                    "heightmap": heightmap,
                    "material": material
                    })
                print("Terrain: {}".format(terrain.attrib))

            #Portal Section
            elif section[0] == "Portal":
                #Parse portal data
                pos = section[1]
                radius = section[2]
                dest_map = section[3]

                #Add portal to XML
                portal = etree.SubElement(root, "portal", {
                    "pos": pos,
                    "radius": radius,
                    "destmap": dest_map
                    })
                print("Portal: {}".format(portal.attrib))

            #Gate Section
            elif section[0] == "Gate":
                #Parse gate data
                material = section[1]
                pos = section[2]
                dest_map = section[3]
                dest_vec = section[4]

                #Add gate to XML
                gate = etree.SubElement(root, "gate", {
                    "material": material,
                    "pos": pos,
                    "destmap": dest_map,
                    "destvec": dest_vec
                    })
                print("Gate: {}".format(gate.attrib))

            #WaterPlane Section
            elif section[0] == "WaterPlane":
                #Parse water plane data
                pos = section[1]
                scale_x = section[2]
                scale_z = section[3]
                material = section[4] if len(section) > 4 else ""
                sound = section[5] if len(section) > 5 else ""
                is_solid = section[6] if len(section) > 6 else "false"

                #Add water plane to XML
                water_plane = etree.SubElement(root, "waterplane", {
                    "pos": pos,
                    "scale": scale_x + " " + scale_z,
                    "material": material,
                    "sound": sound,
                    "issolid": is_solid
                    })
                print("WaterPlane: {}".format(water_plane.attrib))

            #Object Section
            elif section[0] == "Object":
                #Parse object data
                mesh = os.path.splitext(section[1])[0]
                pos = section[2]
                scale = section[3]
                rot = section[4]
                sound = section[5] if len(section) > 5 else ""
                material = section[6] if len(section) > 6 else ""

                #Add object to XML
                obj = etree.SubElement(root, "object", {
                    "mesh": mesh,
                    "pos": pos,
                    "scale": scale,
                    "rot": rot,
                    "sound": sound,
                    "material": material
                    })
                print("Object: {}".format(obj.attrib))

            #Particle Section
            elif section[0] == "Particle":
                #Parse particle data
                name = section[1]
                pos = section[2]
                sound = section[3] if len(section) > 3 else ""

                #Add particle to XML
                particle = etree.SubElement(root, "particle", {
                    "name": name,
                    "pos": pos,
                    "sound": sound
                    })
                print("Particle: {}".format(particle.attrib))

            #WeatherCycle Section
            elif section[0] == "WeatherCycle":
                #Parse weather cycle data
                name = section[1]

                #Add weather cycle to XML
                weather_cycle = etree.SubElement(root, "weathercycle", {
                    "name": name
                    })
                print("WeatherCycle: {}".format(weather_cycle.attrib))

            #Interior Section
            elif section[0] == "Interior":
                #Parse interior data
                if len(section) > 3:
                    color = section[1]
                    height = section[2]
                    material = section[3]

                else:
                    color = ""
                    height = section[1]
                    material = section[2]

                #Add interior data to XML
                interior = etree.SubElement(terrain, "interior", {
                    "color": color,
                    "height": height,
                    "material": material
                    })
                print("Interior: {}".format(interior.attrib))

            #Light Section
            elif section[0] == "Light":
                #Parse light data
                pos = section[1]
                color = section[2]

                #Add light to XML
                light = etree.SubElement(root, "light", {
                    "pos": pos,
                    "color": color
                    })
                print("Light: {}".format(light.attrib))

            #Billboard Section
            elif section[0] == "Billboard":
                #Parse billboard data
                pos = section[1]
                scale = section[2]
                material = section[3]

                #Add billboard to XML
                billboard = etree.SubElement(root, "billboard", {
                    "pos": pos,
                    "scale": scale,
                    "material": material
                    })
                print("Billboard: {}".format(billboard.attrib))

            #SphereWall Section
            elif section[0] == "SphereWall":
                #Parse sphere wall data
                pos = section[1]
                radius = section[2]
                is_inside = section[3]

                #Add sphere wall to XML
                sphere_wall = etree.SubElement(root, "spherewall", {
                    "pos": pos,
                    "radius": radius,
                    "isinside": is_inside
                    })
                print("SphereWall: {}".format(sphere_wall.attrib))

            #BoxWall Section
            elif section[0] == "BoxWall":
                #Parse box wall data
                pos = section[1]
                range = section[2]
                is_inside = section[3]

                #Add box wall to XML
                box_wall = etree.SubElement(root, "boxwall", {
                    "pos": pos,
                    "range": range,
                    "isinside": is_inside
                    })
                print("BoxWall: {}".format(box_wall.attrib))

            #MapEffect Section
            elif section[0] == "MapEffect":
                #Parse map effect data
                name = section[1]

                #Add map effect to XML
                map_effect = etree.SubElement(root, "mapeffect", {
                    "name": name
                    })
                print("MapEffect: {}".format(map_effect.attrib))

            #Grass Section
            elif section[0] == "Grass":
                #Parse grass data
                material = section[1]
                grass_map = section[2]
                color_map = section[3]

                #Add grass to XML
                grass = etree.SubElement(root, "grass", {
                    "material": material,
                    "grassmap": grass_map,
                    "colormap": color_map
                    })
                print("Grass: {}".format(grass.attrib))

            #RandomTrees Section
            elif section[0] == "RandomTrees":
                #Parse random tree data
                tree1 = os.path.splitext(section[1])[0]
                tree2 = os.path.splitext(section[2])[0]
                tree3 = os.path.splitext(section[3])[0]
                tree_cnt = section[4]

                #Add random trees to XML
                rand_trees = etree.SubElement(root, "randomtrees", {
                    "count": tree_cnt
                    })
                etree.SubElement(rand_trees, "tree", {
                    "mesh": tree1
                    })
                etree.SubElement(rand_trees, "tree", {
                    "mesh": tree2
                    })
                etree.SubElement(rand_trees, "tree", {
                    "mesh": tree3
                    })
                print("RandomTrees: {}".format(rand_trees.attrib))
                print("    Trees: {}".format(
                    [child.attrib for child in list(rand_trees)]))

            #RandomBushes Section
            elif section[0] == "RandomBushes":
                #Parse random bush data
                bush1 = os.path.splitext(section[1])[0]
                bush2 = os.path.splitext(section[2])[0]
                bush3 = os.path.splitext(section[3])[0]
                bush_cnt = section[4]

                #Add random bushes to XML
                rand_bushes = etree.SubElement(root, "randombushes", {
                    "count": count
                    })
                etree.SubElement(rand_bushes, "bush", {
                    "mesh": bush1
                    })
                etree.SubElement(rand_bushes, "bush", {
                    "mesh": bush2
                    })
                etree.SubElement(rand_bushes, "bush", {
                    "mesh": bush3
                    })
                print("RandomBushes: {}".format(rand_bushes.attrib))
                print("    Bushes: {}".format(
                    [child.attribs for child in list(rand_bushes)]))

            #Trees Section
            elif section[0] == "Trees" or section[0] == "NewTrees":
                #Parse tree data
                tree_file = section[1]
                self.load_it_trees(os.path.join(map_dir, tree_file), root)

            #Bushes Section
            elif section[0] == "Bushes" or section[0] == "NewBushes":
                #Parse bush data
                bush_file = section[1]
                self.load_it_bushes(os.path.join(map_dir, bush_file), root)

            #FloatingBushes Section
            elif (section[0] == "FloatingBushes" or 
                section[0] == "NewFloatingBushes"):
                #Parse bush data
                bush_file = section[1]
                self.load_it_bushes(os.path.join(map_dir, bush_file), root)

            #CollBox Section
            elif section[0] == "CollBox":
                #Parse collision box data
                pos = section[1]
                size = section[2]

                #Add collision box to XML
                colbox = etree.SubElement(root, "colbox", {
                    "pos": pos,
                    "size": size
                    })
                print("ColBox: {}".format(colbox.attrib))

            #CollSphere Section
            elif section[0] == "CollSphere":
                #Parse collision sphere data
                pos = section[1]
                radius = section[2]

                #Add collision sphere to XML
                colsphere = etree.SubElement(root, "colsphere", {
                    "pos": pos,
                    "radius": radius
                    })
                print("ColSphere: {}".format(colsphere.attrib))

            #SpawnCritters Section
            elif section[0] == "SpawnCritters":
                #Parse critter spawns
                critter_file = section[1]
                self.load_it_critters(os.path.join(map_dir, critter_file), root)

            #FreezeTime Section
            elif section[0] == "FreezeTime":
                #Parse freeze time
                time = section[1]

                #Add time freeze to XML
                freeze_time = etree.SubElement(root, "freezetime", {
                    "time": time
                    })
                print("FreezeTime: {}".format(freeze_time.attrib))

            #Music Section
            elif section[0] == "Music":
                #Parse music data
                song = section[1]

                #Add music to XML data
                music = etree.SubElement(root, "music", {
                    "song": song
                    })
                print("Music: {}".format(music.attrib))

            #Unknown Section
            else:
                print("WARNING: Unknown world section '{}' encountered.".format(
                    section[0]))

        #Save prettified XML
        xml = minidom.parseString(etree.tostring(root))
        
        with open(world_file.replace(".world", ".xml"), "w") as f:
            xml.writexml(f, addindent = "    ", newl = "\n")

        print("done")

    def run(self):
        """Run this app."""
        #Display header
        print("NeoIT-Py Map Upgrader v{}".format(__version__))
        print(__copyright__)
        print()

        #Parse command-line arguments
        argparser = argparse.ArgumentParser(description = __doc__)
        argparser.add_argument("maps", nargs = "+")
        args = argparser.parse_args()

        for map in args.maps:
            if os.path.isdir(map):
                #Build path to world file
                map = os.path.join(map, os.path.basename(map) + ".world")

            if (os.path.splitext(map)[1] == ".world" and 
                os.path.exists(map)):
                #Upgrade the map
                self.upgrade_map(map)

            else:
                print("ERROR: Failed to process map '{}'".format(map))


#Entry Point
#==============================================================================
MapUpgrader().run()