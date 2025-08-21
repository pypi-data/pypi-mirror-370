import os
from pathlib import Path

from robot.utils import abspath

from .applicationcache import ApplicationCache


def escape_xpath_value(value):
    value = str(value)
    if '"' in value and '\'' in value:
        parts_wo_apos = value.split('\'')
        return "concat('%s')" % "', \"'\", '".join(parts_wo_apos)
    if '\'' in value:
        return "\"%s\"" % value
    return "'%s'" % value


def read_file(file_path):
    with open(_absnorm(file_path), encoding='UTF-8', errors='strict', newline="") as f:
        file_content = f.read().replace("\r\n", "\n")
    return file_content


def _absnorm(path):
    return abspath(_normalize_path(path))


def _normalize_path(path, case_normalize=False):
    """Normalizes the given path.

    - Collapses redundant separators and up-level references.
    - Converts ``/`` to ``\\`` on Windows.
    - Replaces initial ``~`` or ``~user`` by that user's home directory.
    - Converts ``pathlib.Path`` instances to ``str``.
    On Windows result would use ``\\`` instead of ``/`` and home directory
    would be different.
    """
    if isinstance(path, Path):
        path = str(path)
    else:
        path = path.replace("/", os.sep)
    path = os.path.normpath(os.path.expanduser(path))
    # os.path.normcase doesn't normalize on OSX which also, by default,
    # has case-insensitive file system. Our robot.utils.normpath would
    # do that, but it's not certain would that, or other things that the
    # utility do, desirable.
    if case_normalize:
        path = os.path.normcase(path)
    return path or "."
