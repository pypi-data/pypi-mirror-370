# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2025-08-21

### Added

- Stable minor release with improved release process
- Enhanced CI/CD workflow for reliable PyPI publishing
- Implemented `no-guess-dev` version scheme for clean releases

### Fixed

- Resolved setuptools-scm versioning issues
- Improved tag-based release workflow
- Corrected PyPI publishing to use exact version for tags

## [1.1.0] - 2025-01-21

### Added

- Stable minor release with improved release process
- Enhanced CI/CD workflow for reliable PyPI publishing

### Fixed

- Resolved setuptools-scm versioning issues
- Improved tag-based release workflow

## [1.0.0] - 2025-01-21

### Added

- First stable major release
- Production-ready interactive graph visualization
- Complete feature set with comprehensive documentation

### Changed

- Promoted to stable release (1.0.0)
- Updated development status to stable

## [0.1.2] - 2025-01-21

### Fixed

- Fixed CI workflow to trigger on tag pushes for PyPI publishing
- Removed redundant PyPI publishing documentation
- Streamlined release process for better automation

### Changed

- Simplified documentation structure
- Improved release workflow reliability

## [0.1.0] - 2025-01-21

### Added

- Interactive graph visualization for MkDocs documentation
- Dual view modes: full-site overview and local page connections
- Seamless integration with Material for MkDocs themes
- Configurable node naming strategies (`title` or `file_name`)
- Debug logging support for development
- Extensive CSS customization via CSS variables
- Responsive design for desktop and mobile devices
- D3.js-powered interactive graph rendering
- Performance-optimized lightweight implementation

### Configuration Options

- `name`: Node naming strategy configuration
- `debug`: Debug logging toggle

### CSS Variables

- `--md-graph-node-color`: Default node color
- `--md-graph-node-color--hover`: Node hover color
- `--md-graph-node-color--current`: Current page node color
- `--md-graph-link-color`: Connection line color
- `--md-graph-text-color`: Node label text color

### Documentation

- Comprehensive documentation site
- Getting started tutorial
- Configuration reference
- Customization guide
- Developer contribution guide

### Development

- Python 3.10+ support
- Material for MkDocs v9.0.0+ compatibility
- Automated testing with pytest
- Code quality tools (ruff, pyright)
- Pre-commit hooks
- GitHub Actions CI/CD pipeline
- Development environment setup with uv

## [0.0.1.dev7] - 2025-01-21

### Added

- Initial development release
- Core plugin functionality
- Basic graph visualization features
- Project structure and tooling setup

---

## Release Notes

### Version Scheme

This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

### Development Versions

Development versions follow the pattern `X.Y.Z.devN` where N is the development iteration.

### Links

- [PyPI Package](https://pypi.org/project/mkdocs-graph-plugin/)
- [Documentation](https://develmusa.github.io/mkdocs-graph-plugin/)
- [GitHub Repository](https://github.com/develmusa/mkdocs-graph-plugin)
- [Issue Tracker](https://github.com/develmusa/mkdocs-graph-plugin/issues)

[Unreleased]: https://github.com/develmusa/mkdocs-graph-plugin/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/develmusa/mkdocs-graph-plugin/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/develmusa/mkdocs-graph-plugin/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/develmusa/mkdocs-graph-plugin/compare/v0.1.2...v1.0.0
[0.1.2]: https://github.com/develmusa/mkdocs-graph-plugin/compare/v0.1.0...v0.1.2
[0.1.0]: https://github.com/develmusa/mkdocs-graph-plugin/compare/v0.0.1.dev7...v0.1.0
[0.0.1.dev7]: https://github.com/develmusa/mkdocs-graph-plugin/releases/tag/v0.0.1.dev7
