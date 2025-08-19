"""
This file defines the renovation measures used in the Renovation Explorer,
and functions to automatically filter the relevant ones based on the
pre-renovation state.
"""

from copy import deepcopy
from renovexpy.parametric import generate_input_configs
from renovexpy.kpi import load_cost_data
import pandas as pd
import numpy as np


def remove_redundant_insulation_measures(renovation_measures: dict) -> dict:
    D_cost = load_cost_data()
    for key in [
        "wood_floor_insulation",
        "concrete_floor_insulation",
        "wall_insulation",
        "roof_insulation",
    ]:
        options = renovation_measures[key]
        # Get arrays with cost and R-value
        R_values = np.array([opt[2] for opt in options.keys()])
        costs = np.array([D_cost[code] for code in options.values()])
        codes = list(options.keys())
        # Split R-values in N bins (splitting the min-max range) and select the
        # option with highest R-value to cost ratio in each bin
        bins = [1, 1.5, 2, 2.5, 3, 4, 6]
        bin_indices = np.digitize(R_values, bins) - 1
        ratios = R_values / costs
        result = []
        for b in range(len(bins) - 1):
            indices_in_bin = np.where(bin_indices == b)[0]
            if len(indices_in_bin) > 0:
                best_idx = indices_in_bin[np.argmax(ratios[indices_in_bin])]
                result.append(best_idx)
        renovation_measures[key] = {codes[i]: options[tuple(codes[i])] for i in result}
    return renovation_measures


def get_applicable_insulation(pre_renov_config: dict) -> dict:
    """
    Returns a dictionary of applicable insulation measures based on the pre-renovation
    configuration.
    """
    D = {}
    for param in ["floor_insulation", "roof_insulation", "wall_insulation"]:
        # Get current insulation
        _, curr_ins_pos, curr_ins_R = pre_renov_config[param]
        # Get insulation options
        if "floor" in param:
            floor_type = pre_renov_config["floor_type"].lower()
            options = renovation_measures[f"{floor_type}_{param}"]
        else:
            options = renovation_measures[param]
        options = [opt[:-1] for opt in options.keys()]
        # If insulation already present, keep options with different positions
        if curr_ins_R > 0:
            options = [opt for opt in options if opt[1] != curr_ins_pos]
        # Add current state to options
        options.append(tuple(pre_renov_config[param]))
        # Format into tuple of list
        options = tuple([list(opt) for opt in options])
        D[param] = options
    return D


def get_applicable_glazing(pre_renov_config: dict) -> dict:
    curr_glazing, curr_frame = pre_renov_config[("glazing", "window_frame")]
    options = list(renovation_measures["glazing"].keys())
    glazing_to_keep = {
        "HR++": ["TripleGlz", "HR++ Sun Protection"],
        "HR++ Sun Protection": ["TripleGlz"],
        "TripleGlz": [],
    }
    if curr_glazing in glazing_to_keep:
        options = [opt for opt in options if opt[0] in glazing_to_keep[curr_glazing]]
    # Add current state to options
    options.append((curr_glazing, curr_frame))
    # Format into tuple of list
    options = tuple([list(opt) for opt in options])
    return {("glazing", "window_frame"): options}


def get_applicable_ventilation_system(pre_renov_config: dict) -> dict:
    curr_vent_type = pre_renov_config["vent_type"]
    options = [
        opt[1]
        for opt in renovation_measures["ventilation"].keys()
        if opt[0] == curr_vent_type
    ]
    # Add current state to options
    options.append(curr_vent_type)
    return {"vent_type": tuple(options)}


def get_applicable_heating_system(pre_renov_config: dict) -> dict:
    curr_hs = pre_renov_config["heating_system"]
    options = list(renovation_measures["heating_system"].keys())
    hs_to_keep = {
        "VR": [
            "HR107",
            "HP 5kW",
            "HP 7kW",
            "HP 10kW",
            "HP 3kW Intergas + HR107 Parallel",
        ],
        "HR107": ["HP 5kW", "HP 7kW", "HP 10kW", "HP 3kW Intergas + HR107 Parallel"],
        "HP 5kW": ["HP 7kW", "HP 10kW"],
        "HP 7kW": ["HP 10kW"],
        "HP 10kW": [],
        "HP 3kW Intergas + HR107 Parallel": ["HP 5kW", "HP 7kW", "HP 10kW"],
    }
    options = hs_to_keep[curr_hs]
    # Add current state to options
    options.append(curr_hs)
    return {"heating_system": tuple(options)}


def get_applicable_airtightness(pre_renov_config: dict) -> dict:
    curr_airtightness = pre_renov_config["airtightness"]
    options = sorted(renovation_measures["airtightness"].keys())
    # Only keep options that are less than or equal to the current airtightness
    options = [at for at in options if at < curr_airtightness]
    options.append(curr_airtightness)
    return {"airtightness": tuple(options)}


def get_applicable_shading(pre_renov_config: dict) -> dict:
    """
    Returns a dictionary of applicable shading measures based on the pre-renovation
    configuration.
    """
    curr_shading = pre_renov_config["shaded_surfaces"]
    options = (
        [],
        ["SouthWall_0F", "SouthWall_1FS"],
        ["SouthWall_0F", "SouthWall_1FS", "NorthWall_0F", "NorthWall_1FN"],
    )
    idx = options.index(curr_shading)
    return {"shaded_surfaces": options[idx:]}


def get_applicable_PV(pre_renov_config: dict) -> dict:
    """
    Returns a dictionary of applicable PV measures based on the pre-renovation
    configuration.
    """
    curr_N_pv = pre_renov_config["N_pv"]
    # TODO: Update when using different roof geometries (with different N_pv)
    options = [0, 11, 22]
    idx = options.index(curr_N_pv)
    return {"N_pv": tuple(options[idx:])}


def get_applicable_radiators(pre_renov_config: dict) -> dict:
    curr_rad_area = pre_renov_config["radiator_area"]
    options = [4, 6, 8]
    idx = options.index(curr_rad_area)
    return {"radiator_area": tuple(options[idx:])}


def get_post_renov_configs(
    pre_renov_config: dict, unknown_params: dict, N_scenarios: int = 50
) -> pd.DataFrame:
    param_specs = deepcopy(pre_renov_config)
    for func in [
        get_applicable_insulation,
        get_applicable_glazing,
        get_applicable_ventilation_system,
        get_applicable_heating_system,
        get_applicable_airtightness,
        get_applicable_shading,
        get_applicable_PV,
        get_applicable_radiators,
    ]:
        param_specs.update(func(pre_renov_config))
    # Generate all combinations of the parameters
    post_renov_configs = generate_input_configs(param_specs, sampling="grid")
    scenarios = generate_input_configs(unknown_params, sampling="random", N=N_scenarios)
    # Combine the post-renovation configurations with the unknown parameters
    # cross product
    post_renov_configs = pd.merge(post_renov_configs, scenarios, how="cross")
    return post_renov_configs


def get_rm_options() -> dict:
    """
    Returns a dictionary of renovation measures (including no renovation).
    This is used in the demo to select the pre-renovation/existing state.
    """
    # Initialize with unrenovated options
    renov_options = {
        "wood_floor_insulation": [["Rockwool", "External", 0]],
        "concrete_floor_insulation": [["Rockwool", "External", 0]],
        "wall_insulation": [["Rockwool", "External", 0]],
        "roof_insulation": [["Rockwool", "External", 0]],
        ("glazing", "window_frame"): [
            ("SingleGlz", "Wood"),
            ("SingleGlz", "Aluminum"),
            ("DoubleGlz", "Wood"),
            ("DoubleGlz", "Aluminum"),
        ],
        "vent_type": ["A", "C1"],
        "heating_system": ["VR"],
        "radiator_area": [4, 6, 8],
        "N_pv": [0, 11, 22],
        "airtightness": [2],
        "shaded_surfaces": [
            [],
            ["SouthWall_0F", "SouthWall_1FS"],
            ["SouthWall_0F", "SouthWall_1FS", "NorthWall_0F", "NorthWall_1FN"],
        ],
    }
    for key, D_rm in renovation_measures.items():
        if "insulation" in key:
            options = [list(opt[:-1]) for opt in D_rm.keys()]
        elif key == "ventilation":
            options = list(set([opt[1] for opt in D_rm.keys()]))
            key = "vent_type"
        elif key in ["glazing", "heating_system", "airtightness"]:
            options = list(D_rm.keys())
            if key == "glazing":
                key = ("glazing", "window_frame")
        else:
            continue
        renov_options[key].extend(options)
    # Sort airtightness options
    renov_options["airtightness"] = sorted(renov_options["airtightness"], reverse=True)
    return renov_options


renovation_measures = {
    "wood_floor_insulation": {
        # (Material, Position, R-value, Thickness): Code
        ("Rockwool", "External", 2.4, 90): "WB002a",
        ("EPS", "External", 2.1, 100): "WB002c",
        # ("PIR/PUR", "External", 3.7, 100): "WB002e",
        ("PIR/PUR", "External", 3.7, 100): "WB002f",  # Same as above but cheaper
    },
    "concrete_floor_insulation": {
        ("Rockwool", "External", 2.4, 90): "WB002b",
        ("Rockwool", "External", 3.7, 140): "WB262",
        ("EPS", "External", 2.8, 100): "WB002d",
        # ("PIR/PUR", "External", 3.7, 100): "WB002e", Same as WB143 but higher cost
        ("PIR/PUR", "External", 4.2, 100): "WB153",
        ("PIR/PUR", "External", 3.1, 80): "WB204",
        ("PIR/PUR", "External", 3.7, 90): "WB143",
        # ("PIR/PUR", "External", 4.2, 100): "WB002g", # Same as WB153
        ("PIR/PUR", "External", 5.7, 130): "WB164",
    },
    "wall_insulation": {
        ("Rockwool", "Cavity", 1.1, 40): "WB392",
        ("Rockwool", "Cavity", 1.4, 50): "WB009a",
        ("Rockwool", "Cavity", 1.7, 60): "WB398",
        ("EPS", "Cavity", 1.6, 50): "WB009b",
        ("PIR/PUR", "Cavity", 2.1, 50): "WB009c",
        ("Rockwool", "Internal", 2, 70): "WB268",
        ("Rockwool", "Internal", 2.9, 100): "WB269",
        ("PIR/PUR", "Internal", 3.15, 70): "WB242",
        ("PIR/PUR", "Internal", 4.5, 100): "WB207",
        ("PIR/PUR", "Internal", 5.9, 130): "WB165",
        ("PIR/PUR", "Internal", 7.3, 180): "WB155",
        ("PIR/PUR", "Internal", 9.5, 210): "WB166",
        ("Biobased", "Internal", 2.1, 80): "WB243",
        ("Biobased", "Internal", 2.6, 100): "WB244",
        ("Biobased", "Internal", 3.7, 140): "WB364",
        ("EPS", "External", 3.5, 120): "WB008b",
        ("EPS", "External", 5.9, 200): "WB224",
        ("Rockwool", "External", 2.6, 100): "WB008a",
    },
    "roof_insulation": {
        ("PIR/PUR", "External", 3.6, 81): "WB004",
        ("PIR/PUR", "External", 6.45, 142): "WB212a",
        ("PIR/PUR", "External", 8.3, 175): "WB212b",
        ("EPS", "External", 5, 160): "WB413",
        ("EPS", "External", 6.3, 199): "WB414",
        ("EPS", "External", 8, 256): "WB415",
        ("PIR/PUR", "Internal", 3.1, 80): "WB005",
        ("PIR/PUR", "Internal", 3.7, 95): "WB223",
        ("PIR/PUR", "Internal", 4.2, 110): "WB205",
        ("PIR/PUR", "Internal", 5.2, 140): "WB145",
        ("PIR/PUR", "Internal", 6.8, 185): "WB167",
        ("PIR/PUR", "Internal", 7.3, 200): "WB154",
        ("PIR/PUR", "Internal", 8.3, 230): "WB168",
        ("Rockwool", "Internal", 4.3, 140): "WB230",
        ("Rockwool", "Internal", 4.5, 170): "WB264",
        ("Icynene", "Internal", 2.1, 55): "WB236",
        ("Icynene", "Internal", 6.3, 165): "WB237",
    },
    "glazing": {
        # (Glazing, Frame): (Code window, Code window + frame)
        ("HR++", "Wood"): ("WB019a", "WB252"),
        ("HR++", "Aluminum"): ("WB019a", "WB254"),
        ("HR++ Sun Protection", "Wood"): ("WB019a", "WB253"),  # NOTE: may add +61€
        ("HR++ Sun Protection", "Aluminum"): ("WB019a", "WB255"),  # same
        ("TripleGlz", "Wood"): ("WB147a", "WB161a"),
        ("TripleGlz", "Aluminum"): ("WB147a", "WB220"),
        ("TripleGlz", "PVC"): ("WB147a", "WB221"),
    },
    "ventilation": {
        # (Old, New): Code
        ("A", "C2"): "WB089a",
        ("C1", "C4a"): "WB170",
        ("A", "C4a"): "WB171",
        ("C1", "D5c"): "WB418",
        ("C2", "D5c"): "WB418",
        ("A", "D5c"): "WB089a + WB418",
    },
    "heating_system": {
        "HR107": "WB042b",
        "HP 5kW": "WB149b-min",
        "HP 7kW": "WB149b-mid",
        "HP 10kW": "WB149b-max",
        "HP 3kW Intergas + HR107 Parallel": {"VR": "WB159", "HR107": "WB199"},
    },
    "PV": "WB234",  # {"Multicrystalline": "WB158", "Monocrystalline": "WB234"},
    "airtightness": {0.4: "WB226", 0.7: "WB093", 1.0: "WB092"},
    "shading": "WB140",  # External
}

renovation_measures = remove_redundant_insulation_measures(renovation_measures)
