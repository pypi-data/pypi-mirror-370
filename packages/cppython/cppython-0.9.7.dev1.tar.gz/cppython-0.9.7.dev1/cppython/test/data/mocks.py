"""Mocked types and data for testing plugins"""

from collections.abc import Sequence

from cppython.core.plugin_schema.generator import Generator
from cppython.core.plugin_schema.provider import Provider
from cppython.core.plugin_schema.scm import SCM
from cppython.test.mock.generator import MockGenerator
from cppython.test.mock.provider import MockProvider
from cppython.test.mock.scm import MockSCM


def _mock_provider_list() -> Sequence[type[Provider]]:
    """Mocked list of providers

    Returns:
        A list of mock providers
    """
    variants = []

    # Default
    variants.append(MockProvider)

    return variants


def _mock_generator_list() -> Sequence[type[Generator]]:
    """Mocked list of generators

    Returns:
        List of mock generators
    """
    variants = []

    # Default
    variants.append(MockGenerator)

    return variants


def _mock_scm_list() -> Sequence[type[SCM]]:
    """Mocked list of SCMs

    Returns:
        List of mock SCMs
    """
    variants = []

    # Default
    variants.append(MockSCM)

    return variants


provider_variants = _mock_provider_list()
generator_variants = _mock_generator_list()
scm_variants = _mock_scm_list()
