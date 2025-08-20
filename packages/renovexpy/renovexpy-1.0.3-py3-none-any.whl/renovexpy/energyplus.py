import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import renovexpy.geometry as geometry
import renovexpy.utils as utils

curr_dir = Path(__file__).parent


class EPSimulation:

    def __init__(self, vent_type: str, sim_dir: str | Path = None):
        """
        Initialize an EnergyPlus simulation with the idf template that corresponds to
        the ventilation type.

        Inputs:
        -------
        vent_type: str
            The ventilation type to be used.
            Allowed values are: "A", "C1", "C2", "C4a", "D5c".
        """
        # Get the paths to the EnergyPlus executable and IDD file for v24.2 or v24.1
        os = "linux" if sys.platform.startswith("linux") else "windows"
        eplus_dir = None
        for version in ["24-2-0", "24-1-0"]:
            if os == "linux":
                eplus_dir = Path(f"/usr/local/EnergyPlus-{version}")
                if not eplus_dir.exists():  # Snellius
                    eplus_dir = Path().home() / f"EnergyPlus-{version}"
            else:
                eplus_dir = Path(f"C:/EnergyPlusV{version}")
            if eplus_dir.exists():
                break
        assert eplus_dir is not None, f"EnergyPlus v24.2 or v24.1 not found"
        eplus_exec, idd_file = eplus_dir / "energyplus", eplus_dir / "Energy+.idd"
        if os == "windows":
            eplus_exec = eplus_exec.with_suffix(".exe")
        assert eplus_dir.exists(), f"EnergyPlus executable '{eplus_exec}' not found"
        assert idd_file.exists(), f"IDD file '{idd_file}' not found"
        # Store variables
        self.eplus_exec = eplus_exec
        self.idd_file = idd_file
        self.vent_type = vent_type
        if sim_dir is not None:
            self.sim_dir = Path(sim_dir)
            self.sim_dir.mkdir(parents=True, exist_ok=True)
        # Load idf template based on the ventilation type
        assert vent_type in ["A", "C1", "C2", "C4a", "D5c"], "Invalid ventilation type"
        idf_file = curr_dir / f"data/{vent_type}.idf"
        self.epjson = utils.load_epjson_from_idf(idf_file, self.eplus_exec)
        # Load template materials
        mat_file = curr_dir / f"data/materials.idf"
        self.add_materials_and_constructions(mat_file, overwrite=True)
        # Retrieve old zone names
        self.old_zones = list(self.epjson["Zone"].keys())
        # Init pre-defined schedules
        self.init_schedules()
        return

    ### GEOMETRY

    def get_zone_floor_areas(self):
        """Return a dictionary with the floor area (in m2) of each zone."""
        D = {zone: 0 for zone in self.zones}
        vertices, surfaces = self.vertices, self.surfaces
        surf_areas = geometry.get_surface_areas(vertices, surfaces)
        for zone in self.zones:
            for surf_name in surfaces:
                if zone in surf_name and "Floor" in surf_name:
                    # Compute the area and add the area to the dictionary
                    # This is needed when a zone has multiple floors
                    D[zone] += surf_areas[surf_name]
        return D

    def get_zone_volumes(self):
        """Return a dictionary with the volume (in m3) of each zone."""
        return geometry.get_zone_volume(self.vertices, self.surfaces)

    def get_surface_areas(self):
        """Return a dictionary with the area (in m2) of each surface."""
        return geometry.get_surface_areas(self.vertices, self.surfaces)

    def set_geometry(self, building_type: str, building_position: str, **kwargs):
        """
        Set the geometry of the simulated object. Vertices and surfaces are obtained
        based on the building type using functions in the geometry module.

        Inputs:
        -------
        building_type: str
            The type of building to be simulated.
            Allowed values are "terraced_house" or "apartment".
        building_position: str
            The position of the building, which determines which surfaces are shared
            with neighbors.
            For terraced houses, allowed values are "middle" or "corner".
            For apartments, allowed values are NOTE: to fill.
        """
        # Get vertices, surfaces, and shared surfaces
        assert building_type in ["terraced_house", "apartment"], "Invalid building type"
        assert building_position in ["middle", "corner"], "Invalid building position"
        if building_type == "terraced_house":
            height = kwargs.pop("height", 8)
            vertices, surfaces = geometry.create_terraced_house(height)
            if building_position == "middle":
                shared_surfaces = ["WestWall", "EastWall"]
            else:
                shared_surfaces = ["WestWall"]
        elif building_type == "apartment":
            length = kwargs.pop("length", 10)
            width = kwargs.pop("width", 6.74)
            height = kwargs.pop("height", 2.8)
            n_zones = kwargs.pop("n_zones", 2)
            frac_south_zone_area = kwargs.pop("frac_south_zone_area", 0.7)
            vertices, surfaces = geometry.create_apartment(
                length, width, height, n_zones, frac_south_zone_area
            )
            # TODO: add shared surfaces for apartments
        # Store geometry data
        self.building_type = building_type
        self.building_position = building_position
        self.vertices, self.surfaces = vertices, surfaces
        self.shared_surfaces = shared_surfaces
        geometry.check_for_naked_edges(self.surfaces)
        self.zones = list(sorted(set([surf.split("_")[1] for surf in self.surfaces])))
        matching_surf = geometry.find_matching_surfaces(self.surfaces)
        ### Set zones
        self.epjson["Zone"] = {
            zone: {
                "direction_of_relative_north": 0,
                "floor_area": "Autocalculate",
                "multiplier": 1,
                "part_of_total_floor_area": "Yes",
                "type": 1,
                "volume": "Autocalculate",
                "x_origin": 0,
                "y_origin": 0,
                "z_origin": 0,
                "zone_inside_convection_algorithm": "TARP",
            }
            for zone in self.zones
        }
        # Also create a zone list object
        self.epjson["ZoneList"] = {
            "AllZones": {"zones": [{"zone_name": zone} for zone in self.zones]}
        }
        ### Set BuildingSurface:Detailed
        D = {}
        for surf_name, surf_vert in self.surfaces.items():
            surf_base_name, surf_zone = surf_name.split("_")
            # surf_type = surf_base_name.rstrip("0123456789")
            surf_type = [x for x in ["Wall", "Roof", "Floor"] if x in surf_base_name][0]
            # Check if surface is internal, shared or external
            if surf_name in matching_surf:
                out_bc, out_bc_obj = "Surface", matching_surf[surf_name]
                surf_constr = f"Internal{surf_type}_Construction"
            elif surf_base_name in self.shared_surfaces:
                out_bc, out_bc_obj = "Adiabatic", ""
                surf_constr = f"Shared{surf_type}_Construction"
            else:
                if surf_type == "Floor":
                    out_bc, out_bc_obj = (
                        # NOTE: should we use "Ground" for out_bc ?
                        "OtherSideConditionsModel",
                        "Default Slab - Slab Boundary Condition Model - 1",
                    )
                    surf_constr = "GroundFloor_Construction"
                else:  # External Wall or Roof
                    out_bc, out_bc_obj = "Outdoors", ""
                    surf_constr = f"{surf_base_name}_Construction"
            # TODO: as such the roof wall "EastWall_2F" is also insulated like lower
            # floors. Is this realistic?
            # Set construction name
            D[surf_name] = {
                "zone_name": surf_zone,
                "surface_type": surf_type,
                "construction_name": surf_constr,  # NOTE: if the construction for internal
                # components is not symmetric we should use 2 reversed constructions
                "outside_boundary_condition": out_bc,
                "outside_boundary_condition_object": out_bc_obj,
                "sun_exposure": "SunExposed" if out_bc == "Outdoors" else "NoSun",
                "wind_exposure": "WindExposed" if out_bc == "Outdoors" else "NoWind",
                "number_of_vertices": len(surf_vert),
                "vertices": [
                    {
                        f"vertex_{x}_coordinate": val
                        for x, val in zip(["x", "y", "z"], self.vertices[i])
                    }
                    for i in surf_vert
                ],
                "view_factor_to_ground": "Autocalculate",
            }
        self.epjson["BuildingSurface:Detailed"] = D
        # Remove ground slab if not needed
        if "Floor" in self.shared_surfaces:
            self.epjson.pop("Site:GroundDomain:Slab", None)
            self.epjson.pop("SurfaceProperty:OtherSideConditionsModel", None)
        return

    def set_orientation(self, orientation: str):
        """
        Set the orientation of the simulated object. For example, if orentation = "S",
        then the south facade will receive most of the solar radiation.

        Inputs
        ------
        orientation : str
            The orientation of the building.
            Should be in ["W", "SW", "S", "SE", "E", "NE", "N", "NW"].
        """
        D = {
            "W": -180,
            "SW": -135,
            "S": -90,
            "SE": -45,
            "E": 0,
            "NE": 45,
            "N": 90,
            "NW": 135,
        }
        assert orientation in D, f"Orientation should be in {list(D.keys())}"
        self.epjson["Building"]["Building"]["north_axis"] = D[orientation]
        return

    def show_surface_info(self):
        """
        Returns a dataframe with the name, type, zone, area and construction of each surface.
        """
        D = self.epjson["BuildingSurface:Detailed"]
        cols = ["Zone", "Surface", "Construction", "Area [m2]"]
        surf_areas = self.get_surface_areas()
        df = pd.DataFrame(columns=cols, index=range(len(D)))
        for i, (surf_name, surf_params) in enumerate(D.items()):
            df.loc[i, "Zone"] = surf_params["zone_name"]
            df.loc[i, "Surface"] = surf_name
            df.loc[i, "Construction"] = surf_params["construction_name"]
            df.loc[i, "Area [m2]"] = surf_areas[surf_name]
        return df

    ### MATERIALS AND CONSTRUCTIONS

    def set_constructions(
        self,
        floor_type: str,
        floor_insulation: list | None,
        roof_insulation: list | None,
        wall_insulation: dict[str, list] | list | None,
    ):
        """
        Set construction for each surface (except windows) of the simulated object.
        Should be used after the method `load_materials_and_constructions`.

        Inputs:
        -------
        """

        def apply_insulation(constr, insulation_params):
            constr = deepcopy(constr)
            if insulation_params is not None:
                ins_mat, ins_pos, ins_R = insulation_params
                if ins_R > 0:
                    ins_layer = f"{ins_mat}_R={ins_R}"
                    if ins_pos == "Internal":
                        constr = constr + [ins_layer]
                    elif ins_pos == "External":
                        constr = [ins_layer] + constr
                    elif ins_pos == "Cavity":
                        cavity_idx = constr.index("Air_Gap_Cavity")
                        constr[cavity_idx] = ins_layer
            return constr

        D_bs = self.epjson["BuildingSurface:Detailed"]
        surf_types = set([x["construction_name"].split("_")[0] for x in D_bs.values()])
        ### Define constructions
        constructions = {}
        assert floor_type in ["Wood", "Concrete"], "Invalid floor type"
        # Floor
        base_floor = ["Plywood_19mm"] if floor_type == "Wood" else ["Concrete_200mm"]
        constructions["GroundFloor"] = apply_insulation(base_floor, floor_insulation)
        # Roof
        base_roof = ["Plywood_19mm"]
        for surf_type in surf_types:
            if "Roof" in surf_type:
                constructions[surf_type] = apply_insulation(base_roof, roof_insulation)
        # Wall
        base_wall = ["Brick_100mm", "Air_Gap_Cavity", "Brick_100mm"]
        for surf_type in surf_types:
            if "Wall" in surf_type:
                if isinstance(wall_insulation, list):
                    constr = apply_insulation(base_wall, wall_insulation)
                elif isinstance(wall_insulation, dict):
                    constr = apply_insulation(base_wall, wall_insulation[surf_type])
                constructions[surf_type] = constr
        # Internal / Shared
        constructions["InternalFloor"] = constructions["InternalRoof"] = base_floor
        constructions["SharedFloor"] = constructions["SharedRoof"] = base_floor
        constructions["InternalWall"] = "Gypsum_Cavity_Gypsum"
        constructions["SharedWall"] = base_wall
        # Update self.epjson["Construction"]
        layers = ["outside_layer"] + [f"layer_{k}" for k in range(2, 10)]
        D = {}
        for surf_type in surf_types:
            # Check that construction is defined
            assert surf_type in constructions, f"No construction for {surf_type}"
            constr = constructions[surf_type]
            D[surf_type] = {}
            if isinstance(constr, str):  # Directly use pre-defined construction
                assert constr in self.epjson["Construction"], f"Unknown {constr}"
                D[surf_type] = self.epjson["Construction"][constr]
            else:  # Create new construction from list of materials
                for idx, mat_name in enumerate(constr):
                    # If the material is not already defined, create it
                    if not any(
                        mat_name in self.epjson[f]
                        for f in [
                            "Material",
                            "Material:AirGap",
                            "WindowMaterial:Glazing",
                            "WindowMaterial:Gas",
                        ]
                    ):
                        self.set_material(mat_name)
                    D[surf_type][layers[idx]] = mat_name
        # Rename keys in D by adding "_Construction"
        D = {surf_type + "_Construction": constr for surf_type, constr in D.items()}
        self.epjson["Construction"].update(D)
        return

    def set_material(self, mat_name):
        """
        Given an existing material, create a duplicate with a different thickness.

        Inputs:
        -------
        mat_name: str
            Name of the material to be used. The name should provide either the
            thickness of the material (e.g. "Brick_80mm"), or its R-value
            (e.g. "Brick_R=1").

        """
        # Extract base material
        base_mat, val = mat_name.rsplit("_", 1)
        # Get properties of the base material
        properties = None
        for mat_k in self.epjson["Material"]:
            base_mat_k = mat_k.rsplit("_", 1)[0]
            if base_mat == base_mat_k:
                properties = self.epjson["Material"][mat_k]
                break
        assert properties is not None, f"Material '{base_mat}' not found"
        # Calculate thickness from val
        if val.endswith("mm"):
            th = float(val[:-2]) / 1000
        elif val.startswith("R="):
            # Calculate thickness to match R-value
            R_val = float(val[2:])
            th = properties["conductivity"] * R_val
        else:
            raise ValueError(f"Invalid material name '{mat_name}'")
        # Create new material
        self.epjson["Material"][mat_name] = deepcopy(properties)
        self.epjson["Material"][mat_name]["thickness"] = th
        return

    def add_materials_and_constructions(self, idf_file, overwrite=False):
        """
        Load materials, constructions and glazings from an IDF file.
        These materials and constructions are then used when creating the walls,
        roofs, floors and windows.

        Inputs:
        -------
        input_file: str or Path
            Path to the IDF file with the materials/constructions to be used.
        overwrite: bool
            Whether to overwrite the existing materials/constructions from the
            original IDF template.

        """
        fields_to_update = [
            "Material",
            "Material:AirGap",
            "WindowMaterial:Glazing",
            "WindowMaterial:Gas",
            "WindowMaterial:Shade",
            "Construction",
            "WindowProperty:FrameAndDivider",
        ]
        epjson = utils.load_epjson_from_idf(idf_file, self.eplus_exec)
        for field in fields_to_update:
            if overwrite:
                self.epjson[field] = {}
            if field in epjson:
                self.epjson[field].update(epjson[field])
        return

    def set_windows_old(self, params_per_window):
        """
        Add windows to the simulated object. Note that only windows on exterior and
        non-shared walls are allowed.

        Inputs:
        -------
        params_per_window: dict
            Dictionary with the windows to be added. The keys are the names of the
            surfaces where the windows will be added, and the values are tuples with
            the glazing, frame and WWR, e.g. ("SingleGlz", "wood", 0.5).
        """
        D = {}
        D_bs = self.epjson["BuildingSurface:Detailed"]
        for surf, (glazing, frame, wwr) in params_per_window.items():
            # Check that surface exists, is a wall and is outdoor
            assert surf in self.surfaces, f"Surface '{surf}' is not defined"
            assert D_bs[surf]["surface_type"] == "Wall", f"{surf} is not a wall"
            assert (
                D_bs[surf]["outside_boundary_condition"] == "Outdoors"
            ), f"{surf} is not outdoors"
            assert glazing in self.epjson["Construction"], f"{glazing} is not defined"
            assert (
                f"{frame}_frame" in self.epjson["WindowProperty:FrameAndDivider"]
            ), f"{frame}_frame is not defined"
            surf_vert = self.surfaces[surf]
            D[f"Window_{surf}"] = {
                "surface_type": "Window",
                "construction_name": glazing,
                "building_surface_name": surf,
                "Frame_and_Divider_Name": f"{frame}_frame",
                "Multiplier": 1,
                "Number_of_Vertices": len(surf_vert),
            }
            # Scale surface based on window to wall ratio
            # NOTE: if surface is not convex, this will not work
            xyz_surf = np.array([self.vertices[i] for i in surf_vert])
            xyz_center = xyz_surf.mean(axis=0)
            xyz_window = xyz_center + (xyz_surf - xyz_center) * (wwr**0.5)
            for i, (x, y, z) in enumerate(xyz_window):
                D[f"Window_{surf}"][f"vertex_{i + 1}_x_coordinate"] = x
                D[f"Window_{surf}"][f"vertex_{i + 1}_y_coordinate"] = y
                D[f"Window_{surf}"][f"vertex_{i + 1}_z_coordinate"] = z
        self.epjson["FenestrationSurface:Detailed"] = D
        return

    def set_windows(self, glazing: str, window_frame: str, WWR: float):
        """
        Add windows to the simulated object. Note that only windows on exterior and
        non-shared walls are allowed.

        Inputs:
        -------
        params_per_window: dict
            Dictionary with the windows to be added. The keys are the names of the
            surfaces where the windows will be added, and the values are tuples with
            the glazing, frame and WWR, e.g. ("SingleGlz", "wood", 0.5).
        """
        # Do checks
        assert glazing in self.epjson["Construction"], f"{glazing} is not defined"
        assert (
            f"{window_frame}_frame" in self.epjson["WindowProperty:FrameAndDivider"]
        ), f"{window_frame}_frame is not defined"
        assert 0 <= WWR <= 1, f"Window to wall ratio (WWR) should be between 0 and 1"
        # Create params_per_window
        if self.building_type == "terraced_house":
            self.window_surfaces = [
                "NorthWall_0F",
                "SouthWall_0F",
                "NorthWall_1FN",
                "SouthWall_1FS",
            ]
        elif self.building_type == "apartment":
            self.window_surfaces = ["NorthWall_0FN", "SouthWall_0FS"]  # TODO: check
        params_per_window = {
            surf: (glazing, window_frame, WWR) for surf in self.window_surfaces
        }
        # Fill FenestrationSurface:Detailed
        D = {}
        D_bs = self.epjson["BuildingSurface:Detailed"]
        for surf, (glazing, frame, wwr) in params_per_window.items():
            # Check that surface exists, is a wall and is outdoor
            assert surf in self.surfaces, f"Surface '{surf}' is not defined"
            assert D_bs[surf]["surface_type"] == "Wall", f"{surf} is not a wall"
            assert (
                D_bs[surf]["outside_boundary_condition"] == "Outdoors"
            ), f"{surf} is not outdoors"
            assert glazing in self.epjson["Construction"], f"{glazing} is not defined"
            assert (
                f"{frame}_frame" in self.epjson["WindowProperty:FrameAndDivider"]
            ), f"{frame}_frame is not defined"
            surf_vert = self.surfaces[surf]
            D[f"Window_{surf}"] = {
                "surface_type": "Window",
                "construction_name": glazing,
                "building_surface_name": surf,
                "Frame_and_Divider_Name": f"{frame}_frame",
                "Multiplier": 1,
                "Number_of_Vertices": len(surf_vert),
            }
            # Scale surface based on window to wall ratio
            # NOTE: if surface is not convex, this will not work
            xyz_surf = np.array([self.vertices[i] for i in surf_vert])
            xyz_center = xyz_surf.mean(axis=0)
            xyz_window = xyz_center + (xyz_surf - xyz_center) * (wwr**0.5)
            for i, (x, y, z) in enumerate(xyz_window):
                D[f"Window_{surf}"][f"vertex_{i + 1}_x_coordinate"] = x
                D[f"Window_{surf}"][f"vertex_{i + 1}_y_coordinate"] = y
                D[f"Window_{surf}"][f"vertex_{i + 1}_z_coordinate"] = z
        self.epjson["FenestrationSurface:Detailed"] = D
        return

    def set_airtightness(self, airtightness, wind_exposure="normal", flow_exp=0.65):
        """
        Inputs
        ------
        airtightness : float
            The qv10 airtightness, i.e. the air leakage rate at a pressure of 10 Pascals,
            in dm3/(s.m2). This value typically ranges from 0.4 to 1.
        wind_exposure : str, optional
            The wind exposure condition, one of "sheltered," "normal," or "exposed"
            (default: "normal").
        flow_exp : float, optional
            The flow exponent used in the Qv10 method (default: 0.65).
        """
        # Get the espilon value based on building height
        height = self.vertices[:, 2].max() - self.vertices[:, 2].min()
        eps_value = 1.5 if height > 30 else 1.2 if height > 10 else 1
        # Get the number of exterior surface  per zone
        n_zone_ext_surf = {zone: 0 for zone in self.zones}
        for surf_info in self.epjson["BuildingSurface:Detailed"].values():
            surf_zone = surf_info["zone_name"]
            if surf_info["outside_boundary_condition"] == "Outdoors":
                n_zone_ext_surf[surf_zone] += 1

        ### Loop over zones and calculate the ACH
        zone_floor_areas = self.get_zone_floor_areas()
        zone_volumes = self.get_zone_volumes()
        D_wind_exp = {
            "sheltered": [0.01, 0.1, 0.02],
            "normal": [0.01, 0.02, 0.03],
            "exposed": [0.01, 0.03, 0.05],
        }
        D_inf = {}
        assert wind_exposure in D_wind_exp, f"Invalid wind exposure '{wind_exposure}'"
        for zone in self.zones:
            n_ext_surf = n_zone_ext_surf[zone]
            floor_area, volume = zone_floor_areas[zone], zone_volumes[zone]
            # Get the wind exposure coefficient
            wind_coef = D_wind_exp[wind_exposure][min(n_ext_surf, 2)]
            # Calculate the air leakage rate at 50 Pa (n50) using the Qv10 method formula
            n50 = (5**flow_exp) * airtightness * 3.6 * floor_area / volume
            # Calculate the air changes per hour (ACH) using the provided formula
            ach = 2 * n50 * eps_value * wind_coef
            # Fill the ZoneInfiltration:DesignFlowRate object
            D_inf[f"Infiltration_{zone}"] = {
                "air_changes_per_hour": ach,
                "constant_term_coefficient": 1,
                "design_flow_rate_calculation_method": "AirChanges/Hour",
                "schedule_name": "On 24/7",
                "temperature_term_coefficient": 0,
                "velocity_squared_term_coefficient": 0,
                "velocity_term_coefficient": 0,
                "zone_or_zonelist_or_space_or_spacelist_name": zone,
            }
        self.epjson["ZoneInfiltration:DesignFlowRate"] = D_inf
        return

    ### OCCUPANT BEHAVIOR

    def init_schedules(self):
        """Load pre-defined schedules for the simulation."""
        D_sched = {
            # Common schedules
            "Always_50": {"0-24": 50},  # Used to disable cooling
            "On 24/7": {"0-24": 1},
            "Off 24/7": {"0-24": 0},
            ### Heating setpoints
            # Schedules for heated zones
            "Always_21": {"0-24": 21},
            "N17_D19": {"23-9": 17.5, "9-23": 19.5},
            "N15_D19": {"23-9": 15, "9-23": 19.5},
            "N17_D20": {"23-9": 17, "9-23": 20.5},
            "N15_M17_D16_E19": {"23-6": 15.5, "6-9": 17.5, "9-18": 16.5, "18-23": 19.5},
            # Schedules for unheated zones (should be consistent with the schedule
            # used for heated zones)
            "Always_17": {"0-24": 17},  # "Always_21"/"N17_D20"
            "Always_17.5": {"0-24": 17.5},  # "N17_D19"
            "Always_15": {"0-24": 15},  # "N15_D19"
            "Always_15.5": {"0-24": 15.5},  # "N15_M17_D16_E19"
            "Always_10": {"0-24": 10},  # Used for the attic only
        }
        sched_file = curr_dir / "data/schedules.idf"
        self.add_schedules(sched_file, D_sched)
        # Init Schedule:File
        self.epjson["Schedule:File"] = {}
        return

    def add_schedules(self, sched_file=None, D_sched={}, overwrite=False):
        """
        Load schedules (heating, occupancy, etc...) from a IDF file or/and a dictionary.

        Inputs:
        -------
        schedule_file: str or Path or None
            Path to the IDF file with the schedules to be imported.
        D_sched: dict
            A dictionary that can be used to manually define schedule.
            Each key is the name of the schedule and its value is either a list of
            24 values (one for per hour) or a dictionary mapping hour periods to values,
            e.g. {"22-6": 18, "6-8": 22, "8-22": 20}.
        overwrite: bool
            Whether to overwrite the existing schedules from the initial template file.
        """

        assert sched_file != None or D_sched != {}, "No schedules provided"
        if sched_file is not None:  # Load schedules from file
            epjson = utils.load_epjson_from_idf(sched_file, self.eplus_exec)
            assert "Schedule:Compact" in epjson, "No schedules found in file"
        ### Update the fields in epjson
        if overwrite:
            self.epjson["Schedule:Compact"] = {}
        # Add schedules from file
        if sched_file is not None:
            self.epjson["Schedule:Compact"].update(epjson["Schedule:Compact"])
        # Add manually defined schedules
        # TODO: allow schedules that vary through time (e.g. occupancy on week days/ends)
        for sched_name, sched in D_sched.items():
            assert isinstance(sched, dict) or (
                type(sched) in [list, np.ndarray] and len(sched) == 24
            ), f"'{sched_name}' should be a list with 24 values or a dictionary mapping time periods with values"
            if isinstance(sched, dict):
                sched = utils.convert_schedule_to_list(sched)
            D = {
                "data": [{"field": "Through: 31 Dec"}, {"field": "For: AllDays"}],
                "schedule_type_limits_name": "Any Number",
            }
            for i in range(24):
                D["data"].append({"field": f"Until: {(i+1)}:00"})
                D["data"].append({"field": sched[i]})
            self.epjson["Schedule:Compact"][sched_name] = D
        return

    def set_heating(self, heated_zones: list[str], heating_setpoint: str):
        """
        Set the heating temperature schedules in each zone. Cooling schedules are set
        to 50°C for all zones (no cooling). Available setpoints for heated/non-heated
        zones are based on the WoON data.

        Inputs:
        -------
        heating_setpoint: str
            The heating setpoint to be used. Should be one of the following:
            "Always_21", "N17_D20", "N17_D19", "N15_D19", "N15_M17_D16_E19".
        heated_zones: list
            The zones to be heated. Non-heated zones will be modelled as heated but with
            a lower setpoint that is automatically selected based on the heating
            setpoint.
        """
        D_setpoints = {
            # Heating / No-heating setpoints
            "Always_21": "Always_17",
            "N17_D20": "Always_17",
            "N17_D19": "Always_17.5",
            "N15_D19": "Always_15",
            "N15_M17_D16_E19": "Always_15.5",
        }
        # Do checks
        if heating_setpoint not in D_setpoints:
            raise KeyError(f"Supported setpoints are: {list(D_setpoints.keys())}")
        if any([zone not in self.zones for zone in heated_zones]):
            raise KeyError(f"Valid zones are: {self.zones}.")
        ### Set ThermostatSetpoint:DualSetpoint (heating and cooling setpoints)
        D = {}
        for zone in self.zones:
            if zone in heated_zones:
                sched_name = heating_setpoint
            elif zone == "2F":  # Attic
                sched_name = "Always_10"
            else:
                sched_name = D_setpoints[heating_setpoint]
            D[f"HeatingSetpoint_{zone}"] = {
                "cooling_setpoint_temperature_schedule_name": "Always_50",  # No cooling
                "heating_setpoint_temperature_schedule_name": sched_name,
            }
        self.epjson["ThermostatSetpoint:DualSetpoint"] = D
        ### Set ZoneHVAC:Baseboard:RadiantConvective:Water (usage schedule)
        D = {}
        for zone in self.zones:
            frac_rad_people = 0.1
            D[f"{zone} Water Radiator"] = {
                "availability_schedule_name": "On 24/7",  # Always on
                "design_object": "Water Radiator Design Object",
                "inlet_node_name": f"{zone} Water Radiator Hot Water Inlet Node",
                "outlet_node_name": f"{zone} Water Radiator Hot Water Outlet Node",
                "rated_average_water_temperature": 80.0,
                "rated_water_mass_flow_rate": 0.063,
                "maximum_water_flow_rate": "Autosize",
            }
            # Set fraction of radiant energy for each surface
            vertices, surfaces = self.vertices, self.surfaces
            frac_radiant_surf = geometry.get_approximate_solid_angles(
                vertices, surfaces, zone
            )
            surf_fractions = []
            for surf_name, frac_rad in frac_radiant_surf.items():
                surf_fractions.append(
                    {
                        "fraction_of_radiant_energy_to_surface": frac_rad
                        * (1 - frac_rad_people),
                        "surface_name": surf_name,
                    }
                )
            D[f"{zone} Water Radiator"]["surface_fractions"] = surf_fractions
        self.epjson["ZoneHVAC:Baseboard:RadiantConvective:Water"] = D
        # Set ZoneHVAC:Baseboard:RadiantConvective:Water:Design
        self.epjson["ZoneHVAC:Baseboard:RadiantConvective:Water:Design"] = {
            "Water Radiator Design Object": {
                "convergence_tolerance": 0.01,
                "fraction_of_autosized_heating_design_capacity": 3.0,
                "fraction_of_radiant_energy_incident_on_people": frac_rad_people,
                "fraction_radiant": 0.3,
                "heating_design_capacity_method": "FractionOfAutosizedHeatingCapacity",
            }
        }
        return

    def load_occupancy_schedule(self, n_occupants: int) -> dict:
        """
        Load occupancy schedules from WoON data, based on the number of occupants.
        """
        # Load data and filter columns
        df = pd.read_csv(curr_dir / "data/occupancy_profiles.csv")
        df = df.filter(like=f"{n_occupants}P")
        df.columns = df.columns.str.replace(f"{n_occupants}P", "").str.strip()
        # Compute maximum number of occupants per zone
        self.n_occ_per_zone = {}
        for zone in self.zones:
            cols = [f"{zone} Weekday", f"{zone} Weekend"]
            self.n_occ_per_zone[zone] = df[cols].max(axis=None)
            # Normalize the values
            if self.n_occ_per_zone[zone] > 0:
                df[cols] /= self.n_occ_per_zone[zone]
        days_type = {
            "monday": "Weekday",
            "tuesday": "Weekday",
            "wednesday": "Weekday",
            "thursday": "Weekday",
            "friday": "Weekday",
            "saturday": "Weekend",
            "sunday": "Weekend",
            # Other days
            "customday1": "Weekday",
            "customday2": "Weekday",
            "holiday": "Weekday",
            "summerdesignday": "Weekday",
            "winterdesignday": "Weekday",
        }
        # Init schedules fields in needed
        for field in ["Schedule:Day:Hourly", "Schedule:Week:Daily", "Schedule:Year"]:
            if field not in self.epjson:
                self.epjson[field] = {}
        for zone in self.zones:
            for day_type in ["Weekday", "Weekend"]:
                # Add daily schedules
                col = f"{zone} {day_type}"
                hourly_values = df[col].tolist()
                day_sched_name = f"Occupancy_{col.replace(' ', '_')}"
                self.epjson["Schedule:Day:Hourly"][day_sched_name] = {
                    "schedule_type_limits_name": "Fraction",
                    **{f"hour_{i+1}": hourly_values[i] for i in range(24)},
                }
            # Add weekly schedules
            sched_name = f"Occupancy_{zone}"
            self.epjson["Schedule:Week:Daily"][sched_name] = {
                f"{day}_schedule_day_name": f"{sched_name}_{day_type}"
                for day, day_type in days_type.items()
            }
            # Define yearly schedules
            self.epjson["Schedule:Year"][sched_name] = {
                "schedule_type_limits_name": "Fraction",
                "schedule_weeks": [
                    {
                        "schedule_week_name": sched_name,
                        "start_month": 1,
                        "start_day": 1,
                        "end_month": 12,
                        "end_day": 31,
                    }
                ],
            }
            # Remove occupancy schedules from Schedule:Compact because they conflict
            # with the ones defined in Schedule:Year
            if sched_name in self.epjson["Schedule:Compact"]:
                del self.epjson["Schedule:Compact"][sched_name]
        return

    def make_occupancy_schedule(self, n_occupants: int):
        """
        Add two attributes to the instance:
            - the occupancy schedule per zone for each hour of the year
            - the maximum number of occupants per zone
        These schedules are selected from the WoON profiles, depending on n_occupants.
        """
        df = pd.read_csv(curr_dir / "data/occupancy_profiles.csv")
        df = df.filter(like=f"{n_occupants}P")
        df.columns = df.columns.str.replace(f"{n_occupants}P", "").str.strip()
        # Compute maximum number of occupants per zone
        n_occ_per_zone = {}
        for zone in self.zones:
            cols = [f"{zone} Weekday", f"{zone} Weekend"]
            n_occ_per_zone[zone] = df[cols].max(axis=None)
            # Normalize the values
            if n_occ_per_zone[zone] > 0:
                df[cols] /= n_occ_per_zone[zone]
        ### Create occupancy schedule
        hourly_occ = pd.DataFrame(
            data=np.zeros((8760, len(self.zones))),
            columns=self.zones,
            index=pd.date_range(start="2023-01-01 00:00", periods=8760, freq="h"),
        )
        for zone in self.zones:
            # Set weekdays
            mask = hourly_occ.index.dayofweek < 5
            n_weekdays = mask.sum() // 24
            hourly_occ.loc[mask, zone] = np.tile(df[f"{zone} Weekday"], n_weekdays)
            # Set weekends
            mask = hourly_occ.index.dayofweek >= 5
            n_weekends = mask.sum() // 24
            hourly_occ.loc[mask, zone] = np.tile(df[f"{zone} Weekend"], n_weekends)
        # Add binary schedule for the whole house (1 if any zone is occupied)
        hourly_occ["any"] = hourly_occ.any(axis=1).astype(int)
        # Save occupancy schedules in csv file
        sched_file = self.sim_dir / "occupancy.csv"
        hourly_occ.to_csv(sched_file, index=False)
        # Store attributes
        self.hourly_occ = hourly_occ
        self.n_occ_per_zone = n_occ_per_zone
        return

    def set_occupants(self, n_occupants: int, activity_level: str):
        """
        Set the occupancy schedule per zone based on the number of occupants
        using WoON profiles.

        Inputs
        ------
        n_occupants: int
            Number of occupants. It is used to select the corresponding
            occupancy profile from the WoON data. Only n_occupants = 1, 2 and 4
            are supported.
        activity_level: str
            The activity level of occupants = "low", "mid" or "high". It sets the CO2
            generation rate and the watts per person for internal gains.
        """
        # Do checks
        if activity_level not in ["low", "mid", "high"]:
            raise ValueError(f"Invalid activity level '{activity_level}'")
        if n_occupants not in [1, 2, 4]:
            raise ValueError(f"Number of occupants should be in [1, 2, 4]")
        # Define watts per person and CO2 generation rate based on activity level
        D_act_level = {
            # CO2 gen rate and watts per person
            "low": (3.82e-8, 80),
            "mid": (4.51e-8, 100),
            "high": (5.85e-8, 120),
        }
        co2_gen_rate, wpp = D_act_level[activity_level]
        # Make occupancy schedule
        self.make_occupancy_schedule(n_occupants)

        # Fill "People" and "Schedule:File" fields
        D = {}
        for col_idx, zone in enumerate(self.zones):
            D[f"People_{zone}"] = {
                "activity_level_schedule_name": f"OccupantActivity_{wpp}W",
                # if air_velocity is given, then a thermal comfort model must also be given
                # "air_velocity_schedule_name": "Default Air Velocity for Comfort Calculations",
                "carbon_dioxide_generation_rate": co2_gen_rate,
                "enable_ashrae_55_comfort_warnings": "No",
                "fraction_radiant": 0.3,
                "mean_radiant_temperature_calculation_type": "EnclosureAveraged",
                "number_of_people": self.n_occ_per_zone[zone],
                "number_of_people_calculation_method": "People",
                "number_of_people_schedule_name": f"Occupancy_{zone}",
                "people_per_zone_floor_area": 0.04,
                "sensible_heat_fraction": "Autocalculate",
                "zone_or_zonelist_or_space_or_spacelist_name": zone,
            }
            # Add schedule to Schedule:File
            self.epjson["Schedule:File"][f"Occupancy_{zone}"] = {
                "schedule_type_limits_name": "Fraction",
                "file_name": str(self.sim_dir / f"occupancy.csv"),
                "column_number": col_idx + 1,
                "rows_to_skip_at_top": 1,
            }
            # Remove schedule from Schedule:Compact because to avoid conflicts
            if f"Occupancy_{zone}" in self.epjson["Schedule:Compact"]:
                del self.epjson["Schedule:Compact"][f"Occupancy_{zone}"]
        self.epjson["People"] = D
        # Store n_occupants
        self.n_occupants = n_occupants
        return

    def make_window_ventilation_schedule(self, window_vent_profile: int):
        """
        Returns a schedule with the ACH due to window ventilation for each
        hour of the year and each zone
        """
        df = pd.DataFrame(
            data=np.zeros((8760, len(self.zones))),
            columns=self.zones,
            index=pd.date_range(start="2023-01-01 00:00", periods=8760, freq="h"),
        )
        # Define masks for time periods
        mask = {
            "7-19": (df.index.hour >= 7) & (df.index.hour < 19),
            "19-7": (df.index.hour >= 19) | (df.index.hour < 7),
            "6-8": (df.index.hour >= 8) & (df.index.hour < 19),
            "19-22": (df.index.hour >= 22) | (df.index.hour < 6),
            "may-sept": (df.index.month >= 5) & (df.index.month <= 9),
        }
        occ_mask = self.hourly_occ > 0
        if window_vent_profile == 1:
            # 19-7: 1F ajar
            df.loc[mask["19-7"], ["1FS", "1FN"]] = 1
        elif window_vent_profile == 2:
            # 1F ajar all time, but wide open in may-sept between 6-8 and 19-22
            df[["1FS", "1FN"]] = 1
            M = mask["may-sept"] & (mask["6-8"] | mask["19-22"])
            df.loc[M, ["1FS", "1FN"]] = 3
        elif window_vent_profile == 3:
            # Windows closed all year
            pass
        elif window_vent_profile == 4:
            # 1F ajar all year, but open in may-sept between 7-19 if house is occupied
            # 0F ajar in the latter case too
            df[["1FS", "1FN"]] = 1
            M = mask["may-sept"] & mask["7-19"] & occ_mask.any(axis=1)
            df.loc[M, ["1FS", "1FN"]] = 3
            df.loc[M, "0F"] = 1
        # TODO: what about the attic? We dont have windows there, but maybe we should
        # also set a ventilation schedule for it?
        return df

    def make_grilles_ventilation_schedule(self, use_vent_grilles: bool):
        """
        Returns a schedule with the ACH due to grilles ventilation for each
        hour of the year and each zone.
        """
        df = pd.DataFrame(
            data=np.zeros((8760, len(self.zones))),
            columns=self.zones,
            index=pd.date_range(start="2023-01-01 00:00", periods=8760, freq="h"),
        )
        # Get grilles ventilation ACH per zone
        zone_areas = self.get_zone_floor_areas()
        zone_volumes = self.get_zone_volumes()
        zone_ach = {
            zone: 0.7 * 3.6 * zone_areas[zone] / zone_volumes[zone]
            for zone in self.zones
        }
        # Grilles closed on no grilles (type D)
        if not use_vent_grilles or self.vent_type.startswith("D"):  # No ventilation
            return df
        # Grilles open
        for zone, ach in zone_ach.items():
            if self.vent_type == "A":
                df[zone] = ach
            elif self.vent_type.startswith("C"):
                # Fully open in summer, half-open otherwise
                mask = (df.index.month >= 5) & (df.index.month <= 9)
                df.loc[mask, zone] = ach
                df.loc[~mask, zone] = ach / 2
        return df

    def set_natural_ventilation(self, window_vent_profile: int, use_vent_grilles: bool):
        """
        Set natural ventilation in each zone, based on different window
        ventilation profiles and whether ventilation grilles are used.

        Inputs:
        -------
        window_vent_profile: int
            One of 4 profiles:
            1. 1F between 19-7 if temperature condition is met
            2. 1F ajar all time, but wide open in may-sept between 6-8 and 19-22
            3. Windows closed all year
            4. 1F ajar all year, but wide open in may-sept between 7-19 if house is occupied.
        use_vent_grilles: bool
            Whether to use ventilation grilles or not. For type D ventilation, this
            doesn't matter, as there are no grilles.
        """
        # TODO: For profile 1, the ventilation grilles are also closed/open based on,
        # temperature. Ideally we want them to be always open. This explains
        # the weird trend in sensivity analysis.
        if window_vent_profile not in [1, 2, 3, 4]:
            raise ValueError("Window ventilation profile should be in [1, 2, 3, 4]")
        # Make hourly ventilation schedule for the whole year
        window_vent = self.make_window_ventilation_schedule(window_vent_profile)
        grilles_vent = self.make_grilles_ventilation_schedule(use_vent_grilles)
        df_vent = window_vent + grilles_vent
        max_ach_per_zone = df_vent.max(axis=0)
        # Normalize to max ACH per zone
        for zone, max_ach in max_ach_per_zone.items():
            if max_ach > 0:
                df_vent[zone] = df_vent[zone] / max_ach
        df_vent.to_csv(self.sim_dir / "ventilation.csv", index=False)

        # Set ZoneVentilation:DesignFlowRate
        D = {}
        for col_idx, zone in enumerate(self.zones):
            D[f"NaturalVentilation_{zone}"] = {
                "air_changes_per_hour": max_ach_per_zone[zone],
                "constant_term_coefficient": 1,
                "delta_temperature": 0 if window_vent_profile == 1 else -100,
                "design_flow_rate_calculation_method": "AirChanges/Hour",
                "fan_pressure_rise": 0,
                "fan_total_efficiency": 1,
                "maximum_indoor_temperature": 100,
                "maximum_outdoor_temperature": 100,
                "maximum_wind_speed": 40,
                "minimum_indoor_temperature": 19 if window_vent_profile == 1 else -100,
                "minimum_outdoor_temperature": -100,
                "schedule_name": "On 24/7",
                "temperature_term_coefficient": 0,
                "velocity_squared_term_coefficient": 0,
                "velocity_term_coefficient": 0,
                "ventilation_type": "Natural",
                "zone_or_zonelist_or_space_or_spacelist_name": zone,
            }
            # Add schedule to Schedule:File
            self.epjson["Schedule:File"][f"NaturalVentilation_{zone}"] = {
                "schedule_type_limits_name": "Fraction",
                "file_name": str(self.sim_dir / f"ventilation.csv"),
                "column_number": col_idx + 1,
                "rows_to_skip_at_top": 1,
            }
        self.epjson["ZoneVentilation:DesignFlowRate"] = D
        return

    def set_mechanical_ventilation(self, mech_vent_profile: int):
        """
        Set the mechanical ventilation for each zone.
        If vent_type = A, there is no MV.
        If vent_type = C1 or C2, intensity is low, medium, or (low+medium)/2.
        Ideally, the latter one should be low/high depending on occupancy, but E+ doesnt
        allow to do that easily, so we use a constant avg vent level instead.
        If vent_type = C4a or D5c, intensity is low, medium, or CO2 controlled.

        Inputs:
        -------
        usage_sched: dict
            A dictionary mapping each zone to the name of the schedule to be used for
            mechanical ventilation.
        mech_vent_profile: int
            The mechanical ventilation profile, one of 1, 2, 3.
        """
        if mech_vent_profile not in (L := [1, 2, 3]):
            raise ValueError(f"P '{mech_vent_profile}' should be in {L}")
        # Define schedule and coefficient (i.e. mech vent level)
        mv_schedule = "Off 24/7" if self.vent_type == "A" else "On 24/7"
        if mech_vent_profile == 1:  # Low mech vent level
            coef = 0.15
        elif mech_vent_profile == 2:  # Medium mech vent level
            coef = 0.5
        else:
            if self.vent_type in ["C1", "C2"]:  # (Low + Med) / 2
                coef = (0.15 + 0.5) / 2
            else:
                coef = 1
        zone_floor_areas = self.get_zone_floor_areas()

        # Fill AirTerminal:SingleDuct:ConstantVolume:NoReheat
        D = {}
        for zone in self.zones:
            # Compute air flow rate based on zone floor area
            air_flow_rate = 0.9 * zone_floor_areas[zone] * coef / 1000
            D[f"{zone} Single Duct CAV No Reheat"] = {
                "air_inlet_node_name": f"Air Loop Zone Splitter Outlet Node {zone}",
                "air_outlet_node_name": f"{zone} Single Duct CAV No Reheat Supply Outlet",
                "availability_schedule_name": mv_schedule,
                "maximum_air_flow_rate": air_flow_rate,
            }
        self.epjson["AirTerminal:SingleDuct:ConstantVolume:NoReheat"] = D
        # Also update the AirLoopHVAC:ZoneSplitter object to match the new zones
        self.epjson["AirLoopHVAC:ZoneSplitter"]["Air Loop Zone Splitter"] = {
            "inlet_node_name": "Air Loop Demand Side Inlet 1",
            "nodes": [
                {"outlet_node_name": f"Air Loop Zone Splitter Outlet Node {zone}"}
                for zone in self.zones
            ],
        }
        # Set CO2 control for C4a and D5c
        if self.vent_type in ["C4a", "D5c"]:
            co2_sched = "On 24/7" if mech_vent_profile == 3 else "Off 24/7"
            D = {}
            for zone in self.zones:
                if zone == "2F":  # Skip attic because it is unoccupied
                    continue
                D[f"{zone}_CO2_Controller"] = {
                    "carbon_dioxide_control_availability_schedule_name": co2_sched,
                    "carbon_dioxide_setpoint_schedule_name": "CO2 levels threshold",
                    "zone_name": zone,
                }
            self.epjson["ZoneControl:ContaminantController"] = D
            if mech_vent_profile != 3:
                # Modify Controller:OutdoorAir. NOTE: this is needed to ensure that
                # C2/C4a give the same results when not using CO2 control
                D = self.epjson["Controller:OutdoorAir"][
                    "Air Loop AHU Outdoor Air Controller"
                ]
                D["minimum_fraction_of_outdoor_air_schedule_name"] = "On"
                D["minimum_outdoor_air_flow_rate"] = "Autosize"
                D["minimum_limit_type"] = ""
        return

    def set_lighting_and_equipment(self, light_power_per_area=1, eq_power_per_area=1):
        """
        Set the lighting and electric equipment internal gains for each zone.
        These appliances follow the schedules from "appliances_schedules.csv".

        Inputs:
        -------
        light_power_per_area: float, default = 1
            The power per area (in W/m2) to be used for the lights.
        eq_power_per_area: float, default = 1
            The power per area (in W/m2) to be used for the electric equipment.
        """
        D_lights = {}
        D_eq = {}
        # Add schedule file with power fraction
        appliances_sched_file = str(curr_dir / "data/appliances_schedules.csv")
        for idx, key in enumerate(["Lights", "Equipment"]):
            self.epjson["Schedule:File"][key] = {
                "schedule_type_limits_name": "Fraction",
                "file_name": appliances_sched_file,
                "column_number": idx + 1,
                "rows_to_skip_at_top": 1,
            }
        # Fill the Lights and ElectricEquipment objects
        for zone in self.zones:
            D_lights[f"Lights_{zone}"] = {
                "design_level_calculation_method": "Watts/Area",
                # NOTE: need to change Output:Meter to use new zone names
                "end_use_subcategory": f"ELECTRIC EQUIPMENT#{zone}#GeneralLights",
                "fraction_radiant": 0.42,
                "fraction_replaceable": 1,
                "fraction_visible": 0.18,
                "return_air_fraction": 0,
                "schedule_name": "Lights",
                "watts_per_floor_area": light_power_per_area,
                "zone_or_zonelist_or_space_or_spacelist_name": zone,
            }
            D_eq[f"ElectricEquipment_{zone}"] = {
                "carbon_dioxide_generation_rate": 0,
                "design_level_calculation_method": "Watts/Area",
                "end_use_subcategory": "General",
                "fraction_latent": 0,
                "fraction_lost": 0,
                "fraction_radiant": 0.2,
                "fuel_type": "Electricity",
                "power_per_floor_area": eq_power_per_area,
                "schedule_name": "Equipment",
                "zone_or_zonelist_or_space_or_spacelist_name": zone,
            }
        self.epjson["Lights"] = D_lights
        self.epjson["OtherEquipment"] = D_eq
        return

    def make_summer_shading_schedule(self):
        df = pd.DataFrame(
            data=np.zeros((8760, 1)),
            index=pd.date_range(start="2023-01-01 00:00", periods=8760, freq="h"),
        )
        mask = (df.index.month >= 5) & (df.index.month <= 9)
        df.loc[mask, 0] = 1
        df.to_csv(self.sim_dir / "summer_shading.csv", index=False)
        return

    def set_shading(
        self,
        shaded_surfaces: list[str],
        shading_position: str,
        shading_profile: int,
    ):
        """
        Add shading devices to certain windows.

        Inputs:
        -------
        shaded_surfaces: lis[str]
            The surfaces that will be shaded. They must have a window.
        shading_position: str
            The position of the shading device, either "External" or "Internal".
        shading_profile: int
            The shading profile to be used, one of 1, 2, 3 or 4:
            - 1: Always off
            - 2: On if indoor temperature > 22°C and solar irradiance > 200 W/m2
            - 3: On if indoor temperature > 24°C and solar irradiance > 300 W/m2 when occupied
            - 4: Always on during summer, off otherwise
        """
        assert shading_position in ["External", "Internal"], "Invalid shading position"
        assert shading_profile in [1, 2, 3, 4], "Invalid shading profile"
        if shading_profile == 1:  # No shading
            self.epjson["WindowShadingControl"] = {}
            return
        follows_occupancy = True if shading_profile in [3, 4] else False
        if shading_profile == 2:
            min_indoor_temp, min_sol_irradiance = 22, 200
        elif shading_profile == 3:
            min_indoor_temp, min_sol_irradiance = 24, 300
        else:
            min_indoor_temp, min_sol_irradiance = None, None
        # Define shading material based on position
        if shading_position == "External":
            shading_material = "MidRefLowTrans"
        else:
            shading_material = "LoRefLoTrans"
        # Get position in correct format
        shading_position = "Exterior" if shading_position == "External" else "Interior"
        # Get control strategy
        if min_indoor_temp != None and min_sol_irradiance != None:
            control_strategy = "OnIfHighZoneAirTempAndHighSolarOnWindow"
        elif min_indoor_temp != None:
            control_strategy = "OnIfHighZoneAirTemperature"
        elif min_sol_irradiance != None:
            control_strategy = "OnIfHighSolarOnWindow"
        else:
            control_strategy = "AlwaysOn"

        ### Fill the WindowShadingControl object
        D = {}
        D_build_surf = self.epjson["BuildingSurface:Detailed"]
        D_win_surf = self.epjson["FenestrationSurface:Detailed"]
        for surf in shaded_surfaces:
            assert surf in D_build_surf, f"Surface '{surf}' not found"
            # Find all windows on surface
            windows = []
            for window_name, window_params in D_win_surf.items():
                if window_params["building_surface_name"] == surf:
                    windows.append(window_name)
            assert len(windows) > 0, f"No windows found on surface '{surf}'"
            ### Fill the WindowShadingControl object
            for window in windows:
                # Get zone of the window
                building_surf = D_win_surf[window]["building_surface_name"]
                zone = D_build_surf[building_surf]["zone_name"]
                # Set params
                D[f"Shading_{window}"] = {
                    "fenestration_surfaces": [{"fenestration_surface_name": window}],
                    "glare_control_is_active": "No",
                    "multiple_surface_control_type": "Sequential",
                    "shading_control_is_scheduled": "No",
                    "shading_control_type": control_strategy,
                    "shading_device_material_name": shading_material,
                    "shading_type": shading_position + "Shade",
                    "type_of_slat_angle_control_for_blinds": "BlockBeamSolar",
                    "zone_name": zone,
                }
                # Set schedule
                if follows_occupancy:
                    D[f"Shading_{window}"]["shading_control_is_scheduled"] = "Yes"
                    if shading_profile == 3:
                        D[f"Shading_{window}"]["schedule_name"] = f"Occupancy_Any_Zone"
                        # Add Schedule:File for occupancy
                        self.epjson["Schedule:File"][f"Occupancy_Any_Zone"] = {
                            "schedule_type_limits_name": "Fraction",
                            "file_name": str(self.sim_dir / f"occupancy.csv"),
                            "column_number": len(self.zones) + 1,
                            "rows_to_skip_at_top": 1,
                        }
                    elif shading_profile == 4:
                        # TODO: move the part that create Shedule:File to make_summer_shading_schedule
                        self.make_summer_shading_schedule()
                        D[f"Shading_{window}"]["schedule_name"] = "AlwaysOn_Summer"
                        self.epjson["Schedule:File"][f"AlwaysOn_Summer"] = {
                            "schedule_type_limits_name": "Fraction",
                            "file_name": str(self.sim_dir / f"summer_shading.csv"),
                            "column_number": 1,
                            "rows_to_skip_at_top": 1,
                        }
                # Set setpoints
                if control_strategy == "OnIfHighZoneAirTemperature":
                    D[f"Shading_{window}"]["setpoint"] = min_indoor_temp
                elif control_strategy == "OnIfHighSolarOnWindow":
                    D[f"Shading_{window}"]["setpoint"] = min_sol_irradiance
                elif control_strategy == "OnIfHighZoneAirTempAndHighSolarOnWindow":
                    D[f"Shading_{window}"]["setpoint"] = min_indoor_temp
                    D[f"Shading_{window}"]["setpoint_2"] = min_sol_irradiance
        self.epjson["WindowShadingControl"] = D
        return

    ### OTHER FIELDS

    def set_output_variables(self, variables):
        """
        Set the output variables to be included in the simulation results.

        Inputs:
        variables: list of str
            A list with the names of the variables to be included in the output.
            The names should be the same as the ones used in EnergyPlus.
        """
        D = {}
        for var in variables:
            D[var] = {
                "key_value": "*",
                "reporting_frequency": "Hourly",
                "variable_name": var,
            }
        self.epjson["Output:Variable"] = D
        return

    def set_other_fields(self):
        """
        Update other fields (mostly HVAC related) with the new zones.
        """
        self.set_zone_sizing()
        self.set_zone_control_thermostat()
        self.set_HVAC_branch()
        self.set_HVAC_equipment_list()
        self.set_HVAC_air_distribution_unit()
        self.set_HVAC_node_list()
        self.set_HVAC_equipment_connections()
        self.set_HVAC_branch_list()
        self.set_HVAC_connector_splitter()
        self.set_HVAC_connector_mixer()
        self.set_HVAC_zone_mixer()
        self.set_output_meter()
        self.set_zone_air_balance()
        self.set_MV_controller()
        return

    def set_zone_sizing(self):
        ds_out_air_obj = "AllZones Design Specification Outdoor Air Object"
        ds_zone_air_obj = "AllZones Design Specification Zone Air Distribution Object"
        # Set Sizing:Zone field
        D = self.epjson["Sizing:Zone"] = {}
        D["Sizing:Zone 1"] = {
            "account_for_dedicated_outdoor_air_system": "No",
            "cooling_design_air_flow_method": "DesignDay",
            "cooling_design_air_flow_rate": 0.0,
            "cooling_minimum_air_flow": 0.0,
            "cooling_minimum_air_flow_fraction": 0.0,
            "cooling_minimum_air_flow_per_zone_floor_area": 0.00076,
            "dedicated_outdoor_air_high_setpoint_temperature_for_design": "Autosize",
            "dedicated_outdoor_air_low_setpoint_temperature_for_design": "Autosize",
            "dedicated_outdoor_air_system_control_strategy": "NeutralSupplyAir",
            "design_specification_outdoor_air_object_name": ds_out_air_obj,
            "design_specification_zone_air_distribution_object_name": ds_zone_air_obj,
            "heating_design_air_flow_method": "DesignDay",
            "heating_design_air_flow_rate": 0.0,
            "heating_maximum_air_flow": 0.14158,
            "heating_maximum_air_flow_fraction": 0.3,
            "heating_maximum_air_flow_per_zone_floor_area": 0.00203,
            "zone_cooling_design_supply_air_humidity_ratio": 0.009,
            "zone_cooling_design_supply_air_temperature": 14.0,
            "zone_cooling_design_supply_air_temperature_difference": 5.0,
            "zone_cooling_design_supply_air_temperature_input_method": "SupplyAirTemperature",
            "zone_cooling_sizing_factor": 1.15,
            "zone_heating_design_supply_air_humidity_ratio": 0.004,
            "zone_heating_design_supply_air_temperature": 50.0,
            "zone_heating_design_supply_air_temperature_difference": 15.0,
            "zone_heating_design_supply_air_temperature_input_method": "SupplyAirTemperature",
            "zone_heating_sizing_factor": 1.25,
            "zone_or_zonelist_name": "AllZones",
        }
        # Set DesignSpecification:OutdoorAir
        D = self.epjson["DesignSpecification:OutdoorAir"] = {}
        D[ds_out_air_obj] = {
            "outdoor_air_flow_per_zone_floor_area": 0.0009,
            "outdoor_air_method": "Flow/Area",
            "outdoor_air_schedule_name": "On 24/7",
        }
        # Set DesignSpecification:ZoneAirDistribution
        D = self.epjson["DesignSpecification:ZoneAirDistribution"] = {}
        D[ds_zone_air_obj] = {
            "zone_air_distribution_effectiveness_in_cooling_mode": 1.0,
            "zone_air_distribution_effectiveness_in_heating_mode": 1.0,
            "zone_secondary_recirculation_fraction": 0.0,
        }
        return

    def set_zone_control_thermostat(self):
        D = self.epjson["ZoneControl:Thermostat"] = {}
        for zone in self.zones:
            D[f"{zone} Thermostat"] = {
                "control_1_name": f"HeatingSetpoint_{zone}",
                "control_1_object_type": "ThermostatSetpoint:DualSetpoint",
                "control_type_schedule_name": "Control type schedule: Always 4",
                "zone_or_zonelist_name": zone,
            }
        return

    def set_HVAC_branch(self):
        # Remove branches for old zones
        for old_zone in self.old_zones:
            key = f"{old_zone} Water Radiator HW Loop Demand Side Branch"
            if key in self.epjson["Branch"]:
                del self.epjson["Branch"][key]
        # Add branches for new zones
        for zone in self.zones:
            key = f"{zone} Water Radiator HW Loop Demand Side Branch"
            D = {
                "component_inlet_node_name": f"{zone} Water Radiator Hot Water Inlet Node",
                "component_name": f"{zone} Water Radiator",
                "component_object_type": "ZoneHVAC:Baseboard:RadiantConvective:Water",
                "component_outlet_node_name": f"{zone} Water Radiator Hot Water Outlet Node",
            }
            self.epjson["Branch"][key] = {"components": [D]}
        return

    def set_HVAC_equipment_list(self):
        D = self.epjson["ZoneHVAC:EquipmentList"] = {}
        for zone in self.zones:
            D[f"{zone} Equipment"] = {
                "equipment": [
                    {
                        "zone_equipment_cooling_sequence": 2,
                        "zone_equipment_heating_or_no_load_sequence": 2,
                        "zone_equipment_name": f"{zone} Water Radiator",
                        "zone_equipment_object_type": "ZoneHVAC:Baseboard:RadiantConvective:Water",
                        "zone_equipment_sequential_cooling_fraction_schedule_name": "Cooling fraction schedule",
                        "zone_equipment_sequential_heating_fraction_schedule_name": "Heating fraction schedule",
                    },
                    {
                        "zone_equipment_cooling_sequence": 1,
                        "zone_equipment_heating_or_no_load_sequence": 1,
                        "zone_equipment_name": f"{zone} Single Duct CAV No Reheat ADU",
                        "zone_equipment_object_type": "ZoneHVAC:AirDistributionUnit",
                        "zone_equipment_sequential_cooling_fraction_schedule_name": "Cooling fraction schedule",
                        "zone_equipment_sequential_heating_fraction_schedule_name": "Heating fraction schedule",
                    },
                ],
                "load_distribution_scheme": "SequentialLoad",
            }
        return

    def set_HVAC_air_distribution_unit(self):
        D = self.epjson["ZoneHVAC:AirDistributionUnit"] = {}
        for zone in self.zones:
            D[f"{zone} Single Duct CAV No Reheat ADU"] = {
                "air_distribution_unit_outlet_node_name": f"{zone} Single Duct CAV No Reheat Supply Outlet",
                "air_terminal_name": f"{zone} Single Duct CAV No Reheat",
                "air_terminal_object_type": "AirTerminal:SingleDuct:ConstantVolume:NoReheat",
                "constant_downstream_leakage_fraction": 0.0,
                "nominal_upstream_leakage_fraction": 0.0,
            }
        return

    def set_HVAC_node_list(self):
        # Remove nodes for old zones
        for old_zone in self.old_zones:
            key = f"{old_zone} Air Inlet Node List"
            if key in self.epjson["NodeList"]:
                del self.epjson["NodeList"][key]
        # Add nodes for new zones
        for zone in self.zones:
            key = f"{zone} Air Inlet Node List"
            node_name = f"{zone} Single Duct CAV No Reheat Supply Outlet"
            self.epjson["NodeList"][key] = {"nodes": [{"node_name": node_name}]}
        return

    def set_HVAC_zone_mixer(self):
        self.epjson["AirLoopHVAC:ZoneMixer"] = {
            "Air Loop Zone Mixer": {
                "nodes": [
                    {"inlet_node_name": f"Air Loop Zone Mixer Inlet Node {idx+1}"}
                    for idx in range(len(self.zones))
                ],
                "outlet_node_name": "Air Loop Demand Side Outlet",
            }
        }
        return

    def set_output_meter(self):
        D = {
            "Output:Meter 1": {
                "key_name": "Electricity:Facility",
                "reporting_frequency": "Hourly",
            },
            "Output:Meter 2": {
                "key_name": "NATURALGAS:Facility",
                "reporting_frequency": "Hourly",
            },
            "Output:Meter 3": {
                "key_name": "InteriorEquipment:Electricity",
                "reporting_frequency": "Hourly",
            },
            "Output:Meter 4": {
                "key_name": "InteriorLights:Electricity",
                "reporting_frequency": "Hourly",
            },
            "Output:Meter 5": {
                "key_name": "Electricity:Facility",
                "reporting_frequency": "Daily",
            },
            "Output:Meter 6": {
                "key_name": "NATURALGAS:Facility",
                "reporting_frequency": "Daily",
            },
            "Output:Meter 7": {
                "key_name": "InteriorEquipment:Electricity",
                "reporting_frequency": "Daily",
            },
            "Output:Meter 8": {
                "key_name": "InteriorLights:Electricity",
                "reporting_frequency": "Daily",
            },
        }
        self.epjson["Output:Meter"] = D
        return

    def set_HVAC_equipment_connections(self):
        D = self.epjson["ZoneHVAC:EquipmentConnections"] = {}
        for idx, zone in enumerate(self.zones):
            D[f"ZoneHVAC:EquipmentConnections {idx+1}"] = {
                "zone_air_inlet_node_or_nodelist_name": f"{zone} Air Inlet Node List",
                "zone_air_node_name": f"{zone} Zone Air Node",
                "zone_conditioning_equipment_list_name": f"{zone} Equipment",
                "zone_name": zone,
                "zone_return_air_node_or_nodelist_name": (
                    f"Air Loop Zone Mixer Inlet Node {idx+1}"
                ),
            }
        return

    def set_HVAC_branch_list(self):
        branches = [
            {"branch_name": "HW Loop Demand Side Inlet Branch"},
            {"branch_name": "HW Loop Demand Side Bypass Branch"},
        ]
        for zone in self.zones:
            suffix = "Water Radiator HW Loop Demand Side Branch"
            branches.append({"branch_name": f"{zone} {suffix}"})
        branches.append({"branch_name": "HW Loop Demand Side Outlet Branch"})
        self.epjson["BranchList"]["HW Loop Demand Side Branches"] = {
            "branches": branches
        }
        return

    def set_HVAC_connector_splitter(self):
        branches = [{"outlet_branch_name": "HW Loop Demand Side Bypass Branch"}]
        for zone in self.zones:
            suffix = "Water Radiator HW Loop Demand Side Branch"
            branches.append({"outlet_branch_name": f"{zone} {suffix}"})
        self.epjson["Connector:Splitter"]["HW Loop Demand Splitter"] = {
            "branches": branches,
            "inlet_branch_name": "HW Loop Demand Side Inlet Branch",
        }
        return

    def set_HVAC_connector_mixer(self):
        branches = []
        for zone in self.zones:
            suffix = "Water Radiator HW Loop Demand Side Branch"
            branches.append({"inlet_branch_name": f"{zone} {suffix}"})
        branches.append({"inlet_branch_name": "HW Loop Demand Side Bypass Branch"})
        self.epjson["Connector:Mixer"]["HW Loop Demand Mixer"] = {
            "branches": branches,
            "outlet_branch_name": "HW Loop Demand Side Outlet Branch",
        }
        return

    def set_zone_air_balance(self):
        D = {}
        for zone in self.zones:
            D[f"{zone} OA Balance"] = {
                "air_balance_method": "Quadrature",
                "induced_outdoor_air_due_to_unbalanced_duct_leakage": 0,
                "induced_outdoor_air_schedule_name": "On 24/7",
                "zone_name": zone,
            }
        self.epjson["ZoneAirBalance:OutdoorAir"] = D
        return

    def set_MV_controller(self):
        if self.vent_type in ["C4a", "D5c"]:
            self.epjson["Controller:MechanicalVentilation"] = {
                "MV controller": {
                    "availability_schedule_name": "On 24/7",
                    "demand_controlled_ventilation": "Yes",
                    "system_outdoor_air_method": "IndoorAirQualityProcedure",
                    "zone_maximum_outdoor_air_fraction": 1,
                    "zone_specifications": [
                        {
                            "design_specification_outdoor_air_object_name": "AllZones Design Specification Outdoor Air Object",
                            "design_specification_zone_air_distribution_object_name": "AllZones Design Specification Zone Air Distribution Object",
                            "zone_or_zonelist_name": zone,
                        }
                        for zone in self.zones
                    ],
                }
            }
        return

    ### RUN SIMULATION

    def run(self, epw_file: str | Path):
        """
        Simulate the object with EnergyPlus and save the results in an output
        directory.

        Inputs:
        -------
        sim_dir: str or Path
            The directory where the simulation files will be saved.
        epw_file: str or Path, optional
            The path to the EPW file to be used for the simulation. If not provided,
            the default EPW file will be used.
        """
        if epw_file in ["DeBilt_2000", "DeBilt_2050", "DeBilt_2100"]:
            epw_file = curr_dir / f"data/{epw_file}.epw"
        assert epw_file.exists(), f"EPW file '{epw_file}' not found"
        epjson_file = self.sim_dir / f"input_{self.vent_type}.epjson"
        # Create folder if it does not exist
        self.sim_dir.mkdir(parents=True, exist_ok=True)
        # Save the epjson file
        with open(epjson_file, "w") as f:
            json.dump(self.epjson, f, cls=utils.NumpyEncoder, indent=4)
        # Run the simulation
        utils.run_energyplus(
            epjson_file, self.eplus_exec, self.idd_file, epw_file, self.sim_dir
        )
        return


def run_eplus_simulation(
    building_type: str,
    building_position: str,
    building_orientation: str,
    floor_type: str,
    floor_insulation: str | None,
    roof_insulation: str | None,
    wall_insulation: dict[str, list] | list | None,
    glazing: str,
    window_frame: str,
    WWR: float,
    airtightness: float,
    n_occupants: int,
    occupant_activity_level: str,
    heated_zones: list[str],
    heating_setpoint: str,
    vent_type: str,
    window_vent_profile: int,
    use_vent_grilles: bool,
    mech_vent_profile: int,
    lighting_power_per_area: float,
    equipment_power_per_area: float,
    shaded_surfaces: list[str],
    shading_position: str,
    shading_profile: int,
    sim_dir: str | Path,
    epw_file: str | Path,
    output_variables: list[str] = None,
    sim_templates: dict = None,
):
    """
    Run a full EnergyPlus simulation with the specified parameters.

    Parameters:
    -----------
    building_type: str
        The type of building to be simulated.
        Allowed values are "terraced_house" or "apartment".
    building_position: str
        The position of the building, which determines which surfaces are shared
        with neighbors. For terraced houses, allowed values are "middle" or "corner".
        For apartments, allowed values are ... TODO
    building_orientation: str
        The orientation of the building.
        Should be in ["W", "SW", "S", "SE", "E", "NE", "N", "NW"].
    floor_type: str
        The base material for the floor construction. Allowed values: "Wood", "Concrete".
    floor_insulation: list | None
        Insulation parameters for the floor. A list containing:
            - insulation_material_name (str)
            - insulation_position (str: "Internal", "External")
            - insulation_R_value (float)
        If None, no extra insulation is added to the base floor.
    roof_insulation: list | None
        Insulation parameters for the roof. A list containing:
            - insulation_material_name (str)
            - insulation_position (str: "Internal", "External", "Cavity")
            - insulation_R_value (float)
        If None, no extra insulation is added to the base roof.
    wall_insulation: dict[str, list] | list | None
        Insulation parameters for the walls. Can be a list (applied to all outdoor walls)
        or a dictionary mapping surface types to insulation parameters. Each list contains:
            - insulation_material_name (str)
            - insulation_position (str: "Internal", "External", "Cavity")
            - insulation_R_value (float)
        If None, no extra insulation is added to the base walls.
    glazing: str
        The type of glazing to be used for all windows. Allowed values are "SingleGlz",
        "DoubleGlz", "TripleGlz", "HR++" and "HR++ Sun Protection".
    window_frame: str
        The type of frame to be used for all windows.
        Allowed values are "PVC", "Aluminum" and "Wood".
    WWR: float
        Window-to-Wall Ratio, between 0 and 1.
    airtightness: float
        The qv10 airtightness, i.e., the air leakage rate at a pressure of 10 Pascals,
        in dm3/(s.m2). This value typically ranges from 0.4 to 2.
    n_occupants: int
        The number of occupants in the building: 1, 2 or 4.
    occupant_activity_level: str
        The activity level of occupants = "low", "mid" or "high". It sets the CO2
        generation rate and the watts per person for internal gains.
    heated_zones: list[str]
        A list of zone names where heating is active.
    heating_setpoint: str
        The name of the schedule defining the heating setpoint temperature for
        heated zones.
    vent_type: str
        The ventilation type to be used for the simulation template.
        Allowed values are: "A", "C1", "C2", "C4a", "D5c".
    window_vent_profile: int
        The window ventilation profile to be used, one of 1, 2, 3 or 4.
    use_vent_grilles: bool
        Whether to use ventilation grilles. If so, the natural ventilation rate will be
        higher.
    mech_vent_profile: int
        The mechanical ventilation profile: 1 (low intensity), 2 (medium intensity)
        or 3 (CO2 controlled). Doesnt apply for ventilation type A.
    lighting_power_per_area: float
        The power per area (in W/m2) to be used for the lights.
    equipment_power_per_area: float
        The power per area (in W/m2) to be used for the electric equipment.
    shaded_surfaces: list[str]
        A list of building surface names (e.g. "SouthWall_0F") on which to add shading
        to their windows.
    shading_position: str
        The position of the shading device, either "External" or "Internal".
    shading_profile: int
        The shading control profile: 1, 2, 3 or 4.
    output_dir: str | Path
        The directory where the simulation results will be saved.
    epw_file: str | Path, default = None
        The path to the weather file to be used for the simulation.
        If None, a default EPW file will be used.
    output_variables: list[str] | None, default = None
        A list of EnergyPlus output variables to be included in the simulation results.
        If None, the following default variables are used:
            - "Zone Mean Radiant Temperature"
            - "Zone Operative Temperature"
            - "Zone Mean Air Temperature"
            - "Zone Air Relative Humidity"
            - "Schedule Value"
            - "Boiler Heating Rate"
            - "Site Outdoor Air Drybulb Temperature"
            - "Surface Outside Face Incident Solar Radiation Rate per Area"
            - "Fan Electricity Energy"
    """
    # Initialize the simulation object
    if sim_templates is None:
        sim = EPSimulation(vent_type, sim_dir)
    else:
        sim = deepcopy(sim_templates[vent_type])
        sim.sim_dir = Path(sim_dir)
        Path(sim_dir).mkdir(parents=True, exist_ok=True)
    # Geometry
    sim.set_geometry(building_type, building_position)
    sim.set_orientation(building_orientation)
    # Constructions, windows and airtightness
    sim.set_constructions(
        floor_type, floor_insulation, roof_insulation, wall_insulation
    )
    sim.set_windows(glazing, window_frame, WWR)
    sim.set_airtightness(airtightness)
    # Occupant behavior (occupancy, heating, ventilation)
    sim.set_occupants(n_occupants, occupant_activity_level)
    sim.set_heating(heated_zones, heating_setpoint)
    sim.set_natural_ventilation(window_vent_profile, use_vent_grilles)
    sim.set_mechanical_ventilation(mech_vent_profile)
    # Lighting and equipment
    sim.set_lighting_and_equipment(lighting_power_per_area, equipment_power_per_area)
    # Shading
    sim.set_shading(shaded_surfaces, shading_position, shading_profile)
    # Set output variables
    if output_variables is None:
        output_variables = [
            "Zone Mean Radiant Temperature",
            "Zone Operative Temperature",
            "Zone Mean Air Temperature",
            "Zone Air Relative Humidity",
            "Schedule Value",
            "Boiler Heating Rate",
            "Site Outdoor Air Drybulb Temperature",
            "Surface Outside Face Incident Solar Radiation Rate per Area",
            "Fan Electricity Energy",
            "Zone Air CO2 Concentration",
        ]
    sim.set_output_variables(output_variables)
    # Set other fields
    sim.set_other_fields()
    # Run the simulation
    sim.run(epw_file)
    return


# from pathlib import Path
# from renovexpy import __file__ as renovexpy_file
# from renovexpy.energyplus import run_eplus_simulation
# from renovexpy.heating_system import simulate_heating_systems
# from renovexpy.pv import simulate_pv_generation
# from renovexpy.kpi import get_simulated_KPIs

# renovexpy_dir = Path(renovexpy_file).parent
# sim_dir = renovexpy_dir / "examples/simulation/test"

# building_type = "terraced_house"
# building_position = "corner"
# building_orientation = "S"
# floor_type = "Wood"
# floor_insulation = None
# roof_insulation = None
# wall_insulation = ["Rockwool", "Cavity", 3]
# glazing = "DoubleGlz"
# window_frame = "PVC"
# WWR = 0.4
# airtightness = 1
# n_occupants = 2
# occupant_activity_level = "mid"
# heated_zones = ["0F", "1FN", "1FS"]
# heating_setpoint = "N17_D20"
# vent_type = "C4a"
# window_vent_profile = 1
# use_vent_grilles = False
# mech_vent_profile = 1
# lighting_power_per_area = 1
# equipment_power_per_area = 1
# shaded_surfaces = ["SouthWall_0F", "SouthWall_1FS"]
# shading_position = "External"
# shading_profile = 1
# sim_dir = sim_dir
# epw_file = "DeBilt_2000"
