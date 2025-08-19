"""
File with predefined schedules for the simulation.
"""

occupancy = {
    "Worker": {"22-7": "1FS", "7-8": "0F", "17-22": "0F"},
    "RemoteWorker": {"22-7": "1FS", "7-8": "0F", "8-17": "1FN", "17-22": "0F"},
}
schedules = {
    # Common schedules
    "Always_50": {"0-24": 50},  # Used to disable cooling
    "On 24/7": {"0-24": 1},
    "Off 24/7": {"0-24": 0},
    ### Heating setpoints
    # Schedules for heated zones
    "Always_21": {"0-24": 21},
    "N17_D19": {"23-9": 17.5, "9-23": 19.5},
    "N15_D19": {"23-9": 15, "9-23": 19.5},
    "N17_D20": {"23-9": 17, "9-23": 20.5},
    "N15_M17_D16_E19": {"23-6": 15.5, "6-9": 17.5, "9-18": 16.5, "18-24": 19.5},
    # Schedules for unheated zones (should be consistent with the schedule
    # used for heated zones)
    "Always_17": {"0-24": 17},  # "Always_21"/"N17_D20"
    "Always_17.5": {"0-24": 17.5},  # "N17_D19"
    "Always_15": {"0-24": 15},  # "N15_D19"
    "Always_15.5": {"0-24": 15.5},  # "N15_M17_D16_E19"
    "Always_10": {"0-24": 10},  # Used for the attic only
}


def get_heating_patterns():
    L_heated_zones = [
        ("0F",),
        ("0F", "1FS"),
        ("0F", "1FS", "1FN"),
        ("0F", "1FS", "2F"),
        ("0F", "1FS", "1FN", "2F"),
    ]
    L_sched_heated = ["Always_21", "N17_D19", "N15_D19", "N17_D20", "N15_M17_D16_E19"]
    sched_unheated = {
        "Always_21": "Always_17",
        "N17_D20": "Always_17",
        "N17_D19": "Always_17.5",
        "N15_D19": "Always_15",
        "N15_M17_D16_E19": "Always_15.5",
    }
    zones = ["0F", "1FS", "1FN", "2F"]
    # Create a dictionary with the keys as tuples of heated zones and schedules
    patterns = []
    for heated_zones in L_heated_zones:
        for sched_heated in L_sched_heated:
            sched_per_zone = {}
            for zone in zones:
                if zone in heated_zones:
                    sched_per_zone[zone] = sched_heated
                elif zone == "2F":
                    sched_per_zone[zone] = "Always_10"
                else:
                    sched_per_zone[zone] = sched_unheated[sched_heated]
            patterns.append(sched_per_zone)
    return patterns


patterns = get_heating_patterns()
