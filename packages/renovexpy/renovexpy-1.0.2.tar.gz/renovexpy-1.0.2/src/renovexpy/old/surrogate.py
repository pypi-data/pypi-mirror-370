from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    r2_score,
)
from tqdm import tqdm
from joblib import Parallel, delayed
from renovexpy.KPI import SimResultsReader
from threadpoolctl import threadpool_limits
from typing import List

try:
    import epw
except ImportError:
    pass

shared_surf_labels = {
    ### APARTMENTS
    # 3 exposed walls (corner, 1 row)
    ("WestWall", "Roof"): ("Corner", "Ground", "Detached"),
    ("WestWall", "Floor", "Roof"): ("Corner", "Middle", "Detached"),
    ("WestWall", "Floor"): ("Corner", "Top", "Detached"),
    # 2 exposed walls (corner, several rows)
    ("WestWall", "NorthWall", "Roof"): ("Corner", "Ground", "Corner"),
    ("WestWall", "NorthWall", "Floor", "Roof"): ("Corner", "Middle", "Corner"),
    ("WestWall", "NorthWall", "Floor"): ("Corner", "Top", "Corner"),
    # 2 exposed walls (middle, 1 row)
    ("WestWall", "EastWall", "Roof"): ("Middle", "Ground", "Detached"),
    ("WestWall", "EastWall", "Floor", "Roof"): ("Middle", "Middle", "Detached"),
    ("WestWall", "EastWall", "Floor"): ("Middle", "Top", "Detached"),
    # 1 exposed wall (middle, several rows)
    ("WestWall", "EastWall", "NorthWall", "Roof"): ("Middle", "Ground", "Corner"),
    ("WestWall", "EastWall", "NorthWall", "Floor", "Roof"): (
        "Middle",
        "Middle",
        "Corner",
    ),
    ("WestWall", "EastWall", "NorthWall", "Floor"): ("Middle", "Top", "Corner"),
    ### TERRACED HOUSES
    ("WestWall",): ("Corner", "Ground", "Detached"),
    ("WestWall", "EastWall"): ("Middle", "Ground", "Detached"),
}


def get_position_features(df):
    # TODO: use 2 columns, position and floor
    # Replace the shared surfaces with the corresponding labels
    df["shared_surfaces"] = [tuple(x) for x in df["shared_surfaces"]]
    df["shared_surfaces"] = df["shared_surfaces"].map(shared_surf_labels.get)
    # Split the shared surfaces into 3 columns
    position_features = pd.DataFrame(
        df["shared_surfaces"].tolist(),
        index=df.index,
        columns=[f"position_{x}" for x in ["WE", "floor", "NS"]],
    )
    return position_features


def get_insulation_features(constr, base_constr):
    # NOTE: may need to be adapated when using other base constructions
    assert type(constr) == type(base_constr) == list
    if isinstance(constr, str) or constr == base_constr:
        return 0, "None", "None"
    elif constr[0] != base_constr[0]:  # External insulation
        ins_pos = "External"
        ins_layer = constr[0]
    elif constr[-1] != base_constr[-1]:  # Internal insulation
        ins_pos = "Internal"
        ins_layer = constr[-1]
    elif constr[1] != base_constr[1]:  # Cavity insulation
        ins_pos = "Cavity"
        ins_layer = constr[1]
    ins_mat, ins_R = ins_layer.split("_R=")
    return float(ins_R), ins_mat, ins_pos


def get_construction_features(df):
    """
    Add construction features to the dataframe.
    NOTE: Internal and Shared surfaces are skipped.
    TODO: floor base construction is NaN if the floor is shared. Fix this.
    TODO: if wall base construction is not ["Brick_100mm", "Air_Gap_Cavity",
    "Brick_100mm"], it will not work.
    """
    constr_features = []
    for params in df["constructions"]:
        D = {}
        for surf_type, constr in params.items():
            # Skip Internal and Shared surfaces
            if "Internal" in surf_type or "Shared" in surf_type:
                continue
            # Define base construction
            elif "Wall" in surf_type:
                base_constr = ["Brick_100mm", "Air_Gap_Cavity", "Brick_100mm"]
            elif "Roof" in surf_type:
                base_constr = ["Plywood_19mm"]
            elif "Floor" in surf_type:
                if "Plywood_19mm" in constr:
                    base_constr = ["Plywood_19mm"]
                elif "Concrete_200mm" in constr:
                    base_constr = ["Concrete_200mm"]
                # Add feature with base floor construction
                D[f"base_construction_{surf_type}"] = base_constr[0]
            # Get insulation features
            if type(constr) == str:
                constr = [constr]
            ins_R, ins_mat, ins_pos = get_insulation_features(constr, base_constr)
            D[f"insulation_R_{surf_type}"] = ins_R
            D[f"insulation_material_{surf_type}"] = ins_mat
            D[f"insulation_position_{surf_type}"] = ins_pos
        constr_features.append(D)
    return pd.DataFrame(constr_features)


def get_window_features(df):
    window_features = []
    for params in df["windows"]:
        D = {}
        for surf_type, (glazing_type, wwr) in params.items():
            D[f"glazing_{surf_type}"] = glazing_type
            D[f"wwr_{surf_type}"] = wwr
        window_features.append(D)
    return pd.DataFrame(window_features)


def get_heating_features(df):
    heating_features = []
    for params in df["heating_params"]:
        D = {}
        for param, sched_per_zone in params.items():
            for zone, sched in sched_per_zone.items():
                if "Always_" in sched:  # NOTE: update when using other schedules?
                    sched = float(sched.split("_")[1])
                D[f"heating_{param}_{zone}"] = sched
        heating_features.append(D)
    return pd.DataFrame(heating_features)


def get_nat_vent_features(df):
    nat_vent_features = []
    for params in df["nat_vent_params"]:
        D = {}
        for param, sched_per_zone in params.items():
            for zone, sched in sched_per_zone.items():
                D[f"nat_vent_{param}_{zone}"] = sched
        nat_vent_features.append(D)
    return pd.DataFrame(nat_vent_features)


def get_mech_vent_features(df):
    mech_vent_features = []
    for params in df["mech_vent_params"]:
        D = {"mech_vent_level": params["vent_level"]}
        for zone, sched in params["usage_sched"].items():
            D[f"mech_vent_usage_sched_{zone}"] = sched
        mech_vent_features.append(D)
    return pd.DataFrame(mech_vent_features)


def get_occupant_features(df):
    occupant_features = []
    for params in df["occupants_params"]:
        D = {"occupant_activity_level": params["activity_level"]}
        for idx, sched in enumerate(params["occ_sched_names"]):
            D[f"occupant_{idx+1}_sched"] = sched
        occupant_features.append(D)
    return pd.DataFrame(occupant_features)


def get_equipment_features(df):
    return pd.DataFrame(df["equipment_params"].tolist())


def get_shading_features(df):
    shading_features = []
    for params in df["shading_params"]:
        D = {}
        for surf, surf_params in params.items():
            D.update(
                {
                    f"shading_{param}_{surf}": value
                    for param, value in surf_params.items()
                }
            )
        shading_features.append(D)
    return pd.DataFrame(shading_features)


def get_hourly_weather_features(epw_file: Path, time_window: int, n_configs: int):
    """
    Create a dataframe with outdoor temperature in the past X hours.
    """
    # Read epw file used for simulations
    assert Path(epw_file).exists()
    obj = epw.epw()
    obj.read(epw_file)
    # Create datraframe with weather features in the past X hours
    feature_names_and_lags = {
        "Dry Bulb Temperature": ("outdoor_temperature", 5),
        "Relative Humidity": ("humidity", 1),
        "Global Horizontal Radiation": ("solar_radiation", 1),
        "Wind Speed": ("wind_speed", 1),
    }
    df = pd.DataFrame()
    for feature, (col_name, lag) in feature_names_and_lags.items():
        for i in range(lag + 1):
            df[f"{col_name}_{-i}"] = obj.dataframe[feature].shift(i).astype(float)
    # Repeat the dataframe for each configuration
    df = pd.concat([df] * n_configs, ignore_index=True)
    return df


def get_hourly_building_features(
    configs: pd.DataFrame,
    sim_dir: Path,
    time_window: int,
):
    """
    Create a dataframe with hourly building features (zone temperature and
    heating demand).
    """

    def foo(config):
        # Load simulation results
        sim_id = config["id"]
        eso_file = sim_dir / f"{sim_id}/eplusout.eso"
        epjson_file = sim_dir / f"{sim_id}/input.epjson"
        sim_res = SimResultsReader(eso_file, epjson_file)
        # Extract hourly data
        df = pd.DataFrame()
        for zone in config["zones"]:
            col = f"Zone Mean Air Temperature {zone}"
            df[f"temperature_{zone}"] = sim_res.results["hourly"][col]
        df["heating_demand"] = sim_res.results["hourly"]["Boiler Heating Rate BOILER"]
        # Apply shift to temperature columns
        df_shifted = pd.DataFrame()
        for col in df.columns:
            for i in range(time_window + 1):
                df_shifted[f"{col}_{-i}"] = df[col].shift(i)
        return df_shifted

    n_configs = len(configs)
    L_df_shifted = Parallel(n_jobs=-1)(
        delayed(foo)(configs.iloc[i]) for i in tqdm(range(n_configs))
    )
    hourly_bf = pd.concat(L_df_shifted, ignore_index=True)
    return hourly_bf


def get_configs_features(
    configs_file: Path,
    cols_to_keep: List[str] = None,
    remove_redundant_features=False,
    hourly=False,
    epw_file=None,
    time_window=None,
    n_samples="all",
):
    df = pd.read_pickle(configs_file).infer_objects()
    sim_dir = Path(configs_file).parent
    if n_samples != "all" and n_samples < len(df):
        df = df.sample(n=n_samples).reset_index(drop=True)
    n_configs = len(df)
    # Get features
    position_features = get_position_features(df)
    constr_features = get_construction_features(df)
    window_features = get_window_features(df)
    heating_features = get_heating_features(df)
    nat_vent_features = get_nat_vent_features(df)
    mech_vent_features = get_mech_vent_features(df)
    occupant_features = get_occupant_features(df)
    equipment_features = get_equipment_features(df)
    shading_features = get_shading_features(df)
    other_features = df[["ventilation_type", "orientation", "airtightness"]]
    # Concatenate features
    X = pd.concat(
        [
            # Index should be consistent across dataframes
            position_features,
            constr_features,
            window_features,
            heating_features,
            nat_vent_features,
            mech_vent_features,
            occupant_features,
            equipment_features,
            shading_features,
            other_features,
        ],
        axis=1,
    )
    # Replace NaN values by "None" for cat features and -999 for num features
    cat_cols = X.select_dtypes(include="object").columns
    num_cols = X.select_dtypes(include="number").columns
    X[cat_cols] = X[cat_cols].fillna("None")
    X[num_cols] = X[num_cols].fillna(-999)
    if remove_redundant_features:
        # Remove columns with only one unique value
        X = X.loc[:, X.nunique() > 1]
        # Remove columns that are the same as another
        X = X.loc[:, ~X.T.duplicated()]
    # Add other cols (non-features) to X
    if cols_to_keep != None:
        X[cols_to_keep] = df[cols_to_keep]
    # Add hourly features if needed
    # TODO: may need to be adapted in order to return hourly y
    if hourly:
        # Repeat each row of X for each hour
        X = X.loc[np.repeat(X.index, 8760)].reset_index(drop=True)
        hourly_wf = get_hourly_weather_features(epw_file, time_window, n_configs)
        hourly_bf = get_hourly_building_features(df, sim_dir, time_window)
        X = pd.concat([X, hourly_wf, hourly_bf], axis=1)
    return X


def train_surrogate_models(X: pd.DataFrame, y: pd.DataFrame, output_dir: Path = None):
    print("Training surrogate models...")
    cat_features = X.select_dtypes(include="object").columns
    models = {}
    for kpi in y.columns:
        model = HistGradientBoostingRegressor(
            learning_rate=0.03,
            max_iter=4000,
            max_leaf_nodes=50,
            early_stopping=True,  # False
            categorical_features=cat_features,
        )
        # Split data in train/test sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y[kpi], test_size=0.2, random_state=42
        )
        with threadpool_limits(limits=8, user_api="openmp"):
            model.fit(X_train, y_train)
        # Evaluate model
        y_pred = model.predict(X_test)
        scores = {
            "R2 score": r2_score(y_test, y_pred),
            "MAE": mean_absolute_error(y_test, y_pred),
            "MAPE": mean_absolute_percentage_error(y_test, y_pred),
        }
        scores["MAE/mean(y)"] = scores["MAE"] / y_test.mean()
        print(f"# --- {kpi}")
        for metric, value in scores.items():
            print(f"{metric}: {value:.3f}")
        with threadpool_limits(limits=8, user_api="openmp"):
            model.fit(X, y[kpi])
        models[kpi] = model
    # Save models using joblib.
    if output_dir != None:
        output_dir.mkdir(exist_ok=True, parents=True)
        for kpi, model in models.items():
            joblib.dump(model, output_dir / f"{kpi}.joblib")
    return models


def train_hourly_surrogate_model(training_configs, epw_file, time_window):
    X = get_configs_features(
        training_configs,
        hourly=True,
        epw_file=epw_file,
        time_window=time_window,
        n_samples=100,
    )
    # Get targets (hourly heating demand and zone temperatures)
    y = pd.DataFrame()
    for col in X.columns:
        if col.startswith(("temperature", "heating_demand")) and col.endswith("_0"):
            y[col] = X.pop(col)
    # Define features and categorical features
    cat_features = X.select_dtypes(include="object").columns
    features = X.columns
    ### Train models
    # Split data in train/test sets on a per-configuration basis
    idx = np.arange(len(X)).reshape(-1, 8760)
    idx_train, idx_test = train_test_split(idx, test_size=0.2)
    X_train, X_test = X.iloc[idx_train.flatten()], X.iloc[idx_test.flatten()]
    y_train, y_test = y.iloc[idx_train.flatten()], y.iloc[idx_test.flatten()]
    for target in y.columns:
        model = HistGradientBoostingRegressor(categorical_features=cat_features)
        with threadpool_limits(limits=8, user_api="openmp"):
            model.fit(X_train, y_train[target])
            models[target] = model

    # Evaluate in "optimistic" mode (we use the true values for HD/Temp at previous hours)
    opt_hd_pred = models["heating_demand_0"].predict(X_test)
    hd_true = y_test["heating_demand_0"].to_numpy()
    opt_annual_hd_pred = opt_hd_pred.reshape(-1, 8760).sum(axis=1) / 1000
    annual_hd_true = hd_true.reshape(-1, 8760).sum(axis=1) / 1000
    opt_annual_mae = np.abs(opt_annual_hd_pred - annual_hd_true).mean()
    opt_hourly_mae = np.abs(opt_hd_pred - hd_true).mean()
    print(f"Optimistic case: Annual MAE = {int(opt_annual_mae)} kWh")
    print(f"Optimistic case: Hourly MAE = {int(opt_hourly_mae)} kWh")

    ### Evaluate in realistic mode (we use the predicted values for HD/Temp at previous hours)
    # First, erase the values of heating demand and zone temperature at previous hours
    X_test_hidden = X_test.copy()
    for col in X_test_hidden.columns:
        if col.startswith(("temperature", "heating_demand")):
            X_test_hidden[col] = np.nan
    # For each hour, predict the zone temperature and heating demand
    # and fill X_test_hidden with the predictions
    y_pred = y_test.copy()
    y_pred[:] = np.nan
    for hour_idx in tqdm(range(8760)):
        idx_test_hour = idx_test[:, hour_idx]
        for target, model in models.items():
            y_pred_hour = model.predict(X_test_hidden.loc[idx_test_hour])
            # Fill y_pred with the predictions
            y_pred.loc[idx_test_hour, target] = y_pred_hour
            # Fill X_test_hidden with the predictions
            for shift in range(1, time_window + 1):
                if hour_idx + shift < 8760:
                    col_target_shift = target.replace("_0", f"_{-shift}")
                    X_test_hidden.loc[idx_test_hour + shift, col_target_shift] = y_pred
    real_hd_pred = y_pred["heating_demand_0"].to_numpy()
    real_annual_hd_pred = real_hd_pred.reshape(-1, 8760).sum(axis=1) / 1000
    real_annual_mae = np.abs(real_annual_hd_pred - annual_hd_true).mean()
    real_hourly_mae = np.abs(real_hd_pred - hd_true).mean()
    print(f"Realistic case: Annual MAE = {int(real_annual_mae)} kWh")
    print(f"Realistic case: Hourly MAE = {int(real_hourly_mae)} kWh")
    return models, features


# def train_hourly_surrogate_model(training_configs, epw_file, time_window):
#     """Variant where previous HD/Temperature values are not used."""
#     X = get_configs_features(
#         training_configs,
#         hourly=True,
#         epw_file=epw_file,
#         time_window=time_window,
#         n_samples=100,
#     )
#     X.drop(
#         columns=[
#             col
#             for col in X.columns
#             if col.startswith(("temperature", "heating_demand"))
#         ],
#         inplace=True,
#     )
#     # Get targets (hourly heating demand and zone temperatures)
#     y = X.pop("heating_demand_0")
#     # Define features and categorical features
#     cat_features = X.select_dtypes(include="object").columns
#     features = X.columns
#     ### Train models
#     # Split data in train/test sets on a per-configuration basis
#     idx = np.arange(len(X)).reshape(-1, 8760)
#     idx_train, idx_test = train_test_split(idx, test_size=0.2)
#     X_train, X_test = X.iloc[idx_train.flatten()], X.iloc[idx_test.flatten()]
#     y_train, y_test = y.iloc[idx_train.flatten()], y.iloc[idx_test.flatten()]
#     model = HistGradientBoostingRegressor(categorical_features=cat_features)
#     with threadpool_limits(limits=8, user_api="openmp"):
#         model.fit(X_train, y_train)

#     # Evaluate in "optimistic" mode (we use the true values for HD/Temp at previous hours)
#     opt_hd_pred = model.predict(X_test)
#     hd_true = y_test.to_numpy()
#     bias = (opt_hd_pred - hd_true).mean()
#     opt_hd_pred -= bias
#     opt_annual_hd_pred = opt_hd_pred.reshape(-1, 8760).sum(axis=1) / 1000
#     annual_hd_true = hd_true.reshape(-1, 8760).sum(axis=1) / 1000
#     opt_annual_mae = np.abs(opt_annual_hd_pred - annual_hd_true).mean()
#     opt_hourly_mae = np.abs(opt_hd_pred - hd_true).mean()
#     print(f"Optimistic case: Annual MAE = {int(opt_annual_mae)} kWh")
#     print(f"Optimistic case: Hourly MAE = {int(opt_hourly_mae)} kWh")

#     ### Evaluate in realistic mode (we use the predicted values for HD/Temp at previous hours)
#     # First, erase the values of heating demand and zone temperature at previous hours
#     X_test_hidden = X_test.copy()
#     for col in X_test_hidden.columns:
#         if col.startswith(("temperature", "heating_demand")):
#             X_test_hidden[col] = np.nan
#     # For each hour, predict the zone temperature and heating demand
#     # and fill X_test_hidden with the predictions
#     y_pred = y_test.copy()
#     y_pred[:] = np.nan
#     for hour_idx in tqdm(range(8760)):
#         idx_test_hour = idx_test[:, hour_idx]
#         for target, model in models.items():
#             y_pred_hour = model.predict(X_test_hidden.loc[idx_test_hour])
#             # Fill y_pred with the predictions
#             y_pred.loc[idx_test_hour, target] = y_pred_hour
#             # Fill X_test_hidden with the predictions
#             for shift in range(1, time_window + 1):
#                 if hour_idx + shift < 8760:
#                     col_target_shift = target.replace("_0", f"_{-shift}")
#                     X_test_hidden.loc[idx_test_hour + shift, col_target_shift] = y_pred
#     real_hd_pred = y_pred["heating_demand_0"].to_numpy()
#     real_annual_hd_pred = real_hd_pred.reshape(-1, 8760).sum(axis=1) / 1000
#     real_annual_mae = np.abs(real_annual_hd_pred - annual_hd_true).mean()
#     real_hourly_mae = np.abs(real_hd_pred - hd_true).mean()
#     print(f"Realistic case: Annual MAE = {int(real_annual_mae)} kWh")
#     print(f"Realistic case: Hourly MAE = {int(real_hourly_mae)} kWh")
#     return models, features


def populate_database_with_surrogate(ft_file: Path, features: List, models: dict):
    df = pd.read_parquet(ft_file)
    X = df[features]
    with threadpool_limits(limits=8, user_api="openmp"):
        for kpi, model in models.items():
            df[kpi] = np.maximum(model.predict(X), 0)
    # Save the off-the-fly database
    df.to_parquet(ft_file)
    return
