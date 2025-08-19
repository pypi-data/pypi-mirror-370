# SPDX-FileCopyrightText: 2023 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import argparse
import logging
import shutil
import sys
from pathlib import Path
from typing import Final, Optional

from .util import name_of_file, setup_logging, StrPath

DEFAULT_TARGET: Final[Path] = Path("~/.local/share/Odoo/filestore").expanduser()

_LOGGER = logging.getLogger(__name__)

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Restore a filesystem.")
    parser.add_argument(
        "filesystem",
        action="store",
        help="path to filesystem directory to restore",
    )
    parser.add_argument(
        "--new-db-name",
        "-n",
        action="store",
        help="name of database to restore to",
    )
    parser.add_argument(
        "--delete-existing",
        "-D",
        action="store_true",
        help="delete existing filestore before restoration",
    )
    parser.add_argument(
        "--odoo-fs",
        action="store",
        help="odoo filestore directory to restore to",
    )
    return parser


def delete_fs(db_name: str, fs_target: Optional[StrPath] = None) -> None:
    if fs_target is None:
        fs_target = DEFAULT_TARGET
    target = Path(fs_target) / db_name
    try:
        shutil.rmtree(target)
        _LOGGER.info(f"deleted '{target}'")
    except FileNotFoundError:
        pass


def restore_fs(from_path: StrPath, db_name: str, fs_target: Optional[StrPath] = None) -> None:
    if fs_target is None:
        fs_target = DEFAULT_TARGET

    target = Path(fs_target) / db_name
    _LOGGER.info("starting filesystem restoration. this may take a while")
    shutil.copytree(from_path, target, dirs_exist_ok=True)
    _LOGGER.info(f"copied '{from_path}' to '{target}'")


def main() -> int:
    setup_logging()
    parser = create_parser()
    args = parser.parse_args()

    new_db_name = args.new_db_name or name_of_file(args.filesystem)
    if args.delete_existing:
        delete_fs(new_db_name, fs_target=args.odoo_fs)

    restore_fs(args.filesystem, new_db_name, fs_target=args.odoo_fs)

    return 0


if __name__ == "__main__":
    sys.exit(main())
