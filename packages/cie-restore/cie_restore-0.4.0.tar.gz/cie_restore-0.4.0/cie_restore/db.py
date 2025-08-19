# SPDX-FileCopyrightText: 2023 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import argparse
import logging
import subprocess
import sys
from pathlib import Path
from typing import ContextManager, Optional, Union

from .util import StrPath, name_of_file, setup_logging

_LOGGER = logging.getLogger(__name__)

try:
    from importlib.resources import as_file, files

    PY_38 = False
except ImportError:
    from importlib.resources import path as ir_path

    PY_38 = True


def get_resource(package: str, path: str) -> ContextManager[Path]:
    if PY_38:
        return ir_path(package, path)
    return as_file(files(package).joinpath(path))


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Restore a database.")
    parser.add_argument(
        "database",
        action="store",
        help="path to database to restore",
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
        help="drop db (if it exists) before restoring to it",
    )
    parser.add_argument(
        "--jobs",
        "-j",
        action="store",
        type=int,
        help="amount of parallel jobs to pg_restore",
    )
    parser.add_argument(
        "--prod",
        "-p",
        action="store_true",
        help="a posthook that disables all crons and e-mails is run unless this"
        " flag is used",
    )
    return parser


def create_db(db_name: str) -> None:
    try:
        subprocess.run(
            ["createdb", db_name],
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise ValueError(
            f"error creating database '{db_name}'; maybe it already exists?"
        ) from e


def drop_db(db_name: str) -> None:
    result = subprocess.run(["dropdb", db_name], capture_output=True)
    if result.returncode == 0:
        _LOGGER.info(f"dropped '{db_name}'")


def posthook(db_name: str) -> None:
    with get_resource("cie_restore", "posthook.sql") as posthook_path:
        subprocess.run(
            [
                "psql",
                "-f",
                posthook_path,
                db_name,
            ],
            capture_output=True,
            check=True,
        )
        _LOGGER.info(f"ran posthook '{posthook_path}'")


def posthook_ociedoo(db_name: str) -> None:
    ociedoo_posthook = Path("~/.config/ociedoo/posthook.sql").expanduser()
    if ociedoo_posthook.exists():
        subprocess.run(
            [
                "psql",
                "-f",
                str(ociedoo_posthook),
                db_name,
            ],
            capture_output=True,
            check=True,
        )
        _LOGGER.info(f"ran posthook '{ociedoo_posthook}'")


def restore_db(
    db_path: StrPath, db_name: str, jobs: Optional[Union[str, int]] = None, prod: bool = False
) -> None:
    create_db(db_name)

    command = [
        "pg_restore",
        "--no-owner",
        "--dbname",
        db_name,
        db_path,
    ]
    if jobs is not None:
        command.extend(["--jobs", str(jobs)])

    _LOGGER.info("starting database restoration. this may take a while")
    subprocess.run(
        command,
        capture_output=True,
        check=True,
    )
    _LOGGER.info(f"restored '{db_path}' into database '{db_name}'")

    if not prod:
        posthook(db_name)
        posthook_ociedoo(db_name)
        # TODO: posthook to set password on admin, maybe


def main() -> int:
    setup_logging()
    parser = create_parser()
    args = parser.parse_args()

    new_db_name = args.new_db_name or name_of_file(args.database)
    if args.delete_existing:
        drop_db(new_db_name)

    restore_db(args.database, new_db_name, jobs=args.jobs, prod=args.prod)

    return 0


if __name__ == "__main__":
    sys.exit(main())
