import sys
import pprint

from pathlib import Path

from loguru import logger

from mircat_v2.configs import (
    read_models_config,
    read_dbase_config,
    set_threads_per_process,
)
from mircat_v2.nifti import load_nifti_paths

lib_path = Path(__file__).parent.resolve()


def add_segmentation_subparser(subparsers):
    """Add segmentation specific subcommands to mircat-v2 cli interface
    :param subparsers: the subparser for CLI
    """
    # Add subcommands for segmentation itself
    seg_parser = subparsers.add_parser(
        "segment",
        description="""Segment nifti files using nnUNet - accelerated by GPU if available. \
            Input files will be resampled and stored in temporary files to accelerate nnUNet. \
            Make sure you have enough disk space for resampled images!""",
        help="Segment nifti files using nnUNet models.",
    )
    seg_parser.add_argument(
        "niftis",
        type=Path,
        help="Path to a nifti file or a text file containing a list of nifti files",
    )
    seg_parser.add_argument(
        "--data-dir",
        "-d",
        type=Path,
        default=Path(""),
        help="Data directory for the input niftis (i.e. {data_dir}/nifti_path) - useful for remapping in docker. Default is no data directory.",
    )
    seg_parser.add_argument(
        "-tl",
        "--task-list",
        type=str,
        nargs="+",
        required=True,
        help="Space separated list of segmentation model tasks to perform. Identified by nnUNet dataset number. Use mircat-v2 models list to see all available tasks.",
    )
    seg_parser.add_argument(
        "-m",
        "--model-types",
        type=str,
        nargs="+",
        default=["3d"],
        choices=["2d", "3d", "3d_lowres", "3d_cascade"],
        help="Default = 3d for all tasks. The nnUNet model subtype to run for each task, space separated.",
    )
    seg_parser.add_argument(
        "--device",
        "-dv",
        type=str,
        default="cuda:0",
        help="Device for pytorch/nnunet to use for segmentation. Default is cuda:0",
    )
    seg_parser.add_argument(
        "-n",
        "--n-processes",
        type=int,
        default=1,
        help="Default = 1. Number of processes to use for pre/post processing the images.",
    )
    seg_parser.add_argument(
        "-t",
        "--threads-per-process",
        type=int,
        default=4,
        help="Default = 4. Maximum number of threads each process should use.",
    )
    seg_parser.add_argument(
        "-c",
        "--cache-size",
        type=int,
        default=10,
        help="The number of nifti files to work on at one time. Default = 10. This includes saving preprocessed files to disk, so be mindful of storage.",
    )
    seg_parser.add_argument(
        "-db",
        "--dbase-insert",
        action="store_true",
        help="Store model results (completed/failed for each nifti) in the mircat-v2 database. Must be setup!",
    )
    seg_parser.add_argument(
        "-ir",
        "--image-resampler",
        type=str,
        choices=["lanczos", "bspline", "gaussian", "linear"],
        default="bspline",
        help="Interpolator for resampling original images. Default = bspline (speed and quality balance)",
    )
    seg_parser.add_argument(
        "-lr",
        "--label-resampler",
        type=str,
        choices=["gaussian", "linear", "nearest"],
        default="gaussian",
        help="Interpolator for resampling segmentation images. Default = gaussian (slowest but best)",
    )


def segment_nifti_files(args):
    try:
        from mircat_v2.segmentation.segmentor import MircatSegmentor
    except ModuleNotFoundError as e:
        logger.error(
            "Could not import the segmentation module. Please make sure you have installed mircat-v2 with `pip install mircat-v2[seg]`."
        )
        raise e
    logger.debug(
        "Starting segmentation process with the following args:\n{}",
        pprint.pformat(args),
    )
    task_configs = read_models_config()
    _validate_segmentation_args(task_configs, args)
    niftis = load_nifti_paths(args.niftis, args.data_dir)
    segmentor = MircatSegmentor(
        niftis=niftis,
        task_list=args.task_list,
        model_types=args.model_types,
        device=args.device,
        task_configs=task_configs,
        n_processes=args.n_processes,
        threads_per_process=args.threads_per_process,
        cache_size=args.cache_size,
        dbase_config=args.dbase_config,
        img_resampler=args.image_resampler,
        lbl_resampler=args.label_resampler,
    )
    segmentor.run()


def _validate_segmentation_args(task_configs: dict, args):
    """Internal function to validate the given arguments for nnUNet segmentation
    :param model_configs: the internal configuration file for mircat-v2 loaded as a dictionary
    :param args: the passed input parameters
    """
    # Make sure the input argument for the nifti file(s) exists
    args.niftis = args.niftis.resolve()
    if not args.niftis.exists():
        logger.error(
            f"The input nifti file/list of files {args.niftis} does not exist. Please double check your paths."
        )
        sys.exit(1)
    available_models = list(task_configs.keys())
    # Make sure all tasks are available
    if not all([task in available_models for task in args.task_list]):
        missing_tasks = [
            task for task in args.task_list if task not in available_models
        ]
        logger.error(
            "The following tasks are missing from mircat-v2 config file {}. Please use `mircat-v2 models add` to place them in the correct location.",
            missing_tasks,
        )
        sys.exit(1)
    # If only one model type was given, apply it for all tasks
    if len(args.model_types) == 1:
        model_type = args.model_types[0]
        logger.debug(
            "One model type passed to --model-types. Will apply for all given tasks."
        )
        args.model_types = [model_type for task in args.task_list]
    # Ensure that each task has a specified model type
    if len(args.model_types) != len(args.task_list):
        logger.error(
            f"Number of model type parameters must match the number of tasks. Currently have {len(args.model_types)} model types and {len(args.task_list)} tasks.\n\t\
            Please either specify one model type [3d, 2d, 3d_lowres, 3d_casade] for all tasks or have a specific model type for each task."
        )
        sys.exit(1)
    # Ensure that each task has weights for the specific model type
    for task, model in zip(args.task_list, args.model_types):
        model_weights = task_configs[task]["models"].get(model, dict())
        logger.debug(f"{task} configurations: {model_weights}")
        if not model_weights:
            logger.error(f"No {model} configuration found for task {task}.")
            sys.exit(1)
    # Check if the mircat-v2 dbase exists.
    if args.dbase_insert:
        args.dbase_config = read_dbase_config()
    else:
        args.dbase_config = {}

    set_threads_per_process(args)
