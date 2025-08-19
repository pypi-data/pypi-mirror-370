from copy import deepcopy
import inspect
import random
import uuid
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

from renovexpy.simulation.geometry import (
    create_apartment,
    create_terraced_house,
    find_matching_surfaces,
)

renovexpy_dir = Path(__file__).parents[1]


def sample_construction_period(**kwargs):
    D_th = {
        "Until 1945": 0.172,
        "1945-1975": 0.309,
        "1975-1995": 0.338,
        "After 1995": 0.181,
    }
    D_apmt = {
        "Until 1945": 0.187,
        "1945-1975": 0.3004,
        "1975-1995": 0.2464,
        "After 1995": 0.2662,
    }
    D = {"terraced_house": D_th, "apartment": D_apmt}
    ht = kwargs["housing_type"]
    options, probs = list(D[ht].keys()), list(D[ht].values())
    return {"construction_period": np.random.choice(options, p=probs)}


def sample_ventilation_type(**kwargs):
    """
    Sample the ventilation system and corresponding IDF template.
    """
    D_th = {
        "Until 1945": {"A": 0.866, "C": 0.129, "D": 0.005},
        "1945-1975": {"A": 0.791, "C": 0.207, "D": 0.002},
        "1975-1995": {"A": 0.364, "C": 0.621, "D": 0.015},
        "After 1995": {"A": 0.005, "C": 0.832, "D": 0.163},
    }
    D_apmt = {
        "Until 1945": {"A": 0.758, "C": 0.227, "D": 0.015},
        "1945-1975": {"A": 0.528, "C": 0.460, "D": 0.012},
        "1975-1995": {"A": 0.206, "C": 0.781, "D": 0.013},
        "After 1995": {"A": 0.014, "C": 0.781, "D": 0.196},
    }
    D = {"terraced_house": D_th, "apartment": D_apmt}
    # Sample ventilation type
    if kwargs["realistic"]:
        ht, cp = kwargs["housing_type"], kwargs["construction_period"]
        options = list(D[ht][cp].keys())
        probs = list(D[ht][cp].values())
        # Make sure probs sum to 1
        if abs(1 - sum(probs)) < 0.02:  # Normalize probs
            probs = [p / sum(probs) for p in probs]
        else:
            raise ValueError("Probabilities do not sum to 1: ", probs)
        vent_type = np.random.choice(options, p=probs)
    else:
        vent_type = random.choice(["A", "C", "D"])
    return {"ventilation_type": vent_type}


def sample_geometry(**kwargs):
    """
    Get the vertices, surfaces and shared surfaces of the house/apartment.

    Inputs:
    -------
    kwargs: dict
        Dictionary with the following keys
            - housing_type: str
                Type of housing (terraced_house or apartment).
    """
    if kwargs["housing_type"] == "terraced_house":
        vertices, surfaces = create_terraced_house(height=8)
        shared_surf_options = [
            ["WestWall"],  # Corner
            ["WestWall", "EastWall"],  # Middle
        ]
    else:
        # Create vertices and surfaces for apartment
        vertices, surfaces = create_apartment(
            length=10, width=6.74, height=2.8, n_zones=2, frac_south_zone_area=0.7
        )
        shared_surf_options = [
            ### 3 exposed walls (corner, 1 row)
            ["WestWall", "Roof"],  # Ground floor
            ["WestWall", "Floor", "Roof"],  # Middle floor
            ["WestWall", "Floor"],  # Top floor
            ### 2 exposed walls (corner, several rows)
            ["WestWall", "NorthWall", "Roof"],  # Ground floor
            ["WestWall", "NorthWall", "Floor", "Roof"],  # Middle floor
            ["WestWall", "NorthWall", "Floor"],  # Top floor
            ### 2 exposed walls (middle, 1 row)
            ["WestWall", "EastWall", "Roof"],  # Ground floor
            ["WestWall", "EastWall", "Floor", "Roof"],  # Middle floor
            ["WestWall", "EastWall", "Floor"],  # Top floor
            ### 1 exposed wall (middle, several rows)
            ["WestWall", "EastWall", "NorthWall", "Roof"],  # Ground floor
            ["WestWall", "EastWall", "NorthWall", "Floor", "Roof"],  # Middle floor
            ["WestWall", "EastWall", "NorthWall", "Floor"],  # Top floor
        ]
    shared_surfaces = random.choice(shared_surf_options)
    return {
        "vertices": vertices,
        "surfaces": surfaces,
        "shared_surfaces": shared_surfaces,
        "zones": set([surf.split("_")[1] for surf in surfaces]),
    }


def sample_orientation():
    """Sample the house/apartment orientation."""
    return {"orientation": random.choice(["W", "SW", "S", "SE", "E", "NE", "N", "NW"])}


def sample_R_value(**kwargs):
    """
    Sample the R-value of a wall/floor/roof based.
    If method = "realistic", samples from a triangular distribution based on housing
    type and construction period. If method = "uniform", samples uniformly between 0
    and 6.

    Kwargs:
    -------
    realistic: bool
        If True, samples from a realistic distribution. If False, samples uniformly.
    housing_type: str
        Type of housing (terraced_house or apartment).
    construction_period: str
        Construction period of the building.
    surf_type: str
        Type of surface (wall, floor, roof).
    """
    # NOTE: do these distrubutions represent R-value of a single external wall, or
    # the average R-value of all external walls? Are shared walls included?
    D_th = {
        "Until 1945": {
            "floor": [0.15, 5.04, 0.77],
            "wall": [0.19, 2.53, 0.7],
            "roof": [0.22, 2.53, 1.24],
        },
        "1945-1975": {
            "floor": [0.15, 5.48, 0.57],
            "wall": [0.19, 3.5, 0.84],
            "roof": [0.22, 3.78, 1.22],
        },
        "1975-1995": {
            "floor": [0.52, 5.38, 1.16],
            "wall": [0.8, 2.71, 1.53],
            "roof": [0.44, 3.78, 1.5],
        },
        "After 1995": {
            "floor": [1.7, 6, 2.68],
            "wall": [1.51, 7, 2.68],
            "roof": [2, 9, 2.75],
        },
    }
    D_apmt = {
        "Until 1945": {
            "floor": [0.15, 3.5, 0.56],
            "wall": [0.19, 3.5, 0.58],
            "roof": [0.22, 3.78, 1],
        },
        "1945-1975": {
            "floor": [0.15, 4.15, 0.48],
            "wall": [0.19, 4.18, 0.67],
            "roof": [0.22, 2, 0.96],
        },
        "1975-1995": {
            "floor": [0.52, 3.5, 1.16],
            "wall": [0.8, 3.5, 1.66],
            "roof": [1.3, 3.78, 1.66],
        },
        "After 1995": {
            "floor": [0.82, 4.59, 2],
            "wall": [1.69, 5.69, 2.61],
            "roof": [2.5, 3.5, 2.67],
        },
    }
    D = {"terraced_house": D_th, "apartment": D_apmt}
    if kwargs["realistic"]:
        ht, cp = kwargs["housing_type"], kwargs["construction_period"]
        surf_type = kwargs["surf_type"]
        distribution = D[ht][cp][surf_type]
        R_value = random.triangular(*distribution)
    else:
        R_value = random.uniform(0, 6)
    return R_value


def sample_constructions(**kwargs):
    """
    Define the constructions as follows:

    - Floor = Plywood_19mm or Concrete_200mm (+ external insulation for ground floor)
    - Walls = [Brick_100mm, Air_Gap_Cavity, Brick_100mm] + insulation if outdoors
    - Internal walls = Gypsum_Cavity_Gypsum
    - Roofs = Plywood_19mm + insulation

    If realistic = True, R-values are sampled based on the housing type and
    construction period. Otherwise, R-values are sampled uniformly between 0 and 6.
    """
    D = {}
    surfaces, shared_surfaces = kwargs["surfaces"], kwargs["shared_surfaces"]
    internal_surf = find_matching_surfaces(surfaces)
    # Load existing materials for insulation
    ins_mat_options = ["EPS", "PIR/PUR", "Rockwool", "Biobased"]
    ### 1) Floor
    base_floor_constr = random.choice(["Plywood_19mm", "Concrete_200mm"])
    base_floor_R = 0.16 if base_floor_constr == "Plywood_19mm" else 0.10
    floor_R = sample_R_value(surf_type="floor", **kwargs)
    floor_ins_R = round(floor_R - base_floor_R, 2)
    # Internal/shared floor
    if any(["Floor" in surf for surf in internal_surf]):
        D["InternalFloor"] = base_floor_constr
    if any(["Floor" in surf for surf in shared_surfaces]):
        D["SharedFloor"] = base_floor_constr
    # Ground floor
    if "Floor" not in shared_surfaces:
        if floor_ins_R <= 0:
            D["GroundFloor"] = base_floor_constr
        else:
            floor_ins_mat = random.choice(ins_mat_options)
            D["GroundFloor"] = [f"{floor_ins_mat}_R={floor_ins_R}", base_floor_constr]
    ### 2) Walls
    base_wall_constr = ["Brick_100mm", "Air_Gap_Cavity", "Brick_100mm"]
    base_wall_R = 0.32
    # Internal walls
    if any(["Wall" in surf for surf in internal_surf]):
        D["InternalWall"] = "Gypsum_Cavity_Gypsum"
    # Shared walls
    if any(["Wall" in surf for surf in shared_surfaces]):
        D["SharedWall"] = base_wall_constr
    # Outdoor walls
    for surf_name in surfaces:
        surf_type = surf_name.split("_")[0]
        if (
            "Wall" not in surf_name
            or surf_name in internal_surf
            or surf_type in shared_surfaces
        ):
            continue  # Skip surfaces that are not outdoor walls
        # Sample R_value for the wall
        wall_R = sample_R_value(surf_type="wall", **kwargs)
        wall_ins_R = round(wall_R - base_wall_R, 2)
        if wall_ins_R <= 0:
            D[surf_type] = base_wall_constr
        else:
            wall_constr = base_wall_constr.copy()
            wall_ins_mat = random.choice(ins_mat_options)
            wall_ins_pos = random.choice(["Internal", "Cavity", "External"])
            wall_ins_layer = f"{wall_ins_mat}_R={wall_ins_R}"
            if wall_ins_pos == "Internal":
                wall_constr.append(wall_ins_layer)
            elif wall_ins_pos == "Cavity":
                wall_constr[1] = wall_ins_layer
            else:
                wall_constr.insert(0, wall_ins_layer)
            D[surf_type] = wall_constr
    ### 3) Roof
    base_roof_constr = "Plywood_19mm"
    base_roof_R = 0.16
    # Internal/shared roof
    if any(["Roof" in surf for surf in internal_surf]):
        D["InternalRoof"] = base_floor_constr
    if any(["Roof" in surf for surf in shared_surfaces]):
        D["SharedRoof"] = base_floor_constr
    # Outdoor roofs
    for surf_name in surfaces:
        surf_type = surf_name.split("_")[0]
        if (
            "Roof" not in surf_name
            or surf_name in internal_surf
            or surf_type in shared_surfaces
        ):
            continue  # Skip surfaces that are not outdoor roofs
        # Sample R_value for the roof
        roof_R = sample_R_value(surf_type="roof", **kwargs)
        roof_ins_R = round(roof_R - base_roof_R, 2)
        if roof_ins_R <= 0:
            D[surf_type] = base_roof_constr
        else:
            roof_layers = ["Plywood_19mm"]
            roof_ins_mat = random.choice(ins_mat_options)
            roof_ins_pos = random.choice(["Internal", "External"])
            roof_ins_layer = f"{roof_ins_mat}_R={roof_ins_R}"
            if roof_ins_pos == "Internal":
                roof_layers.append(roof_ins_layer)
            else:
                roof_layers.insert(0, roof_ins_layer)
            D[surf_type] = roof_layers
    return {"constructions": D}


def sample_windows(**kwargs):
    """ """
    # Define surfaces that can hist windows
    # NOTE: should we allow corner house/apartment to have windows on the corner?
    win_surf_th = [
        surf
        for surf in ["NorthWall_0F", "NorthWall_1FN", "SouthWall_0F", "SouthWall_1FS"]
        if not any(facade in surf for facade in kwargs["shared_surfaces"])
    ]
    win_surf_apmt = [
        surf
        for surf in ["NorthWall_0FN", "SouthWall_0FS"]  # NOTE: update when n_zones = 1
        if not any(facade in surf for facade in kwargs["shared_surfaces"])
    ]
    D_win_surf = {"terraced_house": win_surf_th, "apartment": win_surf_apmt}
    # Define WWR for each construction period
    wwr_th = {"Until 1945": 31, "1945-1975": 36, "1975-1995": 31, "After 1995": 29}
    wwr_apmt = {"Until 1945": 32, "1945-1975": 40, "1975-1995": 33, "After 1995": 38}
    D_wwr = {"terraced_house": wwr_th, "apartment": wwr_apmt}
    # Define U-values for each construction period
    U_th = {
        "Until 1945": [1.4, 5.1, 2.96],
        "1945-1975": [1.56, 5.59, 2.73],
        "1975-1995": [1.8, 5.62, 2.82],
        "After 1995": [1, 3.31, 2.1],
    }
    U_apmt = {
        "Until 1945": [1.63, 6.2, 3.11],
        "1945-1975": [1.4, 5.96, 2.87],
        "1975-1995": [1.73, 5.4, 2.91],
        "After 1995": [1, 4.1, 2.16],
    }
    U_value_distr = {"terraced_house": U_th, "apartment": U_apmt}
    ### Sample window parameters
    ht, cp = kwargs["housing_type"], kwargs["construction_period"]
    U_glazings = {
        "SingleGlazing": 5.8,
        "DoubleGlazing": 2.8,
        "DoubleGlazing_HR++": 1.2,
        "TripleGlazing_HR+++": 0.6,
    }
    D = {}
    for surf in D_win_surf[ht]:
        # Sample WWR
        wwr = (
            D_wwr[ht][cp] / 100
            if kwargs["realistic"]
            else round(random.uniform(0.2, 0.8), 2)
        )
        if wwr == 0:
            continue
        if kwargs["realistic"]:
            U_value = random.triangular(*U_value_distr[ht][cp])
            # Use glazing with closest U-value
            # NOTE: can we adjust glazing properties to match the U-value?
            glazing = min(U_glazings, key=lambda x: abs(U_glazings[x] - U_value))
        else:
            glazing = random.choice(list(U_glazings.keys()))
        D[surf] = (glazing, wwr)
    return {"windows": D}


def sample_airtightness(**kwargs):
    """
    Sample the airtightness (qv10, in dm3/s.m2) of the house/apartment.
    """
    D_th = {
        "Until 1945": [0.7, 3, 3],
        #  [0.15, 5.04, 0.77],  # NOTE: Weird values, need to check
        "1945-1975": [0.7, 3, 3],
        "1975-1995": [0.7, 2.5, 2],
        "After 1995": [0.7, 1.5, 1],
    }
    D_apmt = {  # NOTE: these values are for an intermediate-intermediate apartment
        # Ideally we need to define these values for each configuration
        "Until 1945": [0.35, 1.5, 1.5],
        "1945-1975": [0.35, 1.5, 1.5],
        "1975-1995": [0.35, 1.25, 1],
        "After 1995": [0.35, 0.75, 0.5],
    }
    D = {"terraced_house": D_th, "apartment": D_apmt}
    ht, cp = kwargs["housing_type"], kwargs["construction_period"]
    if kwargs["realistic"]:
        airtightness = random.triangular(*D[ht][cp])
    else:
        min_max = [0.5, 3] if ht == "terraced_house" else [0.35, 1.5]
        airtightness = random.uniform(*min_max)
    return {"airtightness": round(airtightness, 2)}


def sample_heating_params(**kwargs):
    """
    Set the heating params for each zone as follows:
    - Constant temperature setpoint uniformly sampled between 18 and 21 degrees.
    Except for the attic, which is always set to 10 degrees.
    - Usage schedule is "On 24/7".
    """
    # NOTE: add more scheduling options, maybe different for each zone
    D = {"temp_sched": {}, "usage_sched": {}}
    temp_all_zones = random.choice([18, 19, 20, 21])
    for zone in kwargs["zones"]:
        if zone == "2F":  # Assume the attic is not heated
            D["temp_sched"][zone] = "Always_10"
            D["usage_sched"][zone] = "On 24/7"
        elif kwargs["realistic"]:  # Same temp for all zones, always on
            D["temp_sched"][zone] = f"Always_{temp_all_zones}"
            D["usage_sched"][zone] = "On 24/7"
        else:
            temp = round(random.uniform(18, 21), 1)
            D["temp_sched"][zone] = f"Always_{temp}"
            D["usage_sched"][zone] = "On 24/7"
    # temp_sched_options = ["Always_21", "N17_D21", "N17_M21_D17_E21"]
    return {"heating_params": D}


def sample_nat_vent_params(**kwargs):
    """
    Sample the natural ventilation settings as follows:

    - The usage schedule of each zone is chosen among ["On 24/7", "When occupied"].
    Note that it can be different for each zone.
    - The ACH is set uniformly between 1 and 3.
    - The minimum indoor temperature is set to 24 degrees for all zones, to ensure it
    is used to cool the building.
    - The maximum temperature difference between outdoor and indoor is set to .
    """
    param_names = ["usage_sched", "ach", "min_indoor_temp", "max_temp_delta_out_in"]
    D = {param_name: {} for param_name in param_names}
    # Define options for each parameter
    usage_sched_options = ["On 24/7", "When occupied"]
    mit_options = [24]
    mtdoi_options = [4]
    # Sample min_indoor_temp and max_temp_delta_out_in (same values for all zones)
    min_indoor_temp = random.choice(mit_options)
    max_temp_delta_out_in = random.choice(mtdoi_options)
    # Sample usage schedule for each zone (except attic)
    for zone in kwargs["zones"]:
        ach = 0 if zone == "2F" else random.uniform(1, 3)
        D["usage_sched"][zone] = random.choice(usage_sched_options)
        D["ach"][zone] = ach
        D["min_indoor_temp"][zone] = min_indoor_temp
        D["max_temp_delta_out_in"][zone] = max_temp_delta_out_in
    return {"nat_vent_params": D}


def sample_mech_vent_params(**kwargs):
    """
    Sample the mechanical ventilation settings for each zone.

    - If ventilation type = A, there is no NV.
    - Else, MV is always on with a low/medium/high level in all zones.
    """
    D = {"usage_sched": {}}
    # Define options for each parameter
    # usage_sched_options = ["On 24/7"]  # , "Off 24/7", "When occupied"]
    vent_level_options = ["low", "mid", "high"]
    # Sample vent_level (same value for all zones)
    D["vent_level"] = random.choice(vent_level_options)
    # Sample usage schedule for
    for zone in kwargs["zones"]:
        if kwargs["ventilation_type"] == "A" or zone == "2F":
            D["usage_sched"][zone] = "Off 24/7"
        else:
            D["usage_sched"][zone] = "On 24/7"
    return {"mech_vent_params": D}


def sample_occupants_params():
    """
    Sample occupants parameters as follows:

    - Number of occupants is randomly chosen between 1 and 2.
    - The occupancy schedule of each occupant is either "Worker" or "RemoteWorker".
    - The activity level of all occupants is either "Low", "Mid" or "High".
    """
    occ_sched_options = [["Worker"], ["RemoteWorker"], ["Worker", "RemoteWorker"]]
    D = {
        "occ_sched_names": random.choice(occ_sched_options),
        "activity_level": "Mid",  # random.choice(["Low", "Mid", "High"]),
    }
    return {"occupants_params": D}


def sample_equipment_params():
    D = {
        "light_power_per_area": 1,  # random.randint(1, 3),
        "eq_power_per_area": 1,  # random.randint(1, 3),
    }
    return {"equipment_params": D}


def sample_shading_params(**kwargs):
    """
    Sample the shading settings for each window.
    """
    D = {"shading_params_per_window": {}}
    # Define options for each parameter
    pos_options = ["Interior", "Exterior"]
    mat_options = [
        "HighRefLowTrans",
        "LowRefLowTrans",
        "MidRefMidTrans",
        "MidRefLowTrans",
    ]
    mit_options = [24]  # [None, 18, 20, 22]
    msi_options = [200]  # [None, 200, 300]
    # Find all surfaces with windows
    # Sample shading settings for each window
    for surf in kwargs["windows"]:
        if random.choice([True, False]):  # 50% chance of having shading
            D["shading_params_per_window"][surf] = {
                "material": random.choice(mat_options),
                "position": random.choice(pos_options),
                "follows_occupancy": False,  # random.choice([True, False]),
                "min_indoor_temp": random.choice(mit_options),
                "min_solar_irradiance": random.choice(msi_options),
            }
    return {"shading_params": D}


random_samplers = {
    "construction_period": sample_construction_period,
    "ventilation_type": sample_ventilation_type,
    "geometry": sample_geometry,
    "orientation": sample_orientation,
    "constructions": sample_constructions,
    "windows": sample_windows,
    "airtightness": sample_airtightness,
    "heating": sample_heating_params,
    "nat_vent": sample_nat_vent_params,
    "mech_vent": sample_mech_vent_params,
    "occupants": sample_occupants_params,
    "equipment": sample_equipment_params,
    "shading": sample_shading_params,
}


def generate_random_configs(
    samplers: dict,
    N_samples: int,
    output_file: Path,
    overwrite=False,
    **kwargs,
):
    # Create list with params for each house
    L_params = []
    sampler_order = [
        "construction_period",
        "ventilation_type",
        "geometry",
        "orientation",
        "constructions",
        "windows",
        "airtightness",
        "heating",
        "nat_vent",
        "mech_vent",
        "occupants",
        "equipment",
        "shading",
    ]
    if "construction_period" not in samplers:  # Optional sampler
        sampler_order.remove("construction_period")

    for _ in tqdm(range(N_samples)):
        params = {}
        for key in sampler_order:
            if key not in samplers:
                raise ValueError(f"Sampler for {key} not found")
            sampler = samplers[key]
            argspec = inspect.getfullargspec(sampler)
            if argspec.varkw is not None:
                sampled_params = sampler(**params, **kwargs)
            else:
                sampled_params = sampler()
            params.update(sampled_params)
        L_params.append(params)
    df = pd.DataFrame(L_params)
    # Add "id" column
    df["id"] = [uuid.uuid4().hex for _ in range(N_samples)]
    # Create output dir if needed and save the params to json file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    if output_file.exists() and not overwrite:
        print("Appending to existing file")
        df_old = pd.read_pickle(output_file)
        df = pd.concat([df_old, df], ignore_index=True)
    df.to_pickle(output_file)
    return
