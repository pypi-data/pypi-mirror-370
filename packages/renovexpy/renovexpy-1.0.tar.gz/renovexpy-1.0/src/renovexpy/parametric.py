import random
import json
import uuid
import itertools
from pathlib import Path
from typing import Dict, Any
import pandas as pd
from tqdm import tqdm
from joblib import Parallel, delayed
from renovexpy.energyplus import EPSimulation, run_eplus_simulation
from renovexpy.heating_system import simulate_heating_systems
from renovexpy.pv import simulate_pv_generation
from renovexpy.kpi import get_simulated_KPIs
from renovexpy.utils import save_parquet_with_json

curr_dir = Path(__file__).resolve().parent


def sample_value_from_spec(spec: Any) -> Any:
    """
    Recursively resolves a specification to a single value for random sampling.

    - If spec is a slice object, samples a float uniformly from the range.
    - If spec is a tuple, it's treated as a collection of choices. One element
      is randomly selected. An empty tuple will raise a ValueError.
    - If spec is a list, it's treated as a structural list. Each element
      within the list is recursively resolved.
    - If spec is a dict, it's a structural dictionary. Each value is recursively
      resolved. Handles grouped keys (tuple of strings) by sampling one value
      for the group and assigning it to all keys in the group.
    - Otherwise (e.g. number, string), returns the spec as a fixed value.
    """
    if isinstance(spec, slice):
        return round(random.uniform(spec.start, spec.stop), 2)
    elif isinstance(spec, tuple):  # Tuple means a list of choices
        if not spec:
            raise ValueError("Cannot randomly sample from an empty tuple of options.")
        return random.choice(spec)
    elif isinstance(spec, list):  # List is a structural element
        return [sample_value_from_spec(item) for item in spec]
    elif isinstance(spec, dict):  # Dict is a structural element
        new_dict = {}
        for key, sub_spec_val in spec.items():
            if isinstance(key, tuple) and all(
                isinstance(k_item, str) for k_item in key
            ):  # Grouped keys
                sampled_value_for_group = sample_value_from_spec(sub_spec_val)
                for actual_key_in_group in key:
                    new_dict[actual_key_in_group] = sampled_value_for_group
            else:  # Single string key
                new_dict[key] = sample_value_from_spec(sub_spec_val)
        return new_dict
    else:
        # Fixed value (number, string, etc.)
        return spec


def generate_input_configs(
    param_specs: Dict[str, Any], sampling: str, N: int = 0
) -> pd.DataFrame:
    """
    Generates input comfigurations, i.e. combinations of parameters based on specifications.

    The final value for each parameter in an output combination should be a
    number, string, list, or dictionary. Per user rule, it should NOT be a tuple,
    unless that tuple is part of a list or dictionary structure (e.g., a value within a dict,
    or an element of a list, if the spec was designed that way - though typically tuples
    now signify choices). The function generates based on `param_specs`;
    the user must structure `param_specs` such that chosen options meet this criterion.

    Args:
        param_specs: A dictionary where keys are parameter names (strings) and
                     values define how to generate values for those parameters.

            If sampling == "grid":
                - param_specs[param_name]: Can be a single fixed value (number,
                  string, list, dict) or a TUPLE of such values.
                  Each item in the tuple is a potential complete value for the parameter.
                  Example: {"p1": (1, 2), "p2": "fixed", "p3": (["a",1], ["b",2])}
                  If a tuple of options is empty for any parameter, no combinations
                  will be generated.

            If sampling == "random":
                - param_specs[param_name]:
                    1. A single fixed value (number, string, list, dict).
                       Example: {"p1": 10}
                    2. A TUPLE of choices (each choice being a number, string,
                       list, or dict). One choice is randomly selected.
                       Example: {"p1": (10, 20, 30)}
                       An empty tuple of choices will raise a ValueError.
                    3. If the parameter itself is intended to be a LIST:
                       A list where elements can be fixed values, TUPLES of choices,
                       or range objects.
                       Example: {"p_list": [("a","b"), "fixed", ({"x": (100,200)}, {"y":1}), range(0,4)]}
                       This could result in p_list being like ["a", "fixed", {"x": 150}, 2].
                    4. If the parameter itself is intended to be a DICTIONARY:
                       A dictionary where:
                       - Keys can be strings. Values can be fixed, TUPLES of choices,
                         or range objects.
                         Example: {"p_dict": {"key1": (1,2), "key2": "fixed", "key3": range(10,21)}}
                       - Keys can be tuples of strings (grouped keys). The associated
                         value (fixed, tuple of choices, or range object) is sampled
                         once and assigned to all keys in the group.
                         Example: {"p_dict": {("g1","g2"): (10,20), "g3": range(0,2)}}
                         This could result in p_dict being like {"g1":10, "g2":10, "g3":0}.
                    5. A slice object (e.g., slice(0, 10)) to sample an float uniformly in
                       a certain range.

        sampling: A string, either "grid" or "random".
        N: An integer, number of random combinations to generate. Ignored for "grid".
           Must be non-negative.

    Returns:
        A list of dictionaries, where each dictionary is a parameter combination.
        Example: [{"param1": value1, "param2": value2}, ...]

    Raises:
        ValueError: If 'sampling' is not "grid" or "random", or if N is negative,
                    or if an empty tuple/range of options is provided for random sampling.
    """
    if sampling not in ["grid", "random"]:
        raise ValueError("Sampling mode must be 'grid' or 'random'.")

    param_names = list(param_specs.keys())
    combinations = []

    if sampling == "grid":
        param_options = []
        n_combinations = 1
        for param_name in param_names:
            spec = param_specs[param_name]
            if isinstance(spec, tuple):
                param_options.append(spec)
                n_combinations *= len(spec)
            else:
                param_options.append([spec])
        for value_combination in itertools.product(*param_options):
            combinations.append(value_combination)
        df = pd.DataFrame(combinations, columns=param_names)

    elif sampling == "random":
        # TODO: check if grouped keys are handled correctly
        for _ in range(N):
            current_combination = {}
            for param_name in param_names:
                spec = param_specs[param_name]
                try:
                    current_combination[param_name] = sample_value_from_spec(spec)
                except ValueError as e:
                    raise ValueError(f"Error resolving parameter '{param_name}': {e}")
            combinations.append(current_combination)
        df = pd.DataFrame(combinations)

    # Split grouped keys into separate columns
    for col in df.columns:
        if isinstance(col, tuple):
            for k, sub_col in enumerate(col):
                df[sub_col] = df[col].apply(lambda x: x[k])
            del df[col]
    return df


def get_sim_templates():
    sim_templates = {}
    for vent_type in ["A", "C1", "C2", "C4a", "D5c"]:
        sim = EPSimulation(vent_type)
        sim_templates[vent_type] = sim
    return sim_templates


def run_parametric_simulations(
    sim_dir: Path, param_specs: Dict[str, Any], sampling: str, N: int = 0
):
    sim_dir.mkdir(parents=True, exist_ok=True)
    # Generate input configurations
    df = generate_input_configs(param_specs, sampling, N)
    df["sim_dir"] = [str(sim_dir / uuid.uuid4().hex) for _ in range(len(df))]
    # Define sim templates (to avoid multiple processes writing to the same file)
    sim_templates = get_sim_templates()
    # Run EnergyPlus simulations
    Parallel(n_jobs=-1)(
        delayed(run_eplus_simulation)(**params, sim_templates=sim_templates)
        for _, params in tqdm(
            df.iterrows(), total=len(df), desc="Running E+ simulations"
        )
    )
    # Simulate heating systems
    Parallel(n_jobs=-1)(
        delayed(simulate_heating_systems)(
            sim_dir=sim_dir_k,
            radiator_areas=[4, 6, 8],
            HP_models=["5kW", "7kW", "10kW"],
            DHW_profile=f"{n_occ_k}P Mid",
        )
        for sim_dir_k, n_occ_k in zip(df["sim_dir"], df["n_occupants"])
    )
    # Simulate PV generation
    Parallel(n_jobs=-1)(
        delayed(simulate_pv_generation)(sim_dir=sim_dir_k, N_panels_frac=[0, 0.5, 1])
        for sim_dir_k in df["sim_dir"]
    )
    # Compute KPIs
    L_df_kpis = Parallel(n_jobs=-1)(
        delayed(get_simulated_KPIs)(sim_dir=df["sim_dir"][k])
        for k in tqdm(range(len(df)), desc="Computing KPIs")
    )
    # Merge KPIs with df
    for k in range(len(df)):
        L_df_kpis[k]["sim_dir"] = df["sim_dir"][k]
    df_kpis = pd.concat(L_df_kpis, ignore_index=True)
    df = df.merge(df_kpis, how="left", left_on="sim_dir", right_on="sim_dir")
    # Save df
    save_parquet_with_json(df, sim_dir / "simulated_configs.parquet")
    return
