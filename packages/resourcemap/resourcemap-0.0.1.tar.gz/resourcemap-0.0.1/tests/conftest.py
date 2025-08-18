from pathlib import Path
import pytest

from resourcemap.core.format import Format

@pytest.fixture
def fixture_mock_path(mocker, tmp_path):

    class MockedResourceMap:

        @staticmethod
        def path(app_name: str, author_name: str, format: Format) -> Path:
            return tmp_path / f"{app_name}.{format._extension}"

    mocker.patch(
        'resourcemap.core.resource.ResourceMap.path', side_effect=MockedResourceMap.path
    )
