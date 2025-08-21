import nox

nox.options.default_venv_backend = "uv"


@nox.session(python=["3.10", "3.11", "3.12", "3.13"])
def tests(session):
    """Run the test suite."""
    session.run("uv", "sync")
    session.run("uv", "pip", "install", "-e", ".[dev]")
    session.run("pytest")


@nox.session
def lint(session):
    """Lint the code."""
    session.run("uv", "sync")
    session.run("uv", "pip", "install", "-e", ".[dev]")
    session.run("ruff", "check", ".", "--fix")
    session.run("pyright")


@nox.session
def docs(session):
    """Build the documentation."""
    session.run("uv", "sync")
    session.run("uv", "pip", "install", "-e", ".[dev]")
    session.run("mkdocs", "build")


@nox.session
def build(session):
    """Build distribution packages."""
    session.run("uv", "sync")
    session.run("uv", "pip", "install", "build")
    session.run("python", "-m", "build", "--sdist", "--wheel", "--outdir", "dist/")
