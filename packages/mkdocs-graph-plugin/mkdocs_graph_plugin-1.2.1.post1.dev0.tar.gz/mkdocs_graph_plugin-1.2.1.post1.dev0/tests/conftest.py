import pytest

from mkdocs_graph_plugin.plugin import GraphPlugin


@pytest.fixture
def plugin():
    """Provides a GraphPlugin instance for tests."""
    return GraphPlugin()
