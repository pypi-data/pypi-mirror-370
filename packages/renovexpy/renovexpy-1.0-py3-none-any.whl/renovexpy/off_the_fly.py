"""
File that implements all the steps needed to create the off-the-fly model:
    1. Run parametric simulations
    2. Train the surrogate models
    3. Given a pre-renovation state, get relevant renovation packages
    4. Get the post-renovation KPIs by querying the surrogate models

"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from threadpoolctl import threadpool_limits

from renovexpy.kpi import (
    get_CO2_emissions,
    get_CO2_reduction_per_euro,
    get_payback_period,
    get_renovation_cost,
    get_TCO,
)
from renovexpy.optimization import (
    compute_robustness_indicators,
    pareto_optimization,
    find_optimal_packages,
)
from renovexpy.parametric import run_parametric_simulations
from renovexpy.renovation import get_post_renov_configs, renovation_measures
from renovexpy.surrogate import make_X_y, train_surrogate_models
from renovexpy.utils import load_parquet_with_json

curr_dir = Path(__file__).resolve().parent


def run_sim_and_train_models(sim_dir: Path):
    param_specs_training = {
        "building_type": "terraced_house",
        "building_position": ("corner", "middle"),
        "building_orientation": ("S", "W"),
        "floor_type": ("Wood", "Concrete"),
        "floor_insulation": [("Rockwool", "EPS", "PIR/PUR"), "External", slice(0, 6)],
        "roof_insulation": [
            ("Rockwool", "EPS", "PIR/PUR", "Icynene"),
            ("External", "Internal"),
            slice(0, 10),
        ],
        "wall_insulation": [
            ("Rockwool", "EPS", "PIR/PUR"),
            ("External", "Cavity", "Internal"),
            slice(0, 10),
        ],
        "glazing": (
            "SingleGlz",
            "DoubleGlz",
            "HR++",
            "HR++ Sun Protection",
            "TripleGlz",
        ),
        "window_frame": ("Wood", "Aluminum", "PVC"),
        "WWR": slice(0.2, 0.8),
        "airtightness": slice(0.4, 2),
        "n_occupants": (1, 2, 4),
        "occupant_activity_level": "mid",
        "heated_zones": (
            ["0F"],
            ["0F", "1FS"],
            ["0F", "1FS", "1FN"],
            ["0F", "1FS", "2F"],
            ["0F", "1FS", "1FN", "2F"],
        ),
        "heating_setpoint": (
            "Always_21",
            "N17_D19",
            "N15_D19",
            "N17_D20",
            "N15_M17_D16_E19",
        ),
        "vent_type": ("A", "C1", "C2", "C4a", "D5c"),
        "window_vent_profile": (1, 2, 3, 4),
        "use_vent_grilles": (True, False),
        "mech_vent_profile": (1, 2, 3),
        "lighting_power_per_area": 1,
        "equipment_power_per_area": 1,
        "shaded_surfaces": (
            [],
            ["SouthWall_0F", "SouthWall_1FS"],
            ["SouthWall_0F", "SouthWall_1FS", "NorthWall_0F", "NorthWall_1FN"],
        ),
        "shading_position": "External",
        "shading_profile": (1, 2, 3, 4),
        "epw_file": ("DeBilt_2000", "DeBilt_2050", "DeBilt_2100"),
    }
    run_parametric_simulations(
        sim_dir=sim_dir,
        param_specs=param_specs_training,
        sampling="random",
        N=20000,
    )
    kpis_to_predict = {
        "Heating demand [kWh]": True,
        "Gas consumption [kWh]": True,
        "Electricity consumption [kWh]": True,
        "Electricity OPP [kW]": True,
        "Overheating [h]": True,
        "CO2 excess [h]": True,
        "Average CO2 exposure [ppm]": True,
        "Operational cost [€]": True,
        "CO2 emissions [kgCO2]": False,
    }
    df = load_parquet_with_json(sim_dir / "simulated_configs.parquet")
    X, y = make_X_y(df, kpis_to_predict, N_samples_max=100000)
    train_surrogate_models(
        X,
        y,
        save_dir=curr_dir / "surrogate_models",
        max_iter=1000,
        max_leaf_nodes=50,
        early_stopping=True,
    )
    pd.read_csv(curr_dir / "surrogate_models/scores.csv")
    return


pre_renov_config = {
    "building_type": "terraced_house",
    "building_position": "middle",
    "building_orientation": "S",
    "floor_type": "Wood",
    "floor_insulation": ["Rockwool", "External", 0],
    "roof_insulation": ["Rockwool", "External", 0],
    "wall_insulation": ["Rockwool", "External", 0],
    ("glazing", "window_frame"): ["DoubleGlz", "Wood"],
    "WWR": 0.36,
    "airtightness": 2,
    "vent_type": "A",
    "heating_system": "VR",
    "radiator_area": 4,
    "N_pv": 0,
    "occupant_activity_level": "mid",
    "lighting_power_per_area": 1,
    "equipment_power_per_area": 1,
    "shaded_surfaces": [],
    "shading_position": "External",
}

unknown_params = {
    "n_occupants": (1, 2, 4),
    "heated_zones": (
        ["0F"],
        ["0F", "1FS"],
        ["0F", "1FS", "1FN"],
        ["0F", "1FS", "2F"],
        ["0F", "1FS", "1FN", "2F"],
    ),
    "heating_setpoint": (
        "Always_21",
        "N17_D19",
        "N15_D19",
        "N17_D20",
        "N15_M17_D16_E19",
    ),
    "window_vent_profile": (1, 2, 3, 4),
    "use_vent_grilles": (True, False),
    "mech_vent_profile": (1, 2, 3),
    "shading_profile": (1, 2, 3, 4),
    "epw_file": ("DeBilt_2000", "DeBilt_2050", "DeBilt_2100"),
}


def query_surrogate_models_batch(
    pre_renov_config: dict,
    unknown_params: dict,
    replace_window_frames: bool = False,
    max_rm_per_package: int = 5,
) -> pd.DataFrame:

    # Get features used by surrogate models
    model_files = list((curr_dir / "surrogate_models").glob("*.joblib"))
    kpis = [f.stem for f in model_files]
    models = [joblib.load(f) for f in model_files]
    model_features = models[0].feature_names_in_
    # Get post-renovation configurations
    post_renov_configs = get_post_renov_configs(
        pre_renov_config, unknown_params, N_scenarios=1
    )
    # Remove renovation packages that combine more than X renovation measures
    df_change = pd.DataFrame()
    for param, value in pre_renov_config.items():
        if isinstance(param, tuple):
            for p, v in zip(param, value):
                df_change[p] = post_renov_configs[p] != v
        else:
            if isinstance(value, list):
                df_change[param] = post_renov_configs[param].apply(lambda x: x != value)
            else:
                df_change[param] = post_renov_configs[param] != value
    mask = df_change.sum(axis=1) <= max_rm_per_package
    post_renov_configs = post_renov_configs[mask].reset_index(drop=True)
    X, _ = make_X_y(post_renov_configs, kpis_to_predict={}, use_cols=model_features)
    # Predict KPIs using surrogate models
    for kpi, model in zip(kpis, models):
        with threadpool_limits(limits=1, user_api="openmp"):
            X[kpi] = np.clip(model.predict(X), 0, None)  # Ensure non-negative values
    # Add other KPIs
    X["CO2 emissions [kgCO2]"] = get_CO2_emissions(
        X["Electricity consumption [kWh]"], X["Gas consumption [kWh]"]
    )
    df_cost = get_renovation_cost(
        renovation_measures, pre_renov_config, post_renov_configs, replace_window_frames
    )
    X["Renovation cost [€]"] = df_cost.sum(axis=1).values
    X["TCO over 30 years [€]"] = get_TCO(
        X["Renovation cost [€]"], X["Operational cost [€]"]
    )
    X["Payback period [year]"] = get_payback_period(
        X["Renovation cost [€]"], X["Operational cost [€]"]
    )
    X["CO2 reduction per euro [kgCO2/€]"] = get_CO2_reduction_per_euro(
        X["CO2 emissions [kgCO2]"], X["Renovation cost [€]"]
    )
    return X


def query_surrogate_models(
    pre_renov_config: dict,
    unknown_params: dict,
    N_scenarios: int,
    replace_window_frames: bool = False,
    max_rm_per_package: int = 5,
    save_dir: Path = None,
):
    results = Parallel(n_jobs=-1)(
        delayed(query_surrogate_models_batch)(
            pre_renov_config, unknown_params, replace_window_frames, max_rm_per_package
        )
        for _ in range(N_scenarios)
    )
    n_rp = len(results[0])
    df = pd.concat(results, ignore_index=True)
    print(f"Simulated {n_rp} renovation packages across {N_scenarios} scenarios.")
    # Add rp id and scenario id
    df["rp_id"] = np.tile(np.arange(n_rp), N_scenarios)
    df["scenario_id"] = np.repeat(np.arange(N_scenarios), n_rp)
    # Save to file
    if save_dir is None:
        return df
    fname = save_dir / "post_renovation_configs.parquet"
    df.to_parquet(fname, index=False)
    return


if __name__ == "__main__":
    sim_dir = Path("/projects/0/prjs1234/off_the_fly/MVP_house") / "simulations"
    # run_sim_and_train_models(sim_dir)
    # query_surrogate_models(
    #     pre_renov_config, unknown_params, N_scenarios=100, replace_window_frames=False
    # )
    df = pd.read_parquet(sim_dir.parent / "post_renovation_configs.parquet")
    unknown_params = list(unknown_params.keys())
    # Optimize average
    df_opt = find_optimal_packages(
        df,
        unknown_params,
        kpis=[
            "Overheating [h]",
            "CO2 emissions [kgCO2]",
            "Renovation cost [€]",
            "TCO over 30 years [€]",
            "Electricity OPP [kW]",
        ],
        requirements={},
        robustness_indicator="mean",
        N_top=10,
    )
    pd.set_option("display.max_columns", None)
    df_opt.to_csv(
        "./optimal_packages/lowest_kpi_avg.csv",
        index=False,
    )
    # Optimize CO2 reduction per euro (without requirements)
    df_opt = find_optimal_packages(
        df,
        unknown_params,
        kpis=["CO2 reduction per euro [kgCO2/€]"],
        requirements={},
        robustness_indicator="mean",
        N_top=10,
    )
    pd.set_option("display.max_columns", None)
    df_opt.to_csv(
        "./optimal_packages/lowest_CO2_reduction_per_euro.csv",
        index=False,
    )
    # Optimize CO2 reduction per euro (with requirements)
    df_opt = find_optimal_packages(
        df,
        unknown_params,
        kpis=["CO2 reduction per euro [kgCO2/€]"],
        requirements={
            "Overheating [h]": 300,
            "CO2 excess [h]": 300,
        },
        robustness_indicator="mean",
        N_top=10,
    )
    pd.set_option("display.max_columns", None)
    df_opt.to_csv(
        "./optimal_packages/lowest_CO2_reduction_per_euro_with_requirements.csv",
        index=False,
    )
