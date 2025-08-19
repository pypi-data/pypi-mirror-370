import numpy as np
import SimpleITK as sitk
from skimage.measure import label, regionprops


def calculate_shape_stats(seg: sitk.Image) -> sitk.LabelShapeStatisticsImageFilter:
    """Calculate the shape stats for a segmentation
    Parameters
    ----------
    seg : sitk.Image
        The segmentation to calculate shape stats for
    Returns
    -------
    sitk.LabelShapeStatisticsImageFilter
        The executed shape stats
    """
    shape_stats = sitk.LabelShapeStatisticsImageFilter()
    shape_stats.SetGlobalDefaultCoordinateTolerance(1e-5)
    shape_stats.ComputeOrientedBoundingBoxOn()
    shape_stats.ComputePerimeterOn()
    shape_stats.Execute(seg)
    return shape_stats


def calculate_intensity_stats(
    image: sitk.Image, seg: sitk.Image
) -> sitk.LabelIntensityStatisticsImageFilter:
    """Calculate intensity stats for a segmentation using the reference image
    Parameters
    ----------
    image : sitk.Image
        The reference image
    seg : sitk.Image
        The segmentation of the reference image
    Returns
    -------
    sitk.LabelIntensityStatisticsImageFilter
        The executed intensity stats
    """
    intensity_stats = sitk.LabelIntensityStatisticsImageFilter()
    intensity_stats.SetGlobalDefaultCoordinateTolerance(1e-5)
    intensity_stats.Execute(seg, image)
    return intensity_stats


def filter_segmentation(
    segmentation: sitk.Image,
    labels: str | list[str],
    label_map: dict[str, int],
    largest_connected_component: bool = False,
    remap: bool = False,
) -> sitk.Image:
    """Filter a segmentation to only include specified labels
    Parameters
    ----------
    segmentation : sitk.Image
        The segmentation to filter
    labels : str|list[str]
        The labels to keep in the segmentation
    label_map : dict[str, int]
        A mapping of structure names to label IDs
    remap : bool, optional
        If True, remap the labels indexed starting from 1, by default False
    Returns
    -------
    sitk.Image
        The filtered segmentation
    """
    filtered_segmentation = sitk.Image(segmentation.GetSize(), sitk.sitkUInt8)
    filtered_segmentation.CopyInformation(segmentation)
    if isinstance(labels, str):
        labels = [labels]
    for i, label in enumerate(labels, start=1):
        idx = label_map.get(label, None)
        if idx is not None:
            mask = sitk.BinaryThreshold(segmentation, idx, idx, 1, 0)
            if largest_connected_component:
                mask = get_largest_connected_component(mask)
            new_idx = i if remap else idx
            mask = mask * new_idx
            filtered_segmentation = sitk.Add(filtered_segmentation, mask)
    return filtered_segmentation


def get_largest_connected_component(binary_segmentation: sitk.Image) -> sitk.Image:
    """Get the largest connected component from a binary segmentation
    Parameters
    ----------
    binary_segmentation : sitk.Image
        The binary segmentation to get the largest connected component from
    Returns
    -------
    sitk.Image
        The largest connected component of the binary segmentation
    """
    cc_filter = sitk.ConnectedComponentImageFilter()
    labeled = cc_filter.Execute(binary_segmentation)
    relabel_filter = sitk.RelabelComponentImageFilter()
    relabeled = relabel_filter.Execute(labeled)
    largest_component = sitk.BinaryThreshold(relabeled, 1, 1, 1, 0)
    return largest_component


def get_regionprops(image) -> list:
    """Get region properties from a labeled image
    Parameters
    ----------
    image : np.ndarray
        The labeled image to get region properties from
    Returns
    -------
    list
        A list of region properties for each labeled region in the image
    """
    labeled_image = label(image)
    return regionprops(labeled_image)


def slice_images(
    endpoints: tuple, images: sitk.Image | list
) -> sitk.Image | list[sitk.Image]:
    """Slice any number of matching images to the same region using endpoints
    Parameters:
        endpoints: Specific z-axis endpoints for a region of interest in the shape (start, end). Default is (0, None),
                    which will measure the entire image. If end = None, will measure from start_idx -> rest of the scan
        images: a single sitk.Image or list of sitk.Images -> must be the same shape or error is raised
    Returns:
        A single sitk.Image or list of sitk.Images sliced to the specified endpoints.
    """
    start, end = endpoints
    is_single_image = isinstance(images, sitk.Image)
    if end is None:
        if is_single_image:
            end = images.GetSize()[
                -1
            ]  # This is the full length of the image along the z-axis
        else:
            # Check that all images are the same size
            image_sizes = [img.GetSize() for img in images]
            assert image_sizes.count(image_sizes[0]) == len(image_sizes), ValueError(
                "All images in list must be the same shape"
            )
            end = images[0].GetSize()[-1]  # All images are assumed to be the same size
    if is_single_image:
        images = images[:, :, start:end]
        return images
    else:
        sliced_images = [image[:, :, start:end] for image in images]
        return sliced_images


def calculate_3d_volumes(
    segmentation: sitk.Image,
    label_map: dict[str, int],
    endpoints: tuple = (0, None),
    unit: str = "mm3",
) -> dict[str, float]:
    """Calculate the 3D volumes of each label in a segmentation
    Parameters:
        segmentation: The segmentation to calculate volumes for
        label_map: A mapping of structure names to label IDs
        endpoints: Specific z-axis endpoints for a region of interest in the shape (start, end). Default is (0, None),
                    which will measure the entire image. If end = None, will measure from start_idx -> rest of the scan
        dividend: A value to divide the calculated volumes by, default is 1.0 (no change) - can be used to convert units
    Returns:
        A dictionary mapping structure names to their 3D volumes the native units of the segmentation
    """
    segmentation = slice_images(endpoints, segmentation)
    shape_stats = calculate_shape_stats(segmentation)
    seg_labels = shape_stats.GetLabels()
    volumes = {}
    if unit == "cm3":
        dividend = 1000.0  # Convert from mm^3 to cm^3
        decimal_places = 1
    elif unit == "L":
        dividend = 1000000.0  # Convert from mm^3 to L
        decimal_places = 3
    else:
        dividend = 1.0
        decimal_places = 1
    for name, label in label_map.items():
        if label in seg_labels:
            volume = shape_stats.GetPhysicalSize(label)
            volumes[f"{name}"] = {
                f"volume_{unit}": round(volume / dividend, decimal_places)
            }
    return volumes


def calculate_3d_intensities(
    image: sitk.Image,
    segmentation: sitk.Image,
    label_map: dict[str, int],
    endpoints: tuple = (0, None),
) -> dict[str, float]:
    """Calculate the average intensities of each label in a segmentation
    Parameters:
        image: The reference image to calculate intensities from
        segmentation: The segmentation to calculate volumes for
        label_map: A mapping of structure names to label IDs
        endpoints: Specific z-axis endpoints for a region of interest in the shape (start, end). Default is (0, None),
                    which will measure the entire image. If end = None, will measure from start_idx -> rest of the scan
    Returns:
        A dictionary mapping structure names to their 3D intensities in Hounsfield Units
    """
    image = slice_images(endpoints, image)
    segmentation = slice_images(endpoints, segmentation)
    instensity_stats = calculate_intensity_stats(image, segmentation)
    seg_labels = instensity_stats.GetLabels()
    intensities = {}
    for name, label in label_map.items():
        if label in seg_labels:
            mean_hu = instensity_stats.GetMean(label)
            std_dev_hu = instensity_stats.GetStandardDeviation(label)
            intensities[f"{name}"] = {
                "hu_mean": round(mean_hu, 1),
                "hu_std_dev": round(std_dev_hu, 1),
            }
    return intensities


def calculate_2d_areas(
    seg: sitk.Image,
    label_map: dict,
    slice_idx: int,
    get_perimeter: bool = False,
    units: str = "cm",
) -> dict:
    """Calculate the area of each label in the segmentation within a 2d slice
    :param seg: the segmentation
    :param label_map: the label map
    :param slice_idx: the slice of the segmentation to measure
    :param prefix: the label of the slice (L1, L3, etc)
    :param get_perimeter: Measure the perimeters from the shape stats
    :param units: the base unit to use for the area and perimeter, default is 'cm'
    :return: a dictionary containing the area of each label found within the segmentation
    """
    seg_slice = seg[:, :, slice_idx]
    shape_stats = calculate_shape_stats(seg_slice)
    seg_labels = shape_stats.GetLabels()
    if units == "cm":
        area_div = 100.0
        linear_div = 10.0
    elif units == "mm":
        area_div = 1.0
        linear_div = 1.0
    data = {}
    for name, label in label_map.items():
        # Don't want the background label
        if label == 0 or label not in seg_labels:
            continue
        data[name] = {}
        area = round(shape_stats.GetPhysicalSize(label) / area_div, 1)
        data[name][f"area_{units}2"] = area
        if get_perimeter and (label in seg_labels):
            # Note that the shape touches the border if at least 5 percent of the perimeter is on the border
            border_ratio = shape_stats.GetPerimeterOnBorderRatio(label) * 100
            raw_perim = (
                shape_stats.GetPerimeter(label) / linear_div
            )  # This will be perimeter in cm
            ellipse_perim = _calc_ellipsoid_perimeter(
                shape_stats.GetEquivalentEllipsoidDiameter(label), units
            )
            circ_perim = shape_stats.GetEquivalentSphericalPerimeter(label) / linear_div
            # Use colon to separate the name and the value
            perimeter_data = {
                "border_ratio": round(border_ratio, 1),
                f"raw_perimeter_{units}": round(raw_perim, 1),
                f"ellipse_perimeter_{units}": round(ellipse_perim, 1),
                f"circle_perimeter_{units}": round(circ_perim, 1),
            }
            data[name].update(perimeter_data)
    return data


def _calc_ellipsoid_perimeter(diameters: tuple, unit="cm") -> float:
    """Calculate the estimated ellipsoid diameters from a shape_stats.GetEquivalentEllipsoidDiameter result.
    Uses the Ramanujan estimation.
    :param diameters: the result from shape_stats
    :param unit: the unit of the diameters, default is 'cm'
    :return the perimeter in the specified unit
    """
    minor, major = diameters
    major /= 2
    minor /= 2
    perim = np.pi * (
        3 * (major + minor) - np.sqrt((3 * major + minor) * (major + 3 * minor))
    )
    if unit == "cm":
        dividend = 10.0
    elif unit == "mm":
        dividend = 1.0
    return perim / dividend
