from __future__ import annotations
from typing import Dict, List, Tuple, Optional
import math, re
from typing import Any


class StroomerPredictor:
    """
    Cari JUMLAH unit per perangkat (0..max_count) agar prediksi P, I, PF
    mendekati pembacaan meter. Perangkat punya watt/unit & PF tipikal dari
    catalog bawaan; kamu cukup memberi jumlah maksimal unit yg tersedia.

    API:
      - electronic_list(): lihat catalog bawaan (watt/PF tipikal)
      - configure_catalog({...}): override sebagian nilai default (opsional)
      - set_appliances({name: max_count, ...}): set jumlah maksimal per perangkat
      - predict(voltage=V, current=I, power_factor=PF, power=P): hasilkan counts
    """

    # -------- catalog bawaan (bisa dioverride) --------
    # --- REPLACE these in stroomer/appliance.py ---

    _DEFAULT_CATALOG = {
        # ---------- LIGHTING ----------
        "lampu": {
            "watt": 10,
            "pf": 1,
            "type": "led",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.0,
        },
        "lampu_led_5w": {
            "watt": 5,
            "pf": 1,
            "type": "led",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.0,
        },
        "lampu_led_7w": {
            "watt": 7,
            "pf": 1,
            "type": "led",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.0,
        },
        "lampu_led_9w": {
            "watt": 9,
            "pf": 0.60,
            "type": "led",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.0,
        },
        "lampu_12w": {
            "watt": 12,
            "pf": 1,
            "type": "led",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.0,
        },
        "lampu_18w": {
            "watt": 18,
            "pf": 1,
            "type": "led",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.0,
        },
        "lampu_32w": {
            "watt": 32,
            "pf": 1,
            "type": "led",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.0,
        },
        "downlight_led_12w": {
            "watt": 12,
            "pf": 1,
            "type": "led",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.0,
        },
        "spotlight_led_50w": {
            "watt": 50,
            "pf": 1,
            "type": "led",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.1,
        },
        "lampu_cfl_15w": {
            "watt": 15,
            "pf": 1,
            "type": "smps",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.1,
        },
        "lampu_cfl_23w": {
            "watt": 23,
            "pf": 1,
            "type": "smps",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.1,
        },
        "lampu_tl_18w": {
            "watt": 18,
            "pf": 1,
            "type": "inductive",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.2,
        },
        "lampu_tl_36w": {
            "watt": 36,
            "pf": 1,
            "type": "inductive",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.2,
        },
        "lampu_halogen_20w": {
            "watt": 20,
            "pf": 1,
            "type": "resistive",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.0,
        },
        "lampu_halogen_50w": {
            "watt": 50,
            "pf": 1,
            "type": "resistive",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.0,
        },
        "lampu_meja": {
            "watt": 8,
            "pf": 1,
            "type": "led",
            "phase": 1,
            "standby_w": 0.2,
            "surge_mult": 1.0,
        },
        "lampu_taman": {
            "watt": 5,
            "pf": 1,
            "type": "led",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.0,
        },
        # ---------- FANS / AIR ----------
        "kipas_meja": {
            "watt": 35,
            "pf": 0.70,
            "type": "motor",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.6,
        },
        "kipas_berdiri": {
            "watt": 60,
            "pf": 0.70,
            "type": "motor",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.8,
        },
        "kipas_langit": {
            "watt": 75,
            "pf": 0.75,
            "type": "motor",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 2.0,
        },
        "air_cooler": {
            "watt": 80,
            "pf": 0.60,
            "type": "smps",
            "phase": 1,
            "standby_w": 1,
            "surge_mult": 1.1,
        },
        "air_purifier_small": {
            "watt": 30,
            "pf": 0.60,
            "type": "smps",
            "phase": 1,
            "standby_w": 1,
            "surge_mult": 1.1,
        },
        "air_purifier_medium": {
            "watt": 50,
            "pf": 0.60,
            "type": "smps",
            "phase": 1,
            "standby_w": 1,
            "surge_mult": 1.1,
        },
        "humidifier": {
            "watt": 20,
            "pf": 0.60,
            "type": "smps",
            "phase": 1,
            "standby_w": 1,
            "surge_mult": 1.0,
        },
        "dehumidifier": {
            "watt": 250,
            "pf": 0.85,
            "type": "motor",
            "phase": 1,
            "standby_w": 2,
            "surge_mult": 2.0,
        },
        "exhaust_fan": {
            "watt": 25,
            "pf": 0.75,
            "type": "motor",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.6,
        },
        # ---------- AC / HEATING ----------
        "ac_0_5pk": {
            "watt": 450,
            "pf": 0.95,
            "type": "motor",
            "phase": 1,
            "standby_w": 3,
            "surge_mult": 3.0,
        },
        "ac_1pk": {
            "watt": 900,
            "pf": 0.95,
            "type": "motor",
            "phase": 1,
            "standby_w": 3,
            "surge_mult": 3.0,
        },
        "ac_1_5pk": {
            "watt": 1300,
            "pf": 0.95,
            "type": "motor",
            "phase": 1,
            "standby_w": 3,
            "surge_mult": 3.5,
        },
        "heater_fan_1000w": {
            "watt": 1000,
            "pf": 1.00,
            "type": "resistive",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.0,
        },
        "heater_oil_1200w": {
            "watt": 1200,
            "pf": 1.00,
            "type": "resistive",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.0,
        },
        "water_heater_storage": {
            "watt": 1200,
            "pf": 1.00,
            "type": "resistive",
            "phase": 1,
            "standby_w": 2,
            "surge_mult": 1.0,
        },
        "water_heater_instant": {
            "watt": 3500,
            "pf": 0.98,
            "type": "resistive",
            "phase": 1,
            "standby_w": 2,
            "surge_mult": 1.0,
        },
        # ---------- KITCHEN ----------
        "kulkas_1_pintu": {
            "watt": 120,
            "pf": 0.75,
            "type": "motor",
            "phase": 1,
            "standby_w": 3,
            "surge_mult": 3.0,
        },
        "kulkas_2_pintu": {
            "watt": 180,
            "pf": 0.75,
            "type": "motor",
            "phase": 1,
            "standby_w": 3,
            "surge_mult": 3.0,
        },
        "freezer": {
            "watt": 200,
            "pf": 0.80,
            "type": "motor",
            "phase": 1,
            "standby_w": 3,
            "surge_mult": 3.0,
        },
        "dispenser_hot": {
            "watt": 500,
            "pf": 1.00,
            "type": "resistive",
            "phase": 1,
            "standby_w": 2,
            "surge_mult": 1.0,
        },
        "dispenser_cool": {
            "watt": 100,
            "pf": 0.75,
            "type": "motor",
            "phase": 1,
            "standby_w": 2,
            "surge_mult": 2.0,
        },
        "rice_cooker_cook": {
            "watt": 500,
            "pf": 1.00,
            "type": "resistive",
            "phase": 1,
            "standby_w": 1,
            "surge_mult": 1.0,
        },
        "rice_cooker_warm": {
            "watt": 50,
            "pf": 1.00,
            "type": "resistive",
            "phase": 1,
            "standby_w": 1,
            "surge_mult": 1.0,
        },
        "microwave_700w": {
            "watt": 700,
            "pf": 0.95,
            "type": "smps",
            "phase": 1,
            "standby_w": 2,
            "surge_mult": 1.2,
        },
        "microwave_1000w": {
            "watt": 1000,
            "pf": 0.98,
            "type": "smps",
            "phase": 1,
            "standby_w": 2,
            "surge_mult": 1.2,
        },
        "oven_listrik_1200w": {
            "watt": 1200,
            "pf": 1.00,
            "type": "resistive",
            "phase": 1,
            "standby_w": 1,
            "surge_mult": 1.0,
        },
        "air_fryer_1400w": {
            "watt": 1400,
            "pf": 1.00,
            "type": "resistive",
            "phase": 1,
            "standby_w": 1,
            "surge_mult": 1.0,
        },
        "kompor_induksi_800w": {
            "watt": 800,
            "pf": 0.99,
            "type": "smps",
            "phase": 1,
            "standby_w": 1,
            "surge_mult": 1.0,
        },
        "kompor_induksi_1200w": {
            "watt": 1200,
            "pf": 0.99,
            "type": "smps",
            "phase": 1,
            "standby_w": 1,
            "surge_mult": 1.0,
        },
        "kompor_induksi_2000w": {
            "watt": 2000,
            "pf": 0.99,
            "type": "smps",
            "phase": 1,
            "standby_w": 1,
            "surge_mult": 1.0,
        },
        "kettle_1500w": {
            "watt": 1500,
            "pf": 1.00,
            "type": "resistive",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.0,
        },
        "blender": {
            "watt": 300,
            "pf": 0.70,
            "type": "motor",
            "phase": 1,
            "standby_w": 1,
            "surge_mult": 2.0,
        },
        "juicer": {
            "watt": 400,
            "pf": 0.70,
            "type": "motor",
            "phase": 1,
            "standby_w": 1,
            "surge_mult": 2.0,
        },
        "mixer": {
            "watt": 250,
            "pf": 0.70,
            "type": "motor",
            "phase": 1,
            "standby_w": 1,
            "surge_mult": 1.8,
        },
        "food_processor": {
            "watt": 600,
            "pf": 0.75,
            "type": "motor",
            "phase": 1,
            "standby_w": 1,
            "surge_mult": 2.0,
        },
        "coffee_maker_drip": {
            "watt": 900,
            "pf": 1.00,
            "type": "resistive",
            "phase": 1,
            "standby_w": 1,
            "surge_mult": 1.0,
        },
        "espresso_machine": {
            "watt": 1500,
            "pf": 0.95,
            "type": "smps",
            "phase": 1,
            "standby_w": 3,
            "surge_mult": 1.5,
        },
        "toaster_800w": {
            "watt": 800,
            "pf": 1.00,
            "type": "resistive",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.0,
        },
        # ---------- LAUNDRY / CLEANING ----------
        "mesin_cuci_topload": {
            "watt": 400,
            "pf": 0.80,
            "type": "motor",
            "phase": 1,
            "standby_w": 2,
            "surge_mult": 2.5,
        },
        "mesin_cuci_frontload": {
            "watt": 800,
            "pf": 0.90,
            "type": "motor",
            "phase": 1,
            "standby_w": 2,
            "surge_mult": 3.0,
        },
        "pengering_pakaian": {
            "watt": 2000,
            "pf": 1.00,
            "type": "resistive",
            "phase": 1,
            "standby_w": 2,
            "surge_mult": 1.0,
        },
        "setrika_350w": {
            "watt": 350,
            "pf": 1.00,
            "type": "resistive",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.0,
        },
        "setrika_600w": {
            "watt": 600,
            "pf": 1.00,
            "type": "resistive",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.0,
        },
        "setrika_1000w": {
            "watt": 1000,
            "pf": 1.00,
            "type": "resistive",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.0,
        },
        "vacuum_stick": {
            "watt": 400,
            "pf": 0.90,
            "type": "motor",
            "phase": 1,
            "standby_w": 2,
            "surge_mult": 2.5,
        },
        "vacuum_canister": {
            "watt": 1200,
            "pf": 0.95,
            "type": "motor",
            "phase": 1,
            "standby_w": 2,
            "surge_mult": 3.0,
        },
        "robot_vacuum": {
            "watt": 50,
            "pf": 0.60,
            "type": "smps",
            "phase": 1,
            "standby_w": 3,
            "surge_mult": 1.0,
        },
        "steam_mop": {
            "watt": 1200,
            "pf": 1.00,
            "type": "resistive",
            "phase": 1,
            "standby_w": 1,
            "surge_mult": 1.0,
        },
        # ---------- WATER / PUMPS ----------
        "pompa_air_kecil": {
            "watt": 125,
            "pf": 0.70,
            "type": "motor",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 3.0,
        },
        "pompa_air_sedang": {
            "watt": 250,
            "pf": 0.75,
            "type": "motor",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 3.0,
        },
        "pompa_air_besar": {
            "watt": 750,
            "pf": 0.85,
            "type": "motor",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 3.5,
        },
        "pompa_kolam": {
            "watt": 60,
            "pf": 0.70,
            "type": "motor",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 2.0,
        },
        "aerator_akuarium": {
            "watt": 8,
            "pf": 0.60,
            "type": "motor",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.5,
        },
        # ---------- IT / ENTERTAINMENT ----------
        "tv_32": {
            "watt": 45,
            "pf": 0.90,
            "type": "smps",
            "phase": 1,
            "standby_w": 1,
            "surge_mult": 1.0,
        },
        "tv_43": {
            "watt": 75,
            "pf": 0.90,
            "type": "smps",
            "phase": 1,
            "standby_w": 1,
            "surge_mult": 1.0,
        },
        "tv_55": {
            "watt": 120,
            "pf": 0.90,
            "type": "smps",
            "phase": 1,
            "standby_w": 1,
            "surge_mult": 1.0,
        },
        "set_top_box": {
            "watt": 10,
            "pf": 0.60,
            "type": "smps",
            "phase": 1,
            "standby_w": 3,
            "surge_mult": 1.0,
        },
        "soundbar": {
            "watt": 30,
            "pf": 0.80,
            "type": "smps",
            "phase": 1,
            "standby_w": 2,
            "surge_mult": 1.0,
        },
        "home_theater": {
            "watt": 150,
            "pf": 0.90,
            "type": "smps",
            "phase": 1,
            "standby_w": 5,
            "surge_mult": 1.2,
        },
        "router": {
            "watt": 10,
            "pf": 0.60,
            "type": "smps",
            "phase": 1,
            "standby_w": 5,
            "surge_mult": 1.0,
        },
        "modem": {
            "watt": 8,
            "pf": 0.60,
            "type": "smps",
            "phase": 1,
            "standby_w": 3,
            "surge_mult": 1.0,
        },
        "switch_8port": {
            "watt": 12,
            "pf": 0.60,
            "type": "smps",
            "phase": 1,
            "standby_w": 3,
            "surge_mult": 1.0,
        },
        "nas_2bay": {
            "watt": 25,
            "pf": 0.95,
            "type": "smps",
            "phase": 1,
            "standby_w": 8,
            "surge_mult": 1.0,
        },
        "pc_entry": {
            "watt": 150,
            "pf": 0.95,
            "type": "smps",
            "phase": 1,
            "standby_w": 10,
            "surge_mult": 1.2,
        },
        "pc_gaming": {
            "watt": 350,
            "pf": 0.95,
            "type": "smps",
            "phase": 1,
            "standby_w": 15,
            "surge_mult": 1.2,
        },
        "monitor_24": {
            "watt": 25,
            "pf": 0.90,
            "type": "smps",
            "phase": 1,
            "standby_w": 1,
            "surge_mult": 1.0,
        },
        "monitor_27": {
            "watt": 35,
            "pf": 0.90,
            "type": "smps",
            "phase": 1,
            "standby_w": 1,
            "surge_mult": 1.0,
        },
        "printer_inkjet": {
            "watt": 20,
            "pf": 0.60,
            "type": "smps",
            "phase": 1,
            "standby_w": 3,
            "surge_mult": 1.0,
        },
        "printer_laser_active": {
            "watt": 500,
            "pf": 0.95,
            "type": "smps",
            "phase": 1,
            "standby_w": 10,
            "surge_mult": 2.0,
        },
        "printer_laser_idle": {
            "watt": 10,
            "pf": 0.60,
            "type": "smps",
            "phase": 1,
            "standby_w": 10,
            "surge_mult": 1.0,
        },
        "game_console": {
            "watt": 180,
            "pf": 0.95,
            "type": "smps",
            "phase": 1,
            "standby_w": 5,
            "surge_mult": 1.1,
        },
        "cctv_nvr": {
            "watt": 15,
            "pf": 0.60,
            "type": "smps",
            "phase": 1,
            "standby_w": 5,
            "surge_mult": 1.0,
        },
        "cctv_camera": {
            "watt": 5,
            "pf": 0.60,
            "type": "smps",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.0,
        },
        # ---------- CHARGERS ----------
        "phone_charger_5w": {
            "watt": 5,
            "pf": 0.50,
            "type": "smps",
            "phase": 1,
            "standby_w": 0.2,
            "surge_mult": 1.0,
        },
        "phone_charger_25w": {
            "watt": 25,
            "pf": 0.55,
            "type": "smps",
            "phase": 1,
            "standby_w": 0.5,
            "surge_mult": 1.0,
        },
        "laptop_charger_45w": {
            "watt": 45,
            "pf": 0.60,
            "type": "smps",
            "phase": 1,
            "standby_w": 0.5,
            "surge_mult": 1.0,
        },
        "laptop_charger_65w": {
            "watt": 65,
            "pf": 0.60,
            "type": "smps",
            "phase": 1,
            "standby_w": 0.5,
            "surge_mult": 1.0,
        },
        "laptop_charger_90w": {
            "watt": 90,
            "pf": 0.95,
            "type": "smps",
            "phase": 1,
            "standby_w": 0.5,
            "surge_mult": 1.0,
        },
        "gan_charger_65w": {
            "watt": 65,
            "pf": 0.95,
            "type": "smps",
            "phase": 1,
            "standby_w": 0.5,
            "surge_mult": 1.0,
        },
        "ebike_charger": {
            "watt": 250,
            "pf": 0.95,
            "type": "smps",
            "phase": 1,
            "standby_w": 1,
            "surge_mult": 1.1,
        },
        "emotor_charger": {
            "watt": 500,
            "pf": 0.98,
            "type": "smps",
            "phase": 1,
            "standby_w": 1,
            "surge_mult": 1.1,
        },
        # ---------- EV AC CHARGERS ----------
        "ev_charger_1p_6a": {
            "watt": 1320,
            "pf": 1,
            "type": "smps",
            "phase": 1,
            "standby_w": 4,
            "surge_mult": 1.0,
        },
        "ev_charger_1p_10a": {
            "watt": 2200,
            "pf": 1,
            "type": "smps",
            "phase": 1,
            "standby_w": 4,
            "surge_mult": 1.0,
        },
        "ev_charger_1p_16a": {
            "watt": 3520,
            "pf": 1,
            "type": "smps",
            "phase": 1,
            "standby_w": 4,
            "surge_mult": 1.0,
        },
        "ev_charger_3p_11kw": {
            "watt": 11000,
            "pf": 1,
            "type": "smps",
            "phase": 3,
            "standby_w": 8,
            "surge_mult": 1.0,
        },
        "ev_charger_3p_22kw": {
            "watt": 22000,
            "pf": 1,
            "type": "smps",
            "phase": 3,
            "standby_w": 8,
            "surge_mult": 1.0,
        },
        # ---------- PERSONAL CARE ----------
        "hair_dryer_1000w": {
            "watt": 1000,
            "pf": 1.00,
            "type": "resistive",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.0,
        },
        "hair_dryer_1800w": {
            "watt": 1800,
            "pf": 1.00,
            "type": "resistive",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.0,
        },
        "catokan": {
            "watt": 50,
            "pf": 1.00,
            "type": "resistive",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.0,
        },
        "shaver": {
            "watt": 10,
            "pf": 0.60,
            "type": "smps",
            "phase": 1,
            "standby_w": 1,
            "surge_mult": 1.0,
        },
        # ---------- POWER TOOLS ----------
        "bor_listrik": {
            "watt": 500,
            "pf": 0.90,
            "type": "motor",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 2.5,
        },
        "gerinda": {
            "watt": 700,
            "pf": 0.90,
            "type": "motor",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 2.5,
        },
        "circular_saw": {
            "watt": 1200,
            "pf": 0.90,
            "type": "motor",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 3.0,
        },
        "kompresor_angin": {
            "watt": 1000,
            "pf": 0.85,
            "type": "motor",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 3.0,
        },
        "solder_uap": {
            "watt": 700,
            "pf": 1.00,
            "type": "resistive",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.0,
        },
        "glue_gun": {
            "watt": 40,
            "pf": 1.00,
            "type": "resistive",
            "phase": 1,
            "standby_w": 0,
            "surge_mult": 1.0,
        },
    }

    # banyak sinonim umum (ID/EN) dan typo populer → key katalog
    _ALIASES = {
        # umum
        "tv": "tv_43",
        "televisi": "tv_43",
        "kulkas": "kulkas_2_pintu",
        "fridge": "kulkas_2_pintu",
        "refrigerator": "kulkas_2_pintu",
        "ac": "ac_1pk",
        "air_conditioner": "ac_1pk",
        "ac_split": "ac_1pk",
        "lamp": "lampu",
        "bulb": "lampu",
        "set_top_box": "set_top_box",
        "router_wifi": "router",
        "wifi_router": "router",
        "evse": "ev_charger_1p_10a",
        "charger_ev": "ev_charger_1p_10a",
        "chrger_motor": "emotor_charger",
        "charger_motor": "emotor_charger",
        "rice_cooker": "rice_cooker_cook",
        "magic_jar": "rice_cooker_warm",
        "vacuum": "vacuum_canister",
        "vacuum_cleaner": "vacuum_canister",
        "water_heater": "water_heater_storage",
        "microwave": "microwave_1000w",
        "oven": "oven_listrik_1200w",
        "kompor_induksi": "kompor_induksi_1200w",
        "pompa_air": "pompa_air_sedang",
        # lampu varian generic
        "lampu_18w": "lampu_18w",
        "lampu_32w": "lampu_32w",
        "lampu_led": "lampu",
        "downlight": "downlight_led_12w",
        "spotlight": "spotlight_led_50w",
        # fans
        "kipas": "kipas_berdiri",
        "ceiling_fan": "kipas_langit",
        "desk_fan": "kipas_meja",
    }

    _LAMPU_W_RE = re.compile(r"(?i)lampu[_\-\s]*([0-9]{1,3})\s*w")

    def __init__(self):
        # catalog efektif (deep copy dari default kaya atribut)
        self._catalog: Dict[str, Dict[str, Any]] = {
            k: dict(v) for k, v in self._DEFAULT_CATALOG.items()
        }
        # batas maksimal unit ON per perangkat (diisi via set_appliances)
        self._max_counts: Dict[str, int] = {}
        # batas global default per perangkat (fallback)
        self.global_count_cap: int = 30

        # bobot error gabungan
        self.weights = {"P": 1, "PF": 1}
        # toleransi relatif di domain P untuk pruning awal
        self.tolerance = 0.01  # 1%

        # compile regex nama "lampu_18w", "Lampu 32 W", dst
        self._LAMPU_W_RE = re.compile(r"(?i)\blampu[_\-\s]*([0-9]{1,4})\s*w\b")

    # ------------------ util catalog ------------------
    def electronic_list(self) -> Dict[str, Dict[str, Any]]:
        """
        Lihat catalog efektif. Setiap item berisi:
        { "watt": float, "pf": float[0.3..1.0], "type": "led|smps|motor|resistive|inductive",
          "phase": 1|3, "standby_w": float>=0, "surge_mult": float>=1.0 }
        """
        return {k: dict(v) for k, v in self._catalog.items()}

    def _default_entry(self) -> Dict[str, Any]:
        # default masuk akal untuk perangkat tak dikenal
        return {
            "watt": 100.0,
            "pf": 0.90,
            "type": "smps",
            "phase": 1,
            "standby_w": 0.0,
            "surge_mult": 1.0,
        }

    def configure_catalog(self, overrides: Dict[str, Dict[str, Any]]) -> None:
        """
        Override sebagian nilai default, contoh:
        configure_catalog({"ev_charger": {"watt": 3500, "pf": 0.99, "type": "smps", "phase": 1}})
        """
        ALLOWED_KEYS = {"watt", "pf", "type", "phase", "standby_w", "surge_mult"}
        ALLOWED_TYPES = {"led", "smps", "motor", "resistive", "inductive"}

        for name, spec in overrides.items():
            key = self._canon_name(name)
            cur = dict(self._catalog.get(key, self._default_entry()))
            for k, v in spec.items():
                kk = str(k).lower()
                if kk not in ALLOWED_KEYS:
                    continue
                if kk == "watt":
                    cur["watt"] = max(0.0, float(v))
                elif kk == "pf":
                    cur["pf"] = max(0.3, min(1.0, float(v)))
                elif kk == "type":
                    t = str(v).lower()
                    cur["type"] = t if t in ALLOWED_TYPES else cur.get("type", "smps")
                elif kk == "phase":
                    cur["phase"] = 3 if int(v) == 3 else 1
                elif kk == "standby_w":
                    cur["standby_w"] = max(0.0, float(v))
                elif kk == "surge_mult":
                    cur["surge_mult"] = max(1.0, float(v))
            self._catalog[key] = cur

    # ------------------ parsing nama ------------------
    def _canon_name(self, raw: str) -> str:
        s = str(raw).strip().lower().replace(" ", "_")
        # alias langsung
        if s in self._ALIASES:
            return self._ALIASES[s]
        # pola "lampu_XXw" / "lampu 18 w" → buat entri jika belum ada
        m = self._LAMPU_W_RE.search(s)
        if m:
            watt = float(m.group(1))
            key = f"lampu_{int(watt)}w"
            if key not in self._catalog:
                self._catalog[key] = {
                    "watt": watt,
                    "pf": 1,
                    "type": "led",
                    "phase": 1,
                    "standby_w": 0.0,
                    "surge_mult": 1.0,
                }
            return key
        return s

    # ------------------ konfigurasi ------------------
    def set_appliances(self, counts: Dict[str, int]) -> None:
        """
        counts: mapping nama (bebas/alias) -> jumlah maksimal unit yang mungkin ada.
        Nama boleh alias/varian; akan dinormalkan ke key catalog.
        Contoh:
          {"kipas":5,"lampu_18W":5,"lampu_32W":5,"lampu":3,"TV":2,"Kulkas":2,"AC":1,
           "ev_charger":1,"mesin_cuci":1,"chrger_motor":3}
        """
        maxc: Dict[str, int] = {}
        for raw_name, c in counts.items():
            key = self._canon_name(raw_name)
            if key not in self._catalog:
                # perangkat tak dikenal → buat entri generic lengkap
                self._catalog[key] = self._default_entry()
            maxc[key] = max(0, int(c))
        self._max_counts = maxc

    # ------------------ core perhitungan (tetap) ------------------
    @staticmethod
    def _real_power(
        voltage: Optional[float],
        current: Optional[float],
        power_factor: Optional[float],
        power: Optional[float],
    ) -> Optional[float]:
        if power is not None:
            return float(power)
        if voltage is not None and current is not None and power_factor is not None:
            return float(voltage) * float(current) * float(power_factor)
        return None

    def _aggregate(
        self,
        counts: List[int],
        units_activeP: List[float],
        units_pf: List[float],
        V: Optional[float],
        baseline_P: float,
        I_meas: Optional[float] = None,   # <= NEW: arus terukur (opsional)
    ):
        """
        Hitung (P_sum, I_hat, PF_hat, V_hat) untuk kombinasi counts.
        - baseline_P = total standby semua unit yang ADA (off-state).
        - P_sum = baseline_P + sum(c_i * activeP_i)
        - Q dihitung dari komponen AKTIF (standby ~ resistif → diabaikan).
        - I_hat dihitung jika V tersedia: I_hat = S_sum / V.
        - V_hat:
            * jika V ada → V_hat = V
            * elif I_meas ada → V_hat = S_sum / I_meas
            * else → None
        """
        # daya real total
        P_sum_active = sum(c * p for c, p in zip(counts, units_activeP))
        P_sum = baseline_P + P_sum_active

        # reaktif dari komponen aktif
        Q_sum = 0.0
        for c, p_act, pf in zip(counts, units_activeP, units_pf):
            if c == 0:
                continue
            tan_phi = 0.0 if pf >= 1.0 else math.sqrt(max(0.0, 1.0/(pf*pf) - 1.0))
            Q_sum += c * p_act * tan_phi

        # daya semu total
        S_sum = math.hypot(P_sum, Q_sum)  # sqrt(P^2 + Q^2)

        # arus prediksi (butuh V)
        I_hat = (S_sum / V) if (V is not None and V > 0) else None

        # power factor prediksi
        PF_hat = (P_sum / S_sum) if S_sum > 0 else 1.0

        # tegangan prediksi
        if V is not None and V > 0:
            V_hat = float(V)
        elif I_meas is not None and I_meas > 0:
            V_hat = S_sum / I_meas
        else:
            V_hat = None

        return P_sum, I_hat, PF_hat, V_hat

    def _loss(self, P_hat, I_hat, PF_hat, P_meas, I_meas, PF_meas):
        wP, wPF = self.weights["P"], self.weights["PF"]
        loss = 0.0
        loss += wP * (abs(P_hat - P_meas) / max(1.0, P_meas))
        # if I_meas is not None and I_hat is not None and I_meas > 0:
        #     loss += wI * (abs(I_hat - I_meas) / I_meas)
        if PF_meas is not None and PF_hat is not None:
            loss += wPF * (abs(PF_hat - PF_meas))
        return loss

    def predict(
        self,
        voltage: Optional[float] = None,
        current: Optional[float] = None,
        power_factor: Optional[float] = None,
        power: Optional[float] = None,
        strict: bool = True,          # <= mode telusur fokus-loss
        max_states: int = 1_000_000,  # <= batas aman exhaustive
    ) -> Dict[str, object]:
        """
        Mengembalikan kombinasi dengan LOSS terendah (gabungan P, I, PF).
        Jika strict=True dan ruang-tilik (search space) masih aman, DFS
        tidak melakukan pruning berbasis P saja—supaya tidak salah buang
        kombinasi yang I/PF-nya jauh lebih cocok.
        """
        if not self._max_counts:
            return {"on": {}, "target": {}, "pred": {}, "loss": 1.0, "rel_error_P": 1.0}

        P_meas = self._real_power(voltage, current, power_factor, power)
        if P_meas is None or P_meas <= 0:
            return {"on": {}, "target": {}, "pred": {}, "loss": 1.0, "rel_error_P": 1.0}

        V = float(voltage) if voltage is not None else None
        I_meas = float(current) if current is not None else None
        PF_meas = float(power_factor) if power_factor is not None else None

        # Siapkan item (pakai watt-aktif = watt - standby)
        items: List[Tuple[str, float, float, float, int]] = []
        for name, maxc in self._max_counts.items():
            spec = self._catalog.get(name)
            if not spec:
                continue
            w = float(spec.get("watt", 0.0))
            pf = float(spec.get("pf", 0.9))
            sb = float(spec.get("standby_w", 0.0))
            if w < 0 or maxc <= 0:
                continue
            pf = max(0.3, min(1.0, pf))
            w_active = max(0.0, w - max(0.0, sb))
            items.append((name, w_active, pf, max(0.0, sb), int(maxc)))

        if not items:
            return {"on": {}, "target": {}, "pred": {}, "loss": 1.0, "rel_error_P": 1.0}

        # Urut kontribusi aktif terbesar → kecil
        items.sort(key=lambda t: t[1], reverse=True)
        names         = [n   for (n,   _,   _,   _,  _) in items]
        units_activeP = [wa  for (_,  wa,  _,   _,  _) in items]
        units_pf      = [pf  for (_,  _,   pf,  _,  _) in items]
        bounds        = [min(c, self.global_count_cap) for (_, _, _, _, c) in items]

        # Baseline standby (semua unit ada tapi OFF)
        baseline_P = sum(sb * c for (_, _, _, sb, c) in items)

        # Estimasi ruang-tilik untuk memutuskan strict/exhaustive
        search_space = 1
        for b in bounds:
            search_space *= (b + 1)
            if search_space > max_states:
                break
        do_strict = strict and (search_space <= max_states)

        # Suffix maksimum kontribusi aktif (untuk pruning domain P bila non-strict)
        n = len(items)
        suffix_activeP_max = [0.0] * (n + 1)
        for i in range(n - 1, -1, -1):
            suffix_activeP_max[i] = suffix_activeP_max[i + 1] + units_activeP[i] * bounds[i]

        tol_abs = max(1.0, self.tolerance * P_meas)

        best_loss = float("inf")
        best_counts = [0] * n
        cur_counts = [0] * n

        # ====== Tambahan: siapkan Q per unit + suffix Q max untuk pruning ======
        units_Q = []
        for p_act, pf in zip(units_activeP, units_pf):
            tan_phi = 0.0 if pf >= 1.0 else math.sqrt(max(0.0, 1.0/(pf*pf) - 1.0))
            units_Q.append(p_act * tan_phi)

        suffixQ_max = [0.0] * (n + 1)
        for i in range(n - 1, -1, -1):
            suffixQ_max[i] = suffixQ_max[i + 1] + units_Q[i] * bounds[i]

        # target Q jika ada (butuh V, I, PF)
        Q_meas = None
        if V is not None and I_meas is not None and PF_meas is not None:
            S_meas = float(V) * float(I_meas)
            pf_c = max(0.0, min(1.0, float(PF_meas)))
            Q_meas = math.sqrt(max(0.0, S_meas * S_meas * (1.0 - pf_c * pf_c)))

        # toleransi absolut untuk Q (skala mirip P bila Q_meas tak ada)
        tol_Q_abs = max(1.0, self.tolerance * (Q_meas if (Q_meas and Q_meas > 0) else P_meas))

        # ====== Memoization & early-stop flag ======
        p_grid = max(1.0, self.tolerance * P_meas)  # grid diskret P untuk memo key
        visited = set()
        perfect_found = False

        wP = self.weights.get("P", 1.0)
        wQ = self.weights.get("Q", 0.0)

        def _lower_bound_loss(curP: float, curQ: float, idx: int) -> float:
            """
            Bound loss minimum yang masih mungkin dicapai dari state saat ini.
            Pakai P (dan Q bila tersedia). Komponen I/PF diabaikan (0) agar bound admissible.
            """
            # --- P lower bound ---
            # tidak bisa mengurangi P; hanya bisa menambah
            if curP > P_meas:
                p_err_lb = curP - P_meas
            else:
                p_err_lb = max(0.0, P_meas - (curP + suffix_activeP_max[idx]))
            lb = wP * (p_err_lb / max(1.0, P_meas))

            # --- Q lower bound (opsional) ---
            if Q_meas is not None:
                if curQ > Q_meas:
                    q_err_lb = curQ - Q_meas
                else:
                    q_err_lb = max(0.0, Q_meas - (curQ + suffixQ_max[idx]))
                lb += wQ * (q_err_lb / max(1.0, Q_meas if Q_meas > 1.0 else 1.0))
            return lb

        def _counts_order(c_guess: int, c_max: int):
            """
            Urutan zig-zag dari sekitar tebakan terbaik (greedy around-the-mean):
            c_guess, c_guess-1, c_guess+1, c_guess-2, ...
            """
            c_guess = max(0, min(c_guess, c_max))
            yield c_guess
            for d in range(1, c_max + 1):
                a = c_guess - d
                b = c_guess + d
                if a >= 0: yield a
                if b <= c_max: yield b

        def dfs(idx: int, cur_activeP: float, cur_activeQ: float):
            nonlocal best_loss, best_counts, perfect_found
            if perfect_found:
                return

            cur_P = baseline_P + cur_activeP  # Q baseline diasumsikan ~0 (standby ~ resistif)
            cur_Q = cur_activeQ

            # Memo: diskretkan P agar state space tidak meledak
            state_key = (idx, int(round(cur_P / p_grid)))
            if state_key in visited:
                return
            visited.add(state_key)

            # Pruning domain sederhana (tidak mungkin mendekati P dalam batas suffix)
            if not do_strict:
                if (P_meas - (cur_P + suffix_activeP_max[idx])) > tol_abs:
                    return
                if Q_meas is not None and (Q_meas - (cur_Q + suffixQ_max[idx])) > tol_Q_abs:
                    return

            # Lower-bound loss: jika bahkan bound >= best_loss, buang
            lb = _lower_bound_loss(cur_P, cur_Q, idx)
            if lb >= best_loss - 1e-12:
                return

            if idx == n:
                P_hat, I_hat, PF_hat, V_hat = self._aggregate(cur_counts, units_activeP, units_pf, V, baseline_P, I_meas=I_meas)
                l = self._loss(P_hat, I_hat, PF_hat, P_meas, I_meas, PF_meas)
                if l < best_loss:
                    best_loss = l
                    best_counts = cur_counts.copy()
                    # early stop kalau P sudah tepat dalam toleransi dan loss ~ 0
                    if abs(P_hat - P_meas) <= tol_abs and l <= 1e-12:
                        perfect_found = True
                return

            P_u = units_activeP[idx]
            Q_u = units_Q[idx]
            max_c = bounds[idx]

            # Batas iter dinamis agar tidak overshoot jauh saat non-strict
            if do_strict:
                c_max_iter = max_c
            else:
                c_max_by_P = int(min(max_c, math.ceil((P_meas + tol_abs - cur_P) / max(1.0, P_u))))
                if Q_meas is not None and Q_u > 0:
                    c_max_by_Q = int(math.ceil((Q_meas + tol_Q_abs - cur_Q) / Q_u))
                    c_max_iter = max(0, min(max_c, c_max_by_P, c_max_by_Q))
                else:
                    c_max_iter = max(0, c_max_by_P)

            # Heuristic guess jumlah terbaik untuk indeks ini (berbasis P)
            if P_u > 0:
                c_guess = int(round((P_meas - cur_P) / P_u))
            else:
                c_guess = 0
            c_guess = max(0, min(c_guess, c_max_iter))

            # Iterasi zig-zag sekitar tebakan agar cepat dapat solusi bagus → lebih banyak pruning selanjutnya
            for c in _counts_order(c_guess, c_max_iter):
                cur_counts[idx] = c
                dfs(idx + 1, cur_activeP + c * P_u, cur_activeQ + c * Q_u)
                if perfect_found:
                    break
            cur_counts[idx] = 0

        # ====== panggil DFS baru ======
        dfs(0, 0.0, 0.0)


        on = {names[i]: int(c) for i, c in enumerate(best_counts) if c > 0}
        P_hat, I_hat, PF_hat, V_hat = self._aggregate(best_counts, units_activeP, units_pf, V, baseline_P)
        return {
            "on": on,
            "target": {"P": P_meas, "I": I_meas, "PF": PF_meas, "V": V},
            "pred":   {"P": P_hat,  "I": I_hat,  "PF": PF_hat, "V": V_hat},
            "loss": float(best_loss),
            "rel_error_P": float(abs(P_hat - P_meas) / max(1.0, P_meas)),
        }
