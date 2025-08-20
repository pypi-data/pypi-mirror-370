import json

import Geometry3D
import matplotlib.pyplot as plt
import numpy as np
import shapely
import trimesh
from Geometry3D import HalfLine, Point, Vector, intersection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shapely.geometry import Polygon
from sklearn.decomposition import PCA
from trimesh.creation import triangulate_polygon


def plot_building(vertices, surfaces, surf_to_show="all", show_vertices=True, title=""):
    vertices = np.array(vertices)
    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(projection="3d")
    vertices_to_plot = []
    for surf_name, surf_vert in surfaces.items():
        if surf_name in surf_to_show or surf_to_show == "all":
            xyz_surf = vertices[surf_vert]
            poly = Poly3DCollection([xyz_surf], alpha=0.1, linewidths=1, edgecolors="k")
            ax.add_collection3d(poly)
            vertices_to_plot += surf_vert
    # Add vertices with idx as text and dots
    # for idx_v in range(len(vertices)):
    if show_vertices:
        for idx_v in set(vertices_to_plot):
            vert = vertices[idx_v]
            ax.text(*vert, str(idx_v), color="r", fontsize=10)
    # Set axes limits
    xyz_min, xyz_max = np.min(vertices, axis=0), np.max(vertices)
    ax.set_xlim3d(xyz_min[0], xyz_max)
    ax.set_ylim3d(xyz_min[1], xyz_max)
    ax.set_zlim3d(xyz_min[2], xyz_max)
    # Remove ticks labels
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_zticklabels([])
    plt.title(title)
    plt.show()
    return


def ConvexPolygon(points):
    """
    Create a ConvexPolygon object from a list of points.
    Unlike the ConvexPolygon_old class fron Geomtry3D, this function doesn't require
    the first 3 points to be non-collinear. This is achieved by testing all circular
    permutations of the points.

    Inputs
    ------
    points : array-like of shape (n_points, 3)
        Array of shape (n_vertices, 3) representing the points (x, y, z) of the surface.

    Returns
    -------
    poly : Geometry3D.ConvexPolygon
    """
    # Try all circular permutations of the points when creating the polygon
    # This is because ConvexPolygon requires the first 3 points to be non-collinear,
    # which may not be the case sometimes (e.g. for "EastWall_2F").
    n_points = len(points)
    for i in range(n_points):
        points_perm = np.roll(points, i, axis=0)
        try:
            poly = Geometry3D.ConvexPolygon([Point(p) for p in points_perm])
            return poly
        except ZeroDivisionError:
            continue
    raise ValueError(
        f"Could not create a ConvexPolygon from the given points: {points}"
    )


def get_approximate_solid_angles(vertices, surfaces, zone):
    """
    Approximate solid angles of each surface in a zone by taking the normalized areas.
    """
    # Compute the area of each surface
    surf_areas = get_surface_areas(vertices, surfaces)
    # Remove surfaces not in the zone
    surf_areas = {surf: area for surf, area in surf_areas.items() if zone in surf}
    # Normalize the areas
    total_area = sum(surf_areas.values())
    angles = {surf_name: area / total_area for surf_name, area in surf_areas.items()}
    return angles


def get_solid_angles_ray_tracing(vertices, surfaces, zone):
    """
    Calculate the solid angle of each surface enclosing a zone, using ray tracing.
    TODO: make it work for non-convex surfaces.
    """
    # Create of list of shapely polygons for each floor in the zone
    floor_polygons = []
    for surf_name, surf_vert in surfaces.items():
        surf_zone = surf_name.split("_")[1]
        if surf_zone == zone and "Floor" in surf_name:
            xyz_floor = vertices[surf_vert]
            assert len(set(xyz_floor[:, 2])) == 1, f"{surf_name} is not flat"
            z_floor = xyz_floor[0, 2]
            floor_polygons.append(Polygon(xyz_floor[:, :2]))
    # Compute union of polygons with shapely and get its center
    floor_poly = shapely.unary_union(floor_polygons)
    floor_center = floor_poly.centroid.coords[0]
    # Create view point 20 cm above the floor center
    view_point = np.array([floor_center[0], floor_center[1], z_floor + 0.2])
    # Sample equidistant points on a sphere using fibonacci algorithm
    vectors = fibonacci_sphere(n_points=100)
    lines = [HalfLine(Point(view_point), Vector(vec)) for vec in vectors]
    # Loop over surface and check how many lines intersect them
    cpt_lines = {}
    for surf_name, surf_vert in surfaces.items():
        surf_zone = surf_name.split("_")[1]
        if surf_zone == zone:
            points = vertices[surf_vert]
            poly = ConvexPolygon(points)
            for line in lines:
                if intersection(poly, line) != None:
                    try:
                        cpt_lines[surf_name] += 1
                    except KeyError:
                        cpt_lines[surf_name] = 1
    n_intersect = sum(cpt_lines.values())
    assert n_intersect == len(lines), "Some lines are not intersecting any surface"
    angles = {surf_name: cpt / n_intersect for surf_name, cpt in cpt_lines.items()}
    return angles


def get_surface_areas(vertices, surfaces):
    """
    Compute the area of a surface defined by its vertices.
    The surface should be convex.

    Inputs
    ------
    vertices : array-like of shape (n_vertices, 3)
        Array of shape (n_vertices, 3) representing the vertices of the whole building.
    surfaces : dict
        Dictionary mapping surface names to their vertex indices.
    surf_name : str
        Name of the surface for which to compute the area.
    """
    surf_areas = {}
    for surf_name in surfaces:
        # Get points of the surface
        surf_vert = surfaces[surf_name]
        points = vertices[surf_vert]
        # Triangulate the surface
        points_2d = PCA(n_components=2).fit_transform(points)
        poly = Polygon(points_2d)
        triangles = trimesh.creation.triangulate_polygon(poly, engine="triangle")[1]
        triangles = [[surf_vert[i] for i in tri] for tri in triangles]
        mesh = trimesh.Trimesh(vertices, triangles)
        mesh.fix_normals()
        surf_areas[surf_name] = mesh.area
    return surf_areas


def get_surface_areas_from_epjson(epjson_file):
    with open(epjson_file, "r") as f:
        epjson = json.load(f)
    # Loop over all surfaces and compute their areas
    surface_areas = {}
    for surface, properties in epjson["BuildingSurface:Detailed"].items():
        vertices = [list(v.values()) for v in properties["vertices"]]
        vertices_2d = PCA(n_components=2).fit_transform(vertices)
        poly = Polygon(vertices_2d)
        triangles = trimesh.creation.triangulate_polygon(poly, engine="triangle")[1]
        mesh = trimesh.Trimesh(vertices, triangles)
        mesh.fix_normals()
        surface_areas[surface] = mesh.area
    return surface_areas


# TODO: make function to compute surface tilts and azimuths
# For this, get normals from triangulated surfaces


def get_total_outdoor_area(vertices, surfaces, shared_surfaces):
    """
    Compute the total outdoor area of a building.
    """
    surf_areas = get_surface_areas(vertices, surfaces)
    matching_surf = find_matching_surfaces(surfaces)
    res = 0
    for surf, area in surf_areas.items():
        if "Wall" in surf:  # Consider only walls
            if surf not in matching_surf:  # Exclude internal walls
                # Exclude shared walls
                if not any(facade in surf for facade in shared_surfaces):
                    res += area
    return res


def get_zone_trimesh(vertices, surfaces):
    # Triangulate each surface
    triangles_per_zone = {}
    for surf_name, surf_vert in surfaces.items():
        zone = surf_name.split("_")[1]
        if zone not in triangles_per_zone:
            triangles_per_zone[zone] = []
        points_3d = vertices[surf_vert]
        points_2d = PCA(n_components=2).fit_transform(points_3d)
        poly = Polygon(points_2d)
        triangles = triangulate_polygon(poly, engine="triangle")[1]
        triangles = [[surf_vert[i] for i in tri] for tri in triangles]
        triangles_per_zone[zone].append(triangles)
    mesh_per_zone = {}
    for zone, L_triangles in triangles_per_zone.items():
        triangles = np.concatenate(L_triangles)
        mesh = trimesh.Trimesh(vertices, triangles)
        mesh.fix_normals()
        assert mesh.is_watertight, f"The mesh for zone {zone} is not watertight"
        mesh_per_zone[zone] = mesh
    return mesh_per_zone


def get_zone_volume(vertices, surfaces):
    """
    Compute the volume of a zone defined by its vertices and surfaces.

    Inputs
    ------
    vertices : array-like of shape (n_vertices, 3)
        Array of shape (n_vertices, 3) representing the vertices of the whole building.
    surfaces : dict
        Dictionary mapping surface names to their vertex indices.
    """
    mesh_per_zone = get_zone_trimesh(vertices, surfaces)
    return {zone: mesh.volume for zone, mesh in mesh_per_zone.items()}


def check_for_naked_edges(surfaces):
    """
    Raise an error if there are naked edges in the geometry.
    A naked edge is an edge that is present in only one surface.

    Inputs
    ------
    surfaces : dict
        Dictionary mapping surface names to a list with the index of their vertices.
    """
    edge_counts = {}
    for surf_name, surf_vert in surfaces.items():
        for i1, i2 in zip(surf_vert, surf_vert[1:] + [surf_vert[0]]):
            edge = tuple(sorted([i1, i2]))
            if edge in edge_counts:
                edge_counts[edge] += 1
            else:
                edge_counts[edge] = 1
    naked_edges = [edge for edge, count in edge_counts.items() if count == 1]
    if len(naked_edges) > 0:
        raise ValueError(f"Naked edges found in the geometry: {naked_edges}")
    return


def fix_vertex_ordering(vertices, surfaces):
    """
    First compute the centroid of each zone. Then for each surface, compute its centroid and
    check that its vertices are ordered counterclockwise, when seen from the zone centroid.
    """
    # TODO: Implement this function, use centroid of each zone and surface based on mesh
    # # Compute zone centroids and surface centroids
    # zone_vertices = {zone: set() for zone in set(surf_zones)}
    # surf_centroids = []
    # for surf, surf_zone in zip(surfaces, surf_zones):
    #     zone_vertices[surf_zone].update(surf)
    #     surf_centroids.append(np.mean([vertices[v] for v in surf], axis=0))
    # zone_centroids = {
    #     zone: np.mean([vertices[v] for v in zone_vertices[zone]], axis=0)
    #     for zone in zone_vertices
    # }
    # # Check that surfaces are ordered counterclockwise
    # for surf, surf_centroid in zip(surfaces, surf_centroids):
    #     centroid_diff = surf_centroid - zone_centroids[surf_zone]
    #     vec1 = np.array(vertices[surf[1]]) - np.array(vertices[surf[0]])
    #     vec2 = np.array(vertices[surf[2]]) - np.array(vertices[surf[1]])
    #     normal_vec = np.cross(vec1, vec2)
    #     if np.dot(normal_vec, centroid_diff) < 0:
    #         # Surface is clockwise, so reverse its vertices
    #         idx_surf = surfaces.index(surf)
    #         surfaces[idx_surf] = surf[::-1]
    return surfaces


def fibonacci_sphere(n_points):
    """
    Generate equidistant points on the surface of a sphere using the spherical
    Fibonacci lattice method.

    Inputs
    ------
    n_points : int
        Number of points to generate on the sphere.

    Output
    ------
    points : numpy.ndarray
        An array of shape (samples, 3) representing the points on the sphere.
    """
    points = np.zeros((n_points, 3))
    phi = np.pi * (3.0 - np.sqrt(5.0))  # golden angle in radians
    for i in range(n_points):
        y = 1 - (i / float(n_points - 1)) * 2  # y goes from 1 to -1
        radius = np.sqrt(1 - y * y)  # radius at y
        theta = phi * i  # golden angle increment
        x = np.cos(theta) * radius
        z = np.sin(theta) * radius
        points[i] = [x, y, z]
    return points


def find_matching_surfaces(surfaces):
    """
    Find surface that are the same but with different order of vertices.
    This is used to identify surfaces that separate two adjacent zones.
    """
    matching_surfaces = {}
    for surf_name, surf_vert in surfaces.items():
        for surf_name_2, surf_vert_2 in surfaces.items():
            if set(surf_vert) == set(surf_vert_2) and surf_name != surf_name_2:
                matching_surfaces[surf_name] = surf_name_2
                matching_surfaces[surf_name_2] = surf_name
    return matching_surfaces


def create_terraced_house(height):
    """
    Create a terraced house geometry, which consists of 4 zones:
        - 0F (ground floor, e.g. living room)
        - 1FS (first floor, south side, e.g. bedroom)
        - 1FN (first floor, north side, e.g. workroom). Separated from 1FS by an internal wall.
        - 2F (second floor, e.g. attic)

    Inputs:
    -------
    height: float
        Height of the terraced house (in meters). This is typically between
        7 and 10 meters.
    """
    # Define vertices
    vertices = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 0.75, 0.0],
            [0.0, 0.75, 0.0],
            [0.0, 0.0, 0.35],
            [1.0, 0.0, 0.35],
            [1.0, 0.75, 0.35],
            [0.0, 0.75, 0.35],
            [0.0, 0.0, 0.7],
            [1.0, 0.0, 0.7],
            [1.0, 0.75, 0.7],
            [0.0, 0.75, 0.7],
            [0.5, 0.0, 1.0],
            [0.5, 0.75, 1.0],
            [0.5, 0.0, 0.35],
            [0.5, 0.75, 0.35],
            [0.5, 0.75, 0.7],
            [0.5, 0.0, 0.7],
        ]
    )
    vertices *= height
    # Define surfaces (type, zone, vertices)
    surfaces = {
        # 0th floor
        "Floor_0F": [3, 2, 1, 0],
        "EastWall_0F": [0, 1, 5, 14, 4],  # Add vertex 14 to avoid naked edge
        "NorthWall_0F": [1, 2, 6, 5],
        "WestWall_0F": [2, 3, 7, 15, 6],  # Add vertex 15 to avoid naked edge
        "SouthWall_0F": [3, 0, 4, 7],
        "Roof_0F": [7, 4, 14, 15],
        "Roof2_0F": [15, 14, 5, 6],
        # 1st floor, south zone
        "Floor_1FS": [15, 14, 4, 7],
        "EastWall_1FS": [4, 14, 17, 8],
        "SouthWall_1FS": [7, 4, 8, 11],
        "WestWall_1FS": [16, 15, 7, 11],
        "NorthWall_1FS": [17, 14, 15, 16],
        "Roof_1FS": [11, 8, 17, 16],
        # 1st floor, north zone
        "Floor_1FN": [6, 5, 14, 15],
        "EastWall_1FN": [17, 14, 5, 9],
        "NorthWall_1FN": [9, 5, 6, 10],
        "WestWall_1FN": [10, 6, 15, 16],
        "SouthWall_1FN": [16, 15, 14, 17],
        "Roof_1FN": [16, 17, 9, 10],
        # 2th floor,
        # TODO: when renovating the east wall in a corner house, we also renovate
        # the part of the wall on the 2nd floor. Check if this is the right way to model it.
        "Floor_2F": [16, 17, 8, 11],
        "Floor2_2F": [10, 9, 17, 16],
        "EastWall_2F": [8, 17, 9, 12],  # Add vertex 17 to avoid naked edge
        "WestWall_2F": [10, 16, 11, 13],  # Add vertex 16 to avoid naked edge
        "NorthRoof_2F": [12, 9, 10, 13],
        "SouthRoof_2F": [13, 11, 8, 12],
    }
    return vertices, surfaces


def create_apartment(length, width, height, n_zones, frac_south_zone_area=0.5):
    """
    Create an apartment geometry.

    Inputs:
    -------
    length: float
        Length of the apartment (in meters).
    width: float
        Width of the apartment (in meters). Should be smaller than the length.
    height: float
        Height of the apartment (in meters).
    n_zones: int
        The number of zones in the apartment. Can be 1 or 2.
    frac_south_zone_area: float
        Fraction of the apartment area that the south zone occupies.
        Only used when n_zones=2.
    """
    if n_zones not in [1, 2]:
        raise ValueError("n_zones should be 1 or 2")
    # if width > length:
    #     raise ValueError("Width should be smaller than length")
    # Define vertices
    vertices = [
        [0, 0, 0],
        [1, 0, 0],
        [1, 1, 0],
        [0, 1, 0],
        [0, 0, 1],
        [1, 0, 1],
        [1, 1, 1],
        [0, 1, 1],
    ]
    # Define surfaces (type, zone, vertices)
    if n_zones == 1:
        surfaces = {
            "Floor_0F": [3, 2, 1, 0],
            "EastWall_0F": [0, 1, 5, 4],
            "NorthWall_0F": [1, 2, 6, 5],
            "WestWall_0F": [2, 3, 7, 6],
            "SouthWall_0F": [3, 0, 4, 7],
            "Roof_0F": [7, 4, 5, 6],
        }
    if n_zones == 2:
        # Add vertices of the wall that cuts the apartment in two
        new_vertices = [
            [frac_south_zone_area, 0, 0],
            [frac_south_zone_area, 1, 0],
            [frac_south_zone_area, 0, 1],
            [frac_south_zone_area, 1, 1],
        ]
        vertices += new_vertices
        surfaces = {
            # Floor
            "Floor_0FS": [3, 9, 8, 0],
            "Floor_0FN": [9, 2, 1, 8],
            # Walls 0FS
            "SouthWall_0FS": [7, 3, 0, 4],
            "EastWall_0FS": [4, 0, 8, 10],
            "IntWall_0FS": [10, 8, 9, 11],
            "WestWall_0FS": [11, 9, 3, 7],
            # Walls 0FN
            "IntWall_0FN": [11, 9, 8, 10],
            "EastWall_0FN": [10, 8, 1, 5],
            "NorthWall_0FN": [5, 1, 2, 6],
            "WestWall_0FN": [6, 2, 9, 11],
            # Ceiling
            "Roof_0FS": [7, 4, 10, 11],
            "Roof_0FN": [11, 10, 5, 6],
        }
    # Scale vertices
    vertices = np.array(vertices, dtype=float)
    vertices[:, 0] *= length
    vertices[:, 1] *= width
    vertices[:, 2] *= height
    return vertices, surfaces


def fp():
    vertices = np.array(
        [
            [0.0, 0.0, 0.0],  # x,y,z(height), 0th floor-GroundFloorOutline, p0
            [8.0, 0.0, 0.0],  # p1
            [8.0, 10.0, 0.0],  # p2-
            [0.0, 10.0, 0.0],  # p3
            [0.0, 3.3, 0.0],  # 0th floor-Walls, p4
            [0.0, 4.3, 0.0],  # p5
            [0.0, 7.1, 0.0],  # p6-
            [2.1, 7.1, 0.0],  # p7
            [2.1, 5.3, 0.0],  # p8 !!!
            [3.2, 5.3, 0.0],  # p9
            [3.2, 10.0, 0.0],  # p10
            [8.0, 5.3, 0.0],  # p11
            [5.2, 5.3, 0.0],  # p12
            [5.2, 3.5, 0.0],  # p13
            [3.2, 3.5, 0.0],  # p14
            [5.2, 0.0, 0.0],  # p15
            [3.2, 0.0, 0.0],  # p16
            [2.1, 0.0, 0.0],  # p17
            [2.1, 3.3, 0.0],  # p18
            [2.1, 4.3, 0.0],  # p19
            [0.0, 0.0, 2.6],  # 1st floor-CeilingOutline, p20
            [8.0, 0.0, 2.6],  # p21
            [8.0, 10.0, 2.6],  # p22
            [0.0, 10.0, 2.6],  # p23
            [0.0, 3.3, 2.6],  # 1st floor-Walls, p24
            [0.0, 4.3, 2.6],  # p25
            [0.0, 7.1, 2.6],  # p26
            [2.1, 7.1, 2.6],  # p27
            [2.1, 5.3, 2.6],  # p28 !!!
            [3.2, 5.3, 2.6],  # p29
            [3.2, 10.0, 2.6],  # p30
            [8.0, 5.3, 2.6],  # p31
            [5.2, 5.3, 2.6],  # p32
            [5.2, 3.5, 2.6],  # p33
            [3.2, 3.5, 2.6],  # p34
            [5.2, 0.0, 2.6],  # p35
            [3.2, 0.0, 2.6],  # p36
            [2.1, 0.0, 2.6],  # p37
            [2.1, 3.3, 2.6],  # p38
            [2.1, 4.3, 2.6],  # p39
        ]
    )
    surfaces = {
        # Zone 1: Kitchen
        "Floor_Kitchen": [0, 4, 18, 17],
        "SouthWall_Kitchen": [0, 20, 24, 4],
        "WestWall_Kitchen": [4, 24, 38, 18],
        "NorthWall_Kitchen": [17, 18, 38, 37],
        "EastWall_Kitchen": [0, 17, 37, 20],
        "Roof_Kitchen": [20, 37, 38, 24],
        # Zone 2: Toilet
        "Floor_Toilet": [4, 5, 19, 18],
        "SouthWall_Toilet": [4, 24, 25, 5],
        "WestWall_Toilet": [19, 5, 25, 39],
        "NorthWall_Toilet": [18, 19, 39, 38],
        "EastWall_Toilet": [4, 18, 38, 24],
        "Roof_Toilet": [24, 38, 39, 25],
        # Zone 3: Bathroom
        "Floor_Bathroom": [5, 6, 7, 8, 19],
        "SouthWall_Bathroom": [5, 25, 26, 6],
        "WestWall_Bathroom": [7, 6, 26, 27],
        "NorthWall_Bathroom": [8, 7, 27, 28],
        "NorthWall2_Bathroom": [19, 8, 28, 39],
        "EastWall_Bathroom": [5, 19, 39, 25],
        "Roof_Bathroom": [25, 39, 28, 27, 26],
        # Zone 4: Bedroom1
        "Floor_Bedroom1": [6, 3, 10, 9, 8, 7],
        "SouthWall_Bedroom1": [6, 26, 23, 3],
        "SouthWall2_Bedroom1": [8, 28, 27, 7],
        "WestWall_Bedroom1": [3, 23, 30, 10],
        "NorthWall_Bedroom1": [9, 10, 30, 29],
        "EastWall_Bedroom1": [8, 9, 29, 28],
        "EastWall2_Bedroom1": [6, 7, 27, 26],
        "Roof_Bedroom1": [26, 27, 28, 29, 30, 23],
        # Zone 5: LivingRoom
        "Floor_LivingRoom": [9, 10, 2, 11, 12],
        "SouthWall_LivingRoom": [9, 29, 30, 10],
        "WestWall_LivingRoom": [10, 30, 22, 2],
        "NorthWall_LivingRoom": [11, 2, 22, 31],
        "EastWall_LivingRoom": [11, 31, 32, 12],
        "EastWall2_LivingRoom": [12, 32, 29, 9],
        "Roof_LivingRoom": [29, 32, 31, 22, 30],
        # Zone 6: Bedroom2
        "Floor_Bedroom2": [15, 13, 12, 11, 1],
        "SouthWall_Bedroom2": [15, 35, 33, 13],
        "SouthWall2_Bedroom2": [13, 33, 32, 12],
        "WestWall_Bedroom2": [12, 32, 31, 11],
        "NorthWall_Bedroom2": [1, 11, 31, 21],
        "EastWall_Bedroom2": [15, 1, 21, 35],
        "Roof_Bedroom2": [35, 21, 31, 32, 33],
        # Zone 7: Bedroom3
        "Floor_Bedroom3": [16, 14, 13, 15],
        "SouthWall_Bedroom3": [16, 36, 34, 14],
        "WestWall_Bedroom3": [14, 34, 33, 13],
        "NorthWall_Bedroom3": [15, 13, 33, 35],
        "EastWall_Bedroom3": [16, 15, 35, 36],
        "Roof_Bedroom3": [36, 35, 33, 34],
        # Zone 8: Corridor
        "Floor_Corridor": [17, 18, 19, 8, 9, 12, 13, 14, 16],
        "SouthWall_Corridor": [17, 37, 38, 18],
        "SouthWall2_Corridor": [18, 38, 39, 19],
        "SouthWall3_Corridor": [19, 39, 28, 8],
        "WestWall_Corridor": [9, 8, 28, 29],
        "WestWall2_Corridor": [9, 29, 32, 12],
        "NorthWall_Corridor": [13, 12, 32, 33],
        "NorthWall2_Corridor": [16, 14, 34, 36],
        "EastWall_Corridor": [13, 33, 34, 14],
        "EastWall2_Corridor": [17, 16, 36, 37],
        "Roof_Corridor": [37, 36, 34, 33, 32, 29, 28, 39, 38],
    }
    return vertices, surfaces


def show_floor_and_roof_surfaces(vertices, surfaces):
    M = find_matching_surfaces(surfaces)
    floor_surfaces = [s for s in surfaces if "Floor" in s and s not in M]
    roof_surfaces = [s for s in surfaces if "Roof" in s and s not in M]
    # Plot ground floor and top roof
    plot_building(vertices, surfaces, surf_to_show=floor_surfaces)
    plot_building(vertices, surfaces, surf_to_show=roof_surfaces)
    return


def show_zones(vertices, surfaces):
    zones = set([surf.split("_")[1] for surf in surfaces])
    for zone in zones:
        surf_to_show = [surf for surf in surfaces if zone in surf]
        plot_building(vertices, surfaces, surf_to_show, show_vertices=True, title=zone)
    return


def test_volume_calculation():
    vertices, surfaces = fp()
    zones = set([surf.split("_")[1] for surf in surfaces])
    zone_volume = get_zone_volume(vertices, surfaces)
    for zone in zones:
        volume = zone_volume[zone]
        floor_area = get_surface_area(vertices, surfaces, f"Floor_{zone}")
        assert np.isclose(volume, floor_area * 2.6)
    return


if __name__ == "__main__":
    vertices, surfaces = create_apartment(
        width=10, length=6.74, height=2.8, n_zones=2, frac_south_zone_area=0.7
    )
    # show_zones(vertices, surfaces)
    # vertices2, surfaces2 = fp()
    # show_zones(vertices2, surfaces2)
    # show_floor_and_roof_surfaces(vertices2, surfaces2)
    plot_building(vertices, surfaces, surf_to_show="all", show_vertices=False)
