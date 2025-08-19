# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Custom HTML report themes

## [0.0.1a] - 2025-08-18

### Added
- Initial alpha release of sdk-pytest-checkmate plugin
- **Core Features:**
  - `step(name)` context manager for recording test steps with timing
  - `soft_assert(condition, message)` for non-fatal assertions
  - `add_data_report(data, label)` for attaching arbitrary data to test timeline
- **Pytest Markers:**
  - `@pytest.mark.title(name)` for custom test titles
  - `@pytest.mark.epic(name)` for epic-level test grouping
  - `@pytest.mark.story(name)` for story-level test grouping
- **HTML Reporting:**
  - Rich interactive HTML reports with timeline view
  - Expandable/collapsible epic and story sections
  - Inline data inspection with JSON pretty-printing
  - Status filtering (PASSED, FAILED, SKIPPED, etc.)
  - Step timing and error tracking
  - Soft assertion failure aggregation
- **Command Line Options:**
  - `--report-html[=PATH]` to generate HTML reports
  - `--report-title=TITLE` to customize report title
  - `--report-json=PATH` to export results as JSON
- **Async Support:**
  - Context managers work with both `with` and `async with`
  - Full support for async test functions
- **Type Safety:**
  - Full type hints with `py.typed` marker
  - Compatible with mypy and other type checkers
- **Python Compatibility:**
  - Python 3.10+ support
  - pytest 8.4.1+ compatibility

### Technical Details
- Built with modern Python features (union types, dataclasses)
- Uses pytest's StashKey for test data storage
- Context variables for thread-safe test isolation
- Comprehensive error handling and validation
- JSON serialization for data portability

### Documentation
- Complete README with examples and API reference
- Detailed docstrings for all public functions
- Type annotations for LSP support
- Installation and usage instructions

### Testing
- Comprehensive test suite with 36+ test cases
- Unit tests for all core functionality
- Integration tests for combined features
- Marker functionality tests
- Performance testing for large datasets

### Known Limitations
- Requires Python 3.10+ due to union type syntax
- Large data attachments may impact report size
- HTML reports require modern browsers for full functionality

---

## Version History Legend

- **Added** for new features
- **Changed** for changes in existing functionality  
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes

## Links

- [GitHub Repository](https://github.com/o73k51i/sdk-pytest-checkmate)
- [PyPI Package](https://pypi.org/project/sdk-pytest-checkmate/)
- [Issue Tracker](https://github.com/o73k51i/sdk-pytest-checkmate/issues)
