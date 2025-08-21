# flake8: noqa: F401

def ymd_components_to_ds50(year: int, month: int, day: int, hour: int, minute: int, second: float) -> float:
    """
    Convert year, month, day, hour, minute, and second components to a DS50 time.

    Args:
        year: Year component.
        month: Month component (1-12).
        day: Day component (1-31).
        hour: Hour component (0-23).
        minute: Minute component (0-59).
        second: Second component (0.0-59.999...).

    Returns:
        DS50 time as a float.
    """
    ...

def time_constants_loaded() -> bool:
    """
    Returns:
        True if time constants have been loaded to the SAAL binaries, False otherwise.
    """
    ...

def load_time_constants(file_path: str) -> None:
    """
    Load time constants into from a file for use by the SAAL binaries.

    Args:
        Path to the SAAL-formatted time constants file.
    """
    ...

def ds50_utc_to_ut1(ds50: float) -> float:
    """
    Convert a DS50 UTC time to UT1.

    Args:
        DS50 UTC time

    Returns:
        UT1 time
    """
    ...

def get_fk4_greenwich_angle(ds50_ut1: float) -> float:
    """
    Get the FK4 Greenwich angle.

    Args:
        ds50_ut1: Epoch in DS50 UT1 format

    Returns:
        FK4 Greenwich angle in radians.
    """
    ...

def get_fk5_greenwich_angle(ds50_ut1: float) -> float:
    """
    Get the FK5 Greenwich angle.

    Args:
        ds50_ut1: Epoch in DS50 UT1 format

    Returns:
        FK5 Greenwich angle in radians.
    """
    ...
