from ast import literal_eval
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from renovexpy.off_the_fly import query_surrogate_models
from renovexpy.optimization import find_optimal_packages, pareto_optimization
from renovexpy.renovation import get_rm_options

pd.set_option("display.max_columns", None)


def clean_df_opt(df_opt):
    for surf_type in ["wall", "roof", "floor"]:
        cols = [f"{surf_type}_insulation_{k}" for k in range(3)]
        cols_exist = [col for col in cols if col in df_opt.columns]
        if cols_exist:
            df_opt[surf_type + "_insulation"] = df_opt[cols_exist].apply(
                lambda row: str(list(row.dropna())), axis=1
            )
            df_opt = df_opt.drop(columns=cols_exist)
    return df_opt


# Value and parameter labels for user-friendly display
value_labels = {
    "S": "South",
    "W": "West",
    "VR": "Standard gas boiler",
    "HR107": "High-efficiency gas boiler",
    "HP 5kW": "Heat pump 5kW",
    "HP 7kW": "Heat pump 7kW",
    "HP 10kW": "Heat pump 10kW",
    "HP 3kW Intergas + HR107 Parallel": "Hybrid heat pump 5kW",
    "[]": "None",
    "['SouthWall_0F', 'SouthWall_1FS']": "South facade",
    "['SouthWall_0F', 'SouthWall_1FS', 'NorthWall_0F', 'NorthWall_1FN']": "South + North facades",
    # PV panels
    "11": "11 (Half of roof)",
    "22": "22 (Whole roof)",
    # Insulation materials
    "Rockwool": "Mineral wool",
    "Icynene": "Polyurethane foam",
    "['Mineral wool', 'External', 0]": "No insulation",
    "['Rockwool', 'External', 0]": "No insulation ",
}
param_labels = {
    "building_position": "Building position",
    "building_orientation": "Building orientation",
    "floor_type": "Floor type",
    "WWR": "Window-to-wall ratio",
    "floor_insulation": "Floor insulation [material, position, R-value]",
    "roof_insulation": "Roof insulation [material, position, R-value]",
    "wall_insulation": "Wall insulation [material, position, R-value]",
    ("glazing", "window_frame"): "Glazing and window frame",
    "heating_system": "Heating system",
    "vent_type": "Ventilation system",
    "N_pv": "Number of PV panels",
    "airtightness": "Airtightness",
    "shaded_surfaces": "Shading",
    "radiator_area": "Radiator area [m²]",
}

pre_renov_options = {
    "building_position": ["middle", "corner"],
    "building_orientation": ["S", "W"],
    "floor_type": ["Wood", "Concrete"],
    "WWR": (0.2, 0.8),
}
pre_renov_options.update(get_rm_options())

pre_renov_menu = {
    "📐 Geometry": ["building_position", "building_orientation"],
    "🧱 Constructions": [
        "floor_type",
        "floor_insulation",
        "roof_insulation",
        "wall_insulation",
    ],
    "🪟 Windows": ["WWR", ("glazing", "window_frame"), "shaded_surfaces"],
    "🌡️ Energy and heating": ["heating_system", "radiator_area", "N_pv"],
    "💨 Ventilation": ["vent_type", "airtightness"],
}
categories_in_col1 = ["📐 Geometry", "🌡️ Energy and heating", "💨 Ventilation"]

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

kpis = [
    # Energy
    "Heating demand [kWh]",
    "Electricity OPP [kW]",
    # Cost
    "Renovation cost [€]",
    "TCO over 30 years [€]",
    "Payback period [year]",
    # CO2
    "CO2 emissions [kgCO2]",
    "CO2 reduction per euro [kgCO2/€]",
    # Comfort
    "Overheating [h]",
    "CO2 excess [h]",
]

# Init session state
if "pre_renov_config" not in st.session_state:
    st.session_state.pre_renov_config = {
        "building_type": "terraced_house",
        "occupant_activity_level": "mid",
        "lighting_power_per_area": 1,
        "equipment_power_per_area": 1,
        "shading_position": "External",
    }

# --- Streamlit App ---

st.set_page_config(layout="wide", page_title="Renovation Explorer")


st.title("Renovation Explorer: Demo off-the-fly model")
st.markdown("---")

# Inputs section
st.header("🏠 1. Specify current house state")
col1, col2 = st.columns(2)
for category, L_param in pre_renov_menu.items():
    col = col1 if category in categories_in_col1 else col2
    with col:
        st.subheader(category)
        for param in L_param:
            if param == "floor_insulation":
                floor_type = st.session_state.pre_renov_config.get(
                    "floor_type", "wood"
                ).lower()
                options = pre_renov_options[f"{floor_type}_{param}"]
            else:
                options = pre_renov_options[param]
            if isinstance(options, list):
                st.session_state.pre_renov_config[param] = st.selectbox(
                    param_labels[param], options
                )
            elif isinstance(options, tuple):
                st.session_state.pre_renov_config[param] = st.slider(
                    param_labels[param],
                    min_value=options[0],
                    max_value=options[1],
                    value=(options[0] + options[1]) / 2,
                    step=0.01,
                )
st.markdown("---")


# Simulation section
with col1:
    st.header("⚙️ 2. Simulate renovation packages")
    with st.form("simulation_form"):
        # Menu for simulation parameters
        n_scenarios = st.number_input(
            "Number of scenarios (for unknown parameters)",
            min_value=1,
            value=8,
            help="Number of random scenarios to generate for unknown parameters.",
        )
        replace_window_frames = st.checkbox(
            "Replace window frames?",
            value=False,
            help="If checked, frames will be changed alongside glazing, which significantly increases cost.",
        )
        max_rm_per_package = st.number_input(
            "Maximum number of renovation measures per package",
            min_value=1,
            value=5,
            help="The maximum number of renovation measures to combine in a single package.",
        )

        # Button to run the simulation
        run_simulation_button = st.form_submit_button("Run Simulation")

    if run_simulation_button:
        with st.spinner("Running simulations... This may take a few minutes."):
            st.session_state.unknown_params = unknown_params
            try:
                st.session_state.df = query_surrogate_models(
                    st.session_state.pre_renov_config,
                    unknown_params,
                    N_scenarios=n_scenarios,
                    replace_window_frames=replace_window_frames,
                    max_rm_per_package=max_rm_per_package,
                )
                st.success("Simulation complete!")
            except Exception as e:
                st.error(f"An error occurred during simulation: {e}")

# Optimization section
with col2:
    st.header("🔍 3. Find optimal renovation packages")
    with st.form("optimization_form"):
        # Multiple checkbox to select KPIs for optimization
        kpi_to_optimize = st.multiselect(
            "Select KPIs to optimize",
            options=kpis,
            default=[],
            help="Select the indicators (KPIs) to optimize. for the renovation packages. If several KPIs are selected, the.",
        )
        requirements = {}
        for kpi in ["Renovation cost [€]", "Overheating [h]", "CO2 excess [h]"]:
            if val := st.text_input(f"Maximum allowed {kpi}"):
                requirements[kpi] = int(val)

        robustness_indicator = st.selectbox(
            "Select robustness indicator", options=["mean", "max_regret"]
        )
        n_top = st.number_input(
            "Number of top packages to return", min_value=1, value=10
        )
        # Button to run the optimization
        run_optimization_button = st.form_submit_button("Run Optimization")

        if run_optimization_button:
            with st.spinner("Finding optimal packages..."):
                try:
                    st.session_state.df_opt = find_optimal_packages(
                        st.session_state.df,
                        unknown_params=list(unknown_params.keys()),
                        kpis=kpi_to_optimize,
                        requirements=requirements,
                        robustness_indicator=robustness_indicator,
                        N_top=n_top,
                    )
                    st.success("Optimization complete!")
                except Exception as e:
                    st.error(f"An error occurred during optimization: {e}")

# Display results section
st.header("📊 4. Results")
# Display the DataFrame
if "df_opt" in st.session_state:
    st.dataframe(st.session_state.df_opt)
