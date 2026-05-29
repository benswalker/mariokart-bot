TRACKS = {
    # Mushroom Cup
    "mario_kart_stadium":       "mushroom_cup",
    "water_park":               "mushroom_cup",
    "sweet_sweet_canyon":       "mushroom_cup",
    "thwomp_ruins":             "mushroom_cup",
    # Flower Cup
    "mario_circuit":            "flower_cup",
    "toad_harbor":              "flower_cup",
    "twisted_mansion":          "flower_cup",
    "shy_guy_falls":            "flower_cup",
    # Star Cup
    "sunshine_airport":         "star_cup",
    "dolphin_shoals":           "star_cup",
    "electrodrome":             "star_cup",
    "mount_wario":              "star_cup",
    # Special Cup
    "cloudtop_cruise":          "special_cup",
    "bonk_blue_ruins":          "special_cup",
    "big_blue":                 "special_cup",
    "rainbow_road":             "special_cup",
    # Shell Cup (retro)
    "moo_moo_meadows":          "shell_cup",
    "mario_circuit_gba":        "shell_cup",
    "cheep_cheep_beach":        "shell_cup",
    "toad_circuit":             "shell_cup",
    # Banana Cup (retro)
    "dry_dry_desert":           "banana_cup",
    "donut_plains_3":           "banana_cup",
    "royal_raceway":            "banana_cup",
    "dk_jungle":                "banana_cup",
    # Leaf Cup (retro)
    "wario_stadium":            "leaf_cup",
    "sherbet_land":             "leaf_cup",
    "music_park":               "leaf_cup",
    "yoshi_valley":             "leaf_cup",
    # Lightning Cup (retro)
    "tick_tock_clock":          "lightning_cup",
    "piranha_plant_slide":      "lightning_cup",
    "grumble_volcano":          "lightning_cup",
    "rainbow_road_n64":         "lightning_cup",
    # Booster Course Pass Wave 1
    "paris_promenade":          "booster_course_1",
    "toad_circuit_bc":          "booster_course_1",
    "choco_mountain":           "booster_course_1",
    "coconut_mall":             "booster_course_1",
    "tokyo_blur":               "booster_course_1",
    "shroom_ridge":             "booster_course_1",
    "sky_garden":               "booster_course_1",
    "ninja_hideaway":           "booster_course_1",
    # Booster Course Pass Wave 2
    "new_york_minute":          "booster_course_2",
    "mario_circuit_snes":       "booster_course_2",
    "kalimari_desert":          "booster_course_2",
    "waluigi_pinball":          "booster_course_2",
    "sydney_sprint":            "booster_course_2",
    "snow_land":                "booster_course_2",
    "mushroom_gorge":           "booster_course_2",
    "sky_high_sundae":          "booster_course_2",
    # Booster Course Pass Wave 3
    "london_loop":              "booster_course_3",
    "boo_lake":                 "booster_course_3",
    "rock_rock_mountain":       "booster_course_3",
    "maple_treeway":            "booster_course_3",
    "berlin_byways":            "booster_course_3",
    "peach_gardens":            "booster_course_3",
    "merry_mountain":           "booster_course_3",
    "rainbow_road_3ds":         "booster_course_3",
    # Booster Course Pass Wave 4
    "amsterdam_drift":          "booster_course_4",
    "riverside_park":           "booster_course_4",
    "dks_snowboard_cross":      "booster_course_4",
    "yoshis_island":            "booster_course_4",
    "bangkok_rush":             "booster_course_4",
    "mario_circuit_ds":         "booster_course_4",
    "waluigi_stadium":          "booster_course_4",
    "singapore_speedway":       "booster_course_4",
    # Booster Course Pass Wave 5
    "athens_dash":              "booster_course_5",
    "daisy_cruiser":            "booster_course_5",
    "moonview_highway":         "booster_course_5",
    "squeaky_clean_sprint":     "booster_course_5",
    "los_angeles_laps":         "booster_course_5",
    "sunset_wilds":             "booster_course_5",
    "koopa_cape":               "booster_course_5",
    "vancouver_velocity":       "booster_course_5",
    # Booster Course Pass Wave 6
    "rome_avanti":              "booster_course_6",
    "dks_mountain":             "booster_course_6",
    "daisy_circuit":            "booster_course_6",
    "piranha_plant_cove":       "booster_course_6",
    "madrid_drive":             "booster_course_6",
    "rosalinas_ice_world":      "booster_course_6",
    "bowser_castle_3":          "booster_course_6",
    "rainbow_road_wii":         "booster_course_6",
}

def get_track_path(track_name: str) -> str:
    """Returns the CSV path for a given track name."""
    key = track_name.lower().replace(" ", "_").replace("-", "_")
    if key not in TRACKS:
        raise ValueError(f"Unknown track: '{track_name}'. Check tracks.py for valid names.")
    cup = TRACKS[key]
    return f"tracks/{cup}/{key}.csv"

def list_tracks() -> None:
    for track, cup in sorted(TRACKS.items(), key=lambda x: x[1]):
        print(f"  {cup:<25} {track}")
