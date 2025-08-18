from enum import Enum
from pathlib import Path
from typing import IO, Any, Callable

def load_json(fp):
    import json
    return json.load(fp)

def save_json(fp, obj):
    import json
    return json.dump(obj, fp, sort_keys=True, indent=4, ensure_ascii=False)

def load_yaml(fp):
    try: 
        import yaml
    except ImportError as e:
        raise ImportError("PyYAML is not installed. Please run 'pip install pyyaml'.") from e
    return yaml.load(fp, Loader=yaml.SafeLoader)

def save_yaml(fp, obj):
    try: 
        import yaml
    except ImportError as e:
        raise ImportError("PyYAML is not installed. Please run 'pip install pyyaml'.") from e
    return yaml.dump(obj, fp)

class Format(Enum):
    JSON = 'json', load_json, save_json
    YAML = 'yml', load_yaml, save_yaml

    def __init__(self, extension: str, load_callback: Callable[[IO[Any]], Any], save_callback: Callable[[IO[Any], Any], None]):
        self._extension = extension
        self._load_callback = load_callback
        self._save_callback = save_callback

    def load(self, fp):
        return self._load_callback(fp)
    
    def save(self, fp, obj):
        self._save_callback(fp, obj)
