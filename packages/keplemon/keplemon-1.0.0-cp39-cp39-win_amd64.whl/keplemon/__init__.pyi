# flake8: noqa
from pathlib import Path

def get_thread_count() -> int:
    """
    Returns:
        Number of cores allocated for use by KepLemon
    """
    ...

def set_thread_count(n: int) -> None:
    """
    Set the number of cores allocated for use by KepLemon

    !!! warning
        This function must be called before any other functions in the library

    Args:
        n: Number of cores to allocate
    """
    ...

#: Path to the time constants file
TIME_CONSTANTS_PATH: Path
"""
Path to the default time constants file required by the SAAL binaries

!!! warning
    This path should never be modified and is only exposed to allow inspection of current data.
"""

#: Path to the parent directory of the package
PACKAGE_DIRECTORY: Path
"""Path to the parent directory of the package"""

#: Path to the assets directory containing supporting data files for the package
ASSETS_DIRECTORY: Path
"""Path to the assets directory containing supporting data files for the package"""

def set_license_file_path(path: str) -> None:
    """
    Set the path to the license file required by the SAAL binaries

    Args:
        path: Path to the SGP4 license file
    """
    ...

def get_license_file_path() -> str:
    """
    Returns:
        Path to the SGP4 license file
    """
    ...
