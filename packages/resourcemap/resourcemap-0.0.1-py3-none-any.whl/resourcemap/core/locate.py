import shutil
from importlib.resources import as_file
from importlib.resources.abc import Traversable
from os import PathLike
from pathlib import Path
from typing import Optional
from warnings import warn

from resourcemap.core.resource import ResourceMap, _extract_key


class UnneededAppAuthorWarning(Warning):
    def __init__(self, app_selector, app_author, message=None):
        if message is None:
            message = (
                f"Unneeded app author information provided.\n"
                f"app_selector: {app_selector}\n"
                f"app_author: {app_author}"
            )
        super().__init__(message)
        self.app_selector = app_selector
        self.app_author = app_author

class InvalidAppSelectorError(Exception):
    def __init__(self, app_name, app_author, message=None):
        if message is None:
            message = (
                f"Invalid app selector provided.\n"
                f"app_name: {app_name}\n"
                f"app_author: {app_author}"
            )
        super().__init__(message)
        self.app_name = app_name
        self.app_author = app_author

class NoDefaultFileError(Exception):
    def __init__(self, message="No default file found."):
        super().__init__(message)

class CannotCopyDefaultFileError(Exception):
    def __init__(self, src, dst, message=None):
        if message is None:
            message = (
                f"Cannot copy the default file.\n"
                f"src: {src}\n"
                f"dst: {dst}\n"
            )
        super().__init__(message)
        self.src = src
        self.dst = dst

def get_config_path(app_selector: str|ResourceMap, app_author: str, key: str) -> Path:
    if isinstance(app_selector, ResourceMap):
        if app_author is not None:
            warn(UnneededAppAuthorWarning(app_selector, app_author))
        return app_selector.get(key)
    elif isinstance(app_selector, str):
        if isinstance(app_author, str):
            return ResourceMap.load(app_selector, app_author).get(key)
    raise InvalidAppSelectorError(app_selector, app_author)

def locate(
    path_or_key: PathLike,
    app_selector: str|ResourceMap = None,
    app_author: str = None,
    *,
    default: Optional[Traversable|Path] = None,
) -> Path:
    path = Path(path_or_key)
    if path.exists():
        return path
    
    if app_selector is None:
        raise FileNotFoundError(path)
    path = get_config_path(app_selector, app_author, _extract_key(path))
    if path.exists():
        return path
    
    if default is None:
        raise NoDefaultFileError
    with as_file(default) as default_path:
        if not _copy_file_safe(default_path, path):
            raise CannotCopyDefaultFileError(default_path, path)
        return path

def _copy_file_safe(src: Path, dst: Path) -> bool:
    if not dst.parent.parent.parent.exists():
        return False
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        return True
    except:
        return False
