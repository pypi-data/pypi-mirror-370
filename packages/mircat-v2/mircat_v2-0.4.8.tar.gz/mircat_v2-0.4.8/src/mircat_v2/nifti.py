import re
import gzip
import json
import traceback
import numpy as np
import SimpleITK as sitk

from pathlib import Path
from uuid import uuid4
from loguru import logger
from mircat_v2.configs import read_dbase_config, db_schema
from mircat_v2.dicom_conversion import get_metadata


class Nifti:
    """A class used to represent a nifti file for mircat-v2 - including spacing, metadata, segmentations and others!"""

    def __init__(self, nifti_path: str | Path):
        nifti_path = Path(nifti_path).resolve()
        if not nifti_path.exists():
            message = f"Nifti file not found at {nifti_path}! Please check existence."
            logger.error(message)
            raise FileNotFoundError()
        if ".nii" not in nifti_path.suffixes:
            message = f"Input {nifti_path} not recognized as a nifti file. Please ensure file suffix is *.nii or *.nii.gz"
            logger.error(message)
            raise NotNiftiFileError()
        self.path = nifti_path
        self.parent = nifti_path.parent
        self.name = nifti_path.with_suffix("").stem
        self.seg_folder = self.parent / f"{self.name}_segs"
        self.segmentations = list(self.seg_folder.glob(f"{self.name}*.nii.gz"))
        try:
            self.img = sitk.ReadImage(nifti_path)
        except Exception as e:
            logger.error(
                f"Error loading {nifti_path} with SimpleITK :{e}\n{traceback.format_exc()}"
            )
            raise SimpleITKReadError()
        self.spacing = self.img.GetSpacing()
        self.shape = self.img.GetSize()
        try:
            if (self.parent / "metadata.json").exists():
                logger.trace(f"{self.parent / 'metadata.json'} found. Loading metadata.")
                with (self.parent / "metadata.json").open() as f:
                    self.metadata: dict = json.load(f)
                if self.metadata.get("series_uid") is None:
                    self.metadata["series_uid"] = str(uuid4())
                    self._write_metadata()

            elif (self.parent / "header_info.json").exists():
                logger.trace(
                    f"Old format metadata {self.parent / 'header_info.json'} found. Loading metadata."
                )
                with (self.parent / "header_info.json").open() as f:
                    self.metadata: dict = json.load(f)
                logger.trace("Updating metadata in Nifti.__init__")
                self.update_metadata_file()
            else:
                logger.debug(
                    f"No metadata.json or header_info.json file found next to {nifti_path}. Setting metadata['series_uid'] to a file with a generated uuid."
                )
                self.metadata: dict = {"series_uid": str(uuid4())}
                self._write_metadata()
        except json.JSONDecodeError as e:
            logger.warning('Existing metadata cannot be loaded from json. Creating a generated Series UID')
            self.metadata: dict = {"series_uid": str(uuid4())}
            self._write_metadata()
            
    def update_metadata_file(self) -> None:
        dicoms = list(self.parent.glob("*.dcm"))
        if not dicoms:
            logger.trace(
                f"No .dcm extension file found in {self.parent} - looking for dicom without extension"
            )
            dicoms = [
                f
                for f in self.parent.iterdir()
                if f.is_file() and re.match(r"^[\d.]+$", f.name)
            ]
            if not dicoms:
                logger.trace(f"No reference dicom found in {self.parent}")
                if self.metadata.get("series_number") is None:
                    self.metadata["series_number"] = self.name.split("_")[0]
                self.metadata["series_uid"] = str(uuid4())
                # Delete the old version
        if dicoms:
            self.metadata = get_metadata(dicoms[0])
            if self.metadata.get("series_uid") is None:
                self.metadata["series_uid"] = str(uuid4())
        # (self.parent / 'header_info.json').unlink()
        self._write_metadata()

    def _write_metadata(self):
        with (self.parent / "metadata.json").open("w") as f:
            json.dump(self.metadata, f, indent=2)


class SegNifti(Nifti):
    def __init__(self, nifti_path: str | Path):
        super().__init__(nifti_path)
        self.task_files: dict = {}

    def resample_and_save_for_segmentation(
        self, new_spacing, output_path, interpolator_type
    ) -> None:
        if len(new_spacing) == 2:
            # Set the new spacing z-length to be the same as the original
            new_spacing = [*new_spacing, self.spacing[-1]]
        # Resample image - always not a label
        resampled = resample_with_sitk(
            self.img,
            new_spacing=new_spacing,
            is_label=False,
            interpolator_type=interpolator_type,
        )
        sitk.WriteImage(resampled, output_path)
        logger.debug("Successfully resampled {} and wrote to {}", self.path, output_path)


class StatsNifti(Nifti):
    def __init__(self, nifti_path: str | Path, overwrite: bool = False):
        super().__init__(nifti_path)
        # TODO this needs to be updated to account for gzipping option
        stats_file = self.seg_folder / f"{self.name}_stats.json"
        self.stats_file = stats_file

        if stats_file.exists() and not overwrite:
            logger.trace(f"Stats file {stats_file} found. Loading statistics.")
            try:
                with stats_file.open() as f:
                    self.stats = json.load(f)
            except json.JSONDecodeError:
                logger.warning(
                    f"Error decoding JSON from {stats_file}. Initializing empty stats."
                )
                self.stats = {}
        else:
            if not overwrite:
                logger.trace(
                    f"No stats file found at {stats_file}. Setting stats to empty dictionary."
                )
            else:
                logger.trace(
                    f"Stats file {stats_file} exists but overwrite is set to True. Initializing empty stats."
                )
            self.stats = {}
        self.add_stats("nifti", str(self.path))
        # We want this initialized regardless of it's it's empty or not
        self.add_stats("metadata", self.metadata)
        if self.metadata != {}:
            logger.trace(f"Merging metadata with stats for {self.name}.")
            study_uid = self.metadata.get("study_uid")
            series_uid = self.metadata.get("series_uid")
            if series_uid is None:
                series_uid = self._generate_series_uid()
            self.add_stats("series_uid", series_uid)
            self.add_stats("study_uid", study_uid)
        # TODO - currently vertebrae midlines will load regardless of the desired stats resolution - which is not correct.
        # If the stats resolution is different from the nifti resolution, we must remeasure the midlines.
        if self.stats.get("vertebrae") is not None:
            self.set_vertebrae_midlines(self.stats["vertebrae"])
        # Placeholder for database stats
        self.db_stats: dict[str, list[dict]] = {}

    def set_task_to_id_map(self, task_to_id_map: dict) -> None:
        self.task_to_id_map = task_to_id_map
        return self

    def set_id_to_seg_map(self, id_to_seg_map: dict) -> None:
        """Set the mapping of task IDs to task names for this nifti."""
        self.id_to_seg_map = id_to_seg_map
        return self

    def set_vertebrae_midlines(self, vertebrae_stats: dict = None):
        """Set the vertebrae midlines for this nifti."""
        if vertebrae_stats is None:
            if "vertebrae" not in self.stats:
                logger.warning(
                    "No vertebrae stats found in nifti. Cannot set vertebrae midlines."
                )
                return self
            vertebrae_stats = self.stats["vertebrae"]
        vertebrae_midlines = {
            k: v.get("midline")
            for k, v in vertebrae_stats.items()
            if isinstance(v, dict)
        }
        self.vertebrae_midlines = vertebrae_midlines
        return self

    def add_stats(self, key: str, value: any, subdict=None) -> None:
        """Add a key-value pair to the stats dictionary."""
        if key in self.stats:
            logger.trace(
                f"Key {key} already exists in stats for {self.path}. Overwriting value."
            )
        if subdict:
            self.stats[subdict][key] = value
        else:
            self.stats[key] = value
        return self

    def preprocess_for_stats(
        self, new_spacing, image_resampler, label_resampler
    ) -> None:
        logger.trace(
            "Resampling image and segmentations for nifti {} to new spacing {} using {} for images and {} for labels",
            self.name,
            new_spacing,
            image_resampler,
            label_resampler,
        )
        self.img = resample_with_sitk(
            self.img,
            new_spacing=new_spacing,
            is_label=False,
            interpolator_type=image_resampler,
            reorient="LAI",
        )
        logger.trace("image resampled")
        self.spacing = self.img.GetSpacing()
        self.shape = self.img.GetSize()
        self.add_stats("stats_resolution", new_spacing)
        new_id_to_seg_map = {}
        for seg_id, seg_path in self.id_to_seg_map.items():
            label = sitk.ReadImage(seg_path)
            resampled_label = resample_with_sitk(
                label,
                is_label=True,
                interpolator_type=label_resampler,
                reference_image=self.img,
            )
            assert resampled_label.GetSize() == self.img.GetSize(), (
                f"Resampled label size {resampled_label.GetSize()} does not match image size {self.img.GetSize()}"
            )
            new_id_to_seg_map[seg_id] = resampled_label
        self.set_id_to_seg_map(new_id_to_seg_map)
        return self

    def check_for_segmentations(self, task_list, task_map):
        task_to_id_map = {}
        id_to_segmentation_map = {}
        # These are the mircat-v1 output file suffixes for these 3 tasks - we just have to remap to the new values
        old_to_new_map = {"total": "999", "tissues": "481", "body": "299"}
        for task in task_list:
            allowed_segmentations = task_map.get(task, [])
            for seg_id in allowed_segmentations:
                seg_file = f"{self.name}_{seg_id}.nii.gz"
                if seg_file in [seg.name for seg in self.segmentations]:
                    if old_to_new_map.get(seg_id, False):
                        logger.debug(f"Flipping {seg_id} to {old_to_new_map[seg_id]}")
                        seg_id = old_to_new_map[seg_id]
                    task_to_id_map[task] = seg_id
                    id_to_segmentation_map[seg_id] = self.seg_folder / seg_file
                    # We break because the task_map is sorted by preference
                    break
        logger.debug(f"{task_to_id_map=}")
        self.set_task_to_id_map(task_to_id_map)
        self.set_id_to_seg_map(id_to_segmentation_map)
        return self

    def save_json_stats(self, gzip_file: bool = False) -> None:
        """Save the statistics to a JSON file."""
        if gzip_file:
            logger.trace(f"Compressing stats file {self.stats_file} with gzip.")
            self.add_stats(
                "output_stats_file",
                str(self.stats_file.with_suffix(".json.gz")),
                "metadata",
            )
            save_stats = {k: self._make_json_serializable(v) for k, v in self.stats.items()}
            with gzip.open(
                self.stats_file.with_suffix(".json.gz"), "wt", encoding="utf-8"
            ) as f:
                json.dump(save_stats, f, indent=2)
        else:
            logger.trace(f"Writing stats file {self.stats_file} without compression")
            self.add_stats("output_stats_file", str(self.stats_file), "metadata")
            save_stats = {k: self._make_json_serializable(v) for k, v in self.stats.items()}
            with self.stats_file.open("w") as f:
                json.dump(save_stats, f, indent=2)

    def _make_json_serializable(self, obj):
        """Convert non-JSON serializable objects to serializable forms."""
        if isinstance(obj, np.ndarray):
                return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._make_json_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            # For custom objects, try to convert to dict
            return self._make_json_serializable(obj.__dict__)
        else:
            return obj  

    def format_stats_for_db(self):
        """Format the stats for database insertion. The output dictionary will have keys matching the table names. This function also has internal functions defined in its scope"""
        stats_tables = [
            key for key in db_schema if key not in ["conversions", "segmentations"]
        ]
        formatted_stats: dict[str, list[tuple]] = {}
        nifti_path = str(self.path)
        series_uid = self.stats.get("series_uid", None)
        identifier = {"nifti": nifti_path, "series_uid": series_uid}
        study_uid = self.stats.get("study_uid", None)
        tables = read_dbase_config().get("tables")

        def _format_metadata() -> list[dict]:
            """Format the metadata for database insertion."""
            metadata = self.stats.get("metadata", {})
            if not metadata:
                logger.debug(f"No metadata found in the stats for {self.path}")
                return []
            columns = list(tables["metadata"].keys())
            row_data = {}
            for col in columns:
                value = metadata.get(col)
                if col == "nifti" and col not in metadata:
                    value = nifti_path
                elif col == "series_uid" and col not in metadata:
                    value = series_uid
                elif col == "study_uid" and col not in metadata:
                    value = study_uid
                # There are some columns that have been renamed that we need to check for
                if value is None:
                    if col == "birth_date":
                        value = metadata.get("birthday")
                    elif col == "pixel_length_mm":
                        value = metadata.get("length_mm")
                    elif col == "pixel_width_mm":
                        value = metadata.get("width_mm")
                    elif col == "age":
                        value = metadata.get("age_at_scan")
                    elif col == "model":
                        value = metadata.get("manufacturer_model")
                row_data[col] = value
            return [row_data]

        def _format_vol_int() -> list[dict]:
            "Format the vol_int data for database insertion"
            vol_int = self.stats.get("vol_int", {})
            if not vol_int:
                logger.debug(f"No vol_int stats found in {self.path}")
                return []
            rows = []
            for structure, stats in vol_int.items():
                rows.append(
                    {
                        **identifier,
                        "structure": structure,
                        "volume_cm3": stats.get("volume_cm3"),
                        "hu_mean": stats.get("hu_mean"),
                        "hu_std_dev": stats.get("hu_std_dev"),
                    }
                )
            return rows

        def _format_contrast() -> list[dict]:
            contrast = self.stats.get("contrast", {})
            if not contrast:
                logger.debug(f"No contrast stats found in {self.path}")
                return []
            return [
                {
                    **identifier,
                    "phase": contrast.get("phase"),
                    "probability": contrast.get("probability"),
                    "pi_time": contrast.get("pi_time"),
                    "pi_time_std": contrast.get("pi_time_std"),
                }
            ]

        def _format_vertebrae() -> list[dict]:
            vertebrae = self.stats.get("vertebrae", {})
            if not vertebrae:
                logger.debug(f"No vertebrae stats found in {self.path}")
                return []
            rows = []
            for vertebra, stats in vertebrae.items():
                rows.append(
                    {
                        **identifier,
                        "vertebra": vertebra,
                        "midline": stats.get("midline"),
                    }
                )
            return rows

        def _format_aorta_metrics() -> list[dict]:
            aorta_metrics = self.stats.get("aorta", {})
            kvp = self.stats.get("metadata", {}).get("kvp", None)
            if kvp is None:
                pass
            elif kvp == 120:
                kvp = 1
            else:
                kvp = 0
            if not aorta_metrics:
                logger.debug(f"No aorta metrics found in {self.path}")
                return []
            rows = []
            for region, stats in aorta_metrics.items():
                rows.append(
                    {
                        **identifier,
                        "region": region,
                        "entire_region": stats.get("entire_region"),
                        "length_mm": stats.get("length_mm"),
                        "tortuosity_index": stats.get("tortuosity_index"),
                        "icm": stats.get("icm"),
                        "n_inflections": stats.get("n_inflections"),
                        "peria_volume_cm3": stats.get("peria_volume_cm3"),
                        "peria_ring_volume_cm3": stats.get("peria_ring_volume_cm3"),
                        "peria_fat_volume_cm3": stats.get("peria_fat_volume_cm3"),
                        "peria_hu_mean": stats.get("peria_hu_mean"),
                        "peria_hu_std": stats.get("peria_hu_std"),
                        "calc_volume_mm3": stats.get("calc_volume_mm3"),
                        "calc_agatston": stats.get("calc_agatston"),
                        "calc_count": stats.get("calc_count"),
                        "is_120_kvp": kvp,
                        "mean_diameter_mm": stats.get("mean", {}).get("diameter"),
                        "mean_roundness": stats.get("mean", {}).get("roundness"),
                        "mean_flatness": stats.get("mean", {}).get("flatness"),
                    }
                )
            return rows

        def _format_aorta_diameters() -> list[dict]:
            aorta_metrics = self.stats.get("aorta", {})
            if not aorta_metrics:
                logger.debug(f"No aorta diameters found in {self.path}")
                return []
            rows = []
            measure_keys = ["max", "min", "mid", "proximal", "distal"]
            for region, stats in aorta_metrics.items():
                if region == "whole":
                    continue  # Skip the whole aorta region
                entire_region = stats.get("entire_region")
                for measure in measure_keys:
                    if measure not in stats:
                        continue
                    measure_stats = stats[measure]
                    rows.append(
                        {
                            **identifier,
                            "region": region,
                            "measure": measure,
                            "mean_diameter_mm": measure_stats.get("mean_diameter"),
                            "major_diameter_mm": measure_stats.get("major_diameter"),
                            "minor_diameter_mm": measure_stats.get("minor_diameter"),
                            "area_mm2": measure_stats.get("area"),
                            "roundness": measure_stats.get("roundness"),
                            "flatness": measure_stats.get("flatness"),
                            "rel_distance": measure_stats.get("rel_distance"),
                            "entire_region": entire_region,
                        }
                    )
            return rows

        def _format_tissues_volumetric() -> list[dict]:
            volumetric = self.stats.get("tissues", {}).get("volumetric", {})
            if not volumetric:
                logger.debug(f"No tissue volumetric stats found in {self.path}")
                return []
            rows = []
            for region, stats in volumetric.items():
                for structure, structure_stats in stats.items():
                    rows.append(
                        {
                            **identifier,
                            "region": region,
                            "structure": structure,
                            "volume_cm3": structure_stats.get("volume_cm3"),
                            "hu_mean": structure_stats.get("hu_mean"),
                            "hu_std_dev": structure_stats.get("hu_std_dev"),
                        }
                    )
            return rows

        def _format_tissues_vertebral() -> list[dict]:
            vertebral = self.stats.get("tissues", {}).get("vertebral", {})
            if not vertebral:
                logger.debug(f"No tissue vertebral stats found in {self.path}")
                return []
            rows = []
            for vertebra, stats in vertebral.items():
                for structure, structure_stats in stats.items():
                    for measure, value in structure_stats.items():
                        rows.append(
                            {
                                **identifier,
                                "vertebra": vertebra,
                                "structure": structure,
                                "measurement": measure,
                                "value": value,
                            }
                        )
            return rows

        def _format_iliac() -> list[dict]:
            rows = []
            iliac = self.stats.get("iliac", {})
            if not iliac:
                logger.debug(f"No iliac stats found in {self.path}")
                return rows
            for side, data in iliac.items():
                length_mm = data.pop("length_mm", 0.0)
                for location, metrics in data.items():
                    for metric, value in metrics.items():
                        rows.append(
                            {
                                **identifier,
                                "side": side,
                                "length_mm": length_mm,
                                "location": location,
                                "metric": metric,
                                "value": value,
                            }
                        )
            return rows

        for table in stats_tables:
            match table:
                case "metadata":
                    table_data = _format_metadata()
                case "vol_int":
                    table_data = _format_vol_int()
                case "contrast":
                    table_data = _format_contrast()
                case "vertebrae":
                    table_data = _format_vertebrae()
                case "aorta_metrics":
                    table_data = _format_aorta_metrics()
                case "aorta_diameters":
                    table_data = _format_aorta_diameters()
                case "tissues_volumetric":
                    table_data = _format_tissues_volumetric()
                case "tissues_vertebral":
                    table_data = _format_tissues_vertebral()
                case "iliac":
                    table_data = _format_iliac()
            formatted_stats[table] = table_data
        self.db_stats = formatted_stats
        return self


def resample_with_sitk(
    image,
    new_spacing=None,
    new_size=None,
    is_label=False,
    interpolator_type="gaussian",
    reference_image=None,
    reorient=None,
) -> sitk.Image:
    """Resample a SimpleITK image to a new spacing, size, or reference image.
    :param image: The SimpleITK image to resample.
    :param new_spacing: The new spacing to resample to. If None, the original
        spacing will be used to calculate the new size.
    :param new_size: The new size to resample to. If None, the original
        size will be used to calculate the new spacing.
    :param is_label: Whether the image is a label image. If True, the
        resampling will use label-specific interpolators.
    :param interpolator_type: The type of interpolator to use for resampling.
        Options are 'gaussian', 'linear', 'nearest' for label images, and
        'lanczos', 'bspline', 'gaussian', 'linear' for regular images.
    :param reference_image: An optional reference image to use for resampling.
        If provided, the new spacing and size will be taken from this image.
    :param reorient: The CT orientation to reorient the image to. If None, no reorientation is applied.
    :return: The resampled SimpleITK image."""
    # Get original properties
    original_spacing = image.GetSpacing()
    original_size = image.GetSize()

    resampler = sitk.ResampleImageFilter()
    if reference_image is not None:
        resampler.SetReferenceImage(reference_image)
    else:
        if new_spacing is not None and new_size is not None:
            raise ValueError("Only one of new_spacing and new_size may be specified")
        # Calculate new size based on spacing change
        if new_spacing is not None:
            new_size = [
                int(original_size[i] * original_spacing[i] / new_spacing[i])
                for i in range(3)
            ]
        elif new_size is not None:
            new_spacing = [
                original_spacing[i] * original_size[i] / new_size[i] for i in range(3)
            ]
        else:
            raise ValueError("Must specify either a new_size or new_spacing")
        #    Set up resampling parameters
        resampler.SetOutputSpacing(new_spacing)
        resampler.SetSize(new_size)
        resampler.SetOutputDirection(image.GetDirection())
        resampler.SetOutputOrigin(image.GetOrigin())
        resampler.SetTransform(sitk.Transform())
        resampler.SetDefaultPixelValue(0)

    if is_label:
        if interpolator_type == "gaussian":
            interpolator = sitk.sitkLabelGaussian
        elif interpolator_type == "linear":
            interpolator = sitk.sitkLabelLinear
        elif interpolator_type == "nearest":
            interpolator = sitk.sitkNearestNeighbor
        else:
            raise ValueError(
                f"label interpolator must be in [gaussian, linear, nearest], got {interpolator_type}"
            )
        resampler.SetInterpolator(interpolator)
    else:
        if interpolator_type == "lanczos":
            interpolator = sitk.sitkLanczosWindowedSinc
        elif interpolator_type == "bspline":
            interpolator = sitk.sitkBSpline
        elif interpolator_type == "gaussian":
            interpolator = sitk.sitkGaussian
        elif interpolator_type == "linear":
            interpolator = sitk.sitkLinear
        else:
            raise ValueError(
                f"image interpolator must be in [lanczos, gaussian, linear], got {interpolator_type}"
            )
        resampler.SetInterpolator(interpolator)
    resampled_image = resampler.Execute(image)
    if reorient is not None:
        current_orientation = (
            sitk.DICOMOrientImageFilter_GetOrientationFromDirectionCosines(
                resampled_image.GetDirection()
            )
        )
        if current_orientation != reorient:
            logger.trace(f"Reorienting image from {current_orientation} to {reorient}.")
            reorienter = sitk.DICOMOrientImageFilter()
            reorienter.SetDesiredCoordinateOrientation(reorient)
            resampled_image = reorienter.Execute(resampled_image)
    return resampled_image


def load_nifti_paths(input_arg: Path, data_dir: Path) -> list[Path]:
    """Store either the contents of the input text file or the input nifti as a list of nifti paths
    Parameters
        input_arg: Path - the input argument path
        data_dir: Path - the data directory to prepend to the nifti file name {data_dir} / {nifti_path}
    Returns:
        A list of paths containing the nifti files in the input
    """
    single_file_suffixes = set([".nii", ".gz"])
    # Input arg must exist
    if not input_arg.exists():
        raise FileNotFoundError(
            f"Input argument {input_arg} does not exist. Please check path."
        )
    # If it's a single file - just prepend the data dir and return
    if set(input_arg.suffixes).intersection(single_file_suffixes):
        logger.info(f"Found input nifti {data_dir / input_arg}")
        return [data_dir / input_arg]
    # Otherwise we load the file and validate
    with input_arg.open() as f:
        niftis = [data_dir / Path(line.strip()) for line in f.readlines()]
    if len(niftis) == 0:
        raise ValueError(
            f"Nifti list file {input_arg} is empty. Please check contents."
        )
    logger.info(f"Found {len(niftis)} nifti files to analyze in {input_arg}")
    return niftis


class NotNiftiFileError(ValueError):
    pass


class SimpleITKReadError(ValueError):
    pass
