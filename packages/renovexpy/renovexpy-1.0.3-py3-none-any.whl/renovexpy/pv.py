from pathlib import Path
import numpy as np
import pandas as pd

from renovexpy.kpi import SimResultsReader
from renovexpy.geometry import get_surface_areas_from_epjson


def load_irradiance_data(sim_dir: Path) -> pd.DataFrame:
    """
    Returns a DataFrame with the hourly irradiance data (in W/m2)
    for the roof surfaces.
    """
    res = SimResultsReader(sim_dir)
    # Get irradiance data for surfaces labelled as "roof" and "SunExposed"
    df = pd.DataFrame()
    key = "Surface Outside Face Incident Solar Radiation Rate per Area"
    for surface, properties in res.epjson["BuildingSurface:Detailed"].items():
        if "ROOF" in surface.upper() and properties["sun_exposure"] == "SunExposed":
            df[surface] = res.eplus[f"{key} {surface.upper()}"]
    return df


def get_max_panels_per_surface(
    input_file: Path,
    roof_surfaces: list,
    panel_area: float,
    perc_usable_area: float,
) -> dict:
    """
    Returns a dictionary with the maximum number of panels that can be installed
    on each surface based on the irradiance data and the panel area.
    """
    # Compute maximum number of panels per surface
    surface_areas = get_surface_areas_from_epjson(input_file)
    max_panels = {
        surf: int(surface_areas[surf] * perc_usable_area / panel_area)
        for surf in roof_surfaces
    }
    return max_panels


def assign_panels_to_surfaces(
    N_panels: int,
    df_irradiance: pd.DataFrame,
    max_panels_per_surface: dict,
) -> dict:
    """
    Assigns the number of panels to each surface based on the irradiance data.
    The panels are assigned to the surfaces with the highest irradiance values.
    """
    panels_per_surface = {}
    # Sort surface by average irradiance
    sorted_surfaces = df_irradiance.mean().sort_values(ascending=False).index
    # Assign panels to surfaces
    for surface in sorted_surfaces:
        if N_panels <= 0:
            break
        max_panels = max_panels_per_surface[surface]
        if max_panels > 0:
            panels_to_assign = min(N_panels, max_panels)
            panels_per_surface[surface] = panels_to_assign
            N_panels -= panels_to_assign
    return panels_per_surface


def simulate_pv_generation(
    sim_dir: str | Path,
    N_panels_frac: list[float] = [0, 0.5, 1],
    panel_area: float = 1.93,
    module_efficiency: float = 0.225,
    inverter_efficiency: float = 0.95,
    perc_usable_area: float = 0.8,
):
    """
    Simulate the electricity generation of PV panels for a certain house.
    Save the results to a parquet file with the hourly production for different
    numbers of installed panels.

    Inputs:
    -------
    sim_dir: Path
        Path to the directory containing the EnergyPlus simulation files.
        The same directory will be used to save the output file.
    N_panels_frac: list[float]
        List of fractions of the maximum number of panels to be installed.
        The maximum number of panels is computed based on the usable area.
    panel_area: float
        Area of the PV panel in square meters (default is 1.93 m²).
    module_efficiency: float
        Efficiency of the PV module (default is 22.5%).
    inverter_efficiency: float
        Efficiency of the DC-AC inverter (default is 95%).
    perc_usable_area: float
        Percentage of usable area for PV installation (default is 80%).
    """
    sim_dir = Path(sim_dir)
    input_file = list(sim_dir.glob("input_*.epjson"))[0]
    irradiance_per_surface = load_irradiance_data(sim_dir)
    roof_surfaces = irradiance_per_surface.columns
    max_panels_per_surface = get_max_panels_per_surface(
        input_file, roof_surfaces, panel_area, perc_usable_area
    )
    N_panels_max = sum(max_panels_per_surface.values())
    N_panels_list = np.unique([int(frac * N_panels_max) for frac in N_panels_frac])
    # Compute PV generation per panel for each surface
    pv_gen_per_panel = pd.DataFrame()
    for surface in roof_surfaces:
        pv_gen_per_panel[surface] = (
            irradiance_per_surface[surface]  # W/m2
            * panel_area  # m2
            * module_efficiency
            * inverter_efficiency
            / 1000  # kWh
        )

    # Compute the total PV generation for each surface and different number of panels
    pv_gen = pd.DataFrame()
    for N_panels in N_panels_list:
        panels_per_surface = assign_panels_to_surfaces(
            N_panels, irradiance_per_surface, max_panels_per_surface
        )
        total_pv_gen = np.zeros(len(irradiance_per_surface))
        for surface, N_panels_surf in panels_per_surface.items():
            total_pv_gen += pv_gen_per_panel[surface] * N_panels_surf
        pv_gen[N_panels] = total_pv_gen
    # Save the results to a parquet file
    output_file = sim_dir / "PV_generation.parquet"
    pv_gen.to_parquet(output_file, index=False)
    return
