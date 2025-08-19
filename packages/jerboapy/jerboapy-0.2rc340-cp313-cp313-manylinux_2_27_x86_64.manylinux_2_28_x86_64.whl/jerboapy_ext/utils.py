from jerboapy import *
import math
from .Point3 import Point3
from .Color4 import Color4


def make_polygon(gmap, vertices):
    """Create a polygon in the GMap from a list of vertices.
    Args:
        gmap (GMap): The GMap to which the polygon will be added.
        vertices (list of Point3): A list of Point3 objects representing the vertices of the polygon.

        Returns:
            list of Dart: The list of darts created for the polygon.
    """
    num_vertices = len(vertices)
    if num_vertices < 3:
        raise ValueError("A polygon must have at least 3 vertices.")

    darts = gmap.make_darts(num_vertices * 2)
    color = Color4.randomColor()

    # Compute the normal vector using the first three vertices
    ab = vertices[1] - vertices[0]
    ac = vertices[2] - vertices[0]
    normal = ab.cross(ac)
    normal.normalize()

    for i in range(num_vertices):
        darts[i * 2].ebd123["pos"] = vertices[i]
        darts[i * 2].ebd01["normal"] = normal
        darts[i * 2].ebd01["color"] = color
        darts[i * 2].ebd["orient"] = True

        darts[i * 2 + 1].ebd123["pos"] = vertices[i]
        darts[i * 2 + 1].ebd01["normal"] = normal
        darts[i * 2 + 1].ebd01["color"] = color
        darts[i * 2 + 1].ebd["orient"] = False

        # Link the darts to form the edges of the polygon
        gmap.linkAlpha(1, darts[i * 2], darts[i * 2 + 1])
        gmap.linkAlpha(0, darts[i * 2 + 1], darts[(i * 2 + 2) % (num_vertices * 2)])
    return darts

def make_regular_polygon(gmap, num_sides = 12, center=Point3(0,0,0), radius=1.0):
    """Create a regular polygon in the GMap.
    Args:
        gmap (GMap): The GMap to which the polygon will be added.
        num_sides (int): The number of sides of the polygon.
        center (Point3): The center point of the polygon.
        radius (float): The radius of the polygon.
    Returns:
        list of Dart: The list of darts created for the polygon.
    """
    # Example: Create a regular dodecagon (12-sided polygon)
    angle_step = (2.0 * Point3.PI) / float(num_sides)

    # Generate vertices for the dodecagon
    dodecagon_vertices = [
        center + radius *  Point3(math.cos(i * angle_step), math.sin(i * angle_step), 0)
        for i in range(num_sides)
    ]

    # Create the dodecagon using make_regular_polygon
    make_polygon(gmap, dodecagon_vertices)




def collect(orbittab, gmap, dart, ebdname, defvalue):
	# collect the darts of the orbit
	orbit = Orbit(orbittab)(gmap, dart)
	# collect the ebd of the darts
	ebd = []
	for i in range(len(orbit)):
		ebd.append(gmap[orbit[i]].ebd.get(ebdname, defvalue))
	return ebd

def collect0(orbittab, gmap, dart, ebdname, defvalue):
	# collect the darts of the orbit
	orbit = Orbit(orbittab)(gmap, dart)
	# collect the ebd of the darts
	ebd = []
	for i in range(len(orbit)):
		ebd.append(gmap[orbit[i]].ebd0.get(ebdname, defvalue))
	return ebd

def collect1(orbittab, gmap, dart, ebdname, defvalue):
	# collect the darts of the orbit
	orbit = Orbit(orbittab)(gmap, dart)
	# collect the ebd of the darts
	ebd = []
	for i in range(len(orbit)):
		ebd.append(gmap[orbit[i]].ebd1.get(ebdname, defvalue))
	return ebd

def collect2(orbittab, gmap, dart, ebdname, defvalue):
    # collect the darts of the orbit
    orbit = Orbit(orbittab)(gmap, dart)
    # collect the ebd of the darts
    ebd = []
    for i in range(len(orbit)):
        ebd.append(gmap[orbit[i]].ebd2.get(ebdname, defvalue))
    return ebd

def collect3(orbittab, gmap, dart, ebdname, defvalue):
    # collect the darts of the orbit
    orbit = Orbit(orbittab)(gmap, dart)
    # collect the ebd of the darts
    ebd = []
    for i in range(len(orbit)):
        ebd.append(gmap[orbit[i]].ebd3.get(ebdname, defvalue))
    return ebd


def collect01(orbittab, gmap, dart, ebdname, defvalue):
	# collect the darts of the orbit
	orbit = Orbit(orbittab)(gmap, dart)
	# collect the ebd of the darts
	ebd = []
	for i in range(len(orbit)):
		ebd.append(gmap[orbit[i]].ebd01.get(ebdname, defvalue))
	return ebd

def collect02(orbittab, gmap, dart, ebdname, defvalue):
    # collect the darts of the orbit
    orbit = Orbit(orbittab)(gmap, dart)
    # collect the ebd of the darts
    ebd = []
    for i in range(len(orbit)):
        ebd.append(gmap[orbit[i]].ebd02.get(ebdname, defvalue))
    return ebd

def collect03(orbittab, gmap, dart, ebdname, defvalue):
    # collect the darts of the orbit
    orbit = Orbit(orbittab)(gmap, dart)
    # collect the ebd of the darts
    ebd = []
    for i in range(len(orbit)):
        ebd.append(gmap[orbit[i]].ebd03.get(ebdname, defvalue))
    return ebd

def collect12(orbittab, gmap, dart, ebdname, defvalue):
    # collect the darts of the orbit
    orbit = Orbit(orbittab)(gmap, dart)
    # collect the ebd of the darts
    ebd = []
    for i in range(len(orbit)):
        ebd.append(gmap[orbit[i]].ebd12.get(ebdname, defvalue))
    return ebd

def collect13(orbittab, gmap, dart, ebdname, defvalue):
    # collect the darts of the orbit
    orbit = Orbit(orbittab)(gmap, dart)
    # collect the ebd of the darts
    ebd = []
    for i in range(len(orbit)):
        ebd.append(gmap[orbit[i]].ebd13.get(ebdname, defvalue))
    return ebd

def collect23(orbittab, gmap, dart, ebdname, defvalue):
    # collect the darts of the orbit
    orbit = Orbit(orbittab)(gmap, dart)
    # collect the ebd of the darts
    ebd = []
    for i in range(len(orbit)):
        ebd.append(gmap[orbit[i]].ebd23.get(ebdname, defvalue))
    return ebd

def collect012(orbittab, gmap, dart, ebdname, defvalue):
    # collect the darts of the orbit
    orbit = Orbit(orbittab)(gmap, dart)
    # collect the ebd of the darts
    ebd = []
    for i in range(len(orbit)):
        ebd.append(gmap[orbit[i]].ebd012.get(ebdname, defvalue))
    return ebd

def collect013(orbittab, gmap, dart, ebdname, defvalue):
    # collect the darts of the orbit
    orbit = Orbit(orbittab)(gmap, dart)
    # collect the ebd of the darts
    ebd = []
    for i in range(len(orbit)):
        ebd.append(gmap[orbit[i]].ebd013.get(ebdname, defvalue))
    return ebd

def collect023(orbittab, gmap, dart, ebdname, defvalue):
    # collect the darts of the orbit
    orbit = Orbit(orbittab)(gmap, dart)
    # collect the ebd of the darts
    ebd = []
    for i in range(len(orbit)):
        ebd.append(gmap[orbit[i]].ebd023.get(ebdname, defvalue))
    return ebd

def collect123(orbittab, gmap, dart, ebdname, defvalue):
    # collect the darts of the orbit
    orbit = Orbit(orbittab)(gmap, dart)
    # collect the ebd of the darts
    ebd = []
    for i in range(len(orbit)):
        ebd.append(gmap[orbit[i]].ebd123.get(ebdname, defvalue))
    return ebd

def collect0123(orbittab, gmap, dart, ebdname, defvalue):
    # collect the darts of the orbit
    orbit = Orbit(orbittab)(gmap, dart)
    # collect the ebd of the darts
    ebd = []
    for i in range(len(orbit)):
        ebd.append(gmap[orbit[i]].ebd0123.get(ebdname, defvalue))
    return ebd

