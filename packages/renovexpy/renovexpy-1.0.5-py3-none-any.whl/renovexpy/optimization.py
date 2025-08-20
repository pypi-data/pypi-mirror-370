from pathlib import Path
import pandas as pd
import numpy as np
from fast_pareto import is_pareto_front
from tqdm import tqdm
from joblib import Parallel, delayed
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from scipy.spatial.distance import cdist


def compute_robustness_indicators(
    df: pd.DataFrame, unknown_params: list[str], indicator: str
) -> pd.DataFrame:
    assert indicator in ["mean", "max_regret"]
    # Find kpis columns (those with [*] suffix)
    kpis = [col for col in df.columns if col.endswith("]")]
    # Make df_hc
    hc_params = [col for col in df.columns if col not in kpis + unknown_params]
    N_rp = df["rp_id"].max()
    df_hc = df.loc[:N_rp, hc_params].reset_index(drop=True)
    if indicator == "mean":
        df_robust = df.groupby("rp_id")[kpis].mean().reset_index()
    elif indicator == "max_regret":
        min_across_rp = df.groupby("scenario_id")[kpis].min().reset_index()
        df_robust = df.copy()
        for kpi in kpis:
            df_robust[kpi] -= np.repeat(min_across_rp[kpi].values, N_rp + 1)
        # Group by and get max across scenarios
        df_robust = df_robust.groupby("rp_id")[kpis].max().reset_index()
    # Join with df_hc
    df = df_robust.merge(df_hc, on="rp_id", how="left")
    del df["rp_id"]
    del df["scenario_id"]
    return df


def pareto_optimization(df: pd.DataFrame, kpis: list[str]) -> pd.DataFrame:
    kpis_to_drop = [col for col in df.columns if col not in kpis and col[-1] == "]"]
    X = df[kpis].to_numpy()
    is_optimal = is_pareto_front(X)
    df_opt = df[is_optimal].reset_index(drop=True)
    return df_opt


def minimize_kpis_average(
    df: pd.DataFrame, kpis: list[str], N_top: int
) -> pd.DataFrame:
    """
    Identify the N_top RPs with the lowest average value of the normalized KPIs.
    """
    X = MinMaxScaler().fit_transform(df[kpis])
    idx_best = np.argsort(X.mean(axis=1))[:N_top]
    return df.loc[idx_best].copy()


def find_optimal_packages(
    df,
    unknown_params,
    kpis: list[str],
    requirements: dict[str, float],
    robustness_indicator: str,
    N_top: int = 10,
):
    assert robustness_indicator in ["mean", "max_regret"]
    # Compute robustness indicators
    df_robust = compute_robustness_indicators(
        df, unknown_params, indicator=robustness_indicator
    )
    # Filter configurations that do not meet the requirements
    if requirements != {}:
        kpis_with_req = list(requirements.keys())
        if robustness_indicator == "mean":
            df_req = df_robust[kpis_with_req].copy()
        elif robustness_indicator == "max_regret":
            df_req = compute_robustness_indicators(df, unknown_params, indicator="mean")
        mask = np.ones(df_robust.shape[0], dtype=bool)
        for kpi, req in requirements.items():
            mask &= df_req[kpi] <= req
        df_robust = df_robust[mask].reset_index(drop=True)
    # Minimize average value of normalized KPIs
    df_opt = minimize_kpis_average(df_robust, kpis, N_top)
    return df_opt
