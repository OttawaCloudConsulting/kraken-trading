"""Utility functions for data normalization and transformation."""

import logging

def normalize_timestamp(value) -> int:
    """
    Normalize a Kraken-style timestamp to an integer by truncating the fractional seconds.

    Kraken API may return timestamps as float, stringified float, or already as int.
    This function ensures consistency for storage and comparison by returning an integer.

    Args:
        value: A timestamp value (float, str, or int).

    Returns:
        Integer timestamp.

    Raises:
        ValueError: If the value cannot be converted to a float.
    """
    try:
        return int(float(value))
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid timestamp value: {value}") from e