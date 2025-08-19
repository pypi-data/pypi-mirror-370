"""Functions to support processing of the registry."""

import logging
import re
from typing import Final

logger = logging.getLogger(__name__)

MARKER_INDEX: Final[str] = "INDEX"
MARKER_GOTO: Final[str] = "GOTO"
MARKER_KEY: Final[str] = "KEY"
MARKER_CONTAINS: Final[str] = "CONTAINS"
MARKER_STARTSWITH: Final[str] = "STARTSWITH"
MARKER_ENDSWITH: Final[str] = "ENDSWITH"
MARKER_IS: Final[str] = "IS"
MARKER_REGEX: Final[str] = "REGEX"
MARKER_KEY_EXISTS: Final[str] = "EXISTS"
MARKER_KEY_NO_EXIST: Final[str] = "NOEXIST"
MARKER_IS_TYPE: Final[str] = "ISTYPE"

ALL_KEYS: Final[list] = [
    MARKER_INDEX,
    MARKER_GOTO,
    MARKER_KEY,
    MARKER_CONTAINS,
    MARKER_STARTSWITH,
    MARKER_ENDSWITH,
    MARKER_IS,
    MARKER_REGEX,
    MARKER_KEY_EXISTS,
    MARKER_KEY_NO_EXIST,
    MARKER_IS_TYPE,
]


def at_index(marker: dict, data: dict) -> dict:
    """Provide an ability to investigate an index."""
    idx = marker[MARKER_INDEX]
    try:
        data = data[idx]
        return data
    except IndexError:
        return data


def at_goto(marker: dict, data: dict) -> dict:
    """Goto A key at the top-level of the document."""
    k = marker[MARKER_GOTO]
    try:
        return data[k]
    except KeyError:
        return data


def contains_match(marker: dict, data: dict) -> bool:
    """Determine whether a string value contains part of another value."""
    k = marker[MARKER_KEY]
    v = None
    try:
        v = data[k]
    except KeyError:
        return False
    if not isinstance(v, str):
        return False
    match_pattern = marker[MARKER_CONTAINS]
    return match_pattern in v


def startswith_match(marker: dict, data: dict) -> bool:
    """Determine whether a string value begins with another value."""
    k = marker[MARKER_KEY]
    v = None
    try:
        v = data[k]
    except KeyError:
        return False
    if not isinstance(v, str):
        return False
    match_pattern = marker[MARKER_STARTSWITH]
    return v.startswith(match_pattern)


def endswith_match(marker: dict, data: dict) -> bool:
    """Determine whether a string value ends with another value."""
    k = marker[MARKER_KEY]
    v = None
    try:
        v = data[k]
    except KeyError:
        return False
    if not isinstance(v, str):
        return False
    match_pattern = marker[MARKER_ENDSWITH]
    return v.endswith(match_pattern)


def is_match(marker: dict, data: dict) -> bool:
    """Determine whether a value is an exact match for a given
    value.
    """
    k = marker[MARKER_KEY]
    v = None
    try:
        v = data[k]
    except KeyError:
        return False
    match_pattern = marker[MARKER_IS]
    return v == match_pattern


def is_type(marker: dict, data: dict) -> bool:
    """Match data against type only, i.e. determine if a value is
    a primitive data type, e.g. `dict`, `list`, `string`, `int`.
    """
    k = marker[MARKER_KEY]
    v = None
    try:
        v = data[k]
    except KeyError:
        return False
    match_pattern = marker[MARKER_IS_TYPE]
    try:
        if isinstance(v, match_pattern):
            return True
    except TypeError:
        pass
    return False


def regex_match(marker: dict, data: dict) -> bool:
    """Match data against a regular expression."""
    k = marker[MARKER_KEY]
    v = None
    try:
        v = data[k]
    except KeyError:
        return False
    if not isinstance(v, str):
        return False
    match_pattern = marker[MARKER_REGEX]
    return re.search(match_pattern, v)


def key_exists_match(marker: dict, data: dict) -> bool:
    """Determine if a key exists, i.e. returns `True` if a key
    exists when it is expected to exist.
    """
    k = marker[MARKER_KEY]
    try:
        data[k]
    except KeyError:
        return False
    return True


def key_no_exist_match(marker: dict, data: dict) -> bool:
    """Determine if a key doesn't exist, i.e. negates the existence
    of a key when a specific value isn't supposed to be there.
    """
    k = marker[MARKER_KEY]
    try:
        data[k]
    except KeyError:
        return True
    return False
