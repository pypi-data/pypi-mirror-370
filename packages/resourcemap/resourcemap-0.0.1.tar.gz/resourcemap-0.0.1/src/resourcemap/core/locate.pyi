from importlib.resources.abc import Traversable
from os import PathLike
from pathlib import Path
from typing import Optional

from resourcemap.core.resource import ResourceMap


class UnneededAppAuthorWarning(Warning):
    def __init__(self, app_selector, app_author, message=None): ...

class InvalidAppSelectorError(Exception):
    def __init__(self, app_name, app_author, message=None): ...

class NoDefaultFileError(Exception):
    def __init__(self, message="No default file found."): ...

class CannotCopyDefaultFileError(Exception):
    def __init__(self, src, dst, message=None): ...

def get_config_path(app_selector: str|ResourceMap, app_author: str, key: str) -> Path: ...

def locate(
    path_or_key: PathLike,
    app_selector: str|ResourceMap = None,
    app_author: str = None,
    *,
    default: Optional[Traversable|Path] = None,
) -> Path: ...

def _copy_file_safe(src: Path, dst: Path) -> bool: ...
