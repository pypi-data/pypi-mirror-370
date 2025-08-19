from pathlib import Path
from math import floor
from multiprocessing import cpu_count
from loguru import logger

from mircat_v2.configs import set_threads_per_process
from mircat_v2.nifti import load_nifti_paths


def add_stats_subparser(subparsers):
    stats_parser = subparsers.add_parser(
        "stats",
        help="Calculate statistics on segmentation files",
        description="Calculate statistics on segmentation files in a directory.",
    )
    stats_parser.add_argument(
        "niftis",
        type=Path,
        help="Path to a nifti file with mircat-v2 segmentations or a text file with a list of multiple mircat-v2 nifti files.",
    )
    stats_parser.add_argument(
        "--data-dir",
        "-d",
        type=Path,
        default=Path(""),
        help="Data directory for the input niftis (i.e. {data_dir}/nifti_path) - useful for remapping in docker. Default is no data directory.",
    )
    stats_parser.add_argument(
        "--task-list",
        "-tl",
        type=str,
        nargs="+",
        default=["all"],
        choices=[
            "all",
            "vol-int",
            "contrast",
            "vertebrae",
            "aorta",
            "tissues",
            "iliac",
        ],
        help="List of tasks to calculate statistics for. Default is 'all'. vol-int: volume and intensity statistics, contrast: contrast phase prediction, aorta: aorta specific statistics, tissues: tissue segmentation statistics., iliac: iliac artery diameters and areas",
    )
    stats_parser.add_argument(
        "--resolution",
        "-r",
        type=str,
        choices=["normal", "high", "highest"],
        default="normal",
        help="Isotropic Resolution to transpose images and labels to for statistics. 'normal' is 1mm, 'high' is 0.75mm, and 'highest' is 0.5mm. Default is 'normal'.",
    )
    stats_parser.add_argument(
        "--image-resampler",
        "-ir",
        type=str,
        choices=["lanczos", "bspline", "gaussian", "linear"],
        default="bspline",
        help="Image resampling method to use for statistics. 'bspline' is the default and strikes the best balance between speed and quality. 'lanczos' is the slowest, but has the best quality. 'gaussian' is faster and good for most cases, 'linear' is the fastest but may not be suitable for all images.",
    )
    stats_parser.add_argument(
        "--label-resampler",
        "-lr",
        type=str,
        choices=["gaussian", "linear", "nearest"],
        default="gaussian",
        help="Label resampling method to use for statistics. 'gaussian' is the default and slowest, 'linear' is faster but has lower resolution, 'nearest' is the fastest but may not be suitable for all labels.",
    )
    stats_parser.add_argument(
        "--n-processes",
        "-n",
        type=int,
        default=1,
        help="Number of processes to use for parallel processing. Default is 1 (only one process).",
    )
    stats_parser.add_argument(
        "--threads-per-process",
        "-t",
        type=int,
        default=4,
        help="Number of threads per process for multithreaded processing for python libraries. Default is 4.",
    )
    stats_parser.add_argument(
        "--dbase-insert",
        "-db",
        action="store_true",
        help="Insert the calculated statistics into the database. Requires a database to be set up with mircat-v2 dbase create command. Default is False (do not insert into database).",
    )
    stats_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing stats files if they exist. Default is False (do not overwrite).",
    )
    stats_parser.add_argument(
        "--gzip",
        action="store_true",
        help="Compress the output json stats file with gzip. Default is False (do not compress).",
    )


def run_stats(args):
    """Run the statistics calculation on the provided NiFTi files."""
    from mircat_v2.stats.analyzer import Analyzer

    # Set up threads per process
    set_threads_per_process(args)
    logger.debug("Input arguments: {}", args)
    niftis = load_nifti_paths(args.niftis, args.data_dir)
    analyzer = Analyzer(
        niftis=niftis,
        task_list=args.task_list,
        resolution=args.resolution,
        image_resampler=args.image_resampler,
        label_resampler=args.label_resampler,
        n_processes=args.n_processes,
        threads_per_process=args.threads_per_process,
        dbase_insert=args.dbase_insert,
        overwrite=args.overwrite,
        gzip=args.gzip,
    )
    analyzer.run()
