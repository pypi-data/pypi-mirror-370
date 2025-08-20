import json
from pathlib import Path
from typing import List
from warnings import simplefilter

import esoreader
import numpy as np
import pandas as pd
import pythermalcomfort.models
from joblib import Parallel, delayed
from tqdm import tqdm

import renovexpy.geometry as geometry
from renovexpy.utils import load_epjson_from_idf, run_with_timeout

curr_dir = Path(__file__).parent
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)


class SimResultsReader:
    """
    A class for loading simulation results and computing "primary" KPIs.
    """

    def __init__(self, sim_dir: Path):

        eso_file = sim_dir / "eplusout.eso"
        input_file = list(sim_dir.glob("input_*.epjson"))[0]
        HS_output_file = sim_dir / "HS_consumption.parquet"
        PV_output_file = sim_dir / "PV_generation.parquet"
        self.vent_type = input_file.stem.split("_")[1]
        # Load input file as epjson
        if Path(input_file).suffix == ".idf":
            self.epjson = load_epjson_from_idf(input_file)
        elif Path(input_file).suffix.lower() == ".epjson":
            with open(input_file, "r") as f:
                self.epjson = json.load(f)
        else:
            raise ValueError("Input file must be an IDF or epJSON file.")
        # Load eso file and save hourly results in self.eplus
        try:
            self.eso = run_with_timeout(
                esoreader.read_from_path, args=[eso_file], timeout=30
            )
        except TimeoutError:
            raise TimeoutError("Reading the ESO file took too long.")
        eso_data = {}
        for (freq, obj, var), idx in self.eso.dd.index.items():
            if freq.lower() == "hourly":
                col = f"{var} {obj}" if obj != None else var
                eso_data[col] = self.eso.data[idx]
        self.eplus = pd.DataFrame(eso_data)
        # Add date column to hourly results
        self.eplus["date"] = pd.date_range(
            "2002-01-01", periods=len(self.eplus), freq="h"
        )
        # Get zones names
        self.zones = list(self.epjson["Zone"].keys())
        # Get dictionary linking zones to occupancy schedules
        self.occ_sched_per_zone = {
            val["zone_or_zonelist_or_space_or_spacelist_name"]: key.upper()
            for key, val in self.epjson["People"].items()
        }
        # Get output variables
        self.output_vars = set([key[2] for key in self.eso.dd.index.keys()])
        # If provided, create an attribute self.heat_sys with simulation results
        if HS_output_file.exists():
            self.heat_sys = pd.read_parquet(HS_output_file)
        # If provided, create an attribute self.pv_gen with simulation results
        # self.N_panels = []
        if PV_output_file.exists():
            self.pv_gen = pd.read_parquet(PV_output_file)
            self.pv_gen["0"] = 0
        return

    def get_heating_demand(self, kind):
        """
        Get annual or peak heating demand.

        Inputs
        ------
        kind: str
            Kind of heating demand to compute. Possible values are "annual" or "peak".
        """
        # Do checks
        if kind not in ["annual", "peak"]:
            raise ValueError(f"Parameter 'kind' must be either 'annual' or 'peak'.")
        # Get heating demand data
        hourly_hd = self.eplus["Boiler Heating Rate BOILER"] / 1000  # Convert to kWh
        return np.sum(hourly_hd) if kind == "annual" else np.max(hourly_hd)

    def get_energy_consumption(self, variable: str, kind: str):
        """
        Get the energy consumption (heating + DHW) in kWh for different heating systems:
            - Gas boiler
            - Heat pumps of different capacities (with or without backup)
        Hourly consumptions can then be aggregated to annual, peak or OPP (over 1% of the year).
        """
        assert variable in ["electricity", "gas"], f"Invalid type: {variable}"
        # Get data with gas/electricity columns
        df = self.heat_sys.filter(regex=f"^{variable.capitalize()}").copy()
        # Remove variable name to keep only the heating system name
        df.columns = [",".join(col.split(",")[1:]) for col in df.columns]
        if variable == "electricity":
            # Create variable with PV surplus generation
            self.pv_surplus = {}
            ### Add electricity consumption of other appliances and substract PV generation
            E_other = self.eplus["Electricity:Facility"] / 3.6e6
            # For Type C ventilation, substract electricity from the supply fan
            if self.vent_type in ["C1", "C2", "C4a"]:
                E_supply_fan = (
                    self.eplus["Fan Electricity Energy AIR LOOP AHU SUPPLY FAN"] / 3.6e6
                )
                E_other = E_other - E_supply_fan
            for col in df.columns:  # Loop over heating systems
                df[col] += E_other
                # Substract PV generation
                for N_pv in self.pv_gen.columns:
                    df[f"{col},{N_pv} PV"] = np.clip(
                        df[col] - self.pv_gen[N_pv], 0, None
                    )
                    pv_surplus = np.clip(self.pv_gen[N_pv] - df[col], 0, None).sum()
                    self.pv_surplus[f"{col},{N_pv} PV"] = pv_surplus
                del df[col]
            self.pv_surplus = pd.Series(self.pv_surplus)
        else:
            # For gas, simply duplicate columns for each N_pv
            for col in df.columns:
                for N_pv in self.pv_gen.columns:
                    df[f"{col},{N_pv} PV"] = df[col]
                del df[col]

        # Aggregate data based on the kind parameter
        if kind not in (options := ["annual", "hourly", "peak", "OPP"]):
            raise ValueError(f"Parameter 'kind' must be in {options}.")
        elif kind == "annual":
            df = df.sum()
        elif kind == "peak":
            df = df.max()
        elif kind == "OPP":  # Mean of top 1% peaks
            df = df[df >= df.quantile(0.99)].mean()
        return df

    def get_CO2_excess_hours(
        self, zones, zone_agg, filter_occupied_hours, threshold=1200
    ):
        """
        Return number of hours where CO2 concentration is above the threshold.

        Inputs:
        -------
        zones: list of str, or "all"
            The zones to include in the computation. If "all", all zones are included.
        zone_agg: str
            How to aggregate hours of CO2 excess across zones. If "any", we count the
            number of hours where at least one of the zones has a CO2 excess.
            If "sum", we add the number of hours of CO2 excess per zone.
        count_only_occupied: bool
            If True, hours of CO2 excess only count if the zones are occupied.
        threshold: float, optional
            CO2 concentration threshold in ppm (default: 1200 ppm).
        """
        if zones == "all":
            zones = self.zones
        # Do checks
        if not all(zone in self.zones for zone in zones):
            raise ValueError(f"Invalid zones. Possible values are {self.zones}.")
        if zone_agg not in ["any", "sum"]:
            raise ValueError("Parameter 'zone_agg' must be either 'any' or 'sum'.")
        # Get occupancy mask
        occ_cols = [f"Schedule Value OCCUPANCY_{zone}" for zone in zones]
        if filter_occupied_hours:
            O = (self.eplus[occ_cols] > 0).to_numpy(dtype=float)
        else:
            O = np.ones((len(self.eplus), len(zones)), dtype=float)
        # Fill dataframe with CO2 excess data
        co2_cols = [f"Zone Air CO2 Concentration {zone}" for zone in zones]
        df_co2 = self.eplus[co2_cols].copy()
        co2_excess = (df_co2 > threshold) * O
        if zone_agg == "sum":
            return co2_excess.sum(axis=1).sum()
        else:
            return co2_excess.any(axis=1).sum()

    def get_avg_CO2_exposure(self):
        co2_occ_hours = []
        for zone in self.zones:
            zone_co2 = self.eplus[f"Zone Air CO2 Concentration {zone}"]
            zone_occ = self.eplus[f"Schedule Value OCCUPANCY_{zone}"] > 0
            co2_occ_hours.append(zone_co2[zone_occ].values)
        co2_occ_hours = np.concatenate(co2_occ_hours)
        # Compute average CO2 exposure in ppm
        avg_co2_exposure = co2_occ_hours.mean()
        return avg_co2_exposure

    def get_overheating(
        self,
        input_var: str,
        th: float,
        delta_th: float,
        alpha: float,
        beta: float,
        zones: List[str] | str,
        zone_agg: str,
        filter_occupied_hours: bool,
    ):
        """
        Return the amount of overheating in the building over a whole year.
        For a single zone 'z', this quantity is defined as follows:

            OH(z) = SUM_{i=1}^{8760} w(x_{i,z}) * o_{i,z}

        x_{i,z} is the value of an input variable (e.g. temperature) at the i-th
        hour in zone z.

        w(x) is a weighting function that returns the level of overheating
        associated to x. It relies on a threshold value x_{th} and two parameters alpha
        and beta, and is defined as follows:

            - w(x) = 0 if x < x_{th}
            - w(x) = alpha * (x - x_{th}) + beta if x >= x_{th}

        Alpha and beta can be changed to reproduce various KPIs used in practice.
        For example, with alpha = 0 and beta = 1, w(x) becomes a simple thresholding
        function.

        o_{i,z} is a binary variable that is equal to 1 if zone 'z' is occupied at
        the i-th hour, and 0 otherwise. This allows to measure overheating only when
        the zone is occupied. Note that we can also dismiss occupancy by setting
        o_{i,z} = 1 for all i.

        Finally, the overheating in the whole building is computed by aggregating
        the overheating across all zones. The aggregation can be done in three ways:

        1) "SUM_H-SUM_Z": The overheating levels for all hours and zones are summed.

            OH = SUM([OH(z) for z in zones])

        2) "SUM_H-MAX_Z": For each zone, overheating levels are summed across hours.
        The maximum value across zones is then taken.

            OH = MAX([OH(z) for z in zones])

        3) "MAX_Z-SUM_H": For each hour, the maximum overheating level across zones is
        taken. These values are then summed across hours.

            OH = SUM_{i=1}^{8760} MAX([w(x_{i,z}) * o_{i,z} for z in zones])

        Inputs:
        -------
        input_var: str
            Input variable x to use in the weighting function w(x).
            Possible options are: "air_temp", "operative_temp", "pmv" and "ppd".
        th: float
            Threshold value for the weighting function w(x). If delta_th is
            non-zero, the actual threshold x_{th} will vary throughout the year,
            but will be in average equal to `th`.
        delta_th: float
            This parameter allows the threshold to deviate from `th` by following the
            outdoor temperature T_out, so that the threshold is higher in summer that in
            winter.
            If zero, the threshold value is constant during the year: x_{th} = th.
            If non-zero, the threshold will deviate from `th` by at most `delta_th`.
        alpha: float
            Slope of the linear part of the weighting function w(x).
        beta: float
            Intercept of the linear part of the weighting function w(x).
        zones: list of str, or "all"
            A list with the zones to consider in the computation.
            If zones="all", all zones are included.
        zone_agg: str
            How to aggregate hours of overheating across zones.
            Possible options are: "SUM_H-SUM_Z", "SUM_H-MAX_Z" and "MAX_Z-SUM_H", "SUM_H".
            If "SUM_H", the output is a dictionary with the overheating level for each zone.
        filter_occupied_hours: bool
            If True, o_{i,z} follows the occupancy schedule of each zone, so that
            overheating only matters when the zone is occupied. If False, o_{i,z} = 1
            for all i.

        """
        # Do checks
        if input_var not in (options := ["air_temp", "operative_temp", "pmv", "ppd"]):
            raise ValueError(f"Parameter 'input_var' must be in {options}.")
        if zones != "all" and not all(zone in self.zones for zone in zones):
            raise ValueError(f"Invalid zones. Possible values are {self.zones}.")
        if zone_agg not in (
            options := ["SUM_H-SUM_Z", "SUM_H-MAX_Z", "MAX_Z-SUM_H", "SUM_H"]
        ):
            raise ValueError(f"Parameter 'zone_agg' must be in {options}.")
        if delta_th < 0:
            raise ValueError("Parameter 'delta_th' must be >= 0.")
        # Make numpy array X with input values x_{i,z}
        df = self.eplus
        zones = self.zones if zones == "all" else zones
        if input_var in ["air_temp", "operative_temp"]:
            temp_type = "Mean Air" if input_var == "air_temp" else "Operative"
            cols = [f"Zone {temp_type} Temperature {zone.upper()}" for zone in zones]
            X = df[cols].to_numpy()
        else:  # PMV or PPD
            X = self.get_pmv_pdd()[input_var][zones].to_numpy()
        # Make numpy array O with occupancy values o_{i,z}
        occ_cols = [f"Schedule Value OCCUPANCY_{zone}" for zone in zones]
        if filter_occupied_hours:
            O = (df[occ_cols] > 0).to_numpy(dtype=float)
        else:
            O = np.ones(X.shape)
        # Compute adaptive threshold t_adp (which is static if delta_th = 0)
        t_adp = self.get_adaptive_threshold(th, delta_th)
        # Compute weights W
        W = np.where(X < t_adp, 0, alpha * (X - t_adp) + beta)
        # Compute overheating using W, O and zone_agg
        if zone_agg == "SUM_H-SUM_Z":
            oh = (W * O).sum()
        elif zone_agg == "SUM_H-MAX_Z":
            oh = (W * O).sum(axis=0).max()
        elif zone_agg == "MAX_Z-SUM_H":
            oh = (W * O).max(axis=1).sum()
        elif zone_agg == "SUM_H":
            oh = (W * O).sum(axis=0)
            oh = {zone: oh[i] for i, zone in enumerate(zones)}
        return oh

    def get_adaptive_threshold(self, t_avg, delta_max):
        """
        Compute the adaptive threshold t_adp whose trend follows the outdoor temperature
        T_out. More precisely, it is defined as follows:

            t_adp(T_out) = t_avg + delta_max * alpha(T_out)

        where alpha(T_out) is between -1 and 1, has mean 0 and is defined as:

            alpha(T_out) = (T_out - T_out_avg) / max(abs((T_out - T_out_avg)))

        This formula ensures that in average, t_adp is equal to t_avg, and deviates from
        it by at most delta_max depending on T_out.
        In practice, T_out corresponds to the exponentially weighted mean outdoor
        temperature during the past 7 days, rather than the current outdoor temperature.
        """
        # Get hourly outdoor temperature
        col = "Site Outdoor Air Drybulb Temperature Environment"
        hourly_T_out = self.eplus[col].values
        # Compute daily average outdoor temperature
        daily_T_out = np.mean(hourly_T_out.reshape(-1, 24), axis=1)
        # Compute exponentially weighted mean over previous 7 days
        padded_daily_T_out = np.pad(daily_T_out, 7, mode="wrap")
        kernel = np.array([0] * 8 + [0.8**i for i in range(7)])  # Backward order
        ewm_daily_T_out = 0.253 * np.convolve(padded_daily_T_out, kernel, mode="valid")
        # Center and scale ewm_daily_T_out to obtain alpha
        alpha = ewm_daily_T_out - ewm_daily_T_out.mean()
        alpha = alpha / np.abs(alpha).max()
        # Compute adaptive threshold
        t_adp = t_avg + delta_max * alpha
        # Repeat t_adp for each hour and make it a column vector
        t_adp = np.repeat(t_adp, 24)[:, None]
        return t_adp

    def get_pmv_pdd(
        self, met_rate=0.9, air_velocity=0.137, clo_winter=1, clo_summer=0.5
    ):
        """
        Compute PMV for each zone. Outputs are clipped between -3 and 3.

        Inputs:
        -------
        met_rate: float, optional
            Metabolic rate. Should be between 0.7 and 2 (default: 0.9).
        air_velocity: float, optional
            Air velocity in m/s. Should be between 0 and 1 (default: 0.137 m/s).
        clo_winter: float, optional
            Clothing insulation level for winter. Should be between 0 and 2
            (default: 1).
        clo_summer: float, optional
            Clothing insulation level for summer. Should be between 0 and 2
            (default: 0.5).
        """
        df = self.eplus
        df_pmv, df_ppd = pd.DataFrame(), pd.DataFrame()
        # Define clothing insulation level for the whole year
        clo = np.where(
            (df["date"] > "2002-4-1") & (df["date"] <= "2002-9-30"),
            clo_summer,
            clo_winter,
        )
        for zone in self.zones:
            # Get air/radiant temp and relative humidity
            air_temp = df[f"Zone Mean Air Temperature {zone}"].values
            rad_temp = df[f"Zone Mean Radiant Temperature {zone}"].values
            rel_hum = df[f"Zone Air Relative Humidity {zone}"].values
            # Compute PMV and PPD
            D = pythermalcomfort.models.pmv_ppd(
                air_temp,
                rad_temp,
                air_velocity,
                rel_hum,
                met_rate,
                clo,
                wme=0,
                standard="ISO",
                units="SI",
                limit_inputs=False,
            )
            df_pmv[zone] = np.clip(D["pmv"], -3, 3)
            df_ppd[zone] = np.clip(D["ppd"], 0, 100)
            # Set ppd to 0 when PMV is below 0 to not count underheating
            df_ppd[zone] = np.where(df_pmv[zone] < 0, 0, df_ppd[zone])
        return {"pmv": df_pmv, "ppd": df_ppd}


### Other KPIs derived from primary/simulated KPIs


def get_CO2_emissions(elec_consumption: np.ndarray, gas_consumption: np.ndarray):
    """
    Compute the annual CO2 emissions in kgCO2, by summing the emissions of
    gas and electricity consumption.
    """
    # Define CO2 emissions factors (in kgCO2/kWh)
    # Source: NTA 8800, table 5.2
    EF_elec = 0.34
    EF_gas = 0.183
    # Sum CO2 emissions from electricity and gas
    co2_emissions = EF_elec * elec_consumption + EF_gas * gas_consumption
    return co2_emissions


def get_operational_cost(
    elec_consumption: np.ndarray, gas_consumption: np.ndarray, PV_surplus: np.ndarray
):
    """
    Compute the annual operational cost in €, by summing the costs of
    gas and electricity consumption. We take prices from the 2024CBS data.
    Source: https://www.cbs.nl/en-gb/figures/detail/85592ENG.
    """

    ### Compute energy monthly prices
    # Load data from Feb 2024 to Dec 2024
    df = pd.read_csv(curr_dir / "data/energy_prices.csv").iloc[:11]
    elec_price = (  # €/kWh
        df["Electricity/Variable delivery rate contract prices (Euro/kWh)"]
        + df["Electricity/Energy tax (Euro/kWh)"]
        + df["Electricity/Transport rate (Euro/year)"] / (12 * 3500)  # monthly €/kWh
    )
    gas_price = (
        df["Natural gas/Variable delivery rate contract prices (Euro/m3)"]
        + df["Natural gas/Energy tax (Euro/m3)"]
        + df["Natural gas/Transport rate (Euro/year)"] / (12 * 1500)  # monthly €/kWh
    )
    # Add data for Jan 2024 by repeating the first month and convert gas price to €/kWh
    elec_price = np.concatenate(([elec_price[0]], elec_price))
    gas_price = np.concatenate(([gas_price[0]], gas_price)) / 9.77
    # Tile prices to match the number of hours in the year (730 hours per month)
    elec_price = np.repeat(elec_price, 730)[:, None]
    gas_price = np.repeat(gas_price, 730)[:, None]
    # Compute operational cost
    operational_cost = (
        elec_price * elec_consumption + gas_price * gas_consumption
    ).sum()

    ### Add Net Metering cost/gain due to PV surplus
    df_nm = pd.read_csv(curr_dir / "data/net_metering.csv")
    del df_nm["Year"]
    # Apply VAT (21%)
    df_nm *= 1.21
    # Compute typical net metering price per kWh (how much you get paid for surplus)
    avg_net_price = (df_nm["Central prices"] - df_nm["Energy supplier's margin"]).mean()
    # Compute delivery cost per kWh (how much you pay for delivering surplus)
    # avg_delivery_cost_per_year = df_nm["Delivery costs (eur/year)"].mean()
    # avg_delivery_cost_per_kWh = avg_delivery_cost_per_year / elec_consumption.sum()
    avg_delivery_cost_per_kWh = 0.05  # NOTE: we use a fixed price
    # Compute net metering cost/gain and add it to operational cost
    net_metering_cost = (avg_delivery_cost_per_kWh - avg_net_price) * PV_surplus
    operational_cost += net_metering_cost
    return operational_cost


def load_cost_data():
    # TODO: take into account size of the house (interpolate min/mid/max prices)
    df = pd.read_excel(
        curr_dir / "data/kostenkentallen.xlsx",
        sheet_name="OUTPUT W - €eh",
        usecols=["Code", "Opzichzelfstaand", "Unnamed: 4", "Unnamed: 5"],
    )
    df.columns = ["code", "price-min", "price-mid", "price-max"]
    mask = df["code"].str.startswith("WB", na=False)
    df = df[mask].reset_index(drop=True)
    # Melt into code, category and price
    df = df.melt(id_vars=["code"], value_vars=["price-min", "price-mid", "price-max"])
    df["code"] = df["code"] + "-" + df["variable"].str.split("-").str[1]
    df["value"] = df["value"].astype(float)
    rm_costs = dict(zip(df["code"], df["value"]))
    # Add keys without suffix for the mid price
    for code, price in list(rm_costs.items()):
        if "-mid" in code:
            rm_costs[code[:-4]] = price
    # Map code = None to price = 0
    rm_costs[None] = 0
    ### Add specific keys
    # Vent A -> D5c
    rm_costs["WB089a + WB418"] = rm_costs["WB089a"] + rm_costs["WB418"]
    return rm_costs


def get_renovation_cost(
    renovation_measures: dict,
    pre_renov_config: dict,
    post_renov_configs: pd.DataFrame,
    replace_window_frames: bool = False,
):
    kwargs = {"replace_window_frames": replace_window_frames}
    rm_costs = load_cost_data()
    renov_cost = pd.DataFrame()
    for func in [
        get_insulation_cost,
        get_glazing_cost,
        get_ventilation_system_cost,
        get_heating_system_cost,
        get_radiator_cost,
        get_PV_cost,
        get_airtightness_cost,
        get_shading_cost,
    ]:
        func_name = func.__name__
        rm_type = func_name.split("_")[1]
        renov_cost[rm_type] = func(
            renovation_measures,
            rm_costs,
            pre_renov_config,
            post_renov_configs,
            **kwargs,
        )
    renov_cost.sum(axis=1)
    return renov_cost


def get_TCO(
    renovation_cost: np.ndarray,
    operational_cost: np.ndarray,
    n_years=30,
    inflation_rate=0.02,
):
    """
    Calculate the Total Cost of Ownership (TCO) of renovation packages
    It sums the renovation cost and the operational over n_years,
    assuming a constant inflation rate.

    Inputs
    ------
    renovation_cost: pd.DataFrame
        Dataframe with the renovated configurations. The columns "renovation_cost"
        and "heating_demand" should be present.
    n_years: int or list, optional
        Number of years to consider (default: 30).
    gas_price: float, optional
        Price of gas in €/kWh (default: 1.64€/m3, which is the average of 2022 and 2023
        in the Netherlands).
    inflation_rate: float, optional
        Annual inflation rate (default: 0.02). It is used to increase the gas price
        over the years.
    """
    coef = sum([(1 + inflation_rate) ** i for i in range(n_years)])
    total_operational_cost = operational_cost * coef
    TCO = renovation_cost + total_operational_cost
    return TCO


def get_payback_period(
    renovation_cost: np.ndarray,
    operational_cost: np.ndarray,
):
    mask = renovation_cost == 0
    N_scenarios = mask.sum()
    N_rp = renovation_cost.shape[0] / N_scenarios
    assert N_rp.is_integer()
    pre_renov_op_cost = np.tile(operational_cost[mask], int(N_rp))
    yearly_savings = pre_renov_op_cost - operational_cost
    payback_period = renovation_cost / (yearly_savings + 1e-3)
    # Assign np.inf to configurations with no savings (including no renovation)
    payback_period[yearly_savings <= 0] = 1000
    return payback_period


def get_CO2_reduction_per_euro(co2_emissions: np.ndarray, renovation_cost: np.ndarray):
    mask = renovation_cost == 0
    N_scenarios = mask.sum()
    N_rp = renovation_cost.shape[0] / N_scenarios
    assert N_rp.is_integer()
    pre_renov_co2_emissions = np.tile(co2_emissions[mask], int(N_rp))
    co2_reduction = co2_emissions - pre_renov_co2_emissions  # Lower is better
    co2_red_per_euro = co2_reduction / (renovation_cost + 1e-3)
    return co2_red_per_euro


def get_simulated_KPIs(sim_dir: str | Path) -> pd.DataFrame:
    sim_dir = Path(sim_dir)
    res = SimResultsReader(sim_dir)
    # Compute "primary" KPIs with SimResultsReader
    heating_demand = res.get_heating_demand("annual")
    gas_consumption = res.get_energy_consumption("gas", "hourly")
    elec_consumption = res.get_energy_consumption("electricity", "hourly")
    elec_OPP = res.get_energy_consumption("electricity", "OPP")
    overheating = res.get_overheating(
        input_var="operative_temp",
        th=26,
        delta_th=0,
        alpha=0,
        beta=1,
        zones=["0F", "1FN", "1FS"],
        zone_agg="SUM_H-MAX_Z",
        filter_occupied_hours=True,
    )
    co2_excess = res.get_CO2_excess_hours(
        zones=["0F", "1FN", "1FS"],
        zone_agg="any",
        filter_occupied_hours=True,
        threshold=1200,
    )
    avg_co2_exposure = res.get_avg_CO2_exposure()
    df_kpi = pd.DataFrame(
        {
            "Heating demand [kWh]": heating_demand,
            "Gas consumption [kWh]": gas_consumption.sum(),
            "Electricity consumption [kWh]": elec_consumption.sum(),
            "Electricity OPP [kW]": elec_OPP,
            "Overheating [h]": overheating,
            "CO2 excess [h]": co2_excess,
            "Average CO2 exposure [ppm]": [avg_co2_exposure],
        }
    )
    # Add secondary KPIs
    co2_emissions = get_CO2_emissions(elec_consumption.sum(), gas_consumption.sum())
    operational_cost = get_operational_cost(
        elec_consumption, gas_consumption, res.pv_surplus
    )
    df_kpi["CO2 emissions [kgCO2]"] = co2_emissions
    df_kpi["Operational cost [€]"] = operational_cost
    # Format dataframe
    new_cols = ["heating_system", "radiator_area", "N_pv"]
    df_kpi[new_cols] = df_kpi.index.str.split(",", expand=True).to_list()
    df_kpi.reset_index(drop=True, inplace=True)
    df_kpi["radiator_area"] = df_kpi["radiator_area"].astype(float)
    df_kpi["N_pv"] = df_kpi["N_pv"].str.replace(" PV", "").astype(int)
    return df_kpi


### Renovation cost functions


def get_insulation_cost(
    renovation_measures: dict,
    rm_costs: dict,
    pre_renov_config: dict,
    post_renov_configs: pd.DataFrame,
    **kwargs,
) -> np.ndarray:

    # Get general info
    floor_type = pre_renov_config["floor_type"].lower()
    if pre_renov_config["building_type"] == "terraced_house":
        vertices, surfaces = geometry.create_terraced_house(8)
    surface_areas = geometry.get_surface_areas(vertices, surfaces)
    internal_surfaces = geometry.find_matching_surfaces(surfaces)
    if pre_renov_config["building_position"] == "middle":
        shared_surfaces = ["WestWall", "EastWall"]
    else:
        shared_surfaces = ["WestWall"]

    # TODO: WE DONT ACCOUNT FOR WWR IN THE WALL AREA. TO FIX?
    # Loop over floor, roof, wall and compute renovation cost
    renov_cost = 0
    for surf_type in ["wall", "roof", "floor"]:
        # Get rm codes
        key = f"{surf_type}_insulation"
        if surf_type == "floor":
            rm_codes = renovation_measures[f"{floor_type}_{key}"].copy()
        else:
            rm_codes = renovation_measures[key].copy()
        # Remove thickness from keys and add None for existing state
        rm_codes = {key[:-1]: value for key, value in rm_codes.items()}
        rm_codes[tuple(pre_renov_config[key])] = None
        # Get renovation codes and then price per m2 for each RP
        L_ins = post_renov_configs[key].tolist()
        L_ins_codes = [rm_codes[tuple(x)] for x in L_ins]
        L_cost_per_m2 = [rm_costs[code] for code in L_ins_codes]
        # Multiply by outdoor wall area to get the total cost of wall insulation
        outdoor_wall_area = 0
        for surface, area in surface_areas.items():
            if (
                surf_type.capitalize() in surface
                and not any(s in surface for s in shared_surfaces)
                and surface not in internal_surfaces
            ):
                outdoor_wall_area += area
        renov_cost += np.array(L_cost_per_m2) * outdoor_wall_area
    # TODO: in case different insulations are used, renov_codes[i] should be a dict
    # mapping surfaces to codes
    return renov_cost


def get_glazing_cost(
    renovation_measures: dict,
    rm_costs: dict,
    pre_renov_config: dict,
    post_renov_configs: pd.DataFrame,
    **kwargs,
) -> np.ndarray:
    # Get general info
    if pre_renov_config["building_type"] == "terraced_house":
        vertices, surfaces = geometry.create_terraced_house(8)
        window_surfaces = [
            "SouthWall_0F",
            "SouthWall_1FS",
            "NorthWall_0F",
            "NorthWall_1FN",
        ]
    surface_areas = geometry.get_surface_areas(vertices, surfaces)
    WWR = pre_renov_config["WWR"]

    ### Compute glazing cost
    rm_codes = renovation_measures["glazing"].copy()
    # Add None for current state
    curr_glazing, curr_frame = tuple(pre_renov_config[("glazing", "window_frame")])
    rm_codes[(curr_glazing, curr_frame)] = (None, None)
    L_rm = post_renov_configs[["glazing", "window_frame"]].values.tolist()
    # Get codes (depending on whether we replace window frames or not)
    # TODO: this should apply depend on whether the frame is the same
    L_codes = []
    for new_glazing, new_frame in L_rm:
        if kwargs["replace_window_frames"] or new_frame != curr_frame:
            L_codes.append(rm_codes[(new_glazing, new_frame)][1])
        else:
            L_codes.append(rm_codes[(new_glazing, curr_frame)][0])
    # Get cost per m2
    L_cost_per_m2 = [rm_costs[code] for code in L_codes]
    # Compute total cost of glazing
    # TODO: modify this when different glazings are used on different surfaces
    window_area = sum([surface_areas[surf] * WWR for surf in window_surfaces])
    renov_cost = np.array(L_cost_per_m2) * window_area
    return renov_cost


def get_ventilation_system_cost(
    renovation_measures: dict,
    rm_costs: dict,
    pre_renov_config: dict,
    post_renov_configs: pd.DataFrame,
    **kwargs,
):
    rm_codes = renovation_measures["ventilation"].copy()
    # Add None for current state
    vent_type = pre_renov_config["vent_type"]
    rm_codes[(vent_type, vent_type)] = None
    L_rm = [
        (vent_type, new_vent_type) for new_vent_type in post_renov_configs["vent_type"]
    ]
    for k in range(len(L_rm)):
        # If the new ventilation type is not in rm_codes, set it to None
        if L_rm[k] not in rm_codes:
            L_rm[k] = (vent_type, vent_type)
    # Get codes and cost
    L_codes = [rm_codes[code] for code in L_rm]
    renov_cost = np.array([rm_costs[code] for code in L_codes])
    return renov_cost


def get_heating_system_cost(
    renovation_measures: dict,
    rm_costs: dict,
    pre_renov_config: dict,
    post_renov_configs: pd.DataFrame,
    **kwargs,
):
    rm_codes = renovation_measures["heating_system"].copy()
    rm_codes[pre_renov_config["heating_system"]] = None
    L_rm = post_renov_configs["heating_system"].tolist()
    L_codes = []
    curr_hs = pre_renov_config["heating_system"]
    for rm in L_rm:
        if rm == "HP 3kW Intergas + HR107 Parallel":
            # Use different code depending on pre-renovation state
            code = rm_codes["HP 3kW Intergas + HR107 Parallel"][curr_hs]
        else:
            code = rm_codes[rm]
        L_codes.append(code)
    renov_cost = np.array([rm_costs[code] for code in L_codes])
    return renov_cost


def get_radiator_cost(
    renovation_measures: dict,
    rm_costs: dict,
    pre_renov_config: dict,
    post_renov_configs: pd.DataFrame,
    **kwargs,
):
    # NOTE: cost of radiator = 542€/m2 + fixed cost of 188€
    # Assuming that we only add new radiators, not replace existing ones
    # areas = [0.9, 0.45, 0.25, 0.6, 0.5]
    # price = [364.9, 245.04, 191.8, 285, 258.36]
    # np.mean(np.array(price) / np.array(areas))
    rad_area = post_renov_configs["radiator_area"] - pre_renov_config["radiator_area"]
    renov_cost = 542 * rad_area + 188 * (rad_area > 0).astype(float)
    return renov_cost


def get_PV_cost(
    renovation_measures: dict,
    rm_costs: dict,
    pre_renov_config: dict,
    post_renov_configs: pd.DataFrame,
    **kwargs,
):
    # TODO: change this to account for the type of panel (mono/poly crystalline)
    pv_code = renovation_measures["PV"]
    cost_per_panel = rm_costs[pv_code] * 1.93  # €/m2 * 1.93 m2 per panel
    N_new_pv = np.clip(post_renov_configs["N_pv"] - pre_renov_config["N_pv"], 0, None)
    renov_cost = N_new_pv.values * cost_per_panel
    return renov_cost


def get_airtightness_cost(
    renovation_measures: dict,
    rm_costs: dict,
    pre_renov_config: dict,
    post_renov_configs: pd.DataFrame,
    **kwargs,
):
    rm_codes = renovation_measures["airtightness"].copy()
    # Add None for current state
    rm_codes[pre_renov_config["airtightness"]] = None
    L_rm = post_renov_configs["airtightness"].tolist()
    L_codes = [rm_codes[code] for code in L_rm]
    renov_cost = np.array([rm_costs[code] for code in L_codes])
    return renov_cost


def get_shading_cost(
    renovation_measures: dict,
    rm_costs: dict,
    pre_renov_config: dict,
    post_renov_configs: pd.DataFrame,
    **kwargs,
):
    # Get surface areas and WWR
    if pre_renov_config["building_type"] == "terraced_house":
        vertices, surfaces = geometry.create_terraced_house(8)
    WWR = pre_renov_config["WWR"]
    surface_areas = geometry.get_surface_areas(vertices, surfaces)
    # Get shaded area
    shading_configs = [tuple(x) for x in post_renov_configs["shaded_surfaces"]]
    shaded_area = {}
    for shading_config in set(shading_configs):
        res = 0
        for surf in shading_config:
            res += surface_areas[surf] * WWR
        shaded_area[shading_config] = res
    L_shaded_area = np.array([shaded_area[tuple(x)] for x in shading_configs])
    curr_shaded_area = shaded_area[tuple(pre_renov_config["shaded_surfaces"])]
    # Get cost per m2
    cost_per_m2 = rm_costs[renovation_measures["shading"]]
    renov_cost = cost_per_m2 * (L_shaded_area - curr_shaded_area)
    return renov_cost
