from importlib.resources.abc import Traversable
from os import PathLike
from pathlib import Path
from typing import Any, Callable, Optional


from resourcemap.core.resource import ResourceMap


def load(
    path_or_key: PathLike,
    app_selector: str|ResourceMap = None,
    app_author: str = None,
    *,
    default: Optional[Traversable|Path] = None,
    loader: Callable[[Path], Any],
): ...

def load_json(
    path_or_key: PathLike,
    app_selector: str|ResourceMap = None,
    app_author: str = None,
    *,
    default: Optional[Traversable|Path] = None,
    encoding:str = None
): ...

def load_yaml(
    path_or_key: PathLike,
    app_selector: str|ResourceMap = None,
    app_author: str = None,
    *,
    default: Optional[Traversable|Path] = None,
    encoding:str = None
): ...

def _estimate_encoding(path: Path) -> str: ...