# SPDX-FileCopyrightText: 2023 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging
import sys
from pathlib import Path, PurePath
from os import PathLike
from typing import Union

StrPath = Union[str, PathLike]


def setup_logging(level: int = logging.INFO) -> None:
    library_logger = logging.getLogger("cie_restore")
    library_logger.setLevel(level)
    library_logger.addHandler(logging.StreamHandler(sys.stdout))


def name_of_file(path: StrPath) -> str:
    return PurePath(path).name


def mkdir_p(path: StrPath) -> None:
    """Make directory and its parents."""
    Path(path).mkdir(parents=True, exist_ok=True)
