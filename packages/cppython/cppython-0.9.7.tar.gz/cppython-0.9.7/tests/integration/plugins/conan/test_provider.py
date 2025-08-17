"""Integration tests for the provider"""

from typing import Any

import pytest

from cppython.plugins.conan.plugin import ConanProvider
from cppython.test.pytest.contracts import ProviderIntegrationTestContract

pytest_plugins = ['tests.fixtures.conan']


class TestConanProvider(ProviderIntegrationTestContract[ConanProvider]):
    """The tests for the conan provider"""

    @staticmethod
    @pytest.fixture(name='plugin_data', scope='session')
    def fixture_plugin_data() -> dict[str, Any]:
        """A required testing hook that allows data generation

        Returns:
            The constructed plugin data
        """
        return {}

    @staticmethod
    @pytest.fixture(name='plugin_type', scope='session')
    def fixture_plugin_type() -> type[ConanProvider]:
        """A required testing hook that allows type generation

        Returns:
            The type of the Provider
        """
        return ConanProvider
