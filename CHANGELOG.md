# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.2] - 2026-08-08

### Fixed

- **TypeError in `ComisionesCPD.from_dict()`** when the API returns numeric
  values as strings (e.g., `"138.02"` instead of `138.02`). Added defensive
  conversion helpers (`_to_float`, `_to_int`, `_to_optional_float`,
  `_to_optional_int`) and applied them to every model that receives numeric
  fields from the API (~30 models). The helpers also handle regional number
  formatting (comma decimals, dot thousands) and non-numeric edge cases
  (empty `{}`, `null`). (#4)

## [0.1.1] - 2026-08-04

### Added

- Token caching for authenticated API requests.

### Changed

- Updated the package version to `0.1.1`.
- Adjusted client behavior for Python 3.8 compatibility.

[0.1.2]: https://github.com/ezeprimo/py_iol/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/ezeprimo/py_iol/compare/v0.1.0...v0.1.1
