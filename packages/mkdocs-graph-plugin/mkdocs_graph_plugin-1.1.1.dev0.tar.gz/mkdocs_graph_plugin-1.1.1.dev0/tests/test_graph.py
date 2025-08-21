"""Tests for the graph module."""

import tempfile
from pathlib import Path

from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page

from mkdocs_graph_plugin.graph import Graph


def test_graph_build(mocker):
    """Test that the graph is built correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        # Create some dummy files
        (tmpdir / "index.md").write_text("This is the index.")
        (tmpdir / "page1.md").write_text("This is page 1. [link](page2.md)")
        (tmpdir / "page2.md").write_text("This is page 2. [[index]]")
        (tmpdir / "not_a_page.txt").write_text("This is not a page.")

        files_list = [
            File("index.md", str(tmpdir), str(tmpdir / "site"), False),
            File("page1.md", str(tmpdir), str(tmpdir / "site"), False),
            File("page2.md", str(tmpdir), str(tmpdir / "site"), False),
            File("not_a_page.txt", str(tmpdir), str(tmpdir / "site"), False),
        ]

        config = mocker.Mock()
        config.get.return_value = "http://example.com"

        for file in files_list:
            file.page = Page(None, file, config)

        # Create a Files collection
        files = Files(files_list)

        # Build the graph
        plugin_config = {"name": "title"}
        graph = Graph(plugin_config)(files)
        # Check the nodes
        assert len(graph.nodes) == 3
        assert {
            "id": "index.md",
            "path": str(tmpdir / "index.md"),
            "name": "index",
            "url": "index.html",
        } in graph.nodes
        assert {
            "id": "page1.md",
            "path": str(tmpdir / "page1.md"),
            "name": "page1",
            "url": "page1.html",
        } in graph.nodes
        assert {
            "id": "page2.md",
            "path": str(tmpdir / "page2.md"),
            "name": "page2",
            "url": "page2.html",
        } in graph.nodes

        # Check the edges
        assert len(graph.edges) == 2
        assert {"source": "page1.md", "target": "page2.md"} in graph.edges
        assert {"source": "page2.md", "target": "index.md"} in graph.edges


def test_graph_build_ignores_non_site_links(mocker):
    """Test that the graph build ignores links to files not in the site."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        # Create some dummy files
        (tmpdir / "index.md").write_text("This is the index.")
        (tmpdir / "page1.md").write_text("This is page 1. [link](not_in_site.md)")
        (tmpdir / "not_in_site.md").write_text("This page is not in the site.")

        # Create a Files collection that only includes index.md and page1.md
        files_list = [
            File("index.md", str(tmpdir), str(tmpdir / "site"), False),
            File("page1.md", str(tmpdir), str(tmpdir / "site"), False),
        ]

        config = mocker.Mock()
        config.get.return_value = "http://example.com"

        for file in files_list:
            file.page = Page(None, file, config)

        files = Files(files_list)

        # Build the graph
        plugin_config = {"name": "title"}
        graph = Graph(plugin_config)(files)

        # Check that no edges were created
        assert len(graph.edges) == 0
