"""Tests the Project type"""

import logging
import tomllib
from importlib import metadata
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from cppython.core.schema import (
    CPPythonLocalConfiguration,
    PEP621Configuration,
    ProjectConfiguration,
    PyProject,
    ToolData,
)
from cppython.project import Project
from cppython.test.mock.generator import MockGenerator
from cppython.test.mock.interface import MockInterface
from cppython.test.mock.provider import MockProvider
from cppython.test.mock.scm import MockSCM

pep621 = PEP621Configuration(name='test-project', version='0.1.0')


class TestProject:
    """Various tests for the project object"""

    @staticmethod
    def test_self_construction(request: pytest.FixtureRequest) -> None:
        """The project type should be constructable with this projects configuration

        Args:
            request: The pytest request fixture
        """
        # Use the CPPython directory as the test data
        file = request.config.rootpath / 'pyproject.toml'
        project_configuration = ProjectConfiguration(project_root=file.parent, version=None)
        interface = MockInterface()

        pyproject_data = tomllib.loads(file.read_text(encoding='utf-8'))
        project = Project(project_configuration, interface, pyproject_data)

        # Doesn't have the cppython table
        assert not project.enabled

    @staticmethod
    def test_missing_tool_table(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
        """The project type should be constructable without the tool table

        Args:
            tmp_path: Temporary directory for dummy data
            caplog: Pytest fixture for capturing logs
        """
        file_path = tmp_path / 'pyproject.toml'

        with open(file_path, 'a', encoding='utf8'):
            pass

        project_configuration = ProjectConfiguration(project_root=file_path.parent, version=None)
        interface = MockInterface()

        pyproject = PyProject(project=pep621)

        with caplog.at_level(logging.WARNING):
            project = Project(project_configuration, interface, pyproject.model_dump(by_alias=True))

        # We don't want to have the log of the calling tool polluted with any default logging
        assert len(caplog.records) == 0

        assert not project.enabled

    @staticmethod
    def test_missing_cppython_table(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
        """The project type should be constructable without the cppython table

        Args:
            tmp_path: Temporary directory for dummy data
            caplog: Pytest fixture for capturing logs
        """
        file_path = tmp_path / 'pyproject.toml'

        with open(file_path, 'a', encoding='utf8'):
            pass

        project_configuration = ProjectConfiguration(project_root=file_path.parent, version=None)
        interface = MockInterface()

        tool_data = ToolData()
        pyproject = PyProject(project=pep621, tool=tool_data)

        with caplog.at_level(logging.WARNING):
            project = Project(project_configuration, interface, pyproject.model_dump(by_alias=True))

        # We don't want to have the log of the calling tool polluted with any default logging
        assert len(caplog.records) == 0

        assert not project.enabled

    @staticmethod
    def test_default_cppython_table(tmp_path: Path, mocker: MockerFixture, caplog: pytest.LogCaptureFixture) -> None:
        """The project type should be constructable with the default cppython table

        Args:
            tmp_path: Temporary directory for dummy data
            mocker: Pytest mocker fixture
            caplog: Pytest fixture for capturing logs
        """
        # Insert ourself into the builder and load the mock plugins by returning them directly in the expected order
        #   they will be built
        mocker.patch(
            'cppython.builder.entry_points',
            return_value=[metadata.EntryPoint(name='mock', value='mock', group='mock')],
        )
        mocker.patch.object(metadata.EntryPoint, 'load', side_effect=[MockGenerator, MockProvider, MockSCM])

        file_path = tmp_path / 'pyproject.toml'

        with open(file_path, 'a', encoding='utf8'):
            pass

        project_configuration = ProjectConfiguration(project_root=file_path.parent, version=None)
        interface = MockInterface()

        cppython_config = CPPythonLocalConfiguration()
        tool_data = ToolData(cppython=cppython_config)
        pyproject = PyProject(project=pep621, tool=tool_data)

        with caplog.at_level(logging.WARNING):
            project = Project(project_configuration, interface, pyproject.model_dump(by_alias=True))

        # We don't want to have the log of the calling tool polluted with any default logging
        assert len(caplog.records) == 0

        assert project.enabled
