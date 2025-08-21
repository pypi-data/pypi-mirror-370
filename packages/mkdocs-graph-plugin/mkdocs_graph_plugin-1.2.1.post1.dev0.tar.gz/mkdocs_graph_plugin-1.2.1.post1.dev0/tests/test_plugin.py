"""Tests for the plugin module."""

import json
import os
import tempfile
from pathlib import Path

from mkdocs.config import load_config
from mkdocs.structure.files import File, Files
from mkdocs.structure.nav import Navigation
from mkdocs.structure.pages import Page

from mkdocs_graph_plugin.plugin import GraphPlugin


def test_write_graph_file(mocker):
    """Test that the graph is written to a file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        site_dir = tmpdir / "site"
        os.makedirs(site_dir)

        # Create some dummy files
        (tmpdir / "docs").mkdir()
        (tmpdir / "docs" / "index.md").write_text("This is the index.")
        (tmpdir / "docs" / "page1.md").write_text("This is page 1. [link](page2.md)")
        (tmpdir / "docs" / "page2.md").write_text("This is page 2. [[index]]")

        files_list = [
            File("index.md", str(tmpdir / "docs"), str(site_dir), False),
            File("page1.md", str(tmpdir / "docs"), str(site_dir), False),
            File("page2.md", str(tmpdir / "docs"), str(site_dir), False),
        ]

        # Create a Files collection
        files = Files(files_list)

        # Create a config
        config = load_config(
            config_file_path=None,
            site_dir=str(site_dir),
        )

        config["extra_javascript"] = []
        config["extra_css"] = []

        for file in files.documentation_pages():
            file.page = Page(None, file, config)

        # Instantiate the plugin
        plugin = GraphPlugin()
        plugin.load_config({})
        plugin.on_config(config)
        plugin.on_pre_build(config=config)
        nav = mocker.Mock(spec=Navigation)
        plugin.on_nav(nav, config=config, files=files)
        plugin.on_post_build(config=config)

        # Check that the file was created
        graph_file = site_dir / "graph" / "graph.json"
        assert graph_file.exists()

        # Check the contents of the file
        with open(graph_file, "r") as f:
            graph = json.load(f)

        assert len(graph["nodes"]) == 3
        assert {
            "id": "index.md",
            "path": str(tmpdir / "docs" / "index.md"),
            "name": "index",
            "url": "index.html",
        } in graph["nodes"]
        assert {
            "id": "page1.md",
            "path": str(tmpdir / "docs" / "page1.md"),
            "name": "page1",
            "url": "page1.html",
        } in graph["nodes"]
        assert {
            "id": "page2.md",
            "path": str(tmpdir / "docs" / "page2.md"),
            "name": "page2",
            "url": "page2.html",
        } in graph["nodes"]

        assert len(graph["edges"]) == 2
        assert {"source": "page1.md", "target": "page2.md"} in graph["edges"]
        assert {"source": "page2.md", "target": "index.md"} in graph["edges"]


def test_output_dir_is_ignored(mocker):
    """Test that the output_dir config option is ignored."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        site_dir = tmpdir / "site"
        os.makedirs(site_dir)

        # Create some dummy files
        (tmpdir / "docs").mkdir()
        (tmpdir / "docs" / "index.md").write_text("This is the index.")

        files_list = [
            File("index.md", str(tmpdir / "docs"), str(site_dir), False),
        ]

        # Create a Files collection
        files = Files(files_list)

        # Create a config
        config = load_config(
            config_file_path=None,
            site_dir=str(site_dir),
        )

        config["extra_javascript"] = []
        config["extra_css"] = []

        for file in files.documentation_pages():
            file.page = Page(None, file, config)

        # Instantiate the plugin with an output_dir that should be ignored
        plugin = GraphPlugin()
        plugin.load_config({"output_dir": "my-custom-dir"})
        plugin.on_config(config)
        plugin.on_pre_build(config=config)
        nav = mocker.Mock(spec=Navigation)
        plugin.on_nav(nav, config=config, files=files)
        plugin.on_post_build(config=config)

        # Check that the file was created in the hardcoded directory
        graph_file = site_dir / "graph" / "graph.json"
        assert graph_file.exists()

        # Check that the custom directory was not created
        custom_dir = site_dir / "my-custom-dir"
        assert not custom_dir.exists()
