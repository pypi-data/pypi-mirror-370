"""
Simulate a heat pump and gas boiler as follows:
    1) Load simulation data from E+. This includes hourly outdoor temperature and
    heating demand.
    2) Optional: Compute the heating demand at design temperature (-10 °C), and
    size the radiator area to meet this demand. Otherwise, use the provided
    radiator area.
    3) Compute the temperature needed in radiators to meet the heating demand, and
    the corresponding supply and return flow temperatures.
    4) Compute the efficiency of the gas boiler / heatpump.
    5) Compute the hourly gas consumption of the boiler.
    6) Compute the maximum load of the heat pump based on the outdoor temperature
    and flow temperature.
    7) Compute the hourly electricity consumption of the heat pump, and the part of
    the heating demand covered by the electric backup.
    8) Save the results to an output file.
"""

import re
from pathlib import Path
from typing import Callable, Tuple

import numpy as np
import pandas as pd
from scipy import interpolate
from scipy.interpolate import LinearNDInterpolator

from renovexpy.kpi import SimResultsReader

curr_dir = Path(__file__).parent


def load_simulation_data(sim_dir: Path) -> Tuple[np.ndarray, np.ndarray]:
    """
    Returns the hourly outdoor temperature and heating demand from E+ simulation data.
    """
    df = SimResultsReader(sim_dir).eplus
    T_outdoor = df["Site Outdoor Air Drybulb Temperature Environment"].to_numpy()
    Q_loss = df["Boiler Heating Rate BOILER"].to_numpy() / 1000  # Convert to kWh
    return T_outdoor, Q_loss


def convert_dhw_Lph_to_kWh(
    Q_dhw_Lph: np.ndarray, T_cold: float = 10, T_hot: float = 60
) -> np.ndarray:
    """
    Returns the DHW demand in kWh. The input is the DHW demand in L/h.
    """
    dhw_Lph_yearly = np.tile(Q_dhw_Lph, 365)  # L/h
    Q_dhw = dhw_Lph_yearly * 1 * 4.18 * (T_hot - T_cold) / 3600  # kWh
    return Q_dhw


def get_Qloss_design(
    T_outdoor: np.ndarray, Q_loss: np.ndarray, T_design: float, cold_fraction: float
) -> float:
    """
    Estimates the heating demand at design temperature using a linear regression
    on simulation data during coldest hours.
    """
    mask = Q_loss > (1 - cold_fraction) * Q_loss.max()
    coef = np.polyfit(T_outdoor[mask], Q_loss[mask], 1)
    Q_loss_design = coef[0] * T_design + coef[1]
    return Q_loss_design


def K22_radiator() -> Tuple[Callable, Callable]:
    """
    Returns the relationship between MTW and power for the K22 radiator.
    """
    K22_Power = [
        0,
        57,
        143,
        246,
        360,
        485,
        618,
        759,
        906,
        1220,
        1555,
        1909,
        2281,
        2668,
        3070,
        3485,
        3913,
        4354,
        4805,
    ]
    K22_Power = np.array(K22_Power) / 1000  # Convert to kW
    K22_MWT = [
        20,
        22.5,
        25,
        27.5,
        30,
        32.5,
        35,
        37.5,
        40,
        45,
        50,
        55,
        60,
        65,
        70,
        75,
        80,
        85,
        90,
    ]
    get_radiator_power = interpolate.interp1d(
        K22_MWT, K22_Power, fill_value=(K22_Power[0], K22_Power[-1]), bounds_error=False
    )
    get_radiator_MTW = interpolate.interp1d(
        K22_Power, K22_MWT, fill_value=(K22_MWT[0], K22_MWT[-1]), bounds_error=False
    )
    return get_radiator_power, get_radiator_MTW


def size_radiator_area(Q_loss_design: float, MWT: float) -> float:
    """
    Return the area of radiator (in m2) needed to meet the design load, given the MWT.
    """
    get_radiator_power, _ = K22_radiator()
    power_at_MTW = get_radiator_power(MWT)
    radiator_area = Q_loss_design / power_at_MTW
    return radiator_area


def get_gas_boiler_efficiency(
    boiler: str, T_flow_boiler_return: np.ndarray
) -> np.ndarray:
    if boiler == "HR107":
        T = [
            5.399239543726235,
            8.6787072243346,
            14.712927756653992,
            19.566539923954373,
            26.519011406844108,
            33.99619771863118,
            36.88212927756654,
            40.81749049429658,
            43.30988593155894,
            45.67110266159696,
            48.29467680608365,
            50.655893536121674,
            53.148288973384034,
            54.19771863117871,
            55.640684410646394,
            59.444866920152094,
            69.54562737642587,
            78.46577946768062,
            89.61596958174906,
            97.7490494296578,
            105.88212927756655,
            113.88403041825096,
            118.08174904942966,
        ]
        efficiency_at_T = [
            99.4186046511628,
            99.13953488372093,
            98.5813953488372,
            97.79069767441861,
            96.81395348837209,
            95.55813953488372,
            94.81395348837209,
            93.95348837209302,
            93.02325581395348,
            92.09302325581396,
            91.23255813953489,
            90.06976744186046,
            88.69767441860465,
            87.97674418604652,
            87.16279069767442,
            86.95348837209302,
            86.48837209302326,
            86.13953488372093,
            85.72093023255815,
            85.37209302325581,
            85.02325581395348,
            84.69767441860465,
            84.53488372093024,
        ]
    elif boiler == "VR":
        T = [5, 120]
        efficiency_at_T = [87, 87]
    else:
        raise ValueError(f"Unknown boiler type: {boiler}")
    return np.interp(T_flow_boiler_return, T, efficiency_at_T) / 100


def get_gas_boiler_load(
    boiler: str,
    Q_loss: np.ndarray,
    Q_dhw: np.ndarray,
    radiator_area: float,
    dT_boiler: float,
    T_room: float,
    T_cold_dhw: float = 10,
) -> np.ndarray:
    """
    Returns the hourly load (in kWh) of a gas boiler for heating and DHW.
    """
    # Compute the radiator MTW, deduce the boiler return temperature and
    # efficiency
    _, get_radiator_MTW = K22_radiator()
    T_flow_boiler_return = get_radiator_MTW(Q_loss / radiator_area) - dT_boiler / 2
    T_flow_boiler_return = np.clip(T_flow_boiler_return, T_room, None)
    T_flow_boiler_return_dhw = np.full_like(Q_dhw, T_cold_dhw)
    boiler_efficiency = get_gas_boiler_efficiency(boiler, T_flow_boiler_return)
    boiler_efficiency_dhw = get_gas_boiler_efficiency(boiler, T_flow_boiler_return_dhw)
    # Compute the boiler load
    boiler_load = (Q_loss / boiler_efficiency) + (Q_dhw / boiler_efficiency_dhw)
    return boiler_load


def get_heat_pump_efficiency(
    T_flow_heatpump_supply: np.ndarray,
    T_outdoor: np.ndarray,
    Carnot_factor: float,
) -> np.ndarray:

    Carnot = (
        Carnot_factor
        * (T_flow_heatpump_supply + 273.15)
        / (T_flow_heatpump_supply - T_outdoor + 1e-6)  # Avoid division by zero
    )
    # Sometimes T_flow < T_outdoor, which gives negative Carnot values.
    # This is not physically possible, so we set them to 8. This is okay because Qloss
    # is 0 for these cases. We also cap the Carnot efficiency at 8.
    mask = (Carnot <= 0) & (Carnot > 8)
    Carnot[mask] = 8
    return Carnot


def get_heat_pump_min_max_load(
    T_flow_heatpump_supply: np.ndarray, T_outdoor: np.ndarray, HP_model: str
) -> np.ndarray:
    # Load heat pump capacity data for the specified model
    options = ["3kW Intergas", "3.5kW", "5kW", "7kW", "10kW", "12kW"]
    if HP_model not in options:
        raise ValueError(f"Invalid heat pump capacity. Choose from {options}")
    df = pd.read_csv(curr_dir / "data/heatpump_capacity.csv", sep=";")
    min_capacity, max_capacity = df[[f"{HP_model} min", f"{HP_model} max"]].values.T
    # Compute min/max output based on capacity, outdoor and flow temperatures
    Outdoor_T = [-20, -15, -12, -7, -2, 0, 2, 7, 10, 12, 15, 20]
    Flow_T = [35, 45, 55, 65]
    points = [(T, x) for T in Outdoor_T for x in Flow_T]
    get_min_load = LinearNDInterpolator(points, min_capacity)
    get_max_load = LinearNDInterpolator(points, max_capacity)
    # Replace outdoor and T flow temperatures with clipped values to avoid extrapolation
    T_flow_heatpump_supply_ = np.clip(T_flow_heatpump_supply, 35, 65)
    T_outdoor_ = np.clip(T_outdoor, -20, 20)
    runtime = 3  # If it is 4, heat pump needs to run at least 15 min etc
    min_load = get_min_load(T_outdoor_, T_flow_heatpump_supply_) / runtime
    max_load = get_max_load(T_outdoor_, T_flow_heatpump_supply_)
    return min_load, max_load


def get_heat_pump_load(
    Q_loss: np.ndarray,
    Q_dhw: np.ndarray,
    T_outdoor: np.ndarray,
    HP_model: str,
    radiator_area_heatpump: float,
    dT_heatpump: float,
    T_room: float,
    Carnot_factor: float,
) -> np.ndarray:
    """
    Returns the hourly load (in kWh) of a heat pump for heating and DHW.
    """
    Q_emitter = Q_loss / radiator_area_heatpump  # heat load per m^2 emitter
    _, get_radiator_MWT = K22_radiator()
    T_flow_heatpump_supply = get_radiator_MWT(Q_emitter) + dT_heatpump / 2
    T_flow_heatpump_supply = np.clip(T_flow_heatpump_supply, T_room + dT_heatpump, None)
    if max(T_flow_heatpump_supply) > 65:
        print("Supply of HP above 65, this is stupid and leads to inaccurate results")
    Carnot = get_heat_pump_efficiency(T_flow_heatpump_supply, T_outdoor, Carnot_factor)
    min_load, max_load = get_heat_pump_min_max_load(
        T_flow_heatpump_supply, T_outdoor, HP_model
    )
    # Compute electricity backup load (when the heat pump cannot meet the demand)
    # NOTE: Adding Q_dwh to Q_loss is a simple approximation, but DHW doesn't have
    # a big impact on the heating load, so it should be fine.
    E_backup_load = np.clip(Q_loss + Q_dhw - max_load, 0, None)
    HP_load = (Q_loss + Q_dhw - E_backup_load) / Carnot
    HP_and_backup_load = HP_load + E_backup_load
    return HP_load, HP_and_backup_load


def get_hybrid_heat_pump_load(
    Q_loss: np.ndarray,
    hp_load: np.ndarray,
    Q_loss_shortage: np.ndarray,
    boiler_load: np.ndarray,
    T_outdoor: np.ndarray,
    alternate_on: str,
) -> Tuple[np.ndarray, np.ndarray]:
    # Parallel operation: the boiler supplies exactly the shortage
    # NOTE: we make an approximation here: the flow temperature used in boiler_load
    # could be different than the one used in practice (e.g. the same as the heat pump).
    parallel_hp_load = hp_load
    parallel_boiler_load = np.zeros_like(hp_load)
    # Use mask to avoid dividing by 0 when Q_loss = 0
    mask = Q_loss > 0
    parallel_boiler_load[mask] = Q_loss_shortage[mask] / (Q_loss * boiler_load)[mask]
    # Alternate operation: the boiler supplies the entire load whenever the heat pump
    # cannot meet the demand.
    # However, this would make the HP turn off/on too often. In practice, we can also switch
    # the HP based on outdoor temperature.
    # NOTE: when alternating on T_outdoor, the heat pump may still not reach Q_loss for
    # some hours. Should we add electric backup?
    if alternate_on == "outdoor_temperature":
        mask = T_outdoor < 0
    elif alternate_on == "shortage":
        mask = Q_loss_shortage > 0
    else:
        raise ValueError(f"Invalid alternate_on value: {alternate_on}")
    alternate_hp_load = np.where(mask, 0, hp_load)
    alternate_boiler_load = np.where(mask, boiler_load, 0)
    return (
        parallel_hp_load,
        parallel_boiler_load,
        alternate_hp_load,
        alternate_boiler_load,
    )


def simulate_heating_systems(
    sim_dir: str | Path,
    boiler_models: list[str] = None,
    HP_models: list[str] = None,
    hybrid_HP_models: list[str] = None,
    radiator_areas: list[float] = None,
    DHW_profile: str = None,
    alternate_on: str = "shortage",
    T_room: float = 21,
    T_design: float = -10,
    T_flow_heatpump: float = 60,
    T_cold_dhw: float = 10,
    T_hot_dhw: float = 60,
    T_flow_boiler: float = 75,
    cold_fraction: float = 0.4,
    Carnot_factor: float = 0.4,
):
    """
    Simulates several heating system (gas boiler, HP, hybrid HP, radiators) that aim to
    meet the simulated heating demand from EnergyPlus. The output is a parquet file
    with the hourly energy consumption (gas and electricity) of each system.
    For heat pumps, we also include the electric backup for heating.

    Inputs:
    -------

    sim_dir: Path
        Path to the directory with EnergyPlus simulation files.
        The same directory will be used to save the output file.
    boiler_models: list[str], default = None
        The list of gas boiler models to simulate. If None, all available models are
        simulated. Currently, only "HR107" is supported.
    HP_models: list[str], default = None
        The list of heat pump models to simulate. If "all", all available models are
        simulated. Currently, the supported models are "3.5kW", "5kW", "7kW", "10kW",
        and "12kW".
    hybrid_HP_models: list[tuple[str]], default = None,
        The list of hybrid heat pump models to simulate. Each model is defined by a
        tuple consisting of a HP model and a boiler model. If "all", all available
        models are simulated. Currently, only the ("3kW Intergas", "HR107") model is
        supported.
    radiator_areas: list[float], default = None
        A list of values for the total radiator area (in m^2).
        If None, the radiator area is sized to meet the design load.
    DHW_profile: str, default = None
        The profile used for DHW demand, e.g. "2P Mid". There is a profile for each number
        of occupants (1, 2, or 4) and each consumption level ("Low", "Mid", "High").
    alternate_on: bool, default = "shortage"
        The variable used to decide when to alternate between heat pump and gas boiler
        in a hybrid system. If "shortage", the gas boiler is used whenever the heat pump
        cannot cover the heating demand. If "outdoor_temperature", the gas boiler is
        used whenever the outdoor temperature goes below zero.
    """
    sim_dir = Path(sim_dir)
    # Load the DHW demand in L/h for the entire year
    if DHW_profile is None:
        Q_dhw = np.zeros(8760)
    else:
        if not re.match(r"^(1|2|4)P (Low|Mid|High)$", DHW_profile):
            raise ValueError(f"Unknown DHW_profile: {DHW_profile}.")
        dhw_Lph_daily = pd.read_csv(curr_dir / "data/DHW_profiles.csv")[DHW_profile]
        Q_dhw = convert_dhw_Lph_to_kWh(dhw_Lph_daily, T_cold_dhw, T_hot_dhw)
    # Get simulation data
    T_outdoor, Q_loss = load_simulation_data(sim_dir)
    # Get Qloss at design temperature
    Q_loss_design = get_Qloss_design(T_outdoor, Q_loss, T_design, cold_fraction)
    # Define MWT and dT for the boiler and heat pump
    dT_boiler = 20
    dT_heatpump = 5
    MWT_boiler = T_flow_boiler - 0.5 * dT_boiler
    MWT_heatpump = T_flow_heatpump - 0.5 * dT_heatpump
    # Define radiator areas for the boiler and heat pump
    if radiator_areas == "autosize":
        # Size radiators to meet the design load
        radiator_areas_boiler = [size_radiator_area(Q_loss_design, MWT_boiler)]
        radiator_areas_hp = [size_radiator_area(Q_loss_design, MWT_heatpump)]
    else:
        radiator_areas_boiler = radiator_areas_hp = radiator_areas
    # NOTE: the HP cannot provide more than 65 °C, which means that the max power of the
    # radiator is not the same as boiler (4.085)
    max_T_emitter_hp = 65 - dT_heatpump / 2
    get_radiator_power, _ = K22_radiator()
    power_at_max_T_emitter_hp = get_radiator_power(max_T_emitter_hp)
    # Define available heating systems
    all_boiler_models = ["HR107", "VR"]
    all_HP_models = ["3.5kW", "5kW", "7kW", "10kW", "12kW"]
    all_hybrid_HP_models = [("3kW Intergas", "HR107")]
    if boiler_models is None:
        boiler_models = all_boiler_models
    if HP_models is None:
        HP_models = all_HP_models
    if hybrid_HP_models is None:
        hybrid_HP_models = all_hybrid_HP_models

    ### Loop over radiator areas
    results = {}
    for rad_area_boiler, rad_area_hp in zip(radiator_areas_boiler, radiator_areas_hp):
        rad_area_boiler, rad_area_hp = round(rad_area_boiler, 2), round(rad_area_hp, 2)
        # Split Q_loss into two parts: one for the emitter and one for electric backup
        # when the emitter cannot meet the demand given the radiator area
        Q_emitter_boiler = np.clip(Q_loss, 0, 4.805 * rad_area_boiler)
        E_backup_emitter_boiler = np.clip(Q_loss - Q_emitter_boiler, 0, None)
        Q_emitter_hp = np.clip(Q_loss, 0, power_at_max_T_emitter_hp * rad_area_hp)
        E_backup_emitter_hp = np.clip(Q_loss - Q_emitter_hp, 0, None)
        # Simulate energy consumption of gas boilers
        for boiler in boiler_models:
            boiler_load = get_gas_boiler_load(
                boiler,
                Q_emitter_boiler,
                Q_dhw,
                rad_area_boiler,
                dT_boiler,
                T_room,
            )
            results[f"Gas,{boiler},{rad_area_boiler}"] = boiler_load
            results[f"Electricity,{boiler},{rad_area_boiler}"] = E_backup_emitter_boiler
        # Simulate energy consumption of heat pumps
        for HP_model in HP_models:
            HP_load, HP_and_backup_load = get_heat_pump_load(
                Q_emitter_hp,
                Q_dhw,
                T_outdoor,
                HP_model,
                rad_area_hp,
                dT_heatpump,
                T_room,
                Carnot_factor,
            )
            E_load = HP_and_backup_load + E_backup_emitter_hp
            results[f"Gas,HP {HP_model},{rad_area_hp}"] = 0
            results[f"Electricity,HP {HP_model},{rad_area_hp}"] = E_load
        # Simulate energy consumption of hybrid heat pumps
        for HP_model, boiler in hybrid_HP_models:
            HP_load, HP_and_backup_load = get_heat_pump_load(
                Q_emitter_hp,
                Q_dhw,
                T_outdoor,
                HP_model,
                rad_area_hp,
                dT_heatpump,
                T_room,
                Carnot_factor,
            )
            E_load = HP_and_backup_load + E_backup_emitter_hp
            hybrid_model = f"HP {HP_model} + {boiler}"
            (
                results[f"Electricity,{hybrid_model} Parallel,{rad_area_hp}"],
                results[f"Gas,{hybrid_model} Parallel,{rad_area_hp}"],
                results[f"Electricity,{hybrid_model} Alternate,{rad_area_hp}"],
                results[f"Gas,{hybrid_model} Alternate,{rad_area_hp}"],
            ) = get_hybrid_heat_pump_load(
                Q_loss=Q_emitter_hp,
                hp_load=HP_load,
                Q_loss_shortage=HP_and_backup_load - HP_load,
                boiler_load=results[f"Gas,{boiler},{rad_area_boiler}"],
                T_outdoor=T_outdoor,
                alternate_on=alternate_on,
            )
    # Save results to output file
    df = pd.DataFrame(results)
    output_file = sim_dir / "HS_consumption.parquet"
    df.to_parquet(output_file, index=False)
    return


def get_underheating_hours(
    Qloss: np.ndarray,
    max_load: np.ndarray,
    thermal_comfort_time: float = 9,
):
    """
    To measure underheating, we can count the number of hours where the heating demand
    is not met. However, the user could heat more than what is needed during previous
    hours, so that the total heating demand over a certain time window is still met
    overall. This is what is done here: we compute the average heating demand over a
    window of 9 hours (thermal comfort time) and count the number of hours where this
    average is below the max load of the heat pump.
    """
    difference_between_demand_and_supply = max_load - Qloss
    # Make a moving average including the edges and calculate how many hours lack of heating within the TCW
    y_padded = np.pad(
        difference_between_demand_and_supply,
        (
            thermal_comfort_time // 2,
            thermal_comfort_time - 1 - thermal_comfort_time // 2,
        ),
        mode="edge",
    )
    y_smooth = np.convolve(
        y_padded, np.ones((thermal_comfort_time,)) / thermal_comfort_time, mode="valid"
    )
    TCW_not_met = (y_smooth < 0).sum()
    # # Instead of hours, calculate how far we are from the desired heating demand
    # movQloss1 = np.pad(
    #     Qloss / 1000,
    #     (
    #         thermal_comfort_time // 2,
    #         thermal_comfort_time - 1 - thermal_comfort_time // 2,
    #     ),
    #     mode="edge",
    # )
    # movQloss2 = (
    #     np.convolve(
    #         movQloss1,
    #         np.ones((thermal_comfort_time,)) / thermal_comfort_time,
    #         mode="valid",
    #     )
    #     * thermal_comfort_time
    # )
    # # Same for the HP capacity
    # movmaxload1 = np.pad(
    #     max_load,
    #     (
    #         thermal_comfort_time // 2,
    #         thermal_comfort_time - 1 - thermal_comfort_time // 2,
    #     ),
    #     mode="edge",
    # )
    # movmaxload2 = (
    #     np.convolve(
    #         movmaxload1,
    #         np.ones((thermal_comfort_time,)) / thermal_comfort_time,
    #         mode="valid",
    #     )
    #     * thermal_comfort_time
    # )
    # # NOTE: only sum hours where the heating demand is not met
    # # Discrepancy = (movQloss2 - movmaxload2) / movQloss2 * 100
    return TCW_not_met


def simulate_heat_pump_old(
    eso_file: Path,
    input_file: Path,
    T_room: float,
    Tdesign: float,
    T_flow_heatpump: float,
    cold_fraction: float,
    Carnot_factor: float,
    T_flow_boiler: float,
    thermal_comfort_time: float,
):
    runtime = 3  # If it is 4, heat pump needs to run at least 15 min etc. This is for the minimum load figure

    ### Extract data from simulation results
    E_plus_data = SimResultsReader(eso_file, input_file).results["hourly"]
    # NOTE: probably we dont need the month, day and hour columns
    E_plus_data["month"] = pd.DatetimeIndex(E_plus_data["date"]).month
    E_plus_data["day"] = pd.DatetimeIndex(E_plus_data["date"]).day
    E_plus_data["hour"] = pd.DatetimeIndex(E_plus_data["date"]).hour
    # Outdoor temperature
    Temperature = E_plus_data[
        "Site Outdoor Air Drybulb Temperature Environment"
    ].to_numpy()
    Temperature = Temperature + 273.15
    # Heating demand
    Qloss = E_plus_data["Boiler Heating Rate BOILER"].to_numpy()
    Qloss = np.round(Qloss, 1)  # NOTE: optional

    # Calculate Design heat load. You can use night hours or not.
    # NOTE: this filtering does nothing, can be removed
    filtered_for_time = E_plus_data[
        (E_plus_data["hour"] >= 0) & (E_plus_data["hour"] < 25)
    ]
    # Linear fit of the cold fraction largest heat load.
    # NOTE: to replace with kernel fit?
    filtered_for_cold = filtered_for_time[
        filtered_for_time["Boiler Heating Rate BOILER"]
        >= ((1 - cold_fraction) * max(filtered_for_time["Boiler Heating Rate BOILER"]))
    ]
    TemperatureD = filtered_for_cold[
        "Site Outdoor Air Drybulb Temperature Environment"
    ].to_numpy()
    QlossD = filtered_for_cold["Boiler Heating Rate BOILER"].to_numpy()
    QlossD = np.round(QlossD, 4)
    coef = np.polyfit(TemperatureD, QlossD, 1)

    Qlossdesign = np.round(coef[0] * Tdesign + coef[1], 0)
    poly1d_fn = np.poly1d(coef)

    # Summary: We have T_outdoor and Qloss from E+, Qlossdesign at Tdesign based on E+ data.
    # What we need is, what flow temperature design do we want at the Tdesign, radiators are at sized at T_design - 0.5 dT = MWT
    # These are the supply temperatures
    dT_boiler = 20
    dT_heatpump = 5
    MWT_boiler = T_flow_boiler - 0.5 * dT_boiler
    MWT_heatpump = T_flow_heatpump - 0.5 * dT_heatpump

    # Define emitter system (minor adaptation from previous code, focus on Mean Water Temperature in Radiator, and a DT for flow T of Boiler and Heat Pump.
    K22_Power = [
        0,
        57,
        143,
        246,
        360,
        485,
        618,
        759,
        906,
        1220,
        1555,
        1909,
        2281,
        2668,
        3070,
        3485,
        3913,
        4354,
        4805,
    ]
    K22_MWT = [
        20,
        22.5,
        25,
        27.5,
        30,
        32.5,
        35,
        37.5,
        40,
        45,
        50,
        55,
        60,
        65,
        70,
        75,
        80,
        85,
        90,
    ]

    Radiator_power_interpolation = interpolate.interp1d(K22_MWT, K22_Power)
    Radiator_temperature_interpolation = interpolate.interp1d(K22_Power, K22_MWT)

    W_output_MWT_boiler = Radiator_power_interpolation(MWT_boiler)
    W_output_MWT_heatpump = Radiator_power_interpolation(MWT_heatpump)

    Radiator_area_boiler = 4.5  # Qlossdesign / W_output_MWT_boiler
    # NOTE: what to do here? Should we design the radiator area for the heat pump as well?
    Radiator_area_heatpump = 4.5  # Qlossdesign/W_output_MWT_heatpump

    # Boiler
    Qemitter = Qloss / Radiator_area_boiler  # heat load per m^2 emitter
    MWT_boiler_hourly = Radiator_temperature_interpolation(Qemitter)
    T_flow_boiler_supply_hourly = MWT_boiler_hourly + dT_boiler / 2
    T_flow_boiler_return_hourly = MWT_boiler_hourly - dT_boiler / 2

    # NOTE: use clip instead of masking and put this before computing
    # supply and return temperatures
    MWT_boiler_hourly[MWT_boiler_hourly < (T_room + 0.5 * dT_boiler)] = (
        T_room + 0.5 * dT_boiler
    )
    T_flow_boiler_supply_hourly[T_flow_boiler_supply_hourly < (T_room + dT_boiler)] = (
        T_room + dT_boiler
    )
    T_flow_boiler_return_hourly[T_flow_boiler_return_hourly < T_room] = T_room

    Tboilereff = [
        5.399239543726235,
        8.6787072243346,
        14.712927756653992,
        19.566539923954373,
        26.519011406844108,
        33.99619771863118,
        36.88212927756654,
        40.81749049429658,
        43.30988593155894,
        45.67110266159696,
        48.29467680608365,
        50.655893536121674,
        53.148288973384034,
        54.19771863117871,
        55.640684410646394,
        59.444866920152094,
        69.54562737642587,
        78.46577946768062,
        89.61596958174906,
        97.7490494296578,
        105.88212927756655,
        113.88403041825096,
        118.08174904942966,
    ]
    effboiler = [
        99.4186046511628,
        99.13953488372093,
        98.5813953488372,
        97.79069767441861,
        96.81395348837209,
        95.55813953488372,
        94.81395348837209,
        93.95348837209302,
        93.02325581395348,
        92.09302325581396,
        91.23255813953489,
        90.06976744186046,
        88.69767441860465,
        87.97674418604652,
        87.16279069767442,
        86.95348837209302,
        86.48837209302326,
        86.13953488372093,
        85.72093023255815,
        85.37209302325581,
        85.02325581395348,
        84.69767441860465,
        84.53488372093024,
    ]
    # NOTE: only return temperature is needed for the boiler efficiency, do we need the rest?
    effiency = np.interp(T_flow_boiler_return_hourly, Tboilereff, effboiler)
    # NOTE: do we need district heating? it is just the annual heating demand
    District_heating = round(sum(Qloss) / 1000)
    Gas_heating = Qloss / (effiency / 100) / 1000

    # Heatpump
    Qemitter = Qloss / Radiator_area_heatpump  # heat load per m^2 emitter
    MWT_heatpump_hourly = Radiator_temperature_interpolation(Qemitter)
    T_flow_heatpump_supply_hourly = MWT_heatpump_hourly + dT_heatpump / 2
    T_flow_heatpump_return_hourly = MWT_heatpump_hourly - dT_heatpump / 2
    # NOTE: same as before, use clip instead of masking and put this before computing
    # supply and return temperatures
    MWT_heatpump_hourly[MWT_heatpump_hourly < (T_room + 0.5 * dT_heatpump)] = (
        T_room + 0.5 * dT_heatpump
    )
    T_flow_heatpump_supply_hourly[
        T_flow_heatpump_supply_hourly < (T_room + dT_heatpump)
    ] = (T_room + dT_heatpump)
    T_flow_heatpump_return_hourly[T_flow_heatpump_return_hourly < T_room] = T_room

    # Effiency of the heatpump
    # if flow and outdoor T are equal you devide by 0, so we check if there are any equal values and add almost nothing to it just to make it work.
    # NOTE: just add a small constant in the denominator to avoid division by zero
    # and remove these lines
    equal_elements = (T_flow_heatpump_supply_hourly + 273.15) == Temperature
    equal_indices = np.where(equal_elements)[0]
    T_flow_heatpump_supply_hourly[equal_indices] += 0.00001

    Carnot = (
        Carnot_factor
        * (T_flow_heatpump_supply_hourly + 273.15)
        / ((T_flow_heatpump_supply_hourly + 273.15) - (Temperature))
    )
    Carnot[Carnot <= 0] = (
        8  # As Flow T is lower than Outdoor T, makes no sense rarely happens but causes negatives that should be fixed
    )
    Carnot[Carnot > 8] = 8  # NOTE: this often happens (>30% of the time)

    Outdoor_T = [-20, -15, -12, -7, -2, 0, 2, 7, 10, 12, 15, 20]
    Flow_T = [35, 45, 55, 65]
    points = [(T, x) for T in Outdoor_T for x in Flow_T]
    # Max output
    HPcapacity_3_5kW = [
        2.7,
        2.5,
        2.1,
        2.1,
        3.3,
        3.1,
        2.9,
        2.9,
        3.7,
        3.4,
        3.2,
        2.1,
        4.2,
        4.0,
        3.7,
        3.3,
        5.0,
        4.7,
        4.3,
        4.0,
        5.1,
        4.9,
        4.5,
        4.4,
        5.2,
        5.2,
        4.8,
        4.7,
        5.9,
        5.8,
        5.6,
        5.0,
        6.8,
        6.4,
        5.9,
        5.6,
        7.0,
        6.7,
        6.0,
        5.8,
        7.2,
        6.8,
        6.4,
        6.0,
        7.2,
        6.8,
        6.4,
        6.0,
    ]
    interpolator3_5kW = LinearNDInterpolator(points, HPcapacity_3_5kW)
    HPcapacity_5kW = [
        4.3,
        3.9,
        3.7,
        4.5,
        4.9,
        4.5,
        4.5,
        4.5,
        5.4,
        4.9,
        4.8,
        4.2,
        6.2,
        5.6,
        5.5,
        5.4,
        7.1,
        6.6,
        6.3,
        6.1,
        7.2,
        6.9,
        6.6,
        6.5,
        7.3,
        7.3,
        6.9,
        6.8,
        8,
        7.9,
        7.6,
        7.2,
        8,
        7.9,
        7.6,
        7.2,
        8,
        7.9,
        7.6,
        7.2,
        8,
        7.9,
        7.6,
        7.2,
        8,
        7.9,
        7.6,
        7.2,
    ]
    interpolator5kW = LinearNDInterpolator(points, HPcapacity_5kW)
    HPcapacity_7kW = [
        5.8,
        5.3,
        5.1,
        5.1,
        6.6,
        6.1,
        5.9,
        5.9,
        7.2,
        6.7,
        5.9,
        4.6,
        8,
        7.8,
        6.9,
        5.4,
        9.4,
        9,
        8.0,
        6.3,
        9.9,
        9.5,
        8.5,
        6.7,
        10.4,
        9.9,
        9,
        7.1,
        12.3,
        11.6,
        9.1,
        8.2,
        11.7,
        11.2,
        9.6,
        8.1,
        10.6,
        10.2,
        9.8,
        8.4,
        9.8,
        9.8,
        9.7,
        7.9,
        8.9,
        8.8,
        8.6,
        8.3,
    ]
    interpolator7kW = LinearNDInterpolator(points, HPcapacity_7kW)
    HPcapacity_10kW = [
        7.3,
        6.8,
        6.4,
        6.4,
        8.0,
        7.4,
        7.1,
        7.1,
        8.7,
        8.2,
        7.7,
        7.3,
        9.7,
        9.6,
        8.8,
        8.4,
        11.7,
        11.2,
        10,
        9.8,
        12.5,
        12,
        10.7,
        10,
        13.3,
        12.8,
        11.4,
        10.2,
        15,
        14.4,
        12.4,
        12.2,
        15.2,
        14.7,
        13.2,
        12.5,
        15.3,
        14.8,
        13.8,
        12.6,
        15.4,
        14.9,
        13.9,
        12.8,
        14.9,
        14.2,
        13.5,
        11.7,
    ]
    interpolator10kW = LinearNDInterpolator(points, HPcapacity_10kW)
    HPcapacity_12kW = [
        9.6,
        9.5,
        7.1,
        7.1,
        10.4,
        10.1,
        7.8,
        7.1,
        11.2,
        11,
        9,
        6.5,
        12.7,
        12.5,
        10.9,
        9.7,
        14.7,
        13.7,
        12.1,
        10.9,
        15.6,
        14.5,
        12.8,
        11.1,
        16.4,
        15.3,
        13.6,
        11.3,
        17.9,
        16.8,
        14.7,
        12.7,
        17.7,
        16.8,
        15,
        13,
        17.4,
        16.7,
        15.2,
        12.1,
        16,
        15.5,
        14.7,
        12.8,
        14.9,
        14.2,
        13.5,
        11.7,
    ]
    interpolator12kW = LinearNDInterpolator(points, HPcapacity_12kW)
    # Min output
    HPmincapacity_3_5kW = [
        0.9,
        0.8,
        1,
        0,
        1.7,
        1.4,
        1.2,
        0,
        1.7,
        1.6,
        1.2,
        2,
        1.5,
        1.3,
        0.9,
        1.3,
        1.7,
        1.5,
        1.2,
        1,
        1.8,
        1.6,
        1.4,
        0.8,
        2,
        1.7,
        1.6,
        0.9,
        2.1,
        1.8,
        1.8,
        1.2,
        2.4,
        2.2,
        1.9,
        1.6,
        2.5,
        2.3,
        2,
        1.9,
        2.6,
        2.5,
        2.1,
        1.9,
        2.8,
        2.6,
        2.1,
        1.9,
    ]
    interpolatormin3_5kW = LinearNDInterpolator(points, HPmincapacity_3_5kW)
    HPmincapacity_5kW = [
        0.9,
        0.8,
        1.0,
        0.0,
        1.6,
        1.4,
        1.2,
        0.0,
        1.9,
        1.7,
        1.5,
        2.0,
        1.7,
        1.6,
        1.1,
        1.3,
        1.7,
        1.5,
        1.2,
        1.3,
        1.8,
        1.6,
        1.4,
        0.8,
        2.0,
        1.7,
        1.6,
        0.9,
        2.1,
        1.8,
        1.8,
        1.2,
        2.4,
        2.2,
        1.9,
        1.6,
        2.5,
        2.3,
        2.0,
        1.9,
        2.6,
        2.5,
        2.1,
        1.9,
        2.8,
        2.6,
        2.1,
        1.9,
    ]
    interpolatormin5kW = LinearNDInterpolator(points, HPmincapacity_5kW)
    HPmincapacity_7kW = [
        1.8,
        1.4,
        1.2,
        0.0,
        2.1,
        1.8,
        1.6,
        0.0,
        2.7,
        2.1,
        1.8,
        1.6,
        2.5,
        2.1,
        1.8,
        1.4,
        2.4,
        2.0,
        1.5,
        1.1,
        2.6,
        2.2,
        1.6,
        1.4,
        2.8,
        2.4,
        1.7,
        1.7,
        3.2,
        2.9,
        2.2,
        2.0,
        3.4,
        3.1,
        2.4,
        2.2,
        3.5,
        3.2,
        2.6,
        2.3,
        3.6,
        3.5,
        2.8,
        2.5,
        3.7,
        3.7,
        3.0,
        2.9,
    ]
    interpolatormin7kW = LinearNDInterpolator(points, HPmincapacity_7kW)
    HPmincapacity_10kW = [
        3.6,
        3.6,
        3.0,
        0.0,
        4.3,
        4.2,
        3.7,
        0.0,
        4.1,
        4.0,
        3.8,
        3.9,
        3.7,
        3.6,
        3.2,
        2.4,
        3.9,
        3.6,
        3.4,
        2.2,
        4.4,
        4.1,
        3.9,
        2.5,
        4.9,
        4.6,
        4.3,
        2.8,
        5.8,
        5.2,
        4.6,
        4.1,
        6.3,
        5.6,
        5.2,
        4.4,
        6.5,
        5.9,
        5.7,
        4.6,
        6.6,
        6.0,
        5.8,
        5.2,
        6.7,
        6.1,
        6.0,
        5.7,
    ]
    interpolatormin10kW = LinearNDInterpolator(points, HPmincapacity_10kW)
    HPmincapacity_12kW = [
        3.6,
        3.6,
        3.0,
        0.0,
        4.3,
        4.2,
        3.7,
        0.0,
        4.8,
        4.7,
        4.2,
        3.9,
        4.3,
        4.2,
        4.0,
        2.4,
        3.9,
        3.6,
        3.4,
        2.2,
        4.4,
        4.1,
        3.9,
        2.5,
        4.9,
        4.6,
        4.3,
        2.8,
        5.8,
        5.2,
        4.6,
        4.1,
        6.3,
        5.6,
        5.2,
        4.4,
        6.5,
        5.9,
        5.7,
        4.6,
        6.6,
        6.0,
        5.8,
        5.2,
        6.7,
        6.1,
        6.0,
        5.7,
    ]
    interpolatormin12kW = LinearNDInterpolator(points, HPmincapacity_12kW)

    result3_5kW = interpolator3_5kW(Tdesign, T_flow_heatpump)
    result5kW = interpolator5kW(Tdesign, T_flow_heatpump)
    result7kW = interpolator7kW(Tdesign, T_flow_heatpump)
    result10kW = interpolator10kW(Tdesign, T_flow_heatpump)
    result12kW = interpolator12kW(Tdesign, T_flow_heatpump)

    if max(T_flow_heatpump_supply_hourly) > 65:
        print("Supply of HP above 65, this is stupid an leads to unaccurate results")
    # For interpolation at least 35 degree and max 65 flow is needed to create this picture and T cannot exceed -20 to 20
    # NOTE: use clip here
    T_flow_heatpump_for_boundary_calc = np.copy(T_flow_heatpump_supply_hourly)
    T_flow_heatpump_for_boundary_calc[T_flow_heatpump_for_boundary_calc < 35] = 35
    T_flow_heatpump_for_boundary_calc[T_flow_heatpump_for_boundary_calc > 65] = 65
    Temperature_for_boundary_calc = Temperature
    # NOTE: use clip here
    Temperature_for_boundary_calc[Temperature_for_boundary_calc > (273.15 + 20)] = (
        273.15 + 20
    )

    if Qlossdesign / 1000 < result3_5kW:
        HP = 1
        min_load = (
            interpolatormin3_5kW(
                Temperature_for_boundary_calc - 273.15,
                T_flow_heatpump_for_boundary_calc,
            )
            / runtime
        )
        max_load = interpolator3_5kW(
            Temperature_for_boundary_calc - 273.15, T_flow_heatpump_for_boundary_calc
        )
    elif Qlossdesign / 1000 < result5kW:
        HP = 2
        min_load = (
            interpolatormin5kW(
                Temperature_for_boundary_calc - 273.15,
                T_flow_heatpump_for_boundary_calc,
            )
            / runtime
        )
        max_load = interpolator5kW(
            Temperature_for_boundary_calc - 273.15, T_flow_heatpump_for_boundary_calc
        )
    elif Qlossdesign / 1000 < result7kW:
        HP = 3
        min_load = (
            interpolatormin7kW(
                Temperature_for_boundary_calc - 273.15,
                T_flow_heatpump_for_boundary_calc,
            )
            / runtime
        )
        max_load = interpolator7kW(
            Temperature_for_boundary_calc - 273.15, T_flow_heatpump_for_boundary_calc
        )
    elif Qlossdesign / 1000 < result10kW:
        HP = 4
        min_load = (
            interpolatormin10kW(
                Temperature_for_boundary_calc - 273.15,
                T_flow_heatpump_for_boundary_calc,
            )
            / runtime
        )
        max_load = interpolator10kW(
            Temperature_for_boundary_calc - 273.15, T_flow_heatpump_for_boundary_calc
        )
    elif Qlossdesign / 1000 < result12kW:
        HP = 5
        min_load = (
            interpolatormin12kW(
                Temperature_for_boundary_calc - 273.15,
                T_flow_heatpump_for_boundary_calc,
            )
            / runtime
        )
        max_load = interpolator12kW(
            Temperature_for_boundary_calc - 273.15, T_flow_heatpump_for_boundary_calc
        )
    elif Qlossdesign / 1000 > result12kW:
        print("No suitable heatpump available")

    HP = 3
    min_load = (
        interpolatormin7kW(
            Temperature_for_boundary_calc - 273.15, T_flow_heatpump_for_boundary_calc
        )
        / runtime
    )
    max_load = interpolator7kW(
        Temperature_for_boundary_calc - 273.15, T_flow_heatpump_for_boundary_calc
    )
    Heatpump_shortage = (
        Qloss - max_load * 1000
    )  # only if the max output is less than the loss we get values
    Heatpump_shortage[Heatpump_shortage < 0] = (
        0  # only if the max output is less than the loss we get values because they will remain positive
    )
    Qloss_byHP = (
        Qloss - Heatpump_shortage
    )  # We split in two, what can be covered by the HP (all that it is not short)
    Qloss_byE = Heatpump_shortage  # And what it is short, by Elec.
    Heatpump_E = (
        Qloss_byHP / Carnot
    )  # The electric input of the heatpump is all is needs to cover devided by its effiency.
    Gridimpact = Heatpump_E + Qloss_byE

    # heat pump
    print("HEAT PUMP:")
    print("Design outdoor Temperature [C]", Tdesign)
    print("Design Heat load [kW]", round(Qlossdesign, 2) / 1000)
    print("Max heat load during year [kW]", max(Qloss / 1000))
    print("Design Flow T HP [C]", T_flow_heatpump)
    print("Max flow T for HP", round(max(T_flow_heatpump_supply_hourly), 1))
    print("Area K22 for HP", round(Radiator_area_heatpump, 2))
    print(
        "Heatpump design powers at design conditions (T outdoor and T Flow)",
        result3_5kW,
        result5kW,
        result7kW,
        result10kW,
        result12kW,
    )
    print("Heat pump number used", HP)
    print(
        "Heat pump",
        round(sum(Heatpump_E / 1000)),
        "kWh",
        "SCOP",
        round(round(sum(Qloss_byHP)) / round(sum(Heatpump_E)), 2),
        "Heat pump Electric Back Up",
        round(sum(Qloss_byE / 1000), 3),
        "kWh",
    )
    print("Max gridload", max(Gridimpact / 1000))

    # boiler
    print("GAS BOILER")
    print("Design Flow T boiler[C]", T_flow_boiler)
    print("Area K22 for Boiler", round(Radiator_area_boiler, 2))
    print("Max flow T for Boiler", round(max(T_flow_boiler_supply_hourly), 1))
    print("Gas", round(sum(Gas_heating)), "kWh", round(sum(Gas_heating) / 9.77), "m^3")

    # Defining the Shortage in heating (using https://stackoverflow.com/questions/47484899/moving-average-produces-array-of-different-length)
    # First we calculated the fucntion
    difference_between_demand_and_supply = max_load - Qloss / 1000
    # Make a moving average including the edges and calculate how many hours lack of heating within the TCW
    y_padded = np.pad(
        difference_between_demand_and_supply,
        (
            thermal_comfort_time // 2,
            thermal_comfort_time - 1 - thermal_comfort_time // 2,
        ),
        mode="edge",
    )
    y_smooth = np.convolve(
        y_padded, np.ones((thermal_comfort_time,)) / thermal_comfort_time, mode="valid"
    )
    TCW_not_met = (y_smooth < 0).sum()

    # Instead of hours, calculate how far we are from the desired heating demand
    movQloss1 = np.pad(
        Qloss / 1000,
        (
            thermal_comfort_time // 2,
            thermal_comfort_time - 1 - thermal_comfort_time // 2,
        ),
        mode="edge",
    )
    movQloss2 = (
        np.convolve(
            movQloss1,
            np.ones((thermal_comfort_time,)) / thermal_comfort_time,
            mode="valid",
        )
        * thermal_comfort_time
    )
    # Same for the HP capacity
    movmaxload1 = np.pad(
        max_load,
        (
            thermal_comfort_time // 2,
            thermal_comfort_time - 1 - thermal_comfort_time // 2,
        ),
        mode="edge",
    )
    movmaxload2 = (
        np.convolve(
            movmaxload1,
            np.ones((thermal_comfort_time,)) / thermal_comfort_time,
            mode="valid",
        )
        * thermal_comfort_time
    )
    # NOTE: only sum hours where the heating demand is not met
    # Discrepancy = (movQloss2 - movmaxload2) / movQloss2 * 100
    return
