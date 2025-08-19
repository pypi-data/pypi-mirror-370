# SPDX-FileCopyrightText: 2023 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import argparse
import contextlib
import logging
import sys
import tempfile
from pathlib import Path
from typing import Optional, Iterator

from .db import drop_db, restore_db
from .download import download, find_repo, from_iso
from .fs import delete_fs, restore_fs
from .util import setup_logging, StrPath, mkdir_p

_LOGGER = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download and restore an archive of a database."
    )
    parser.add_argument(
        "--server",
        "-s",
        action="store",
        help="server from which to download backup",
        required=True,
    )
    parser.add_argument(
        "--prod-server",
        "-P",
        action="store",
        help="original production server from which the backup was made",
    )
    parser.add_argument(
        "--db-only",
        "-D",
        action="store_true",
        help="only download and restore the database",
    )
    parser.add_argument(
        "--date",
        "-d",
        action="store",
        help="latest datetime (ISO 8601) you want a backup from; backups after"
        " this date are not considered",
    )
    parser.add_argument(
        "--target",
        "-t",
        action="store",
        help="path to directory to extract archive to, optional",
    )
    parser.add_argument(
        "--new-db-name",
        "-n",
        action="store",
        help="new name of database",
    )
    parser.add_argument(
        "--jobs",
        "-j",
        action="store",
        type=int,
        help="amount of parallel jobs for database restoration",
    )
    parser.add_argument(
        "--delete-existing",
        "-D",
        action="store_true",
        help="drop existing database and delete existing filestore before restoration",
    )
    parser.add_argument(
        "--odoo-fs",
        action="store",
        help="odoo filestore directory to restore to",
    )
    parser.add_argument(
        "--prod",
        "-p",
        action="store_true",
        help="a posthook that disables all crons and e-mails is run unless this"
        " flag is used",
    )
    parser.add_argument(
        "database",
        action="store",
        help="name of database to download",
    )
    return parser


@contextlib.contextmanager
def directory_context(target: Optional[StrPath] = None) -> Iterator[str]:
    if target is None:
        # Use cache directory because `/tmp` may be mounted into RAM.
        cache_dir = Path("~/.cache").expanduser()
        mkdir_p(cache_dir)
        temp_dir = tempfile.TemporaryDirectory(dir=cache_dir)
        try:
            yield temp_dir.name
        finally:
            # clean up temporary directory when exiting context
            temp_dir.cleanup()
    else:
        # don't clean up anything when a target is specified; permanency is
        # expected.
        yield str(target)


def find_db(archive_dir: StrPath) -> Path:
    archive_dir = Path(archive_dir)
    return next(archive_dir.glob(".borgmatic/*/postgresql_databases/*/*"))


def find_fs(archive_dir: StrPath) -> Path:
    archive_dir = Path(archive_dir)
    return next(archive_dir.glob("filestore/*"))


def main() -> int:
    setup_logging()
    parser = create_parser()
    args = parser.parse_args()

    new_db_name = args.new_db_name or args.database

    # Download
    date = None
    if args.date:
        date = from_iso(args.date)

    repo = find_repo(args.server, args.database, prod_server=args.prod_server)

    with directory_context(args.target) as target:
        download(args.server, repo, target, target_date=date, db_only=args.db_only)

        # Restore db
        if args.delete_existing:
            drop_db(new_db_name)

        restore_db(find_db(target), new_db_name, jobs=args.jobs, prod=args.prod)

        # Restore fs
        if args.delete_existing and not args.db_only:
            delete_fs(new_db_name, fs_target=args.odoo_fs)

        if not args.db_only:
            restore_fs(find_fs(target), new_db_name, fs_target=args.odoo_fs)

        return 0


if __name__ == "__main__":
    sys.exit(main())
