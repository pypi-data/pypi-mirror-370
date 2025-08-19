# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
checkpoint utils
"""

import re
from typing import Optional

CHECKPOINT_DIR_REGEX = re.compile(r"^checkpoint\-(\d+)$")


def get_checkpoint_step(checkpoint_dirname: str) -> Optional[int]:
    """
    Returns step from a checkpoint directory name. ex. checkpoint-123 -> 123
    Returns None if checkpoint_dirname is not in valid format. 
    """
    match = CHECKPOINT_DIR_REGEX.search(checkpoint_dirname)
    return int(match.groups()[0]) if match else None
