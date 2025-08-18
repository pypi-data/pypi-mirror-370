from pathlib import Path
import pytest

from resourcemap.core.format import Format
from resourcemap.core.resource import ResourceMap, _extract_key

@pytest.mark.parametrize('app', ['app', '0'])
@pytest.mark.parametrize('author', ['author', '0'])
@pytest.mark.parametrize('format', [Format.JSON, Format.YAML])
def test_create(fixture_mock_path, app, author, format):
    ResourceMap.create(app, author, format).save()
    assert ResourceMap.path(app, author, format).exists()

@pytest.mark.parametrize('app', ['app', '0'])
@pytest.mark.parametrize('author', ['author', '0'])
@pytest.mark.parametrize('format', [Format.JSON, Format.YAML])
@pytest.mark.parametrize('map', [{'key': 'path'}, {'key1': 'path/to/file1', 'key2': 'path/to/file2'}])
def test_create_set_save_load_get(fixture_mock_path, app, author, format, map):
    resmap = ResourceMap.create(app, author, format)
    for k, v in map.items():
        resmap.set(k, v)
    resmap.save()
    
    resmap2 = ResourceMap.load(app, author, format=format)
    for k, v in map.items():
        assert resmap2.get(k) == Path(v)

@pytest.mark.parametrize('expected,arg', [
    ('key', 'key'),
    ('key', 'path/to/key'),
    ('key', 'path/to/key.json'),
    ('key', 'path/to/key.tar.gz'),
    ('key', Path('key')),
    ('key', Path('path/to/key')),
    ('key', Path('path/to/key.json')),
    ('key', Path('path/to/key.tar.gz')),
])
def test_extract_key(expected, arg):
    assert _extract_key(arg) == expected
