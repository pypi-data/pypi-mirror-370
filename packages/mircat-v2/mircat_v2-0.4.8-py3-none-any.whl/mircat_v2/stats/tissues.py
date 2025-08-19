from loguru import logger

from mircat_v2.stats.utilities import (
    calculate_2d_areas,
    calculate_3d_volumes,
    calculate_3d_intensities,
)


def calculate_tissue_stats(
    nifti,
    tissue_seg_id: str,
    tissue_label_map: dict,
    body_seg_id: str,
    body_label_map: dict,
) -> dict:
    """Calculate tissue statistics for a given Nifti object.

    Parameters:
        nifti (StatsNifti): The Nifti object containing the image data.
        tissue_seg_id (str): The segmentation ID for the tissue.
        tissue_label_map (dict): A mapping of tissue labels to their IDs.
        body_seg_id (str): The segmentation ID for the body.
        body_label_map (dict): A mapping of body labels to their IDs.
    Returns:
        dict: A dictionary containing the calculated tissue statistics.
    """
    if not nifti.vertebrae_midlines:
        logger.warning(
            "Vertebrae midlines are not set. Cannot calculate tissue statistics."
        )
        return {}
    logger.trace(f"Calculating tissue statistics for {nifti.name}")
    # Get the data points we need
    stats = {"volumetric": {}, "vertebral": {}}
    tissue_seg = nifti.id_to_seg_map.get(tissue_seg_id)
    body_seg = nifti.id_to_seg_map.get(body_seg_id)
    vertebrae_midlines = nifti.vertebrae_midlines
    # We include the thoracic to measure around the heart
    verts_to_measure = {
        v: vertebrae_midlines[v]
        for v in ["T5", "T6", "T7", "T8", "L1", "L3", "L5"]
        if v in vertebrae_midlines
    }
    is_abdominal = "L1" in vertebrae_midlines and "L5" in vertebrae_midlines
    is_chest = "T3" in vertebrae_midlines and "T12" in vertebrae_midlines
    def measure_tissues(endpoints=(0, None)):
        """Measure the tissue segmentation in a volumetric region."""
        tissue_volumes = calculate_3d_volumes(
            tissue_seg, tissue_label_map, endpoints=endpoints, unit="cm3"
        )
        tissue_intensities = calculate_3d_intensities(
            nifti.img, tissue_seg, tissue_label_map, endpoints=endpoints
        )
        body_volumes = calculate_3d_volumes(
            body_seg, body_label_map, endpoints=endpoints, unit="cm3"
        )
        body_intensities = calculate_3d_intensities(
            nifti.img, body_seg, body_label_map, endpoints=endpoints
        )
        merged_tissues = tissue_volumes.copy()
        for key, value in tissue_intensities.items():
            merged_tissues[key].update(value)
        merged_body = body_volumes.copy()
        for key, value in body_intensities.items():
            merged_body[key].update(value)
        # This final dictionary will be in the format: {structure: {stat: value}}
        return {**merged_tissues, **merged_body}

    # Measure the volumes and intensities of the body and tissue segmentation
    total_stats = measure_tissues()
    stats["volumetric"]["total"] = total_stats
    # Measure region specific volumes
    if is_abdominal:
        endpoints = (vertebrae_midlines["L1"], vertebrae_midlines["L5"])
        abd_stats = measure_tissues(endpoints=endpoints)
        stats["volumetric"]["abdominal"] = abd_stats
    if is_chest:
        endpoints = (vertebrae_midlines["T3"], vertebrae_midlines["T12"])
        chest_stats = measure_tissues(endpoints=endpoints)
        stats["volumetric"]["chest"] = chest_stats
    # Measure the stats for each vertebra
    for vertebra, midline in verts_to_measure.items():
        body_vert_stats = calculate_2d_areas(
            body_seg, body_label_map, midline, get_perimeter=True, units="cm"
        )
        tissue_vert_stats = calculate_2d_areas(
            tissue_seg, tissue_label_map, midline, get_perimeter=False, units="cm"
        )
        stats["vertebral"][vertebra] = {
            **body_vert_stats,
            **tissue_vert_stats,
        }
    return stats
