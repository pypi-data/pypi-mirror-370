import hashlib
import threading
import queue
import json
import re
import shlex
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd


class TimeoutError(Exception):
    pass


def run_with_timeout(func, args=(), kwargs=None, timeout=30):
    if kwargs is None:
        kwargs = {}

    q = queue.Queue()

    def wrapper():
        try:
            result = func(*args, **kwargs)
            q.put(result)
        except Exception as e:
            q.put(e)

    thread = threading.Thread(target=wrapper)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        raise TimeoutError(f"Function execution exceeded {timeout} seconds.")

    result = q.get()
    if isinstance(result, Exception):
        raise result  # Re-raise the exception if the function raised one

    return result


def load_epjson_from_idf(idf_file, eplus_exec) -> dict:
    assert isinstance(
        idf_file, (str, Path)
    ), f"{idf_file} must be a string or Path object"
    idf_file = Path(idf_file)
    assert idf_file.exists(), f"File {idf_file.as_posix()} not found"
    idf_dir = idf_file.parent
    # Convert using EnergyPlus
    cmd = f"'{eplus_exec}' -d '{idf_dir}' --convert-only '{idf_file}'"
    subprocess.run(shlex.split(cmd), shell=False, capture_output=True)
    # Load epsjon file
    epjson_file = idf_file.with_suffix(".epJSON")
    with open(epjson_file, "r") as f:
        epjson = json.load(f)
    # Remove created files
    (idf_dir / "eplusout.end").unlink()
    (idf_dir / "eplusout.err").unlink()
    epjson_file.unlink()
    return epjson


def run_energyplus(epjson_file, eplus_exec, idd_file, epw_file, output_dir):
    cmd = f"'{eplus_exec}' -d '{output_dir}' -i '{idd_file}' -w '{epw_file}' '{epjson_file}'"
    try:
        subprocess.run(shlex.split(cmd), shell=False, capture_output=True)
    except:
        pass
    return


def convert_schedule_to_list(schedule):
    """
    Convert a schedule dictionary to a list of 24 values.

    Inputs
    ------
    schedule : dict
        Dictionary with keys as time periods and values as the corresponding values.
        E.g. {'22-6': 20, '6-8': 22, '8-22': 18}

    Returns
    -------
    L: np.array
        An array of 24 values representing the hourly schedule.
    """
    L = np.zeros(24).astype(type(list(schedule.values())[0]))
    mask = np.zeros(24).astype(bool)
    for period, value in schedule.items():
        assert bool(re.match(r"\d+-\d+", period)), f"Invalid period '{period}'"
        start, end = [int(x) for x in period.split("-")]
        assert start <= 24 and end <= 24 and start != end, f"Invalid period '{period}'"
        if start < end:
            assert not mask[start:end].any(), f"Overlapping periods in {schedule}"
            L[start:end] = value
            mask[start:end] = True
        else:
            assert not mask[:end].any(), f"Overlapping periods in {schedule}"
            L[:end] = value
            mask[:end] = True
            assert not mask[start:].any(), f"Overlapping periods in {schedule}"
            L[start:] = value
            mask[start:] = True
    return L


def make_hashable(obj):
    """Recursively convert an object to a hashable type."""
    if isinstance(obj, (tuple, list)):
        return tuple(make_hashable(e) for e in obj)
    elif isinstance(obj, dict):
        return tuple(sorted((k, make_hashable(v)) for k, v in obj.items()))
    else:
        return obj  # Assume the object is already hashable (e.g., int, str, etc.)


def get_hash(obj):
    """Generate a unique hash for a given object."""
    hashable_obj = make_hashable(obj)
    return hashlib.sha256(repr(hashable_obj).encode()).hexdigest()


def save_parquet_with_json(df, path):
    """
    Save a pandas DataFrame to a parquet file, but encodes
    columns with lists/dicts using json.dumps beforehand.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to save.
    path : str or Path
        The path to save the parquet file and metadata.
    """
    json_cols = []
    for col in df.columns:
        if isinstance(df[col].iloc[0], (list, dict)):
            json_cols.append(col)
            df[col] = df[col].apply(json.dumps)
    df.attrs["json_cols"] = json_cols
    df.to_parquet(path, index=False)
    return


def load_parquet_with_json(path):
    """
    Load a pandas DataFrame from a parquet file, but decode
    columns with lists/dicts using json.loads.

    Parameters
    ----------
    path : str or Path
        The path to save the parquet file and metadata.
    """
    df = pd.read_parquet(path)
    for col in df.attrs["json_cols"]:
        df[col] = df[col].apply(json.loads)
    return df


class NumpyEncoder(json.JSONEncoder):
    """
    The native JSON encoder does not support numpy types.
    So we use this custom encoder instead.
    """

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)
