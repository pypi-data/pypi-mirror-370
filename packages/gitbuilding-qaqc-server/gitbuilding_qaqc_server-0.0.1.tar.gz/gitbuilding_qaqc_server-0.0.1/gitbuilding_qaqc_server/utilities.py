"""Utility functions GitBuilding QA/QC server."""
# SPDX-License-Identifier: AGPL-3.0-or-later

import re
import uuid
from typing import Any

# Regex for allowed GitBuilding IDs: letters, numbers, underscore, hyphen
GITBUILDING_ID_REGEX = re.compile(r"^[a-zA-Z0-9_-]+$")


def validate_uuid(value: Any) -> str:
    """Validate that the input is a string representing a valid UUID4.

    :param value: The value to check.

    :return: The UUID string if valid.

    :raises TypeError: If the value is not a string.
    :raises ValueError: If the string is not a valid UUID4.
    """
    if not isinstance(value, str):
        raise TypeError(f"UUID must be a string, got {type(value).__name__}")
    try:
        u = uuid.UUID(value, version=4)
    except ValueError as e:
        raise ValueError(f"Invalid UUID4 string: {value}") from e
    return str(u)


def validate_gb_id(value: Any) -> str:
    """Validate that the input is a string matching allowed GitBuilding ID format.

    :param value: The value to check.

    :return: The string if valid.

    :raises TypeError: If the value is not a string.
    :raises ValueError: If the string does not match allowed characters.
    """
    if not isinstance(value, str):
        raise TypeError(f"GitBuilding ID must be a string, got {type(value).__name__}")
    if not GITBUILDING_ID_REGEX.match(value):
        raise ValueError(f"Invalid GitBuilding ID: {value}")
    return value


def validate_str(value: Any) -> str:
    """Validate that the input is a string.

    :param value: The value to validate.

    :return: The validated string.

    :raises TypeError: If the value is not a string.
    """
    if not isinstance(value, str):
        raise TypeError(f"Value must be a string, got {type(value).__name__}")
    return value
