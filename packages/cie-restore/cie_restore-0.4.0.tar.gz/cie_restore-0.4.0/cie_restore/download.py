# SPDX-FileCopyrightText: 2023 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import argparse
import datetime
import json
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from getpass import getpass
from typing import Dict, Final, Iterable, Optional, Tuple
from .util import name_of_file, setup_logging, StrPath, mkdir_p

BORDREAD_USER = "borgread"
# The same database name can be used by multiple servers. With this constant, we
# prioritise a given server/host to disambiguate. Items that appear first in the
# list have higher priority.
PRIORITY_HOSTS: Final[Tuple[str, ...]] = [
    "sixteen.prod.srv.coopiteasy.be",
    "fourteen.prod.srv.coopiteasy.be",
    "bees.prod.srv.coopiteasy.be",
    "spp.prod.srv.coopiteasy.be",
    "synergie.prod.srv.coopiteasy.be",
    "twelve.prod.srv.coopiteasy.be",
    "lachaf.prod.srv.coopiteasy.be",
    "nine.prod.srv.coopiteasy.be",
]
PRIORITY_LOOKUP: Final[Dict[str, int]] = {
    host: i for i, host in enumerate(PRIORITY_HOSTS)
}

_LOGGER = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Download an archive of a database.")
    parser.add_argument(
        "--server",
        "-s",
        action="store",
        help="server from which to download backup, required",
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
        help="only download the database",
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
        help="path to directory to extract archive to (default: ./archive)",
        default="./archive",
    )
    parser.add_argument(
        "database",
        action="store",
        help="name of database to download",
    )
    return parser


def from_iso(iso: str) -> datetime.datetime:
    """Convert an ISO 8601 string to a datetime. If the string already contains
    time information, preserve it. If it does not, set the time information to
    their latest values.
    """
    try:
        result_date = datetime.date.fromisoformat(iso)
        return datetime.datetime.combine(result_date, datetime.datetime.max.time())
    except ValueError:
        pass
    return datetime.datetime.fromisoformat(iso)


def clear_directory(path: StrPath) -> None:
    """Delete everything inside of a directory without deleting the directory
    itself.
    """
    path: Path = Path(path)
    if path.is_dir():
        for item in path.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)


def authenticate() -> None:
    if not os.environ.get("BORG_PASSPHRASE"):
        os.environ["BORG_PASSPHRASE"] = getpass(
            prompt="Enter passphrase of borg repository: "
        )


def get_list_of_archives(server, repo_path) -> dict:
    list_result = subprocess.run(
        [
            "borg",
            "--bypass-lock",
            "list",
            "--json",
            f"{BORDREAD_USER}@{server}:{repo_path}",
        ],
        capture_output=True,
        check=True,
    )
    return json.loads(list_result.stdout)


def get_latest_archive(
    archives_dict: dict, target_date: Optional[datetime.datetime] = None
) -> str:
    if target_date is None:
        # Roundabout way of getting the latest time for today.
        target_date = from_iso(datetime.date.today().isoformat())
    delta = datetime.timedelta.max
    zero_delta = datetime.timedelta()
    latest_archive = None
    for archive in archives_dict:
        archive_date = datetime.datetime.fromisoformat(archive["time"])
        if (
            new_delta := (target_date - archive_date)
        ) < delta and new_delta >= zero_delta:
            delta = new_delta
            latest_archive = archive
    if latest_archive is not None:
        return latest_archive["archive"]
    raise ValueError(f"could not find any archive before {target_date}")


def download_archive(
    server: str,
    repo_path: str,
    archive: str,
    destination: StrPath,
    db_only: bool = False,
) -> None:
    command = [
        "borg",
        # lock is bypassed because BORG_USER may not be allowed to write to
        # the lock file.
        "--bypass-lock",
        "extract",
        "--progress",
        f"{BORDREAD_USER}@{server}:{repo_path}::{archive}",
    ]
    if db_only:
        command += [
            "--pattern",
            "+.borgmatic/*/postgresql_databases/*",
            "--pattern",
            "-*",
        ]
    clear_directory(destination)
    mkdir_p(destination)
    subprocess.run(
        command,
        check=True,
        cwd=destination,
        stdout=sys.stdout,
        stderr=subprocess.STDOUT,
    )


def find_repo(server: str, dbname: str, prod_server: Optional[str] = None) -> str:
    """Given a server and a database name, return a path to the repository, such
    as '/borg/fourteen.prod.srv.coopiteasy.be-dbname'.
    """
    # This _cannot_ be run using the regular borg user as presently configured
    # (2023-05-24). The regular borg user is strictly restricted to the `borg
    # serve` command.
    #
    # Instead, we run this with a special read-only user that is in the same
    # group as the borg user. It is able to get a list of directories using the
    # below command, which we can then use to find the repo we want/need.
    find_result = subprocess.run(
        [
            "ssh",
            f"{BORDREAD_USER}@{server}",
            "--",
            "find",
            "/borg",
            "-maxdepth",
            "1",
            "-mindepth",
            "1",
            "-print0",
        ],
        capture_output=True,
        check=True,
    )
    repos = find_result.stdout.decode("utf-8").split("\0")
    db_repos = [repo for repo in repos if repo.endswith(f"-{dbname}")]
    if not db_repos:
        raise ValueError(f"could not find repository for {dbname}")
    if prod_server:
        # This should result in only a single item in the list.
        db_repos = [
            repo for repo in db_repos if name_of_file(repo).startswith(prod_server)
        ]
    repo = get_highest_priority_repo(db_repos)
    _LOGGER.info(f"found repo '{server}:{repo}'")
    return repo


def get_highest_priority_repo(repos: Iterable[str]) -> str:
    """From a list of repositories which have matching database names, pick the
    one with the highest priority.
    """
    lowest_priority = len(PRIORITY_HOSTS)
    sorted_repos = sorted(
        repos,
        key=lambda repo: (
            PRIORITY_LOOKUP.get(name_of_file(repo).split("-")[0], lowest_priority),
            # Fallback alphabetical sort.
            repo,
        ),
    )
    return sorted_repos[0]


def download(
    server: str,
    repo_path: str,
    destination: str,
    prod_server: Optional[str] = None,
    target_date: Optional[datetime.datetime] = None,
    db_only: bool = False,
) -> None:
    """Fairly meta everything-method."""
    authenticate()

    list_result_dict = get_list_of_archives(server, repo_path)

    archive = get_latest_archive(list_result_dict["archives"], target_date=target_date)
    _LOGGER.info(f"found archive '{archive}'")

    download_archive(server, repo_path, archive, destination, db_only=db_only)
    _LOGGER.info(f"extracted archive to '{destination}'")


def main() -> int:
    setup_logging()
    parser = create_parser()
    args = parser.parse_args()

    date = None
    if args.date:
        date = from_iso(args.date)

    repo = find_repo(args.server, args.database, prod_server=args.prod_server)

    download(args.server, repo, args.target, target_date=date, db_only=args.db_only)

    return 0


if __name__ == "__main__":
    sys.exit(main())
