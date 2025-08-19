from dataclasses import dataclass
import SimpleITK as sitk
import numpy as np
import xs3d

from kimimaro import skeletonize
from skimage.filters import gaussian
from skimage.morphology import remove_small_holes, remove_small_objects
from loguru import logger
from mircat_v2.stats.centerline import Centerline
from mircat_v2.stats.utilities import filter_segmentation, get_regionprops


class Vessel:
    """A class to represent a single vessel with its centerline and properties."""

    def __init__(
        self,
        segmentation,
        label,
        label_map,
        remap=True,
        largest_connected_component=True,
    ):
        """
        Initialize the Vessel class with segmentation data and label map.
        :param segmentation: The segmentation data for the vessel.
        :param label: The label of the vessel to be processed.
        :param label_map: A dictionary mapping structure names to label IDs.
        :param remap: Whether to remap the labels in the segmentation.
        :param largest_connected_component: Whether to filter to the largest connected component for the label.
        """
        self.segmentation = filter_segmentation(
            segmentation,
            label,
            label_map,
            remap=remap,
            largest_connected_component=largest_connected_component,
        )
        self.anisotropy = list(self.segmentation.GetSpacing())
        self.array = sitk.GetArrayFromImage(self.segmentation)
        self.label = label
        self.label_idx = 1 if remap else label_map.get(label, 0)
        if remap:
            self.label_map = {1: label}
        else:
            self.label_map = {label_map.get(label, 0): label}
        self.skeletonization_kwargs = {
            "teasar_params": {
                "scale": 1.0,
                "const": 40,
            },
            "object_ids": None,
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
        self.skeleton = None
        self.centerline = None
        self.cpr = None
        self.cpr_stats = None

    @property
    def length(self):
        """
        Calculate the length of the vessel's centerline in physical space.
        :return: The length of the centerline in physical units.
        """
        if not hasattr(self, "centerline"):
            raise ValueError(
                "Centerline has not been created. Call create_centerline() first."
            )
        # self.centerline.length is voxel space - need to convert with spacing
        return round(self.centerline.length * min(self.anisotropy), 1)

    def create_skeleton(self, **kwargs):
        """
        Create a centerline skeleton for the vessel.
        :param kwargs: Additional keyword arguments for kimimaro skeletonization.
        :return: The Vessel instance with the skeleton created.
        """
        self.skeletonization_kwargs.update(kwargs)
        skeletons = skeletonize(self.array, **self.skeletonization_kwargs)
        self.skeleton = skeletons[self.label_idx]
        return self

    def create_centerline(self, **kwargs):
        """
        Create a centerline for the vessel.
        :param kwargs: Additional keyword arguments for kimimaro skeletonization.
        :return: The Vessel instance with the centerline created.
        """
        if self.skeleton is None:
            logger.trace("Skeleton not created yet. Creating skeleton first.")
            self.create_skeleton(**kwargs)
            if self.skeleton is None:
                raise ValueError(
                    "Skeleton for the vessel is None. Ensure skeletonization was successful."
                )
        # This orders the centerline in physical space
        coordinates = self.skeleton.paths()[0]
        coordinates = (coordinates / self.anisotropy).round().astype(int)
        centerline = Centerline(
            label=self.label_idx, vessel=self.label, coordinates=coordinates
        )
        self.centerline = centerline
        return self

    def process_centerline(
        self, target_points: int, smoothing_factor: float = 1.0, degree: int = 3
    ):
        """
        Postprocess the centerline by resampling it with spline interpolation to a desired number of points and calculate tangent vectors.
        :param target_points: Number of points in the resampled centerline.
        :param smoothing_factor: Smoothing factor for spline interpolation.
        :param degree: Degree of the spline (1=linear, 2=quadratic, 3=cubic).
        """
        if not hasattr(self, "centerline"):
            raise ValueError(
                "Centerline has not been created. Call create_centerline() first."
            )
        self.centerline.resample_with_spline(
            target_points=target_points, smoothing=smoothing_factor, degree=degree
        )
        self.centerline.calculate_tangent_vectors()
        return self

    def create_straightened_cpr(self, radius: int = 100):
        """
        Create a straightened CPR (Curved Planar Reformation) from the vessel's centerline.
        :param radius: The radius of the sliced image in physical units of the scan (e.g., 50 = 50mm radius if spacing is in mm).
        :return: A 2D numpy array representing the straightened CPR.
        """
        if not hasattr(self, "centerline"):
            raise ValueError(
                "Centerline has not been created. Call create_centerline() first."
            )
        cpr = create_straightened_cpr_from_array(
            self.array,
            self.centerline.coordinates,
            self.centerline.tangents,
            self.anisotropy,
            radius=radius,
            is_label=True,
        )
        assert len(cpr) == len(self.centerline.coordinates), (
            "CPR length does not match centerline coordinates length."
        )
        self.cpr = cpr
        return self

    def calculate_straightened_cpr_cross_section_stats(self):
        """
        Calculate statistics for each cross section of the CPR.
        Each cross section is analyzed for its mean diameter, major diameter, minor diameter, area, flatness, and roundness.
        :return: The Vessel instance with the CPR statistics calculated.
        """
        if self.cpr is None:
            raise ValueError(
                "CPR has not been created. Call create_straightened_cpr() first."
            )
        # Implement statistics calculation logic here
        cross_section_spacing = self.anisotropy[
            1:
        ]  # we assume the first dimension is the slice dimension
        stats = {
            idx: self.calculate_cross_section_stats(
                cross_section, pixel_spacing=cross_section_spacing
            )
            for idx, cross_section in enumerate(self.cpr)
        }
        assert len(stats) == len(self.cpr) == len(self.centerline), (
            "Stats length mismatch with CPR or centerline."
        )
        self.cpr_stats = stats
        return self

    @staticmethod
    def calculate_cross_section_stats(
        cross_section: np.ndarray, pixel_spacing: tuple | np.ndarray
    ) -> dict:
        """
        Calculate statistics for a single cross section.

        The "roundness" is calculated as (4 * pi * area) / (perimeter ** 2), which is a standard measure of how close the shape is to a perfect circle.

        """
        # This uses a custom get_regionprops wrapper (which internally uses skimage.measure.regionprops) to calculate the properties of the cross section
        regionprops = get_regionprops(cross_section)
        # This uses skimage.measure.regionprops to calculate the properties of the cross section
        regionprops = get_regionprops(cross_section)
        data_dict = {
            "mean_diameter": None,
            "major_diameter": None,
            "minor_diameter": None,
            "area": None,
            "flatness": None,
            "roundness": None,
            "centroid": None,
        }
        if len(regionprops) == 0:
            return data_dict
        region = regionprops[0]
        major_endpoints, minor_endpoints = _get_cross_section_diameter_endpoints(region)
        major_endpoints = [np.array(pt) * pixel_spacing for pt in major_endpoints]
        minor_endpoints = [np.array(pt) * pixel_spacing for pt in minor_endpoints]
        major_diameter = np.linalg.norm(
            np.array(major_endpoints[1]) - np.array(major_endpoints[0])
        ).round(1)
        minor_diameter = np.linalg.norm(
            np.array(minor_endpoints[1]) - np.array(minor_endpoints[0])
        ).round(1)
        data_dict = {
            "mean_diameter": np.mean([major_diameter, minor_diameter]).round(1),
            "major_diameter": major_diameter,
            "minor_diameter": minor_diameter,
            "area": region.area * np.prod(pixel_spacing),
            "flatness": round(major_diameter / minor_diameter, 3)
            if minor_diameter > 0
            else 0,
            "roundness": round((4 * np.pi * region.area) / (region.perimeter**2), 3)
            if region.perimeter > 0
            else 0,
            "centroid": tuple(round(x) for x in region.centroid),
        }
        return data_dict

    def _plot_centerline(self):
        """
        Plot the centerline of the vessel against segmentation in two axes. Meant for debugging.
        """
        if self.centerline is None:
            raise ValueError(
                "Centerline has not been created. Call create_centerline() first."
            )
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(1, 2, figsize=(12, 6))
        ax[0].imshow(self.array.max(axis=2), cmap="gray")
        ax[0].plot(
            self.centerline.coordinates[:, 1],
            self.centerline.coordinates[:, 0],
            color="red",
            linewidth=2,
        )
        ax[0].set_title(f"Saggital View of {self.label}")
        ax[1].imshow(self.array.max(axis=1), cmap="gray")
        ax[1].plot(
            self.centerline.coordinates[:, 2],
            self.centerline.coordinates[:, 0],
            color="red",
            linewidth=2,
        )
        ax[1].set_title(f"Coronal View of {self.label}")
        plt.tight_layout()
        plt.show()


def _get_cross_section_diameter_endpoints(region) -> tuple[tuple, tuple]:
    """
    Get the major and minor diameter endpoints of a cross section from a regionprops object.
    :param region: A regionprops object containing the properties of the region.
    :return: A tuple containing the major and minor diameter endpoints.
    The endpoints are tuples of (y, x) coordinates.
    """

    def _get_axis_endpoints(centroid, orientation, axis_length):
        y0, x0 = centroid
        # calculate the endpoints of the major axis using the centroid
        x1 = x0 - np.sin(orientation) * 0.5 * axis_length
        x2 = x0 + np.sin(orientation) * 0.5 * axis_length
        y1 = y0 - np.cos(orientation) * 0.5 * axis_length
        y2 = y0 + np.cos(orientation) * 0.5 * axis_length
        return (y1, x1), (y2, x2)

    centroid = region.centroid
    orientation = region.orientation
    major_axis_length = region.major_axis_length
    minor_axis_length = region.minor_axis_length
    major_endpoints = _get_axis_endpoints(centroid, orientation, major_axis_length)
    minor_endpoints = _get_axis_endpoints(centroid, orientation, minor_axis_length)
    return major_endpoints, minor_endpoints


def create_straightened_cpr_from_array(
    array: np.ndarray,
    centerline: np.ndarray,
    tangents: np.ndarray,
    anisotropy: tuple | list,
    radius: int = 200,
    is_label: bool = True,
) -> np.ndarray:
    """
    Create a straightened CPR (Curved Planar Reformation) of an array from a centerline and relevant tangent vectors.
    :param array: The 3D numpy array to slice.
    :param centerline: numpy array containing the coordinates of the centerline.
    :param tangents: numpy array containing the tangent vectors at each point of the centerline
    :param anisotropy: A tuple or list representing the spacing of the image (e.g., (1.0, 1.0, 1.0)).
    :param radius: The radius of the sliced image in physical units of the scan (i.e. 50 = 50mm radius if spacing is in mm). 200 units is default.
    :return: A 2D numpy array representing the straightened CPR.
    """
    array = np.asfortranarray(array)
    expected_length = int(np.ceil(radius / min(anisotropy))) * 2
    expected_size = (expected_length, expected_length)
    pad_value = np.min(array)
    min_size = int(
        round(25 / min(anisotropy))
    )  # Minimum for a segmentation allowed in the cross section
    cpr = []
    for point, tangent in zip(centerline, tangents):
        cross_section = xs3d.slice(
            array, point, tangent, anisotropy, standardize_basis=True, crop=radius
        )
        cross_section = _resize_cross_section(cross_section, expected_size, pad_value)
        if is_label:
            cross_section = _postprocess_label_cross_section(cross_section, min_size)
        cpr.append(cross_section)
    cpr = np.array(cpr, dtype=array.dtype)
    return cpr


def _resize_cross_section(
    cross_section: np.ndarray, target_size: tuple, pad_value: float | int
) -> np.ndarray:
    """
    Resize cross_section to target_size by padding or cropping from center.

    :param cross_section: 2D array to resize
    :param target_size: Target (height, width)
    :return: Resized array
    """
    current_h, current_w = cross_section.shape
    target_h, target_w = target_size

    # Calculate padding/cropping for each dimension
    h_diff = target_h - current_h
    w_diff = target_w - current_w

    # Start with the original cross section
    result = cross_section

    # Handle height dimension
    if h_diff > 0:
        # Need to pad
        pad_top = h_diff // 2
        pad_bottom = h_diff - pad_top
        result = np.pad(
            result,
            ((pad_top, pad_bottom), (0, 0)),
            mode="constant",
            constant_values=pad_value,
        )
    elif h_diff < 0:
        # Need to crop
        crop_top = (-h_diff) // 2
        crop_bottom = crop_top + target_h
        result = result[crop_top:crop_bottom, :]

    # Handle width dimension
    if w_diff > 0:
        # Need to pad
        pad_left = w_diff // 2
        pad_right = w_diff - pad_left
        result = np.pad(
            result,
            ((0, 0), (pad_left, pad_right)),
            mode="constant",
            constant_values=pad_value,
        )
    elif w_diff < 0:
        # Need to crop
        crop_left = (-w_diff) // 2
        crop_right = crop_left + target_w
        result = result[:, crop_left:crop_right]

    return result


def _postprocess_label_cross_section(
    cross_section: np.ndarray, min_size: int
) -> np.ndarray:
    """
    Postprocess a label cross-section by removing small holes and smoothing.

    :param cross_section: 2D array representing the label cross-section
    :return: Processed 2D array
    """
    labels = [label for label in np.unique(cross_section) if label > 0]
    if len(labels) == 0:
        return cross_section
    output_cross_section = np.zeros_like(cross_section, dtype=np.uint8)
    for label in labels:
        mask = (cross_section == label).astype(np.uint8)
        regionprops = get_regionprops(mask)
        if len(regionprops) == 0:
            centered_label = np.zeros_like(mask)
        elif len(regionprops) > 1:
            centered_label = _closest_to_centroid(mask, regionprops)
        else:
            centered_label = mask
        centered_label = centered_label.astype(bool)
        centered_label = remove_small_holes(centered_label)
        centered_label = remove_small_objects(centered_label, min_size=10)
        centered_label = gaussian(centered_label, sigma=2).round().astype(np.uint8)
        output_cross_section[centered_label == 1] = label
    return output_cross_section


def _closest_to_centroid(cross_section: np.ndarray, regions: list) -> np.ndarray:
    """Filter a cross-section label using skimage.measure.regionprops to the region closest
    to the center
    :param cross_section: the cross-section array
    :param regions: the list output from skimage.measure.regionprops
    :return: the filtered numpy array
    """
    center_of_plane = np.array(cross_section.shape) / 2.0
    centroids = [np.array(region.centroid) for region in regions]
    distance_per_region = np.asarray(
        [np.linalg.norm(centroid - center_of_plane) for centroid in centroids]
    )
    min_distance_region_idx = int(np.argmin(distance_per_region))
    center_region = regions[min_distance_region_idx]
    center_label = np.zeros_like(cross_section, dtype=np.uint8)
    center_label[center_region.coords[:, 0], center_region.coords[:, 1]] = 1
    return center_label


@dataclass
class CrossSectionStat:
    index: int
    mean_diameter: float | None
    major_diameter: float | None
    minor_diameter: float | None
    area: float | None
    flatness: float | None
    roundness: float | None
    centroid: tuple | None
