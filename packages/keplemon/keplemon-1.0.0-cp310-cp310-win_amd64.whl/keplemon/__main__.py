from __future__ import annotations
import click
from pathlib import Path
from keplemon import TIME_CONSTANTS_PATH
from keplemon.time import request_time_constants_update


@click.command()
@click.option(
    "--update-eop",
    help="Update time constants and EOP data (global or path/to/output/file)",
    type=click.Path(exists=False),
)
def cli(update_eop: Path | None) -> None:
    if update_eop is not None:
        if update_eop == "global":
            update_eop = TIME_CONSTANTS_PATH
        print("Requesting time constants and EOP data from USNO...")
        request_time_constants_update(update_eop)
        print(f"Updated time constants at {update_eop}")
