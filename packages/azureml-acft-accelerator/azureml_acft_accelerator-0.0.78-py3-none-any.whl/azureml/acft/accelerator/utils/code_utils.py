# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
code utils
"""


from pathlib import Path
import shutil
from typing import List, Dict
import json

from azureml.acft.common_components import get_logger_app


logger = get_logger_app(__name__)


def get_absolute_path(relative_path: str):
    """returns absolute path of a given path"""
    return str(Path(relative_path).resolve())


def get_model_custom_code_files(model_name_or_path: str, model):
    """return list of custom code files from model directory"""

    code_files_list = []

    if Path(model_name_or_path).is_dir():
        model_path = model_name_or_path
    else:
        try:
            import transformers_modules
            model_path = str(Path(transformers_modules.__path__[0], *type(model).__module__.split('.')[1:-1]))
        except ImportError:
            model_path = None

    if model_path is None:
        return []

    # convert relative to absolute path
    model_path = get_absolute_path(model_path)

    logger.info(f"Searching in {model_path} for code files")
    code_files_list = [file for file in Path(model_path).glob("*.py")]

    logger.info(f"Found code files - {code_files_list}")

    return code_files_list


def copy_code_files(code_files_list: List, destination_paths: List):
    """copies list of files to list of destination folders"""
    for code_file in code_files_list:
        for dst_folder in destination_paths:
            shutil.copy(code_file, get_absolute_path(dst_folder))


def update_json_file_and_overwrite(json_file_path: str, update_dict: Dict):
    """updates a json file with given dictionary and overwrites the json"""
    try:
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)
        data.update(update_dict)
        with open(json_file_path, "w") as json_file:
            json.dump(data, json_file, indent=2)
        
        logger.info(f"Updated {json_file_path}")
    except Exception:
        logger.info(f"Failed to update {json_file_path}")
