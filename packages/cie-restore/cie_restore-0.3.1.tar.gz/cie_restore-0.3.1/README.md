# cie_restore

A module in four parts (and with four corresponding scripts):

- `cie_download_archive`/`download` to download archives from the Borg server.
- `cie_restore_db`/`db` to restore a database using `pg_restore`.
- `cie_restore_fs`/`fs` to copy an Odoo filestore into the correct place.
- `cie_download_restore`/`all` to do all of the above operations in succession.

There is some repetition involved (in the argparse parsers and in the main
functions) to make these four components work independently of each other, but
the repetition is reduced to a minimum.

## Usage tip

Set the `BORG_PASSPHRASE` environment variable to a correct passphrase before
running the download scripts.

## Roadmap

The module does very minimal error handling. If you did something wrong (e.g.
you gave a path where a database name was expected), you will probably get an
error, but the error may not be entirely clear to you.
