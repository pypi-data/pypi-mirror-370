import json
import os
from pathlib import Path

import pytest

from resourcemap.core.format import Format
from resourcemap.core.locate import CannotCopyDefaultFileError, InvalidAppSelectorError, NoDefaultFileError, UnneededAppAuthorWarning, _copy_file_safe, locate
from resourcemap.core.resource import ResourceMap


@pytest.fixture
def fixture_create_file_for_locate(tmp_path, request):
    path_or_key, app_name, app_author = request.param
    expected_path = tmp_path / f'{path_or_key}'
    with open(expected_path, 'w') as fp:
        json.dump({'key': 'value'}, fp)
    if app_name is not None and app_author is not None:
        resmap = ResourceMap.create(app_name, app_author, Format.JSON)
        resmap.set(path_or_key, expected_path)
        resmap.save()
    return expected_path, path_or_key, app_name, app_author

@pytest.mark.parametrize('fixture_create_file_for_locate', [
    (('temp0.json', None, None)),
], indirect=['fixture_create_file_for_locate'])
def test_locate_by_direct_path(fixture_mock_path, fixture_create_file_for_locate):
    expected_path, _, _, _ = fixture_create_file_for_locate
    assert locate(str(expected_path)).exists()
    assert locate(str(expected_path)) == expected_path

@pytest.mark.parametrize('fixture_create_file_for_locate', [
    (('path', 'app', 'author')),
], indirect=['fixture_create_file_for_locate'])
def test_locate_by_app_name_author(fixture_mock_path, fixture_create_file_for_locate):
    expected_path, path_or_key, app_name, app_author = fixture_create_file_for_locate
    assert locate(path_or_key, app_name, app_author).exists()
    assert locate(path_or_key, app_name, app_author) == expected_path
    assert locate(path_or_key, ResourceMap.load(app_name, app_author)).exists()
    assert locate(path_or_key, ResourceMap.load(app_name, app_author)) == expected_path

@pytest.mark.parametrize('fixture_create_file_for_locate', [
    (('path', 'app', 'author')),
], indirect=['fixture_create_file_for_locate'])
def test_locate_warn(fixture_mock_path, fixture_create_file_for_locate):
    expected_path, path_or_key, app_name, app_author = fixture_create_file_for_locate
    with pytest.warns(UnneededAppAuthorWarning):
        assert locate(path_or_key, app_name, app_author).exists()
        assert locate(path_or_key, app_name, app_author) == expected_path
        assert locate(path_or_key, ResourceMap.load(app_name, app_author), app_author).exists()
        assert locate(path_or_key, ResourceMap.load(app_name, app_author), app_author) == expected_path

@pytest.mark.parametrize('exception,fixture_create_file_for_locate,default', [
    (InvalidAppSelectorError, ('path', None, 'author'), None),
    (InvalidAppSelectorError, ('path', 'app', None), None),
    (InvalidAppSelectorError, ('path', None, None), None),
    (NoDefaultFileError, ('path', 'app', 'author'), None),
    (CannotCopyDefaultFileError, ('path', 'app', 'author'), Path(os.getcwd()) / 'missing/file'),
], indirect=['fixture_create_file_for_locate'])
def test_locate_raises(fixture_mock_path, fixture_create_file_for_locate, exception, default):
    expected_path, path_or_key, app_name, app_author = fixture_create_file_for_locate
    expected_path.unlink()
    with pytest.raises(exception):
        locate(path_or_key, app_name, app_author, default=default)

@pytest.fixture
def fixture_copy_file_safe(tmp_path, request):
    _src, _dst = request.param
    src, dst = tmp_path / _src, tmp_path / _dst
    with open(src, 'w') as fp:
        json.dump({'key': 'value'}, fp)
    return src, dst

@pytest.mark.parametrize('fixture_copy_file_safe', [
    (('src', 'dst')),
    (('src', 'app/dst')),
    (('src', 'author/app/dst')),
], indirect=['fixture_copy_file_safe'])
def test_copy_file_safe(tmp_path, fixture_copy_file_safe):
    src, dst = fixture_copy_file_safe
    assert not dst.exists()
    assert _copy_file_safe(src, dst)
    assert dst.exists()

@pytest.mark.parametrize('fixture_copy_file_safe', [
    (('src', 'parent/author/app/dst')),
    (('src', 'ancestor/parent/author/app/dst')),
], indirect=['fixture_copy_file_safe'])
def test_copy_file_safe_abnormal(tmp_path, fixture_copy_file_safe):
    src, dst = fixture_copy_file_safe
    assert not dst.exists()
    assert not _copy_file_safe(src, dst)
    assert not dst.exists()
