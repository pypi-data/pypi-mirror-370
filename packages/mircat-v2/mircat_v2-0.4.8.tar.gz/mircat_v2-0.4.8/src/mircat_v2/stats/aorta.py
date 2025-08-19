from dataclasses import dataclass
from pathlib import Path
import csv
import gzip
import numpy as np
import SimpleITK as sitk

from loguru import logger
from skimage import draw
from mircat_v2.stats.utilities import filter_segmentation, get_regionprops
from mircat_v2.stats.vessel import Vessel, create_straightened_cpr_from_array


def calculate_aorta_stats(nifti, seg_id: str, label_map: dict) -> dict:
    """Calculate aorta specific statistics for a given nifti file.
    :param nifti: StatsNifti object containing the nifti file and its metadata.
    :param seg_id: The segmentation ID to calculate statistics for.
    :param label_map: Dictionary mapping structure names to label IDs.
    :return: Dictionary containing aorta specific statistics.
    """
    logger.trace(f"Calculating aorta stats for {nifti.name}.")
    if not hasattr(nifti, "vertebrae_midlines"):
        logger.debug(
            f"Vertebrae midlines not found in {nifti.name}. Skipping aorta stats calculation."
        )
        return {}
    segmentation = nifti.id_to_seg_map.get(seg_id)
    aorta = Aorta(
        nifti.img,
        segmentation,
        nifti.vertebrae_midlines,
        label_map,
    )
    aorta.calculate_stats()
    aorta.write_aorta_summary(nifti.seg_folder / f"{nifti.name}_aorta_summary.csv.gz")
    return aorta.stats


@dataclass
class AortaStraightenedCPRCrossSection:
    """
    A dataclass to represent a cross-section of a straightened CPR.
    """

    index: int
    coordinates: np.ndarray
    thickness: float | None
    mean_diameter: float | None
    major_diameter: float | None
    minor_diameter: float | None
    area: float | None
    flatness: float | None
    roundness: float | None
    centroid: tuple[float, float] | None
    peria_total_volume: float
    peria_ring_volume: float
    peria_fat_volume: float
    peria_fat_hus: list[int]
    calc_volume_score: float
    calc_agatston_score: float
    calc_regions: int
    anatomical_region: str | None = None


class Aorta(Vessel):
    """Class for aorta-specific statistics and operations for the custom segmentation model specifically."""

    anatomical_regions_vertebrae_map = {
        "thoracic": [f"T{i}" for i in range(4, 13)],
        "desc": [f"T{i}" for i in range(5, 13)],
        "up_abd": ["T12", "L1", "L2"],
        "lw_abd": ["L2", "L3", "L4", "L5", "S1"],
    }
    # Assume that the aortic root is approximately 20mm in length
    root_length_mm: int = 20

    def __init__(
        self,
        image: sitk.Image,
        segmentation: sitk.Image,
        vertebrae_midlines: dict[str, int],
        label_map: dict,
    ):
        """
        Initialize the Aorta class with a nifti file and segmentation ID.

        Parameters:
            image: the ct scan in hounsfield units as a SimpleITK Image.
            segmentation: the segmentation containing the aorta as a SimpleITK Image.
            vertebrae_midlines: Dictionary mapping vertebrae names to their midline coordinates.
            label_map: Dictionary mapping structure names to label IDs.
        """
        # We need to include the brachiocephalic trunk and left subclavian artery to separate anatomical regions
        labels = ["aorta", "brachiocephalic_trunk", "subclavian_artery_left"]
        self.image = image
        self.segmentation = filter_segmentation(
            segmentation,
            labels=labels,
            label_map=label_map,
            remap=True,
            largest_connected_component=True,
        )
        self.anisotropy = list(self.segmentation.GetSpacing())
        self.array = sitk.GetArrayFromImage(self.segmentation)
        # We clip the hounsfield units to a range that is easier to see and useful for us
        self.image_array = sitk.GetArrayFromImage(self.image).clip(-400, 600)
        self.label_map = {label: idx for idx, label in enumerate(labels, start=1)}
        self.label = "aorta"
        self.label_idx = 1
        self.skeletonization_kwargs = {
            "teasar_params": {
                "scale": 1.0,
                "const": 40,
            },
            "object_ids": [1],  # Aorta is always label 1 in the segmentation
            "anisotropy": self.anisotropy,
            "dust_threshold": 1000,
            "progress": False,
            "fix_branching": True,
            "in_place": False,
            "fix_borders": True,
            "parallel": 1,
            "parallel_chunk_size": 100,
            "extra_targets_before": [],
            "extra_targets_after": [],
            "fill_holes": False,
            "fix_avocados": False,
            "voxel_graph": None,
        }
        self.vertebrae_midlines: dict = vertebrae_midlines
        # We will store these when needed - it does not need to be initialized immediately
        self.img_array: np.ndarray = np.array([])
        self.skeleton = None
        self.centerline = None
        self.cpr = np.array([])
        self.img_cprs = {}
        self.cross_section_stats: list[AortaStraightenedCPRCrossSection] = []
        self._regions: dict = None
        self.regions_by_index: dict = {}
        self.stats: dict = {}

    @property
    def regions(self):
        """
        Get the anatomical regions of the aorta.
        :return: Dictionary containing the anatomical regions and their properties.
        """
        if self._regions is None:
            self.determine_anatomical_regions()
        return self._regions

    def determine_anatomical_regions(self):
        """
        Determine the anatomical regions of the aorta in the segmentation based on vertebrae midlines.
        """
        regions = {}
        for region, vertebrae in self.anatomical_regions_vertebrae_map.items():
            midlines = [
                self.vertebrae_midlines[vert]
                for vert in vertebrae
                if self.vertebrae_midlines.get(vert) is not None
            ]
            # Need at least two midlines to determine a region
            if len(midlines) > 1:
                regions[region] = {
                    "in_image": True,
                    "entire_region": len(midlines) == len(vertebrae),
                    "start": min(midlines),
                    "end": max(midlines),
                }
            else:
                regions[region] = {
                    "in_image": False,
                    "entire_region": False,
                    "start": None,
                    "end": None,
                }
        # In order to properly measure the thoracic aorta - the entirety must be in the scan
        if regions["thoracic"]["in_image"] and regions["thoracic"]["entire_region"]:
            del regions["desc"]
        else:
            del regions["thoracic"]
        self._regions = regions
        return self

    def create_straightened_cprs(self, radius: int = 100):
        """
        Create both straightened CPRs of the segmentation and image from the centerline of the aorta.

        Parameters:
            radius: int - desired radius of the cross section in mm.
        Returns:
            self: The Aorta instance with the CPRs created.
        """
        # First calculate the segmentation cpr
        super().create_straightened_cpr(radius=radius)
        # Then calculate the image cpr
        img_cpr = create_straightened_cpr_from_array(
            self.image_array,
            self.centerline.coordinates,
            self.centerline.tangents,
            self.anisotropy,
            radius=radius,
            is_label=False,
        )
        # Assert that the image CPR matches the segmentation CPR and centerline
        assert len(img_cpr) == len(self.centerline.coordinates) == len(self.cpr), (
            "Image CPR length does not match centerline coordinates length."
        )
        # Boolean mask for fat voxels
        # periaortic fat should be between -190 and -30 HU
        fat = (-190 <= img_cpr) & (img_cpr <= -30)
        # Boolean mask for calcification
        # aortic calcification should be above 130 HU
        calcificiation = img_cpr >= 130
        self.img_cprs = {
            "image": img_cpr,
            "fat": fat,
            "calc": calcificiation,
        }
        return self

    # Overwriting the parent class method so we can use the AortaStraightenedCPRCrossSection dataclass
    def calculate_straightened_cpr_cross_section_stats(self):
        """
        Calculate statistics for each cross section of the CPR for the entirety of the aorta segmentation.
        Each cross section is analyzed for its mean diameter, major diameter, minor diameter, area, flatness, and roundness.
        :return: The Vessel instance with the CPR statistics calculated.
        """
        if self.cpr is None:
            raise ValueError(
                "CPR has not been created. Call create_straightened_cpr() first."
            )
        # we assume the first dimension is the slice dimension
        cross_section_spacing = self.anisotropy[1:]
        voxel_area = np.prod(cross_section_spacing)
        for idx, cross_section in enumerate(self.cpr):
            cross_section_stats = self.calculate_cross_section_stats(
                cross_section, cross_section_spacing
            )
            if idx == len(self.centerline.segment_lengths):
                # Estimate the final cross section thickness as the mean segment length
                thickness = self.centerline.segment_lengths.mean().round(2)
            else:
                thickness = self.centerline.segment_lengths[idx].round(2)
            periaortic_stats = self._calculate_cross_section_periaortic_fat(
                idx,
                voxel_area,
                thickness,
                cross_section_stats["mean_diameter"],
                cross_section_stats["centroid"],
            )
            calcification_stats = self._calculate_cross_section_calcification(
                idx, voxel_area, thickness
            )
            cross_section_stats.update(periaortic_stats)
            cross_section_stats.update(calcification_stats)
            cross_section_stats["index"] = idx
            cross_section_stats["coordinates"] = self.centerline.coordinates[idx]
            # cross_section_stats["array"] = cross_section
            cross_section_stats["thickness"] = thickness
            self.cross_section_stats.append(
                AortaStraightenedCPRCrossSection(**cross_section_stats)
            )
        assert len(self.cross_section_stats) == len(self.cpr) == len(self.centerline), (
            "Stats length mismatch with CPR or centerline."
        )
        return self

    def _calculate_cross_section_periaortic_fat(
        self,
        idx: int,
        area_per_voxel: float,
        thickness: float,
        diameter: float,
        centroid: tuple[int, int],
    ) -> dict:
        """
        Calculate the volume and collect the HUs of the periaortic fat in a cross section
        Parameters:
            idx: the index of the image and fat cpr to use
            thickness: the thickness of the cross section in mm
            diameter: the mean diameter of the segmentation cross section in mm
            centroid: the centroid of the segmentation cross section
        """
        if diameter is None or centroid is None:
            return {
                "peria_total_volume": 0,
                "peria_ring_volume": 0,
                "peria_fat_volume": 0,
                "peria_fat_hus": [],
            }
        # Get the appropriate slices
        seg_cs = self.cpr[idx] == self.label_map["aorta"]
        img_cs = self.img_cprs["image"][idx]
        fat_cs = self.img_cprs["fat"][idx]
        voxel_volume = area_per_voxel * thickness
        # Draw the disk around the centroid
        radius = (
            int(diameter / 2) + 10
        )  # we add 1cm to the radius when drawing the circle
        center_y, center_x = centroid
        # This is a boolean mask of the circle around the centroid
        ring_mask = np.zeros_like(img_cs, dtype=bool)
        # Draw the disk in the mask
        rr, cc = draw.disk((center_y, center_x), radius, shape=img_cs.shape)
        ring_mask[rr, cc] = True
        # Get the total volume of the mask before removing the aorta
        total_volume = np.sum(ring_mask) * voxel_volume
        # Remove the aorta from the mask
        ring_mask[seg_cs == 1] = False
        # Calculate the volume of the periaortic fat
        ring_volume = np.sum(ring_mask) * voxel_volume
        fat_volume = np.sum(fat_cs[ring_mask]) * voxel_volume
        # We get the fat_hu values as an array so that we can find the average for each aortic anatomical region
        fat_hus = img_cs[fat_cs & ring_mask]
        return {
            "peria_total_volume": total_volume,
            "peria_ring_volume": ring_volume,
            "peria_fat_volume": fat_volume,
            "peria_fat_hus": fat_hus,
        }

    def _calculate_cross_section_calcification(
        self, idx: int, voxel_area: float, thickness: float
    ) -> dict:
        """Calculate the calcification found within the cross section of the aorta
        Parameters:
            idx: the index of the cprs to measure
            voxel_area: the area of a voxel in the CPR in physical space (1mm, 1mm), (0.75mm, 0.75mm), etc.
            thickness: the thickness of the slice in mm
        Returns:
            a dictionary containing the derived calcification statistics
        """
        seg_cs = self.cpr[idx] == self.label_map["aorta"]
        if seg_cs.sum() == 0:
            return {"calc_volume_score": 0, "calc_agatston_score": 0, "calc_regions": 0}
        img_cs = self.img_cprs["image"][idx]
        calc_cs = self.img_cprs["calc"][idx]
        # Calcification has to be both >=130HU and within the aorta
        calc_in_aorta = calc_cs & seg_cs
        # Measure the calcification
        voxel_volume = voxel_area * thickness
        calc_volume_score = 0
        calc_agatston_score = 0
        calc_regions = get_regionprops(calc_in_aorta)
        for region in calc_regions:
            if region.area >= 1:
                # Volume score is just the amount of calcification in the cs
                calc_volume_score += region.area * voxel_volume
                # Agatston weights the area based on maximum HU inside the calcification
                max_calc_hu = img_cs[region.coords].max()
                assert max_calc_hu >= 130
                if 130 <= max_calc_hu < 200:
                    density_weighting_factor = 1
                elif 200 <= max_calc_hu < 300:
                    density_weighting_factor = 2
                elif 300 <= max_calc_hu < 400:
                    density_weighting_factor = 3
                else:
                    density_weighting_factor = 4
                calc_agatston_score += (
                    region.area * density_weighting_factor * voxel_area
                )
        return {
            "calc_volume_score": calc_volume_score,
            "calc_agatston_score": calc_agatston_score,
            "calc_regions": len(calc_regions),
        }

    def split_anatomical_regions_by_indicies(self) -> dict[str, list[int]]:
        """
        Split the aorta into [root, asc, arch, desc, up_abd, lw_abd] anatomical regions with reference to the indices of it's centerline/cpr.
        :return: Dictionary with region names as keys and lists of indices as values.
        """

        def _split_thoracic_aorta_by_index() -> dict[str, list[int]]:
            """Internal function to break apart the thoracic aorta"""
            # Check if both brachiocephalic trunk and left subclavian artery are in the cpr
            brach_label = self.label_map["brachiocephalic_trunk"]
            subclavian_label = self.label_map["subclavian_artery_left"]
            arch_start: int = None
            arch_end: int = None
            start, end = (
                self.regions["thoracic"]["start"],
                self.regions["thoracic"]["end"],
            )
            thoracic_indices = (
                self.centerline.get_indices_within_dimensional_coordinates(start, end)
            )
            # We use the anatomical method if the 2 extra segmentations were found
            if np.all(np.isin([brach_label, subclavian_label], self.cpr)):
                logger.trace("Using aortic CPR to define aortic arch")
                # We shrink this so we don't include the abdominal aorta
                thoracic_cpr = self.cpr[thoracic_indices]
                # The brachiocephalic trunk signifies the start of the aortic arch
                for idx, cross_section in enumerate(thoracic_cpr):
                    if brach_label in cross_section:
                        arch_start = idx
                        break
                # The left subclavian artery signifies the end of the aortic arch, so we go in reverse
                for idx, cross_section in enumerate(thoracic_cpr[::-1]):
                    if subclavian_label in cross_section:
                        arch_end = len(thoracic_cpr) - idx
            # Otherwise, we use the morphology of the aorta to define the regions
            else:
                logger.trace("Using aortic morphology to define aortic arch")
                # Need at least 50mm2 to be considered
                min_segmentation_area = 50
                # This is the peak of the centerline
                split = None
                arch_peak = int(self.centerline.coordinates[:, 0].min())
                aorta_array = self.array == self.label_map["aorta"]
                for idx, axial_slice in enumerate(self.array):
                    regions = get_regionprops(axial_slice)
                    # If there are two regions in the image, then we know the ascending and descending aorta
                    # are visible within the segmentation slice
                    if len(regions) == 2 and idx > arch_peak:
                        reg0 = regions[0]
                        reg1 = regions[1]
                        # If both sections of the aorta are sufficiently large,
                        if (
                            reg0.area > min_segmentation_area
                            and reg1.area > min_segmentation_area
                        ):
                            split = idx
                            break
                if split is None:
                    raise ValueError("Aortic arch could not be defined from morphology")
                # We shrink this to exclude the abdominal aorta
                thoracic_centerline = self.centerline.coordinates[thoracic_indices]
                for idx, coordinate in enumerate(thoracic_centerline):
                    if coordinate[0] <= split:
                        arch_start = idx
                        break
                for idx, coordinate in enumerate(thoracic_centerline[::-1]):
                    if coordinate[0] <= split:
                        arch_end = len(thoracic_centerline) - idx
                        break
                if arch_start is None or arch_end is None:
                    raise ValueError("Aortic arch could not be defined from morphology")
            # extract the aortic root as a separate region from the ascending aorta
            ascending_start = 0
            for idx, length in enumerate(self.centerline.cumulative_lengths):
                if length > self.root_length_mm:
                    ascending_start = idx
                    break
            return {
                "root": thoracic_indices[:ascending_start],
                "asc": thoracic_indices[ascending_start:arch_start],
                "arch": thoracic_indices[arch_start:arch_end],
                "desc": thoracic_indices[arch_end:],
            }

        if not self.centerline:
            raise ValueError(
                "Centerline was not found for the aorta. Cannot split aortic regions of the CPR."
            )
        elif not self.cpr.any():
            raise ValueError(
                "CPR is empty. Cannot split Aorta CPR into appropriate anatomical regions."
            )
        for region, info in self.regions.items():
            # If the region is not in the image, we move on
            if not info["in_image"]:
                continue
            if region == "thoracic":
                self.regions_by_index.update(_split_thoracic_aorta_by_index())
            else:
                self.regions_by_index[region] = (
                    self.centerline.get_indices_within_dimensional_coordinates(
                        info["start"], info["end"]
                    )
                )
        return self

    def aggregate_stats(self):
        """Aggregate all the desired stats into a dictionary to be sent out for storage"""
        aggregated = {}
        aggregated["whole"] = self._aggregate_region(include_diameters=False)
        for region, indices in self.regions_by_index.items():
            for index in indices:
                self.cross_section_stats[index].anatomical_region = region
            if len(indices) < 3:
                logger.debug(
                    f"Skipping aortic region {region} with less than 3 indices."
                )
                continue
            logger.trace(f"Aggregating stats for aortic region: {region}")
            # we only run these if the whole thing is there
            if region in ["root", "asc", "arch"]:
                entire_region = 1
            elif region == "desc" and "root" in self.regions_by_index:
                entire_region = 1
            else:
                entire_region = int(self.regions[region]["entire_region"])
            aggregated[region] = {
                "entire_region": entire_region,
                **self._aggregate_region(region_indices=indices),
            }
        # Denote if the entire aorta is present
        all_regions = {"whole", "root", "asc", "arch", "desc", "up_abd", "lw_abd"}
        if all(
            region.get("entire_region", 1) for region in aggregated.values()
        ) and all_regions == set(aggregated.keys()):
            aggregated["whole"]["entire_region"] = 1
        else:
            aggregated["whole"]["entire_region"] = 0
        self.stats = aggregated
        return self

    def _aggregate_region(
        self, region_indices: list[int] | None = None, include_diameters: bool = True
    ) -> dict:
        """
        Aggregate a specific region of the aorta using indices to extract from cross_section_stats

        Parameters:
            region_indices: list[int] - the list of indices to extract from the cross_section_stats. Defaults to entire aorta
        Returns:
            a dictionary containing the aggregated stats for the region
        """
        if region_indices is None:
            region_indices = [i for i in range(self.centerline.len())]
        # Get the region

        region = [self.cross_section_stats[x] for x in region_indices]
        start_idx = region_indices[0]
        end_idx = region_indices[-1]
        # Length is just the cumulative length over the region
        length = round(
            self.centerline.cumulative_lengths[end_idx]
            - self.centerline.cumulative_lengths[start_idx],
            1,
        )
        # Tortuosity from start to end
        tortuosity = self.centerline.calculate_tortuosity(start_idx, end_idx)
        # Initialize cumulative metrics
        ## Periaortic fat data
        peria_vol = 0
        peria_ring_vol = 0
        peria_fat_vol = 0
        peria_hus = []
        ## Calcification data
        calc_volume = 0
        calc_agatston = 0
        n_calcs = 0
        for cs in region:
            peria_vol += cs.peria_total_volume
            peria_ring_vol += cs.peria_ring_volume
            peria_fat_vol += cs.peria_fat_volume
            peria_hus.extend(cs.peria_fat_hus)
            calc_volume += cs.calc_volume_score
            calc_agatston += cs.calc_agatston_score
            n_calcs += cs.calc_regions
        peria_hu_mean, peria_hu_std = (
            np.array(peria_hus).mean(),
            np.array(peria_hus).std(),
        )
        if include_diameters:
            diameters = self._extract_diameters(region)
        else:
            diameters = {}

        return {
            "length_mm": length,
            **tortuosity,
            "peria_volume_cm3": round(peria_vol / 1000, 2),
            "peria_ring_volume_cm3": round(peria_ring_vol / 1000, 2),
            "peria_fat_volume_cm3": round(peria_fat_vol / 1000, 2),
            "peria_hu_mean": round(peria_hu_mean, 2),
            "peria_hu_std": round(peria_hu_std, 2),
            "calc_volume_mm3": round(calc_volume, 1),
            "calc_agatston": round(calc_agatston, 1),
            "calc_count": n_calcs,
            **diameters,
        }

    def _extract_diameters(
        self, region: list[AortaStraightenedCPRCrossSection]
    ) -> dict:
        diameters = {}
        # Filter out any cross section missing diameters or too small/uncircular to be sure about
        diam_cross_sections = []
        for cs in region:
            if cs.mean_diameter is not None:
                if cs.mean_diameter > 5 and cs.roundness >= 0.7:
                    diam_cross_sections.append(cs)
        # if it's empty, return the empty dictionary
        if len(diam_cross_sections) == 0:
            return diameters
        # Metrics across the region
        start_idx = region[0].index
        end_idx = region[-1].index
        rel_idx = end_idx - start_idx
        mean_diameter = np.mean([x.mean_diameter for x in diam_cross_sections]).round(1)
        mean_roundness = np.mean([x.roundness for x in diam_cross_sections]).round(2)
        mean_flatness = np.mean([x.flatness for x in diam_cross_sections]).round(2)
        # Max diameter stats in the region
        max_diam = max(diam_cross_sections, key=lambda x: x.mean_diameter)
        mid_diam = region[len(region) // 2]  # This should basically never be missing
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
        return {
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
            "proximal": {
                "rel_distance": rel_dists["prox"],
                "mean_diameter": prox_diam.mean_diameter,
                "major_diameter": prox_diam.major_diameter,
                "minor_diameter": prox_diam.minor_diameter,
                "area": prox_diam.area,
                "roundness": prox_diam.roundness,
                "flatness": prox_diam.flatness,
            },
            "distal": {
                "rel_distance": rel_dists["dist"],
                "mean_diameter": dist_diam.mean_diameter,
                "major_diameter": dist_diam.major_diameter,
                "minor_diameter": dist_diam.minor_diameter,
                "area": dist_diam.area,
                "roundness": dist_diam.roundness,
                "flatness": dist_diam.flatness,
            },
        }

    def calculate_stats(
        self, sampling_factor: float = 0.67, cross_section_radius: int = 100
    ):
        """
        Top-level method to calculate basic statistics for the aorta segmentation.
        Will create and process the centerline, create a straightened CPR,
        and calculate cross-section statistics.

        Parameters:
            sampling_factor: float - factor to downsample the centerline for smoothing and resampling - defaults to 0.67 (take 2 out of every 3 points).
            cross_section_radius: int - radius of the generated cross section in mm- defaults to 50.
        Returns:
            The Aorta instance with all statistics calculated stored as `cpr_cross_section_stats`.
        ### WILL EVENTUALLY BE DEPRECATED FOR A FULL AORTA STATISTICS CALCULATION METHOD
        return - The Aorta instance with all statistics calculated stored as `cpr_cross_section_stats`.
        """
        (
            self.determine_anatomical_regions()
            .create_centerline()
            .process_centerline(round(sampling_factor * self.centerline.len()))
            .create_straightened_cprs(cross_section_radius)
            .calculate_straightened_cpr_cross_section_stats()
            .split_anatomical_regions_by_indicies()
            .aggregate_stats()
        )
        return self

    def write_aorta_summary(self, output_path: str | Path, separator: str = ","):
        output_path = Path(output_path)
        col_order = {
            "index": "index",
            "anatomical_region": "region",
            "mean_diameter": "mean_diameter_mm",
            "major_diameter": "major_diameter_mm",
            "minor_diameter": "minor_diameter_mm",
            "area": "area",
            "roundness": "roundness",
            "flatness": "flatness",
            "peria_total_volume": "periaortic_total_volume_mm3",
            "peria_ring_volume": "periaortic_ring_volume_mm3",
            "peria_fat_volume": "periaortic_fat_volume_mm3",
            "calc_volume_score": "calc_volume_score",
            "calc_agatston_score": "calc_agatston_score",
            "calc_regions": "calc_regions",
        }
        data = []
        for cs in self.cross_section_stats:
            row = {col: getattr(cs, key) for key, col in col_order.items()}
            if row["region"] is None or row["mean_diameter_mm"] is None:
                continue
            for col, val in row.items():
                if isinstance(val, float):
                    row[col] = round(val, 2)
                elif isinstance(val, int):
                    row[col] = int(val)
            data.append(row)
        if output_path.suffix == ".gz":
            with gzip.open(output_path, mode="wt", newline="") as f:
                writer = csv.DictWriter(
                    f, fieldnames=col_order.values(), delimiter=separator
                )
                writer.writeheader()
                writer.writerows(data)
        else:
            with open(output_path, mode="w", newline="") as f:
                writer = csv.DictWriter(
                    f, fieldnames=col_order.values(), delimiter=separator
                )
                writer.writeheader()
                writer.writerows(data)
