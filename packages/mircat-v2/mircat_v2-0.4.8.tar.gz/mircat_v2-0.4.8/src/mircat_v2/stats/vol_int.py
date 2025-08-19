import SimpleITK as sitk
from loguru import logger
from mircat_v2.nifti import StatsNifti
from mircat_v2.stats.utilities import calculate_shape_stats, calculate_intensity_stats


def calculate_volume_and_intensity_stats(
    nifti: StatsNifti, seg_id: str, label_map: dict
) -> tuple[list[dict], dict]:
    """Calculate volume and intensity statistics for a given nifti file for the mircat-v2 custom segmentation.
    :param nifti: StatsNifti object containing the nifti file and its metadata.
    :param seg_id: The segmentation ID to calculate statistics for.
    :param label_map: Dictionary mapping structure names to label IDs.
    :return: Dictionary containing volume and intensity statistics.
    """
    logger.trace(f"Calculating volume and intensity stats for {nifti.name}.")
    segmentation = nifti.id_to_seg_map[seg_id]
    # Use SimpleITK to calculate the shape and intensity statistics
    shape_stats = calculate_shape_stats(segmentation)
    intensity_stats = calculate_intensity_stats(nifti.img, segmentation)
    # Get the average HU and volume for each label in the segmentation
    volumes_and_intensities = {}
    seg_labels = shape_stats.GetLabels()
    for structure, label in label_map.items():
        # Zero is background, so we skip it
        if label in seg_labels and label != 0:
            volume = round(shape_stats.GetPhysicalSize(label) / 1000, 1)
            avg_hu = round(intensity_stats.GetMean(label), 1)
            std_dev_hu = round(intensity_stats.GetStandardDeviation(label), 1)
            volumes_and_intensities[f"{structure}"] = {
                "volume_cm3": volume,
                "hu_mean": avg_hu,
                "hu_std_dev": std_dev_hu,
            }
    return volumes_and_intensities
