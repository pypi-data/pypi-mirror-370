"""Module containing utility methods to support playlist2podcast."""

from pathlib import Path
from typing import Annotated

import msgspec
import typer
from loguru import logger as log

from playlist2podcast.playlist_2_podcast import Config

log.catch()


def convert_json_to_toml(
    json_config_path: Annotated[
        Path,
        typer.Option(
            "--json_config",
            help="Path to old style JSON configuration file",
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ],
    toml_config_path: Annotated[
        Path,
        typer.Option(
            "--toml_config",
            help="Path to new style TOML configuration file",
            file_okay=True,
            dir_okay=False,
            writable=True,
            resolve_path=True,
        ),
    ],
) -> None:
    """Convert old JSON based configuration to new TOML based configuration."""
    with json_config_path.open("r") as json_file:
        toml_config = Config(**msgspec.json.decode(json_file.read()))

    with toml_config_path.open("wb") as toml_config_file:
        toml_config_file.write(msgspec.toml.encode(toml_config))


def convert_to_toml():
    """Shim to invoke typer."""
    typer.run(convert_json_to_toml)
