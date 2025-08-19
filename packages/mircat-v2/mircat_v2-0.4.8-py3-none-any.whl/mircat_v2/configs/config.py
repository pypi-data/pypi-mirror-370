import json
import sys
from math import floor
from multiprocessing import cpu_count
from pathlib import Path
from loguru import logger

__all__ = [
    "config_path",
    "config_file",
    "dbase_schema_file",
    "read_config",
    "write_config",
    "read_segmentation_config",
    "read_dbase_config",
    "read_segmentation_config",
    "read_models_config",
    "read_stats_models_config",
    "logger_setup",
    "set_threads_per_process",
    "db_schema",
]


def generate_config() -> None:
    """Generate the default config"""
    with config_file.open("w") as f:
        json.dump(default_config, f, indent=2)


def read_config() -> dict[str, dict]:
    "Read and return the entire config file"
    try:
        with config_file.open() as f:
            return json.load(f)
    except json.decoder.JSONDecodeError as e:
        logger.error("the mircat-v2 config.json file could not be decoded.")
        raise e


def write_config(new_config: dict, key=str, subkey: str = None) -> None:
    """Write a new configuration to a specific key within the config.json file
    Parameters:
        new_config: dict - the new configuration to write
        key: str - the key that the configuration should be stored in, inside the config.json
    """
    config = read_config()
    if subkey is not None:
        config[key][subkey] = new_config
    else:
        config[key] = new_config
    with config_file.open("w") as f:
        json.dump(config, f, indent=2)
    logger.success(
        f"{key}{'[' + subkey + ']' if subkey is not None else ''} configuration saved to {config_file}"
    )


def read_segmentation_config() -> dict[str, dict]:
    "Read the config file and return the segmentation configuration"
    with config_file.open() as f:
        return json.load(f).get("segmentation", {})


def read_models_config() -> dict[str, dict]:
    "Read the config file and return the segmentation model configuration"
    with config_file.open() as f:
        return json.load(f).get("models", {})


def read_stats_models_config() -> dict[str, dict]:
    "Read the config file and return the stats models configuration"
    with config_file.open() as f:
        return json.load(f).get("stats_models", {})


def read_dbase_config() -> dict[str, dict]:
    """Read the config file and return the database configuration"""
    with config_file.open() as f:
        return json.load(f).get("dbase", {})


def logger_setup(verbose: bool, quiet: bool) -> None:
    """Set up logger for mircat-v2
    :param verbose: be verbose in the output by adding debug to stdout
    :param quiet: be quiet in the output by only showing successes and errors - no warnings or info.
    """
    logger.remove()
    # Regular
    stdout_fmt = "<green>{time: DD-MM-YYYY -> HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>"
    stderr_fmt = "<red>{time: DD-MM-YYYY -> HH:mm:ss}</red> | <level>{level}</level> | <level>{message}</level>"
    if quiet:
        # Only show success messages and error messages
        logger.add(
            sys.stdout,
            format=stdout_fmt,
            level="SUCCESS",
            filter=lambda record: record["level"].no <= 25,
            enqueue=True,
        )
        logger.add(sys.stderr, format=stderr_fmt, level="ERROR", enqueue=True)
    elif verbose:
        # Include debugging output
        logger.add(
            sys.stdout,
            format=stdout_fmt,
            level="DEBUG",
            filter=lambda record: record["level"].no <= 25,
            enqueue=True,
        )
        logger.add(
            sys.stderr,
            format=stderr_fmt,
            level="WARNING",
            enqueue=True,
        )
    else:
        # Show everything above INFO
        logger.add(
            sys.stdout,
            format=stdout_fmt,
            level="INFO",
            filter=lambda record: record["level"].no <= 25,
            enqueue=True,
        )
        logger.add(
            sys.stderr,
            format=stderr_fmt,
            level="WARNING",
            enqueue=True,
        )


def set_threads_per_process(args):
    # Do some thread matching
    total_threads = cpu_count()
    required_threads = args.n_processes * args.threads_per_process
    logger.debug(
        f"Total threads on machine: {total_threads}. Requested threads for segmentation: {required_threads}"
    )
    if total_threads < required_threads:
        # args.threads_per_process = floor(total_threads / args.n_processes)
        logger.warning(
            "Desired threads (n_processes * threads_per_process) > total threads on device ({}>{}). Monitor and change either the number of workers or threads if performance drops.",
            required_threads,
            total_threads,
            args.threads_per_process,
        )


config_path = Path(__file__).parent.resolve()
# Config will always be stored in the package files - easier to manage
config_file = config_path / "config.json"
dbase_schema_file = config_path / "dbase.sql"
db_schema = {
    "conversions": {
        "series_uid": {"type": "TEXT", "pk": 1},
        "study_uid": {"type": "TEXT", "pk": 0},
        "nifti": {"type": "TEXT", "pk": 0},
        "modality": {"type": "TEXT", "pk": 0},
        "mrn": {"type": "TEXT", "pk": 0},
        "accession": {"type": "TEXT", "pk": 0},
        "series_name": {"type": "TEXT", "pk": 0},
        "series_number": {"type": "INTEGER", "pk": 0},
        "scan_date": {"type": "TEXT", "pk": 0},
        "original_series_name": {"type": "TEXT", "pk": 0},
        "study_description": {"type": "TEXT", "pk": 0},
        "ct_direction": {"type": "TEXT", "pk": 0},
        "image_type": {"type": "TEXT", "pk": 0},
        "sex": {"type": "TEXT", "pk": 0},
        "age": {"type": "INTEGER", "pk": 0},
        "birth_date": {"type": "TEXT", "pk": 0},
        "height_m": {"type": "REAL", "pk": 0},
        "weight_kg": {"type": "REAL", "pk": 0},
        "pregnancy_status": {"type": "INTEGER", "pk": 0},
        "pixel_length_mm": {"type": "REAL", "pk": 0},
        "pixel_width_mm": {"type": "REAL", "pk": 0},
        "slice_thickness_mm": {"type": "REAL", "pk": 0},
        "manufacturer": {"type": "TEXT", "pk": 0},
        "model": {"type": "TEXT", "pk": 0},
        "kvp": {"type": "REAL", "pk": 0},
        "sequence_name": {"type": "TEXT", "pk": 0},
        "protocol_name": {"type": "TEXT", "pk": 0},
        "contrast_bolus_agent": {"type": "TEXT", "pk": 0},
        "contrast_bolus_route": {"type": "TEXT", "pk": 0},
        "contrast_bolus_volume": {"type": "REAL", "pk": 0},
        "dicom_folder": {"type": "TEXT", "pk": 0},
        "conversion_date": {"type": "TEXT", "pk": 0},
    },
    "segmentations": {
        "nifti": {"type": "TEXT", "pk": 1},
        "series_uid": {"type": "TEXT", "pk": 0},
        "task": {"type": "INTEGER", "pk": 2},
        "seg_file": {"type": "TEXT", "pk": 0},
        "seg_date": {"type": "TEXT", "pk": 3},
        "status": {"type": "TEXT", "pk": 0},
        "failed_error": {"type": "TEXT", "pk": 0},
    },
    "metadata": {
        "nifti": {"type": "TEXT", "pk": 1},
        "series_uid": {"type": "TEXT", "pk": 0},
        "study_uid": {"type": "TEXT", "pk": 0},
        "output_stats_file": {"type": "TEXT", "pk": 0},
        "modality": {"type": "TEXT", "pk": 0},
        "mrn": {"type": "TEXT", "pk": 0},
        "accession": {"type": "TEXT", "pk": 0},
        "series_name": {"type": "TEXT", "pk": 0},
        "series_number": {"type": "INTEGER", "pk": 0},
        "scan_date": {"type": "TEXT", "pk": 0},
        "original_series_name": {"type": "TEXT", "pk": 0},
        "study_description": {"type": "TEXT", "pk": 0},
        "ct_direction": {"type": "TEXT", "pk": 0},
        "abdominal_scan": {"type": "INTEGER", "pk": 0},
        "chest_scan": {"type": "INTEGER", "pk": 0},
        "correct_vertebrae_order": {"type": "INTEGER", "pk": 0},
        "lowest_vertebra": {"type": "TEXT", "pk": 0},
        "highest_vertebra": {"type": "TEXT", "pk": 0},
        "image_type": {"type": "TEXT", "pk": 0},
        "sex": {"type": "TEXT", "pk": 0},
        "age": {"type": "INTEGER", "pk": 0},
        "birth_date": {"type": "TEXT", "pk": 0},
        "height_m": {"type": "REAL", "pk": 0},
        "weight_kg": {"type": "REAL", "pk": 0},
        "pregnancy_status": {"type": "INTEGER", "pk": 0},
        "pixel_length_mm": {"type": "REAL", "pk": 0},
        "pixel_width_mm": {"type": "REAL", "pk": 0},
        "slice_thickness_mm": {"type": "REAL", "pk": 0},
        "manufacturer": {"type": "TEXT", "pk": 0},
        "model": {"type": "TEXT", "pk": 0},
        "kvp": {"type": "REAL", "pk": 0},
        "sequence_name": {"type": "TEXT", "pk": 0},
        "protocol_name": {"type": "TEXT", "pk": 0},
        "contrast_bolus_agent": {"type": "TEXT", "pk": 0},
        "contrast_bolus_route": {"type": "TEXT", "pk": 0},
        "contrast_bolus_volume": {"type": "REAL", "pk": 0},
        "dicom_folder": {"type": "TEXT", "pk": 0},
        "conversion_date": {"type": "TEXT", "pk": 0},
    },
    "vol_int": {
        "nifti": {"type": "TEXT", "pk": 1},
        "series_uid": {"type": "TEXT", "pk": 0},
        "structure": {"type": "TEXT", "pk": 2},
        "volume_cm3": {"type": "REAL", "pk": 0},
        "hu_mean": {"type": "REAL", "pk": 0},
        "hu_std_dev": {"type": "REAL", "pk": 0},
    },
    "contrast": {
        "nifti": {"type": "TEXT", "pk": 1},
        "series_uid": {"type": "TEXT", "pk": 0},
        "phase": {"type": "TEXT", "pk": 0},
        "probability": {"type": "REAL", "pk": 0},
        "pi_time": {"type": "REAL", "pk": 0},
        "pi_time_std": {"type": "REAL", "pk": 0},
    },
    "vertebrae": {
        "nifti": {"type": "TEXT", "pk": 1},
        "series_uid": {"type": "TEXT", "pk": 0},
        "vertebra": {"type": "TEXT", "pk": 2},
        "midline": {"type": "INTEGER", "pk": 0},
    },
    "aorta_metrics": {
        "nifti": {"type": "TEXT", "pk": 1},
        "series_uid": {"type": "TEXT", "pk": 0},
        "region": {"type": "TEXT", "pk": 2},
        "entire_region": {"type": "INTEGER", "pk": 0},
        "length_mm": {"type": "REAL", "pk": 0},
        "tortuosity_index": {"type": "REAL", "pk": 0},
        "icm": {"type": "REAL", "pk": 0},
        "n_inflections": {"type": "INTEGER", "pk": 0},
        "peria_volume_cm3": {"type": "REAL", "pk": 0},
        "peria_ring_volume_cm3": {"type": "REAL", "pk": 0},
        "peria_fat_volume_cm3": {"type": "REAL", "pk": 0},
        "peria_hu_mean": {"type": "REAL", "pk": 0},
        "peria_hu_std": {"type": "REAL", "pk": 0},
        "calc_volume_mm3": {"type": "REAL", "pk": 0},
        "calc_agatston": {"type": "REAL", "pk": 0},
        "calc_count": {"type": "INTEGER", "pk": 0},
        "is_120_kvp": {"type": "INTEGER", "pk": 0},
        "mean_diameter_mm": {"type": "REAL", "pk": 0},
        "mean_roundness": {"type": "REAL", "pk": 0},
        "mean_flatness": {"type": "REAL", "pk": 0},
    },
    "aorta_diameters": {
        "nifti": {"type": "TEXT", "pk": 1},
        "series_uid": {"type": "TEXT", "pk": 0},
        "region": {"type": "TEXT", "pk": 2},
        "measure": {"type": "TEXT", "pk": 3},
        "mean_diameter_mm": {"type": "REAL", "pk": 0},
        "major_diameter_mm": {"type": "REAL", "pk": 0},
        "minor_diameter_mm": {"type": "REAL", "pk": 0},
        "area_mm2": {"type": "REAL", "pk": 0},
        "roundness": {"type": "REAL", "pk": 0},
        "flatness": {"type": "REAL", "pk": 0},
        "rel_distance": {"type": "REAL", "pk": 0},
        "entire_region": {"type": "INTEGER", "pk": 0},
    },
    "tissues_volumetric": {
        "nifti": {"type": "TEXT", "pk": 1},
        "series_uid": {"type": "TEXT", "pk": 0},
        "region": {"type": "TEXT", "pk": 2},
        "structure": {"type": "TEXT", "pk": 3},
        "volume_cm3": {"type": "REAL", "pk": 0},
        "hu_mean": {"type": "REAL", "pk": 0},
        "hu_std_dev": {"type": "REAL", "pk": 0},
    },
    "tissues_vertebral": {
        "nifti": {"type": "TEXT", "pk": 1},
        "series_uid": {"type": "TEXT", "pk": 0},
        "vertebra": {"type": "TEXT", "pk": 2},
        "structure": {"type": "TEXT", "pk": 3},
        "measurement": {"type": "TEXT", "pk": 4},
        "value": {"type": "REAL", "pk": 0},
    },
    "iliac": {
        "nifti": {"type": "TEXT", "pk": 1},
        "series_uid": {"type": "TEXT", "pk": 0},
        "side": {"type": "TEXT", "pk": 2},
        "length_mm": {"type": "REAL", "pk": 0},
        "location": {"type": "TEXT", "pk": 3},
        "metric": {"type": "TEXT", "pk": 4},
        "value": {"type": "REAL", "pk": 0},
    },
}

needed_stats = {
    "999": {
        "background": 0,
        "spleen": 1,
        "kidney_right": 2,
        "kidney_left": 3,
        "gallbladder": 4,
        "liver": 5,
        "stomach": 6,
        "pancreas": 7,
        "adrenal_gland_right": 8,
        "adrenal_gland_left": 9,
        "lung_upper_lobe_left": 10,
        "lung_lower_lobe_left": 11,
        "lung_upper_lobe_right": 12,
        "lung_middle_lobe_right": 13,
        "lung_lower_lobe_right": 14,
        "esophagus": 15,
        "trachea": 16,
        "thyroid_gland": 17,
        "small_bowel": 18,
        "duodenum": 19,
        "colon": 20,
        "urinary_bladder": 21,
        "prostate": 22,
        "sacrum": 23,
        "vertebrae_S1": 24,
        "vertebrae_L5": 25,
        "vertebrae_L4": 26,
        "vertebrae_L3": 27,
        "vertebrae_L2": 28,
        "vertebrae_L1": 29,
        "vertebrae_T12": 30,
        "vertebrae_T11": 31,
        "vertebrae_T10": 32,
        "vertebrae_T9": 33,
        "vertebrae_T8": 34,
        "vertebrae_T7": 35,
        "vertebrae_T6": 36,
        "vertebrae_T5": 37,
        "vertebrae_T4": 38,
        "vertebrae_T3": 39,
        "vertebrae_T2": 40,
        "vertebrae_T1": 41,
        "vertebrae_C7": 42,
        "vertebrae_C6": 43,
        "vertebrae_C5": 44,
        "vertebrae_C4": 45,
        "vertebrae_C3": 46,
        "vertebrae_C2": 47,
        "vertebrae_C1": 48,
        "heart": 49,
        "aorta": 50,
        "pulmonary_vein": 51,
        "brachiocephalic_trunk": 52,
        "subclavian_artery_right": 53,
        "subclavian_artery_left": 54,
        "common_carotid_artery_right": 55,
        "common_carotid_artery_left": 56,
        "brachiocephalic_vein_left": 57,
        "brachiocephalic_vein_right": 58,
        "atrial_appendage_left": 59,
        "superior_vena_cava": 60,
        "inferior_vena_cava": 61,
        "portal_vein_and_splenic_vein": 62,
        "iliac_artery_left": 63,
        "iliac_artery_right": 64,
        "iliac_vena_left": 65,
        "iliac_vena_right": 66,
    },
    "485": {
        "background": 0,
        "subq_fat": 1,
        "visc_fat": 2,
        "skeletal_muscle": 3,
        "intermuscular_fat": 4,
    },
    "481": {"background": 0, "subq_fat": 1, "visc_fat": 2, "skeletal_muscle": 3},
    "299": {"background": 0, "body": 1, "body_extremities": 2},
    "300": {"background": 0, "body": 1, "body_extremities": 2},
}

# We want the standard dbase schema to always be there - all we need to update is the path to the database file
default_config = {
    "dbase": {"tables": db_schema},
    "stats_models": needed_stats,
    "models": {},
}
if not config_file.exists():
    generate_config()
