from functools import cache
from pathlib import Path
from typing import Dict

from appdirs import AppDirs
from pydantic import BaseModel

from resourcemap.core.format import Format

class ResourceMap(BaseModel):
    author: str
    app: str
    format: Format
    map: Dict[str, Path]

    def get(self, key: str) -> Path:
        if not key in self.map:
            raise KeyError(key)
        return self.map[key]

    def set(self, key: str|Path, path: Path) -> 'ResourceMap':
        self.map[_extract_key(Path(key))] = path
        return self

    def set_default(self, key: str|Path) -> 'ResourceMap':
        return self.set(key, Path(AppDirs(self.app, self.author).user_data_dir) / key)
    
    def save(self, exist_ok = False, encoding='utf-8-sig'):
        path = ResourceMap.path(self.app, self.author, self.format)
        if not exist_ok and path.exists():
            raise FileExistsError(path)

        if not path.parent.parent.parent.exists():
            raise FileNotFoundError(path.parent.parent.parent)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, mode='w', encoding=encoding) as fp:
            _map = {k: str(v) for k, v in self.map.items()}
            self.format.save(fp, _map)
        ResourceMap.load.cache_clear()
    
    @staticmethod
    def path(app_name: str, author_name: str, format: Format) -> Path:
        return Path(AppDirs("resmap", author_name).user_data_dir) / f"{app_name}.{format._extension}"
    
    @cache
    @staticmethod
    def load(app_name: str, author_name: str, encoding='utf-8-sig', format: Format=Format.JSON) -> 'ResourceMap':
        path = ResourceMap.path(app_name, author_name, format)
        if not path.exists():
            raise FileNotFoundError(path)
        with open(path, mode='r', encoding=encoding) as fp:
            map = format.load(fp)
        
        return ResourceMap(
            author=author_name,
            app=app_name,
            format=format,
            map=map
        )

    @staticmethod
    def create(app_name: str, author_name: str, format: Format=Format.JSON) -> 'ResourceMap':
        return ResourceMap(
            author=author_name,
            app=app_name,
            format=format,
            map={}
        )

def _extract_key(path: Path|str) -> str:
    try:
        _path = Path(path)
        name = _path.name
        parts = name.split('.')
        if len(parts) == 1:
            return name
        return parts[0]
    except:
        return str(path)
