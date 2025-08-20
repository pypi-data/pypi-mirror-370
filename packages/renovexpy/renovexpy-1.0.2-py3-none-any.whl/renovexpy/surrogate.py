from pathlib import Path
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
from threadpoolctl import threadpool_limits


def make_X_y(
    df: pd.DataFrame,
    kpis_to_predict: dict,
    N_samples_max: int = None,
    use_cols: list = [],
):
    """
    Read the simulation results and return the features and targets.
    """
    if "sim_dir" in df.columns:
        del df["sim_dir"]
    # Subsample if needed
    if isinstance(N_samples_max, int):
        df = df.sample(n=N_samples_max, random_state=42).reset_index(drop=True)
    # Separate KPIs and inputs
    y = df[[kpi for kpi, val in kpis_to_predict.items() if val and kpi in df.columns]]
    X = df.drop(columns=kpis_to_predict.keys(), errors="ignore")
    ### Featurize the inputs
    cols_to_explode = ["wall_insulation", "roof_insulation", "floor_insulation"]
    for param in X.columns.tolist():
        value = X[param].iloc[0]
        if isinstance(value, (list, dict)):
            if param in cols_to_explode:
                if isinstance(value, list):
                    X_param = pd.DataFrame(X[param].tolist())
                else:
                    X_param = pd.DataFrame.from_dict(X[param].tolist())
                X[[f"{param}_{key}" for key in X_param.columns]] = X_param
                del X[param]
            else:  # Convert to string
                X[param] = X[param].astype(str)
    if len(use_cols) == 0:
        # Remove constant columns
        n_unique = X.nunique()
        cols_to_remove = n_unique[n_unique <= 1].index.tolist()
        X.drop(columns=cols_to_remove, inplace=True)
    else:
        X = X[use_cols]
    return X, y


def train_surrogate_models(X: pd.DataFrame, y: pd.DataFrame, save_dir: Path, **kwargs):
    # Train models
    cat_features = X.select_dtypes(include="object").columns
    scores = {}
    for kpi in y.columns:
        print(f"Training model for KPI: {kpi}")
        # model = HistGradientBoostingRegressor(
        #     learning_rate=0.03,
        #     max_iter=4000,
        #     max_leaf_nodes=50,
        #     early_stopping=True,  # False
        #     categorical_features=cat_features,
        # )
        model = HistGradientBoostingRegressor(
            categorical_features=cat_features, **kwargs
        )
        # Fit/predict on train/test sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y[kpi], test_size=0.2, random_state=42
        )
        with threadpool_limits(limits=8, user_api="openmp"):
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
        # Evaluate model
        scores[kpi] = {
            "R2 score": r2_score(y_test, y_pred),
            "MAE": mean_absolute_error(y_test, y_pred),
            "MAPE": mean_absolute_percentage_error(y_test, y_pred),
        }
        scores[kpi]["MAE/mean(y)"] = scores[kpi]["MAE"] / y_test.mean()
        # Final fit on all data
        with threadpool_limits(limits=8, user_api="openmp"):
            model.fit(X, y[kpi])
        # Save models using joblib.
        save_dir.mkdir(exist_ok=True, parents=True)
        joblib.dump(model, save_dir / f"{kpi}.joblib")
    # Save scores to csv file
    scores = pd.DataFrame(scores).T
    scores.index.name = "KPI"
    scores.to_csv(save_dir / "scores.csv")
    return
