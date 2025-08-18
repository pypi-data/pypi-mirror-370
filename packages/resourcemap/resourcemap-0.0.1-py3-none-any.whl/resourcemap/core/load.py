from importlib.resources import as_file
from importlib.resources.abc import Traversable
from os import PathLike
from pathlib import Path
from typing import Any, Callable, Optional

from charset_normalizer import from_path

from resourcemap.core.format import Format
from resourcemap.core.locate import CannotCopyDefaultFileError, NoDefaultFileError, locate
from resourcemap.core.resource import ResourceMap


def load(
    path_or_key: PathLike,
    app_selector: str|ResourceMap = None,
    app_author: str = None,
    *,
    default: Optional[Traversable|Path] = None,
    loader: Callable[[Path], Any],
):
    try:
        path = locate(path_or_key, app_selector, app_author, default=default)
    except CannotCopyDefaultFileError:
        with as_file(default) as default_path:
            return loader(default_path)
    return loader(path)

def load_json(
    path_or_key: PathLike,
    app_selector: str|ResourceMap = None,
    app_author: str = None,
    *,
    default: Optional[Traversable|Path] = None,
    encoding:str = None
):
    def _loader(path: Path, encoding=encoding):
        if encoding is None:
            encoding = _estimate_encoding(path)
        with open(path, mode='r', encoding=encoding) as fp:
            return Format.JSON.load(fp)
    return load(path_or_key, app_selector, app_author, default=default, loader=_loader)

def load_yaml(
    path_or_key: PathLike,
    app_selector: str|ResourceMap = None,
    app_author: str = None,
    *,
    default: Optional[Traversable|Path] = None,
    encoding:str = None
):
    def _loader(path: Path, encoding=encoding):
        if encoding is None:
            encoding = _estimate_encoding(path)
        with open(path, mode='r', encoding=encoding) as fp:
            return Format.YAML.load(fp)
    return load(path_or_key, app_selector, app_author, default=default, loader=_loader)

def _estimate_encoding(path: Path) -> str:
    with open(path, 'rb') as f:
        if f.read(3) == b'\xef\xbb\xbf':
            return 'utf-8-sig'
    return from_path(path).best().encoding
