import SimpleITK as sitk
import numpy as np

from loguru import logger
from mircat_v2.stats.utilities import calculate_shape_stats


def calculate_vertebrae_stats(nifti, seg_id: str, label_map: dict) -> dict:
    """Calculate vertebrae midlines and height statistics for a given nifti file
    :param nifti: StatsNifti object containing the nifti file and its metadata.
    :param seg_id: The segmentation ID to calculate statistics for.
    :param label_map: Dictionary mapping structure names to label IDs.
    :return: Dictionary containing vertebrae midlines and height statistics.
    """
    vertebrae_labels = {
        k.replace("vertebrae_", ""): v
        for k, v in label_map.items()
        if "vertebrae" in k.lower()
    }
    segmentation = nifti.id_to_seg_map[seg_id]
    shape_stats = calculate_shape_stats(segmentation)
    vertebrae_stats = {}
    previous_midline = 1e6
    correct_vertebrae_order = 1
    for vertebra, label in vertebrae_labels.items():
        if label in shape_stats.GetLabels():
            vertebra_indicies = shape_stats.GetIndexes(label)
            z_indices = vertebra_indicies[2::3]
            midline = int(np.median(z_indices))
            vertebrae_stats[vertebra] = {"midline": midline}
            if midline > previous_midline:
                logger.debug(
                    f"Vertebrae {vertebra} midline {midline} is greater than previous midline {previous_midline}. "
                    "This may indicate an incorrect order of vertebrae."
                )
                correct_vertebrae_order = 0
            previous_midline = midline

    lowest_vertebra = max(vertebrae_stats, key=lambda k: vertebrae_stats[k]["midline"])
    highest_vertebra = min(vertebrae_stats, key=lambda k: vertebrae_stats[k]["midline"])
    vertebrae_stats["lowest_vertebra"] = lowest_vertebra
    vertebrae_stats["highest_vertebra"] = highest_vertebra
    vertebrae_stats["correct_vertebrae_order"] = correct_vertebrae_order
    vertebrae_stats["abdominal_scan"] = int(
        "L1" in vertebrae_stats and "L5" in vertebrae_stats
    )
    vertebrae_stats["chest_scan"] = int(
        "T3" in vertebrae_stats and "T12" in vertebrae_stats
    )
    return vertebrae_stats


# TODO - Add vertebrae height statistics
