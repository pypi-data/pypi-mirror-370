# SPDX-FileCopyrightText: 2023 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from pathlib import Path, PurePath
from os import PathLike
from typing import Union

StrPath = Union[str, PathLike[str]]


def name_of_file(path):
    return PurePath(path).name


def mkdir_p(path: StrPath) -> None:
    """Make directory and its parents."""
    Path(path).mkdir(parents=True, exist_ok=True)
