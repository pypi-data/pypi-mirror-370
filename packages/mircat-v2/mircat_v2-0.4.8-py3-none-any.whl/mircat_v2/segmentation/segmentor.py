import os
import torch
import SimpleITK as sitk

from multiprocessing import Pool
from datetime import date
from pathlib import Path
from loguru import logger
from nnunetv2.inference.predict_from_raw_data import nnUNetPredictor
from threadpoolctl import threadpool_limits

from mircat_v2.configs import read_models_config
from mircat_v2.dbase import insert_data_batch
from mircat_v2.nifti import SegNifti, resample_with_sitk


class MircatSegmentor:
    def __init__(
        self,
        niftis: list[Path],
        task_list: list[str],
        model_types: list[str],
        device: str,
        task_configs: dict | None = None,
        n_processes: int = 1,
        threads_per_process: int = 4,
        cache_size: int = 1,
        dbase_config: dict = {},
        img_resampler: str = "bspline",
        lbl_resampler: str = "gaussian",
    ):
        """Initialize segmentor tasks.
        :param task_list: list of all desired segmentation tasks
        :param model_types: list of task model types [3d, 2d, etc.]'
        :param device: the device for pytorch to use
        :param task_configs: dictionary containing task configs. If not passed, will load from library.
        :param n_processes: the number of workers for preprocessing, nnUNet, and postprocessing
        :param threads_per_process: the number of threads each worker can use.
        :param cache_size: Number of nifti files to work on at one time. Default = 1.
        :param dbase_config: dictionary containing database configuration. If empty, no database insertion will be performed.
        :param img_resampler: the type of resampling to use for images, default is "bspline"
        :param lbl_resampler: the type of resampling to use for labels, default is "gaussian"
        """
        self.niftis = niftis
        self.task_list = task_list
        self.model_types = model_types
        self.device = device
        self.n_processes = n_processes
        self.threads_per_process = threads_per_process
        self.cache_size = cache_size
        self.dbase_config = dbase_config
        self.dbase_insert = not dbase_config == {}
        self.img_resampler = img_resampler
        self.lbl_resampler = lbl_resampler
        # Logic for loading task configurations
        if isinstance(task_configs, dict):
            self.task_configs = task_configs
        elif task_configs is None:
            self.task_configs = read_models_config()
        else:
            message = "task_configs argument must be a dictionary or None."
            logger.error(message)
            raise ValueError(message)
        # Get the voxel spacings for each task/model type pair
        self.task_spacings = {
            task: tuple(self.task_configs[task]["models"][model]["spacing"])
            for task, model in zip(task_list, model_types)
        }

        self.task_model_paths = {
            task: self.task_configs[task]["models"][model]["path"]
            for task, model in zip(task_list, model_types)
        }

    def run(self):
        """Summary method to run all specified tasks on all given niftis
        :param niftis: path to either a single nifti file or a text file containing paths (preferably absolute paths) to all niftis for segmentation.
        """
        self._get_nifti_batches()
        for i, nifti_batch in enumerate(self.nifti_batches, start=1):
            self.current_batch = i
            self.run_batch(nifti_batch)

    def run_batch(self, nifti_batch: list[Path]):
        good_niftis, bad_niftis = self._load_nifti_batch(nifti_batch)
        self.niftis_to_segment = good_niftis
        self.failed_niftis = bad_niftis
        self._preprocess_batch()
        self._run_tasks()
        self._postprocess_batch()
        if self.dbase_insert:
            self._insert_batch_to_dbase()
        logger.success(
            "Batch [{}/{}] segmentation complete!",
            self.current_batch,
            self.total_batches,
        )
        # logic for uploading bad_nifti results to dbase

    def _load_nifti_batch(self, nifti_batch: list[Path]):
        """Load niftis in the batch and filter out bad ones
        :param nifti_batch: the list of nifti paths
        """
        good_niftis = []
        bad_niftis = []
        for nifti_path in nifti_batch:
            try:
                nifti = SegNifti(nifti_path)
                good_niftis.append(nifti)
            except Exception as e:
                bad_niftis.append(
                    {
                        "nifti": str(nifti_path),
                        "seg_date": date.today().isoformat(),
                        "status": "FAILED",
                        "failed_error": type(e).__name__,
                    }
                )
        logger.debug(
            f"Found {len(good_niftis)} niftis able to be loaded by SimpleITK for segmentation, failed to load {len(bad_niftis)} niftis."
        )
        return good_niftis, bad_niftis

    def _preprocess_batch(self) -> None:
        """Preprocess each nifti in a batch by writing each necessary temporary file
        :param good_niftis: the list of pre-validated Niftis instances from _load_nifti_batch
        """
        preprocessed = []
        logger.info(
            "Starting preprocessing for batch [{}/{}]",
            self.current_batch,
            self.total_batches,
        )
        with Pool(self.n_processes) as pool:
            for i, nifti in enumerate(
                pool.imap_unordered(self._preprocess_nifti, self.niftis_to_segment),
                start=1,
            ):
                preprocessed.append(nifti)
                logger.info(
                    "Batch [{}/{}]: [{}/{}] preprocessed",
                    self.current_batch,
                    self.total_batches,
                    i,
                    len(self.niftis_to_segment),
                )
        logger.success(
            f"Batch [{self.current_batch}/{self.total_batches}] preprocessed!"
        )
        self.niftis_to_segment = preprocessed

    def _preprocess_nifti(self, nifti: SegNifti) -> SegNifti:
        """Preprocess a single nifti file for segmentation by creating the necessary spacing files and storing the information
        :param nifti: An instance of the Nifti class
        """
        limits = threadpool_limits(self.threads_per_process)
        sitk.ProcessObject.SetGlobalDefaultNumberOfThreads(self.threads_per_process)
        with limits:
            if not nifti.seg_folder.exists():
                logger.debug("Making segmentation folder {}", nifti.seg_folder)
                nifti.seg_folder.mkdir()
            else:
                logger.debug(
                    "Segmentation folder aready found for {}", nifti.seg_folder
                )
            preprocessed_files = {}
            for task, spacing in self.task_spacings.items():
                spacing_str: str = "_".join([str(x) for x in spacing])
                preprocessed_file: Path = (
                    nifti.seg_folder / f"{nifti.name}_{spacing_str}.nii.gz"
                )
                output_file: Path = (
                    nifti.seg_folder / f"{nifti.name}_{spacing_str}_{task}"
                )
                if not preprocessed_file.exists():
                    logger.debug(f"Making {preprocessed_file} for task {task}..")
                    nifti.resample_and_save_for_segmentation(
                        spacing, preprocessed_file, self.img_resampler
                    )
                else:
                    logger.debug(
                        f"Preprocessed file {preprocessed_file} already exists for task {task}."
                    )
                preprocessed_files[task] = {
                    "input": preprocessed_file,
                    "output": output_file,
                }
            nifti.task_files = preprocessed_files
            return nifti

    def _get_nifti_batches(self) -> None:
        """Ensure that the input niftis are in the correct format. If the input is a text file, we read the contents to get the paths of all niftis."""
        self.nifti_batches = [
            self.niftis[i : i + self.cache_size]
            for i in range(0, len(self.niftis), self.cache_size)
        ]
        self.total_batches = len(self.nifti_batches)
        logger.info(
            f"Running tasks {self.task_list} on {len(self.nifti_batches)} batches of {self.cache_size} niftis per batch."
        )

    def _run_tasks(self):
        if self.device != "cpu":
            # nnUNet compile only seems to want to work with GPUs
            os.environ["nnUNet_compile"] = "True"
        device = torch.device(self.device)
        logger.info("Running on torch.device {}", device)
        for task in self.task_list:
            logger.info("Starting task {} with nnUNet", task)
            input_files = [
                [str(nifti.task_files.get(task).get("input"))]
                for nifti in self.niftis_to_segment
            ]
            output_files = [
                str(nifti.task_files.get(task).get("output"))
                for nifti in self.niftis_to_segment
            ]
            predictor = nnUNetPredictor(
                tile_step_size=0.5,
                use_gaussian=True,
                use_mirroring=False,
                perform_everything_on_device=True if self.device != "cpu" else False,
                device=device,
                verbose=False,
                verbose_preprocessing=False,
                allow_tqdm=True,
            )
            model_path = self.task_model_paths.get(task)
            if not isinstance(model_path, str) or not model_path:
                raise ValueError(
                    f"Model path for task '{task}' is missing or not a string."
                )
            predictor.initialize_from_trained_model_folder(
                model_path,
                use_folds=(0,),
                checkpoint_name="checkpoint_final.pth",
            )
            predictor.predict_from_files(
                input_files,
                output_files,
                save_probabilities=False,
                overwrite=True,
                num_processes_preprocessing=self.n_processes,
                num_processes_segmentation_export=self.n_processes,
            )
            del predictor

    def _postprocess_batch(self):
        n_niftis = len(self.niftis_to_segment)
        completed = []
        with Pool(self.n_processes) as pool:
            for i, dbase_insert in enumerate(
                pool.imap_unordered(self._postprocess_nifti, self.niftis_to_segment),
                start=1,
            ):
                completed.extend(dbase_insert)
                logger.info(
                    f"Batch [{self.current_batch}/{self.total_batches}]: {i}/{n_niftis} postprocessed"
                )
        self.completed_niftis = completed

    def _postprocess_nifti(self, nifti: SegNifti):
        sitk.ProcessObject.SetGlobalDefaultNumberOfThreads(self.threads_per_process)
        dbase_insert = []
        with threadpool_limits(self.threads_per_process):
            for task, task_files in nifti.task_files.items():
                input_nifti = task_files["input"]
                tmp_output_nifti = Path(f"{task_files['output']}.nii.gz")
                resampled_name = nifti.seg_folder / f"{nifti.name}_{task}.nii.gz"
                # Delete the preprocessed input
                if input_nifti.exists():
                    input_nifti.unlink()
                # Resample the output and create the new output file, delete the old after
                if tmp_output_nifti.exists():
                    lbl = sitk.ReadImage(str(tmp_output_nifti))
                    new_lbl = resample_with_sitk(
                        lbl,
                        new_size=nifti.shape,
                        is_label=True,
                        interpolator_type=self.lbl_resampler,
                    )
                    sitk.WriteImage(new_lbl, resampled_name)
                    logger.debug("successfully wrote {}", resampled_name)
                    tmp_output_nifti.unlink()
                else:
                    logger.warning(f"Output file {tmp_output_nifti} not found!")
                dbase_task = {
                    "nifti": str(nifti.path),
                    "series_uid": nifti.metadata.get("series_uid"),
                    "task": int(task),
                    "seg_file": str(resampled_name),
                    "seg_date": date.today().isoformat(),
                    "status": "SUCCESS",
                    "failed_error": None,
                }
                dbase_insert.append(dbase_task)
        return dbase_insert

    def _insert_batch_to_dbase(self):
        logger.info(
            "Batch [{}/{}]: Inserting results into mircat-v2 database",
            self.current_batch,
            self.total_batches,
        )
        insert_data_batch(self.dbase_config, "segmentations", self.completed_niftis)
        logger.debug(
            "Batch [{}/{}]: completed niftis successfully inserted",
            self.current_batch,
            self.total_batches,
        )
        insert_data_batch(self.dbase_config, "segmentations", self.failed_niftis)
        logger.debug(
            "Batch [{}/{}]: failed niftis successfully inserted",
            self.current_batch,
            self.total_batches,
        )
        logger.success(
            "Batch [{}/{}]: Results have been inserted into mircat-v2 database!",
            self.current_batch,
            self.total_batches,
        )
