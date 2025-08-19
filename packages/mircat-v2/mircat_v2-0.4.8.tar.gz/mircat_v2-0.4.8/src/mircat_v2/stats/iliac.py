from dataclasses import dataclass
import numpy as np
from mircat_v2.stats.vessel import Vessel, CrossSectionStat


def calculate_iliac_artery_stats(nifti, seg_id: str, label_map: dict) -> dict:
    segmentation = nifti.id_to_seg_map.get(seg_id)
    iliac_left = Vessel(segmentation, "iliac_artery_left", label_map)
    iliac_right = Vessel(segmentation, "iliac_artery_right", label_map)
    try:
        (
            iliac_left.create_centerline(teasar_params={"scale": 1.0, "const": 10})
            .process_centerline(len(iliac_left.centerline) // 2)
            .create_straightened_cpr(radius=50)
            .calculate_straightened_cpr_cross_section_stats()
        )
    except KeyError:
        iliac_left = None
    try:
        (
            iliac_right.create_centerline(teasar_params={"scale": 1.0, "const": 10})
            .process_centerline(len(iliac_right.centerline) // 2)
            .create_straightened_cpr(radius=50)
            .calculate_straightened_cpr_cross_section_stats()
        )
    except KeyError:
        iliac_right = None
    iliac_stats = {}
    for art in [iliac_left, iliac_right]:
        if art is None:
            continue
        seg_name = art.label
        art_length = round(art.centerline.length, 1)
        cross_sections = [CrossSectionStat(k, **v) for k, v in art.cpr_stats.items()]
        start_idx = cross_sections[0].index
        end_idx = cross_sections[-1].index
        rel_idx = end_idx - start_idx
        rel_dist = lambda x: round((x.index - start_idx) / rel_idx, 2)
        diam_cross_sections = []
        for cs in cross_sections:
            if cs.mean_diameter is not None:
                if cs.mean_diameter > 0.5 and cs.roundness > 0.7:
                    diam_cross_sections.append(cs)
        mean_diameter = np.mean([x.mean_diameter for x in diam_cross_sections]).round(1)
        mean_roundness = np.mean([x.roundness for x in diam_cross_sections]).round(2)
        mean_flatness = np.mean([x.flatness for x in diam_cross_sections]).round(2)
        # Max diameter stats in the region
        max_diam = max(diam_cross_sections, key=lambda x: x.mean_diameter)
        mid_diam = cross_sections[
            len(cross_sections) // 2
        ]  # This should basically never be missing
        if mid_diam.mean_diameter is None:
            mid_diam = diam_cross_sections[len(diam_cross_sections) // 2]
        min_diam = min(diam_cross_sections, key=lambda x: x.mean_diameter)
        # first measured cross section
        prox_diam = diam_cross_sections[0]
        # Last measured cross section
        dist_diam = diam_cross_sections[-1]
        rel_dist = lambda x: round((x.index - start_idx) / rel_idx, 2)
        rel_dists = {
            "max": rel_dist(max_diam),
            "min": rel_dist(min_diam),
            "prox": rel_dist(prox_diam),
            "mid": rel_dist(mid_diam),
            "dist": rel_dist(dist_diam),
        }
        iliac_stats[seg_name] = {
            "length_mm": art_length,
            "mean": {
                "diameter": mean_diameter,
                "roundness": mean_roundness,
                "flatness": mean_flatness,
            },
            "max": {
                "rel_distance": rel_dists["max"],
                "mean_diameter": max_diam.mean_diameter,
                "major_diameter": max_diam.major_diameter,
                "minor_diameter": max_diam.minor_diameter,
                "area": max_diam.area,
                "roundness": max_diam.roundness,
                "flatness": max_diam.flatness,
            },
            "min": {
                "rel_distance": rel_dists["min"],
                "mean_diameter": min_diam.mean_diameter,
                "major_diameter": min_diam.major_diameter,
                "minor_diameter": min_diam.minor_diameter,
                "area": min_diam.area,
                "roundness": min_diam.roundness,
                "flatness": min_diam.flatness,
            },
            "mid": {
                "rel_distance": rel_dists["mid"],
                "mean_diameter": mid_diam.mean_diameter,
                "major_diameter": mid_diam.major_diameter,
                "minor_diameter": mid_diam.minor_diameter,
                "area": mid_diam.area,
                "roundness": mid_diam.roundness,
                "flatness": mid_diam.flatness,
            },
            # "proximal": {
            #     "rel_distance": rel_dists["prox"],
            #     "mean_diameter": prox_diam.mean_diameter,
            #     "major_diameter": prox_diam.major_diameter,
            #     "minor_diameter": prox_diam.minor_diameter,
            #     "area": prox_diam.area,
            #     "roundness": prox_diam.roundness,
            #     "flatness": prox_diam.flatness,
            # },
            # "distal": {
            #     "rel_distance": rel_dists["dist"],
            #     "mean_diameter": dist_diam.mean_diameter,
            #     "major_diameter": dist_diam.major_diameter,
            #     "minor_diameter": dist_diam.minor_diameter,
            #     "area": dist_diam.area,
            #     "roundness": dist_diam.roundness,
            #     "flatness": dist_diam.flatness,
            # },
        }
    return iliac_stats
