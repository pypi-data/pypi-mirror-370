import json
import pprint
from argparse import ArgumentParser
from pathlib import Path
from shutil import copytree

from loguru import logger
from mircat_v2.configs import write_config, read_models_config

models_path = Path(__file__).parent.resolve()


def add_models_subparser(subparsers: ArgumentParser) -> None:
    """Add the model subcommand to mircat-v2 cli interface
    Parameters:
        subparsers: ArgumentParser - the main parser from mircat_v2.main
    """
    # Model specific operations
    models_parser = subparsers.add_parser(
        "models",
        description="""List models available, copy new models to the correct mircat-v2 location, or update the config file for segmentation""",
        help="List, add or update models available to mircat-v2.",
    )
    models_subparser = models_parser.add_subparsers(dest="models_command")
    list_subparser = models_subparser.add_parser(
        "list",
        help="List tasks and their descriptions currently available to mircat-v2.",
    )
    list_subparser.add_argument(
        "-t",
        "--task",
        type=str,
        default="all",
        help="Specific task number to list configuration for. Default is to show all tasks.",
    )
    add_command = models_subparser.add_parser(
        "add",
        description="Add nnUNet model(s) to mircat-v2 options.",
        help="Add nnUNet model or folder of nnUNet models to mircat library",
    )
    add_command.add_argument(
        "folder",
        type=Path,
        help="Path to nnUNet model or folder containing multiple nnUNet models. \
            Should either be in the format DatasetXXX_* or be a folder containing folders in that format.",
    )
    add_command.add_argument(
        "--overwrite",
        action="store_true",
        help="If a model task already exists in the mircat models file, overwrite it.",
    )
    models_subparser.add_parser("update", help="Update the model configurations file.")


def _get_available_models():
    task_folders = sorted(models_path.glob("Dataset*/"))
    logger.debug(
        """Found {} models in {}. They are:\n{}""",
        len(task_folders),
        str(models_path),
        pprint.pformat([str(x.name) for x in task_folders]),
    )
    if len(task_folders) == 0:
        raise FileNotFoundError(
            f"No folders found in {models_path}. Use mircat-v2 models copy to copy in some nnUNet models!"
        )
    return task_folders


def update_models_config():
    # We call them tasks as this is the nnUNet style - Dataset###_descriptor
    task_folders = _get_available_models()
    # The keys here are what UNet calls each model type
    # The values are what we will use as flags to select a model
    unet_configs = {
        "2d": "2d",
        "3d_fullres": "3d",
        "3d_lowres": "3d_lowres",
        "3d_cascade_fullres": "3d_cascade",
    }
    model_configs = {}
    for folder in task_folders:
        splits = folder.name.split("_")
        task = splits[0].replace("Dataset", "")
        description = "_".join(splits[1:])
        task_models = sorted(folder.glob("*/"))
        logger.debug(f"Task: {task}, Models: {task_models}")
        task_config = {"description": description, "models": {}}
        if len(task_models) == 0:
            logger.warning(f"No model options found in {folder}.")
            continue
        # Pull a reference model
        ref_model = task_models[0]
        if not (ref_model / "dataset.json").exists():
            logger.error(f"No dataset info found for {folder}. Skipping.")
            continue
        if not (ref_model / "plans.json").exists():
            logger.error(f"No model plans found for {folder}. Skipping.")
        with (ref_model / "dataset.json").open() as f:
            dataset = json.load(f)
        with (ref_model / "plans.json").open() as f:
            plans = json.load(f)
            configs = plans["configurations"]
        labels = dataset.get("labels")
        task_config["labels"] = labels
        # Get all of the nnUNet model options for the task that are available.
        for unet_config, option in unet_configs.items():
            for model in task_models:
                if unet_config in model.name:
                    model_specific_config = configs.get(unet_config)
                    task_config["models"][option] = {
                        "path": str(model),
                        "patch_size": model_specific_config.get("patch_size"),
                        "spacing": model_specific_config.get("spacing"),
                    }
        model_configs[task] = task_config
    write_config(model_configs, "models")


def add_models_to_mircat(args) -> None:
    folder: Path = args.folder
    overwrite: bool = args.overwrite
    if overwrite:
        confirmed = input(
            "Overwrite option was given to copy command. Are you sure you want to overwrite existing models? (y/n) "
        )
        confirmed = confirmed == "y"
        if not confirmed:
            logger.info("Aborting copy operation.")
            return

    folder = folder.resolve()
    if not folder.is_dir():
        logger.error(
            f"Given path {folder} is not a folder. Please make sure you are passing an nnUNet folder."
        )
        return
    if not any(folder.iterdir()):
        logger.error(
            f"Folder {folder} is empty. Please check that your path is correct."
        )
        return
    logger.info(f"Copying models from {folder} to {models_path}.")
    if folder.name.startswith("Dataset"):
        logger.info(f"Found 1 model to copy: {folder}")
        logger.info(f"Copying {folder} to {models_path}")
        destination = models_path / folder.name
        copytree(folder, destination, dirs_exist_ok=overwrite)
        logger.success(
            f"{folder} succesfully copied to mircat-v2 models. Updating config."
        )
    else:
        models = list(folder.glob("*/Dataset*"))
        n_models = len(models)
        if n_models == 0:
            logger.error(
                f"No models found in {folder}. Please make sure the input is either of format 'DatasetXXX_*' or folder/DatasetXXX_*"
            )
            return
        model_tasks = {
            model.name.split("_")[0].replace("Dataset", ""): model for model in models
        }
        logger.info(
            f"Found {n_models} models to copy in {folder} - Task numbers are {', '.join(model_tasks.keys())}"
        )
        for i, (task, model_path) in enumerate(model_tasks.items(), start=1):
            destination = models_path / model_path.name
            copytree(model_path, destination, dirs_exist_ok=overwrite)
            logger.success(
                f"{i}/{n_models} - Succesfully copied task {task} from {model_path} to mircat library."
            )
        logger.info("All models copied. Updating config.")
    update_models_config()


def list_mircat_models(args):
    configs = read_models_config()
    if args.task == "all":
        pprint.pprint(configs, indent=2, sort_dicts=False)
        return
    else:
        subdict = configs.get(args.task)
        if subdict is None:
            logger.error(
                f"Task number {args.task} not found in model configs. Available tasks are\n\t{list(configs.keys())}",
            )
            return
        pprint.pprint(subdict, indent=2, sort_dicts=False)
