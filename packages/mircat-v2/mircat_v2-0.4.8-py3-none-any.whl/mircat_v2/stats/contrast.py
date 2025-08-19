import pickle
import numpy as np

from pathlib import Path
from loguru import logger

def predict_contrast(intensities: dict):
    """Predict CT contrast phase based on intensity statistics.
    :param intensities: Dictionary containing volume and intensity statistics.
    """
    # These are the structures we use for contrast prediction
    structures = [
        "liver",
        "pancreas",
        "urinary_bladder",
        "gallbladder",
        "heart",
        "aorta",
        "inferior_vena_cava",
        "portal_vein_and_splenic_vein",
        "iliac_vena_left",
        "iliac_vena_right",
        "iliac_artery_left",
        "iliac_artery_right",
        "pulmonary_vein",
        "brain",
        "colon",
        "small_bowel",
        "internal_carotid_artery_right",
        "internal_carotid_artery_left",
        "internal_jugular_vein_right",
        "internal_jugular_vein_left",
    ]
    features = []
    for structure in structures:
        if structure in intensities:
            # Get the average hu if the structure is in the image
            features.append(intensities[structure].get("hu_mean", 0.0))
        else:
            features.append(0.0)
    # features = [intensities.get(f"{structure}_avg_hu", 0.0) for structure in structures]
    if all([x == 0.0 for x in features]):
        logger.warning('No structures found for contrast prediction')
        return {}
    models_file = Path(__file__).parent / "contrast_phase_classifiers_2024_07_19.pkl"
    with models_file.open("rb") as f:
        models = pickle.load(f)
    preds = []
    for clf in models.values():
        pred = clf.predict([features])[0]
        preds.append(pred)
    preds = np.array(preds)
    pi_time = round(float(np.mean(preds)), 2)
    pi_time_std = round(float(np.std(preds)), 4)
    phase, probability = pi_time_to_phase(pi_time)
    return {
        "pi_time": pi_time,
        "pi_time_std": pi_time_std,
        "phase": phase,
        "probability": probability,
    }


def pi_time_to_phase(pi_time: float) -> str:
    """
    Convert the pi time to a phase and get a probability for the value.

    native: 0-10
    arterial_early: 10-30
    arterial_late:  30-60
    portal_venous:  60-100
    delayed: 100+

    returns: phase, probability
    """
    if pi_time < 5:
        return "native", 1.0
    elif pi_time < 10:
        return "native", 0.7
    elif pi_time < 20:
        return "arterial_early", 0.7
    elif pi_time < 30:
        return "arterial_early", 1.0
    elif pi_time < 50:
        return "arterial_late", 1.0
    elif pi_time < 60:
        return "arterial_late", 0.7  # in previous version: "portal_venous"
    elif pi_time < 70:
        return "portal_venous", 1.0
    elif pi_time < 90:
        return "portal_venous", 1.0
    elif pi_time < 100:
        return "portal_venous", 0.7
    else:
        return "portal_venous", 0.3
