# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# Copyright 2020 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---------------------------------------------------------

"""This file defines the util functions used for downloading license file."""

from huggingface_hub import hf_hub_download
from pathlib import Path
from shutil import copyfile

from ..constants import SaveFileConstants
from azureml.acft.common_components import get_logger_app


logger = get_logger_app(__name__)


def download_licence_file_from_huggingface_repo(model_id: str, download_path: str) -> str:
    """
    Download the LICENSE file from huggingface hub
    """
    license_file = hf_hub_download(
        repo_id=model_id,
        filename=SaveFileConstants.LICENSE_SAVE_PATH,
    )
    return license_file


def download_license_file(model_id: str, download_path: str) -> None:
    """
    Download the LICENSE file for ACFT models
    """
    Path(download_path).mkdir(exist_ok=True, parents=True)
    try:
        license_file = download_licence_file_from_huggingface_repo(model_id, download_path)
        logger.info(f"Downloaded LICENSE file at {license_file}")
        copyfile(license_file, str(Path(download_path, SaveFileConstants.LICENSE_SAVE_PATH)))
    except:
        logger.warning(
            f"Unable to fetch LICENSE file for {model_id}. "
            "It is the responsibility of the user to set LICENSE file for the model."
        )

