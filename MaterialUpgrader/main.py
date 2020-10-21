#!/usr/bin/python3
"""IT to NeoIT-Py material upgrader."""

import argparse
import os
from xml.dom import minidom
import xml.etree.ElementTree as etree


#Constants
#==============================================================================
__author__ = "DylanCheetah"
__copyright__ = "(c) 2020 by DylanCheetah"
__license__ = "MIT"
__version__ = "1.0.0"


#Classes
#===============================================================================
class MaterialConverter(object):
    """A basic app class."""
    def parse_texture_unit(self, material):
        """Parse a technique."""
        #Add texture stage to XML
        tex_stage = etree.SubElement(material, "texstage")

        #Find texture unit body
        for line in self.lines:
            #Strip line
            line = line.strip()

            #Start of body?
            if line == "{":
                #Parse texture unit body
                for line in self.lines:
                    #Strip line
                    line = line.strip()

                    #Texture?
                    if line.startswith("texture"):
                        #Add texture to XML
                        texture = etree.SubElement(tex_stage, "texture", {
                            "src": line.split(" ")[1]
                            })
                        print("Adding texture '{}'...".format(
                            texture.attrib["src"]))

                    #Scale?
                    elif line.startswith("scale"):
                        #Add scale to XML
                        tag, x, y = line.split(" ")
                        scale = etree.SubElement(tex_stage, "scale", {
                            "x": x,
                            "y": y
                            })
                        print("Adding texture scale...")

                    #Scroll?
                    elif line.startswith("scroll"):
                        #Add scale to XML
                        tag, x, y = line.split(" ")
                        scale = etree.SubElement(tex_stage, "scroll", {
                            "x": x,
                            "y": y
                            })
                        print("Adding texture scroll...")

                    #Color OP EX
                    elif line.startswith("colour_op_ex"):
                        #Add color op to XML
                        tag, op, src, dst = line.split(" ")
                        color_op = etree.SubElement(tex_stage, "colorop", {
                            "op": op,
                            "src1": src,
                            "src2": dst
                            })
                        print("Adding color OP...")

                    #Color OP
                    elif line.startswith("colour_op"):
                        #Add color op to XML
                        color_op = etree.SubElement(tex_stage, "colorop", {
                            "op": line.split(" ")[1]
                            })
                        print("Adding color OP...")

                    #End of body?
                    elif line == "}":
                        return

                    #Unknown line?
                    else:
                        print("WARNING: Unknown line '{}'.".format(line))

        #Body not found
        print("ERROR: Technique has no body!")

    def parse_pass(self, material):
        """Parse a pass."""
        #Find pass body
        for line in self.lines:
            #Strip line
            line = line.strip()

            #Start of body?
            if line == "{":
                #Parse pass body
                for line in self.lines:
                    #Strip line
                    line = line.strip()

                    #Texture Unit?
                    if line.startswith("texture_unit"):
                        self.parse_texture_unit(material)

                    #End of body?
                    elif line == "}":
                        return

                    #Unknown line?
                    else:
                        print("WARNING: Unknown line '{}'.".format(line))

        #Body not found
        print("ERROR: Pass has no body!")

    def parse_technique(self, material):
        """Parse a technique."""
        #Find technique body
        for line in self.lines:
            #Strip line
            line = line.strip()

            #Start of body?
            if line == "{":
                #Parse technique body
                for line in self.lines:
                    #Strip line
                    line = line.strip()

                    #Pass?
                    if line.startswith("pass"):
                        self.parse_pass(material)

                    #End of body?
                    elif line == "}":
                        return

                    #Unknown line?
                    else:
                        print("WARNING: Unknown line '{}'.".format(line))

        #Body not found
        print("ERROR: Technique has no body!")

    def parse_material(self, name):
        """Parse a material with the given name."""
        #Add material to XML
        material = etree.SubElement(self.root, "material", {"name": name})
        print("Adding material '{}'...".format(name))

        #Find material body
        for line in self.lines:
            #Strip line
            line = line.strip()

            #Start of body?
            if line == "{":
                #Parse material body
                for line in self.lines:
                    #Strip line
                    line = line.strip()

                    #Technique?
                    if line.startswith("technique"):
                        self.parse_technique(material)

                    #End of body?
                    elif line == "}":
                        return

                    #Unknown line?
                    else:
                        print("WARNING: Unknown line '{}'.".format(line))

        #Body not found
        print("ERROR: Material '{}' has no body!".format(name))

    def upgrade_material(self, material):
        """Upgrade a material file."""
        #Upgrade the material
        print("Upgrading material '{}'...".format(material))
        self.root = etree.Element("materials")

        with open(material, "r") as f:
            #Get file iterator
            self.lines = iter(f)

            for line in self.lines:
                #Strip line
                line = line.strip()

                #New material?
                if line.startswith("material"):
                    self.parse_material(line.split(" ")[1])

                #Unknown line
                else:
                    print("WARNING: Unknown line '{}'.".format(line))

        #Save prettified XML
        xml = minidom.parseString(etree.tostring(self.root))

        with open(material.replace(".material", "_mat.xml"), "w") as f:
            xml.writexml(f, indent = "    ", newl = "\n")

        print("done")

    def run(self):
        """Run this app."""
        #Display header
        print("NeoIT-Py Material Upgrader v{}".format(__version__))
        print(__copyright__)
        print()

        #Parse command-line arguments
        argparser = argparse.ArgumentParser(description = __doc__)
        argparser.add_argument("materials", nargs = "+")
        args = argparser.parse_args()

        for material in args.materials:
            if os.path.isfile(material):
                self.upgrade_material(material)

            else:
                print("ERROR: Failed to process material '{}'.".format(material))


#Entry Point
#===============================================================================
MaterialConverter().run()