# Change Log

# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.1] - 2022-09-04
### Changed
- devcontainer to install build and twine

## [1.1.0] - 2022-09-04
### Added
- devcontainer configurations
- Pre-commit tasks
- isort configurations
- template.env to support .env files for testing
- Added -d/--dump parameter to tests/test_mywatertoronto to dump the Home Assistant data to files - used for mock data in HA tests

### Changed
- renamed tests/test.py to tests/test_mywatertoronto
- number of formatting changes due to flake8

### Removed
- tests/test_template.py, replaced with .env functionality

## [1.0.0] - 2022-08-28

### Added

- Initial commit
