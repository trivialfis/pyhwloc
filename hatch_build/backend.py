from typing import Any

import hatchling.build


def build_wheel(
    wheel_directory: str,
    config_settings: dict[str, Any] | None = None,
    metadata_directory: str | None = None,
) -> str:
    wheel_name = hatchling.build.build_wheel(
        wheel_directory, config_settings, metadata_directory
    )
    return wheel_name


def build_sdist(
    sdist_directory: str,
    config_settings: dict[str, Any] | None = None,
) -> str:
    sdist_name = hatchling.build.build_sdist(sdist_directory, config_settings)
    return sdist_name


def build_editable(
    wheel_directory: str,
    config_settings: dict[str, Any] | None = None,
    metadata_directory: str | None = None,
) -> str:
    if config_settings:
        raise NotImplementedError()
    return hatchling.build.build_editable(
        wheel_directory, config_settings, metadata_directory
    )
