from pathlib import Path

import joblib
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy.signal import savgol_filter
from sklearn.decomposition import PCA, DictionaryLearning
from sklearn.cluster import KMeans
from sklearn.model_selection import cross_val_score
from tqdm import tqdm
from joblib import Parallel, delayed

from renovexpy.surrogate import make_X_y
from renovexpy.utils import load_parquet_with_json

sns.set_style("whitegrid")
curr_dir = Path(__file__).parent

param_labels = {
    "building_position": "Building position",
    "building_orientation": "Building orientation",
    "floor_type": "Floor type",
    "glazing": "Glazing type",
    "window_frame": "Window frame",
    "WWR": "Window-to-wall ratio",
    "airtightness": "Airtightness",
    "n_occupants": "Number of occupants",
    "heated_zones": "Heated zones",
    "heating_setpoint": "Heating setpoint",
    "vent_type": "Ventilation type",
    "window_vent_profile": "Window ventilation schedule",
    "use_vent_grilles": "Use of ventilation grilles",
    "mech_vent_profile": "Mechanical ventilation schedule",
    "shaded_surfaces": "Shaded facades",
    "shading_profile": "Shading schedule",
    "epw_file": "Weather scenario",
    "heating_system": "Heating system",
    "radiator_area": "Radiator area",
    "N_pv": "PV panels",
    "floor_insulation_0": "Floor insulation material",
    "floor_insulation_2": "Floor insulation R-value",
    "roof_insulation_0": "Roof insulation material",
    "roof_insulation_1": "Roof insulation position",
    "roof_insulation_2": "Roof insulation R-value",
    "wall_insulation_0": "Wall insulation material",
    "wall_insulation_1": "Wall insulation position",
    "wall_insulation_2": "Wall insulation R-value",
}

param_values = {
    "building_position": ["corner", "middle"],
    "building_orientation": {"S": "South", "W": "West"},
    "floor_type": ["Wood", "Concrete"],
    "glazing": {
        "SingleGlz": "SG",
        "DoubleGlz": "DG",
        "HR++": "DG HR++",
        "HR++ Sun Protection": "DG HR++\nSun Protection",
        "TripleGlz": "TG",
    },
    "window_frame": ["PVC", "Aluminum", "Wood"],
    "WWR": slice(0.2, 0.8),
    "airtightness": slice(0.4, 2.0),
    "n_occupants": [1, 2, 4],
    "heated_zones": {
        "['0F']": "0F",
        "['0F', '1FS']": "0F, 1FS",
        "['0F', '1FS', '1FN']": "0F, 1FS, 1FN",
        "['0F', '1FS', '2F']": "0F, 1FS, 2F",
        "['0F', '1FS', '1FN', '2F']": "0F, 1FS, 1FN, 2F",
    },
    "heating_setpoint": [
        "Always_21",
        "N17_D20",
        "N17_D19",
        "N15_D19",
        "N15_M17_D16_E19",
    ],
    "vent_type": ["A", "C1", "C2", "C4a", "D5c"],
    "window_vent_profile": {
        3: "Always closed",
        1: "1F ajar warm nights",
        2: "1F wide open summer\nmorning/evenings, else ajar",
        4: "0F/1F ajar, but 1F wide\nopen in summer if occupied",
    },
    "use_vent_grilles": {False: "No", True: "Yes"},
    "mech_vent_profile": {1: "Low", 2: "Medium", 3: "Low-Medium/CO2 controlled"},
    "shaded_surfaces": {
        "[]": "None",
        "['SouthWall_0F', 'SouthWall_1FS']": "South facade",
        "['SouthWall_0F', 'SouthWall_1FS', 'NorthWall_0F', 'NorthWall_1FN']": "South and North facades",
    },
    "shading_profile": {
        1: "Off",
        2: "On if T>22 and Irr>200",
        3: "On if T>24, Irr>300 and occupied",
        4: "On during summer",
    },
    "epw_file": {
        "DeBilt_2000": "Year 2000",
        "DeBilt_2050": "Year 2050",
        "DeBilt_2100": "Year 2100",
    },
    "heating_system": {
        "VR": "VR",
        "HR107": "HR107",
        "HP 5kW": "HP 5kW",
        "HP 7kW": "HP 7kW",
        "HP 10kW": "HP 10kW",
        "HP 3kW Intergas + HR107 Parallel": "Hybrid HP",
    },
    "radiator_area": [4, 6, 8],
    "N_pv": {
        0: "None",
        11: "Half-roof",
        22: "Full-roof",
    },
    "floor_insulation_0": {
        "PIR/PUR": "PIR/PUR",
        "EPS": "EPS",
        "Rockwool": "Mineral wool",
    },
    "floor_insulation_2": slice(0, 6),
    "roof_insulation_0": {
        "EPS": "EPS",
        "PIR/PUR": "PIR/PUR",
        "Rockwool": "Mineral wool",
        "Icynene": "Polyurethane foam",
    },
    "roof_insulation_1": ["External", "Internal"],
    "roof_insulation_2": slice(0, 10),
    "wall_insulation_0": {
        "PIR/PUR": "PIR/PUR",
        "Rockwool": "Mineral wool",
        "EPS": "EPS",
    },
    "wall_insulation_1": ["External", "Internal", "Cavity"],
    "wall_insulation_2": slice(0, 10),
}


def load_training_data(sim_results: Path, kpis_to_predict: dict):
    df = load_parquet_with_json(sim_results)
    X, y = make_X_y(df, kpis_to_predict, N_samples_max=100000)
    return X, y


def make_kpi_histograms(y: pd.DataFrame, kpis: list):
    for kpi in kpis:
        fig, ax = plt.subplots(dpi=200, figsize=(4, 2.7))
        sns.histplot(y[kpi], bins=50, kde=True, ax=ax)
        plt.xlabel(kpi)
        # plt.ylabel("Frequency")
        plt.yticks([])
        # plt.title(f"Histogram of {kpi}")
        save_dir = curr_dir / f"sensitivity_analysis/{kpi}"
        save_dir.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_dir / "histogram.png", dpi=200, bbox_inches="tight")
        plt.close()
    return


def load_model(model_file: Path):
    return joblib.load(model_file)


def get_best_comp_idx(components, y, bias=None):
    n_samples = y.shape[0]
    # Get the idx of the component which best fits each sample
    mae = np.zeros((n_samples, len(components)))
    for k, ck in enumerate(components):
        # Gives the best weight for the k-th component (minimum MSE)
        bk = bias[k] if bias is not None else 0
        w = np.dot(y - bk, ck) / np.dot(ck, ck)
        y_sc = ck * w[:, None] + bk
        mae[:, k] = np.mean(np.abs(y - y_sc) ** 2, axis=1)
    # Set weight to 0 for the worst component
    best_comp_idx = np.argmin(mae, axis=1)
    return best_comp_idx


def update_wc_pca(old_c, old_w, old_b, y):
    # Get new_weights for each sample
    best_comp_idx = get_best_comp_idx(old_c, y, bias=old_b)
    mask = best_comp_idx == 0
    # Split the data in two parts based on mask
    y1, y2 = y[mask], y[~mask]
    y1_pd, y2_pd = np.mean(y1, axis=0), np.mean(y2, axis=0)
    new_b = np.vstack([y1_pd, y2_pd])
    # Fit a PCA model with n_component = 1 on each subset of the data
    pca1, pca2 = PCA(n_components=1), PCA(n_components=1)
    new_w1, new_w2 = pca1.fit_transform(y1), pca2.fit_transform(y2)
    new_w = np.zeros_like(old_w)
    new_w[mask, 0] = new_w1.flatten()
    new_w[~mask, 1] = new_w2.flatten()
    new_c = np.vstack([pca1.components_, pca2.components_])
    return new_c, new_w, new_b


def sparse_pca(y):
    """
    Apply Sparse PCA on ICE curves with n_components = 2.
    First divide the samples into 2 groups with different trends (using DL).
    Then fit PCA with 1 component on each group.
    Assign each sample to the component + bias that best fits it.
    Repeat the process until convergence.
    """
    dl = DictionaryLearning(n_components=2, max_iter=5, alpha=0, n_jobs=4)
    W = dl.fit_transform(y)
    C = dl.components_
    # Try improve with PCA
    for k in range(100):
        if k == 0:
            B = None
        C, W, B = update_wc_pca(C, W, B, y)
        Wb = (W != 0).astype(int)
        y_dl = W @ C + Wb @ B
        var_exp = 1 - (np.var(y - y_dl) / np.var(y))
        mae = np.abs(y - y_dl).mean(axis=0)
    return W, C, Wb, B, var_exp, mae


def regular_pca(y):
    """
    Apply regular PCA on ICE curves with n_components = 1.
    """
    pca = PCA(n_components=1)
    W = pca.fit_transform(y)
    C = pca.components_
    Wb = np.ones((W.shape[0], 1))
    B = pca.mean_[None, :]
    y_pca = W @ C + Wb @ B
    var_exp = 1 - (np.var(y - y_pca) / np.var(y))
    mae = np.abs(y - y_pca).mean(axis=0)
    return W, C, Wb, B, var_exp, mae


def compute_ICE_curves(model, X: pd.DataFrame, n_samples: int, save_dir: Path):
    # Remove rows with "HP 3kW Intergas + HR107 Alternate"
    mask = X["heating_system"] != "HP 3kW Intergas + HR107 Alternate"
    X = X[mask].reset_index(drop=True)
    # Sample the input data
    X = X.sample(n=n_samples, random_state=42).reset_index(drop=True)
    # if "Electricity OPP [kW]" == save_dir.name:
    #     # Replace gas boilers by HP or Hybrid HP
    #     HP_systems = [hs for hs in param_values["heating_system"].keys() if "HP" in hs]
    #     X["heating_system"] = np.random.choice(HP_systems, size=n_samples, replace=True)
    D = {"X": X}
    ### Loop over parameters
    for param in tqdm(X.columns):
        x_param = param_values[param]
        # if "Electricity OPP [kW]" == save_dir.name and param == "heating_system":
        #     # Limit the parameter values to HP systems
        #     x_param = [hs for hs in x_param if "HP" in hs]
        # Define set of values for the parameter and do cartesian product
        if isinstance(x_param, slice):
            x_param = np.linspace(x_param.start, x_param.stop, num=101)
        elif isinstance(x_param, dict):
            x_param = list(x_param.keys())
        else:
            pass
        X_ice = X.copy()
        del X_ice[param]
        X_ice = X_ice.merge(pd.DataFrame({param: x_param}), how="cross")
        y_ice = model.predict(X_ice).reshape(-1, len(x_param))
        D[param] = {"x": x_param, "y_ice": y_ice}
    # Save ICE curves to file
    save_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(D, save_dir / "ice_curves.joblib")
    return


def apply_sparse_PCA(save_dir: Path):
    D_ice_curves = joblib.load(save_dir / "ice_curves.joblib")
    for param, data in tqdm(D_ice_curves.items()):
        if param == "X":
            continue
        # Load ICE Curves and subtract the first value
        y_ice = data["y_ice"]
        y_ice = y_ice - y_ice[:, 0][:, None]
        # Smooth the ICE curves
        if len(data["x"]) > 30:
            y_ice = savgol_filter(y_ice, window_length=30, polyorder=2, axis=1)
        # Apply regular PCA and if needed sparse PCA
        W, C, Wb, B, var_exp, mae = regular_pca(y_ice)
        D_ice_curves[param]["pca"] = (W, C, Wb, B, var_exp, mae)
        if var_exp < 0.95:
            print(f"Warning: {param} PCA explained variance is low: {var_exp:.2f}")
            D_ice_curves[param]["sparse_pca"] = sparse_pca(y_ice)
    # Save results
    joblib.dump(D_ice_curves, save_dir / "ice_curves.joblib")
    return


def make_PD_plots(save_dir: Path):
    D_ice_curves = joblib.load(save_dir / "ice_curves.joblib")
    for param, data in tqdm(D_ice_curves.items()):
        if param == "X":
            continue
        # Load data
        x = data["x"]
        if isinstance(param_values[param], dict):
            x = [param_values[param][x_i] for x_i in x]
        if len(x) < 10:
            x = [str(x_i) for x_i in x]
        pca_data = (
            [data["pca"], data["sparse_pca"]] if "sparse_pca" in data else [data["pca"]]
        )
        for W, C, Wb, B, var_exp, mae in pca_data:
            nc = C.shape[0]  # Number of components
            ### Make PD plot
            fig, ax = plt.subplots(dpi=200, figsize=(4, 2.7))
            colors = ["tab:blue", "tab:orange"]
            for k in range(nc):
                mask = W[:, k] != 0
                Wk = W[mask, k]
                Wk_quantiles = np.percentile(Wk, [5, 25, 75, 95])
                freq = round(mask.sum() / len(mask) * 100)
                for wq in Wk_quantiles:
                    y_wq = wq * C[k] + B[k]
                    plt.plot(x, y_wq, linewidth=1, color=colors[k])
                # Add pd curve
                plt.plot(
                    x, B[k], linewidth=1, color="black", label=f"Group {k+1}: {freq}%"
                )
                # Add error envelope with fill_between
                plt.fill_between(x, B[k] - mae, B[k] + mae, color="gray", alpha=1)
            # Set labels
            plt.xlabel(param_labels[param])
            plt.ylabel(f"Change in\n{kpi}")
            if type(x[0]) == str and max([len(x_i) for x_i in x]) > 5:
                plt.xticks(rotation=90, ha="center", fontsize=10)
            if nc > 1:
                plt.legend()
            # Save figure
            save_file = save_dir / param_labels[param] / f"pd_{nc}.png"
            save_file.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_file, dpi=200, bbox_inches="tight")
            plt.close()
    return


def cluster_ICE_curves(y_ice, n_clusters_max=7):
    """
    Cluster the ICE curves using KMeans and return the cluster labels.
    """
    for nc in range(2, n_clusters_max + 1):
        labels = KMeans(nc, random_state=42).fit(y_ice).labels_
        cluster_freq = pd.Series(labels).value_counts(normalize=True)
        if not (cluster_freq > 0.05).all():
            n_clusters = nc - 1
            break
    if nc == n_clusters_max:
        n_clusters = nc
    # Rerun KMeans with the new number of clusters
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(y_ice)
    labels = kmeans.labels_
    y_centroids = kmeans.cluster_centers_
    # Compute 25% and 75% percentiles for each cluster
    y_quantiles = np.zeros((y_centroids.shape[0], y_centroids.shape[1], 2))
    for k in range(y_centroids.shape[0]):
        mask = labels == k
        y_quantiles[k, :, 0] = np.percentile(y_ice[mask], 25, axis=0)
        y_quantiles[k, :, 1] = np.percentile(y_ice[mask], 75, axis=0)
    # Reorder clusters based on centroids similarity
    pca = PCA(n_components=1)
    pca_coef = pca.fit_transform(y_centroids)
    sign = np.sign(pca.components_)[0][-1]
    pca_coef *= sign
    perm = np.argsort(-pca_coef, axis=0).flatten()
    mapping = {i: j for i, j in zip(perm, range(len(perm)))}
    labels = np.array([mapping[label] for label in labels])
    y_centroids = y_centroids[perm]
    y_quantiles = y_quantiles[perm]
    cluster_freq = pd.Series(labels).value_counts(normalize=True)
    cluster_freq = cluster_freq.sort_index()
    return labels, y_centroids, y_quantiles, cluster_freq


def wrap_text_by_length(text, n):
    text = text.replace("\n", " ")  # Remove newlines
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + (1 if current_line else 0) <= n:
            current_line += (" " if current_line else "") + word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return "\n".join(lines)


def make_PD_plots_clustering(save_dir: Path, n_clusters_max: int = 7):
    kpi = save_dir.name
    D_ice_curves = joblib.load(save_dir / "ice_curves.joblib")
    X = D_ice_curves.pop("X")
    mask = X["heating_system"].str.contains("HP")
    if "OPP" in kpi:
        X = X[mask].reset_index(drop=True)
    sns.set_style("whitegrid")
    for param, data in tqdm(D_ice_curves.items()):
        # Load data
        x = data["x"]
        if isinstance(param_values[param], dict):
            x = [param_values[param][x_i] for x_i in x]
        y_ice = data["y_ice"]
        y_ice = y_ice - y_ice[:, 0][:, None]
        if "OPP" in kpi:  # Limit the parameter values to HP systems
            y_ice = y_ice[mask]
        # Smooth the ICE curves
        if len(data["x"]) > 30:
            y_ice = savgol_filter(y_ice, window_length=30, polyorder=2, axis=1)
        # Apply clustering
        labels, y_centroids, y_quantiles, freq = cluster_ICE_curves(
            y_ice, n_clusters_max
        )
        n_clusters = len(freq)
        ### Plot PD curves
        cluster_names = ["A", "B", "C", "D", "E", "F", "G"]
        colors = sns.color_palette("tab10", n_colors=n_clusters_max)
        fig, ax = plt.subplots(dpi=200, figsize=(4, 2.7))
        for k in range(y_centroids.shape[0]):
            y_wq = y_centroids[k]
            # Add pd curve
            plt.plot(
                x,
                y_wq,
                linewidth=1,
                color=colors[k],
                label=f"{cluster_names[k]} ({round(freq[k] * 100)}%)",
            )
            # Add 50% envelope with fill_between
            plt.fill_between(
                x,
                y_quantiles[k, :, 0],
                y_quantiles[k, :, 1],
                color=colors[k],
                alpha=0.3,
            )
        plt.xlabel(param_labels[param])
        plt.ylabel(f"Change in\n{kpi}")
        if type(x[0]) == str and max([len(x_i) for x_i in x]) > 5:
            plt.xticks(rotation=90, ha="center", fontsize=10)
        plt.legend(fontsize=6)
        # Save figure
        save_file = save_dir / param_labels[param] / f"pd_clusters.png"
        save_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_file, dpi=200, bbox_inches="tight")
        plt.close()

        ### Plot cluster characteristics
        X_clusters = X.copy()
        # Bin numerical variables
        D_bins = {
            "wall_insulation_2": [0, 1, 2, 10],
            "roof_insulation_2": [0, 1, 2, 10],
            "floor_insulation_2": [0, 1, 2, 6],
            "WWR": np.linspace(0.2, 0.8, 4),
            "airtightness": np.linspace(0.4, 2.0, 4),
        }
        for col, bins in D_bins.items():
            X_clusters[col] = pd.cut(
                X_clusters[col],
                bins=bins,
                include_lowest=True,
                labels=["Low", "Medium", "High"],
            )
        # One hot encode categorical variables
        for col in [
            "window_vent_profile",
            "mech_vent_profile",
            "shading_profile",
            "N_pv",
            "radiator_area",
            "n_occupants",
        ]:
            X_clusters[col] = X_clusters[col].astype(str)
        X_clusters["use_vent_grilles"] = X_clusters["use_vent_grilles"].astype(str)
        X_clusters = pd.get_dummies(
            X_clusters, drop_first=False, prefix_sep="="
        ).astype(float)
        # Remove redundant columns
        corr = X_clusters.corr().abs()
        upper_tri = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
        to_drop = [
            column for column in upper_tri.columns if any(upper_tri[column] > 0.99)
        ]
        X_clusters = X_clusters.drop(columns=to_drop)
        # Add cluster labels
        X_mean_clusters = X_clusters.groupby(labels).mean()
        X_mean_all = X_clusters.mean()
        X_ratio = X_mean_clusters / X_mean_all
        # Reshape X_log_ratio
        df_reshaped = X_ratio.T
        df_reshaped.columns = [cluster_names[i] for i in df_reshaped.columns]
        df_reshaped = df_reshaped.reset_index().rename(columns={"index": "feature"})
        df_reshaped[["parameter", "value"]] = df_reshaped["feature"].str.split(
            "=", n=1, expand=True
        )
        cluster_cols = [cluster_names[i] for i in range(n_clusters)]
        X_ratio = df_reshaped[["parameter", "value"] + cluster_cols]
        # Find for each cluster the 5 rows with highest abs value
        X_ratio = X_ratio.set_index(["parameter", "value"])
        summary = pd.DataFrame()
        for col in cluster_cols:
            # Find the 5 rows with highest abs value in each cluster
            over_rep_feat = X_ratio[col].nlargest(5).index
            under_rep_feat = X_ratio[col].nsmallest(5).index
            str_over = []
            for ft, value in over_rep_feat:
                symbol = "="
                if type(value) != str and np.isnan(value):
                    ft, value = ft.split(">")
                    symbol = ">"
                try:
                    value = int(value)
                except ValueError:
                    pass
                if value in ["False", "True"]:
                    value = eval(value)
                if isinstance(param_values[ft], dict) and value in param_values[ft]:
                    value = param_values[ft][value]
                str_over.append(f"{param_labels[ft]} {symbol} {value}")
            str_under = []
            for ft, value in under_rep_feat:
                symbol = "="
                if type(value) != str and np.isnan(value):
                    ft, value = ft.split(">")
                    symbol = ">"
                try:
                    value = int(value)
                except ValueError:
                    pass
                if value in ["False", "True"]:
                    value = eval(value)
                if isinstance(param_values[ft], dict) and value in param_values[ft]:
                    value = param_values[ft][value]
                    value.replace("\n", " ")
                str_under.append(f"{param_labels[ft]} {symbol} {value}")
            str_over = "\n".join(str_over)
            str_under = "\n".join(str_under)
            summary.loc[col, "Over-represented characteristics"] = str_over
            summary.loc[col, "Under-represented characteristics"] = str_under
        # Save summary to file
        save_file = save_dir / param_labels[param] / "cluster_summary.csv"
        summary.to_csv(save_file)

    return


def make_importance_boxplot(save_dir: Path):
    kpi = save_dir.name
    D_ice_curves = joblib.load(save_dir / "ice_curves.joblib")
    df = pd.DataFrame()
    X = D_ice_curves.pop("X")
    for param, data in D_ice_curves.items():
        y_ice = data["y_ice"]
        if "OPP" in kpi:
            y_ice = y_ice[X["heating_system"].str.contains("HP")]
        delta_max = y_ice.max(axis=1) - y_ice.min(axis=1)
        df[param_labels[param]] = delta_max
    # Order by mean
    idx_sort = df.mean().sort_values(ascending=False).index
    df = df.reindex(idx_sort, axis=1)
    # Plot boxplot
    fig, ax = plt.subplots(dpi=200, figsize=(4, 7))
    sns.boxplot(data=df, ax=ax, orient="h", showfliers=False, whis=[5, 95])
    xlabel = f"Parameter impact (= maximum change) on\n{kpi}"
    plt.xlabel(xlabel)
    plt.savefig(save_dir / "importance_boxplot.png", dpi=200, bbox_inches="tight")
    plt.tight_layout()
    plt.close()
    return


if __name__ == "__main__":
    # Load training data
    sim_results = curr_dir / "surrogate_models/simulated_configs.parquet"
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
    kpis = [
        "Heating demand [kWh]",
        "Electricity OPP [kW]",
        "Overheating [h]",
        "Average CO2 exposure [ppm]",
    ]
    X, y = load_training_data(sim_results, kpis_to_predict)
    make_kpi_histograms(y, kpis)

    # Compute ICE curves for each KPI
    def foo(kpi):
        save_dir = curr_dir / f"sensitivity_analysis/{kpi}"
        model = load_model(curr_dir / f"surrogate_models/{kpi}.joblib")
        n_samples = 14000 if "OPP" in kpi else 10000
        compute_ICE_curves(model, X, n_samples, save_dir=save_dir)
        # apply_sparse_PCA(save_dir)
        make_importance_boxplot(save_dir)
        # make_PD_plots(save_dir)
        make_PD_plots_clustering(save_dir)
        return

    Parallel(n_jobs=4)(delayed(foo)(kpi) for kpi in kpis)
