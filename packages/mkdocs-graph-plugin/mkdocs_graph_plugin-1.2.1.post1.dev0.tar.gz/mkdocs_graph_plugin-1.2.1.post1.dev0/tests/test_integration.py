import subprocess

import pytest


def run_mkdocs_build(site_dir):
    """Runs the mkdocs build command and returns the output."""
    return subprocess.run(
        ["mkdocs", "build"], cwd=site_dir, capture_output=True, text=True
    )


@pytest.fixture
def temp_site(tmp_path):
    """Creates a temporary mkdocs site for integration testing."""
    site_dir = tmp_path / "test_site"
    docs_dir = site_dir / "docs"
    docs_dir.mkdir(parents=True)

    # Create a minimal mkdocs.yml
    (site_dir / "mkdocs.yml").write_text(
        """
        site_name: Test Site
        plugins:
          - graph
        docs_dir: docs
        """
    )

    # Create a sample markdown file
    (docs_dir / "index.md").write_text("Hello, world!")

    return site_dir


def test_integration_build(temp_site):
    """
    Tests that the plugin correctly modifies the output during an
    actual mkdocs build.
    """
    result = run_mkdocs_build(temp_site)

    assert result.returncode == 0, f"MkDocs build failed: {result.stderr}"

    # Check that the graph file was created
    output_file = temp_site / "site" / "graph" / "graph.json"
    assert output_file.exists()


def test_assets_are_in_build_output(temp_site):
    """
    Tests that the plugin's assets are copied to the site directory.
    """
    result = run_mkdocs_build(temp_site)

    assert result.returncode == 0, f"MkDocs build failed: {result.stderr}"

    # Check that the graph file was created
    js_output_file = temp_site / "site" / "js" / "graph.js"
    css_output_file = temp_site / "site" / "css" / "graph.css"
    assert js_output_file.exists()
    assert css_output_file.exists()
