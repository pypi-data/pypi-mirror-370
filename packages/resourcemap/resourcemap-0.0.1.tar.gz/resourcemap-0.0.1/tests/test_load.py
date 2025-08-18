from pathlib import Path

import pytest

from resourcemap.core.format import Format
from resourcemap.core.load import load_json, load_yaml
from resourcemap.core.locate import InvalidAppSelectorError, NoDefaultFileError
from resourcemap.core.resource import ResourceMap

TEST_DATA = {'key': 'value', 'answer': 42, 'multibyte': 'こんにちは'}

def create_file_for_load(path, app_name, app_author, default, format: Format, encoding='utf-8-sig'):
    if default is None:
        filepath = path
    else:
        filepath = default
    with open(filepath, 'w', encoding=encoding) as fp:
        format.save(fp, TEST_DATA)
    if isinstance(app_name, str) and isinstance(app_author, str):
        resmap = ResourceMap.create(app_name, app_author, Format.JSON)
        resmap.set(path, Path(path))
        resmap.save()

@pytest.fixture
def fixture_create_json_for_load(tmp_path, request):
    path_or_key, app_name, app_author, _default = request.param
    path = tmp_path / path_or_key if path_or_key is not None else None
    default = tmp_path / _default if _default is not None else None
    create_file_for_load(path, app_name, app_author, default, Format.JSON)
    return path, path_or_key, app_name, app_author, default

@pytest.fixture
def fixture_create_yaml_for_load(tmp_path, request):
    path_or_key, app_name, app_author, _default = request.param
    path = tmp_path / path_or_key if path_or_key is not None else None
    default = tmp_path / _default if _default is not None else None
    create_file_for_load(path, app_name, app_author, default, Format.YAML)
    return path, path_or_key, app_name, app_author, default

@pytest.mark.parametrize('fixture_create_json_for_load', [
    (('temp0.json', None, None, None)),
    (('temp0.json', 'app', 'author', None)),
    (('temp0.json', 'app', 'author', Path('default0'))),
    (('path/to/temp0.json', 'app', 'author', Path('default0'))),
    (('ancestor/path/to/temp0.json', 'app', 'author', Path('default0'))),
], indirect=['fixture_create_json_for_load'])
def test_load_json(fixture_mock_path, fixture_create_json_for_load):
    expected_path, path_or_key, app_name, app_author, default = fixture_create_json_for_load
    if app_name is not None and app_author is not None:
        assert load_json(path_or_key, app_name, app_author, default=default) == TEST_DATA
        assert load_json(path_or_key, ResourceMap.load(app_name, app_author), default=default) == TEST_DATA
    else:
        assert load_json(str(expected_path), default=default) == TEST_DATA

@pytest.mark.parametrize('fixture_create_yaml_for_load', [
    (('temp0.yaml', None, None, None)),
    (('temp0.yaml', 'app', 'author', None)),
    (('temp0.yaml', 'app', 'author', Path('default0'))),
    (('path/to/temp0.yaml', 'app', 'author', Path('default0'))),
    (('ancestor/path/to/temp0.yaml', 'app', 'author', Path('default0'))),
], indirect=['fixture_create_yaml_for_load'])
def test_load_yaml(fixture_mock_path, fixture_create_yaml_for_load):
    expected_path, path_or_key, app_name, app_author, default = fixture_create_yaml_for_load
    if app_name is not None and app_author is not None:
        assert load_yaml(path_or_key, app_name, app_author, default=default) == TEST_DATA
        assert load_yaml(path_or_key, ResourceMap.load(app_name, app_author), default=default) == TEST_DATA
    else:
        assert load_yaml(str(expected_path), default=default) == TEST_DATA

@pytest.mark.parametrize('exception,fixture_create_json_for_load', [
    (InvalidAppSelectorError, ('temp0.json', None, None, None)),
    (InvalidAppSelectorError, ('temp0.json', 'app', None, None)),
    (InvalidAppSelectorError, ('temp0.json', None, 'author', None)),
    (InvalidAppSelectorError, ('temp0.json', 'app', 0, None)),
    (InvalidAppSelectorError, ('temp0.json', 0, 'author', None)),
    (NoDefaultFileError, ('temp0.json', 'app', 'author', None)),
], indirect=['fixture_create_json_for_load'])
def test_load_json_abnormal(fixture_mock_path, fixture_create_json_for_load, exception):
    expected_path, path_or_key, app_name, app_author, default = fixture_create_json_for_load
    if expected_path.exists():
        expected_path.unlink()
    with pytest.raises(exception):
        load_json(path_or_key, app_name, app_author, default=default)

@pytest.fixture
def fixture_create_json_for_load_with_encode(tmp_path, request):
    path_or_key, app_name, app_author, encoding = request.param
    path = tmp_path / path_or_key if path_or_key is not None else None
    create_file_for_load(path, app_name, app_author, None, Format.JSON, encoding)
    return path, path_or_key, app_name, app_author

@pytest.fixture
def fixture_create_yaml_for_load_with_encode(tmp_path, request):
    path_or_key, app_name, app_author, encoding = request.param
    path = tmp_path / path_or_key if path_or_key is not None else None
    create_file_for_load(path, app_name, app_author, None, Format.YAML, encoding)
    return path, path_or_key, app_name, app_author

@pytest.mark.parametrize('fixture_create_json_for_load_with_encode', [
    (('temp0.json', None, None, 'utf-8-sig')),
    (('temp0.json', None, None, 'cp932')),
    (('temp0.json', 'app', 'author', 'utf-8-sig')),
    (('temp0.json', 'app', 'author', 'cp932')),
], indirect=['fixture_create_json_for_load_with_encode'])
def test_load_json_with_encode(fixture_mock_path, fixture_create_json_for_load_with_encode):
    expected_path, path_or_key, app_name, app_author = fixture_create_json_for_load_with_encode
    if app_name is not None and app_author is not None:
        assert load_json(path_or_key, app_name, app_author) == TEST_DATA
        assert load_json(path_or_key, ResourceMap.load(app_name, app_author)) == TEST_DATA
    else:
        assert load_json(str(expected_path)) == TEST_DATA
