# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.3] - 2026-08-19

### Fixed

- **MEP and CPD models now map the real API payload keys** instead of the
  previously assumed names, which left cliol `--json` output with null/zero
  fields while the HTTP call succeeded (#10).
  - `EstimacionMEP`: maps `montoDolar`, `montoBrutoPesos`, `montoNetoPesos`,
    `comisionCompra`/`comisionVenta` and IVA/derecho legs; the exchange rate
    is derived from pesos/dólares when the API does not return it.
  - `ParametrosMEP`: maps `idTipoOperacion` (string), `montoLimiteMinimo`,
    `montoLimiteMaximo`, `esHorarioValido`, `horarioApertura`/`horarioCierre`,
    `simboloTituloCompra` and `idPlazoOperatoriaCompra`; `id_tipo_operatoria`
    is now a string and `plazo` an integer.
  - `ValidacionMEP`: reads the `messages[]` array (title/description) into
    `mensaje`.
  - `ComisionesCPD`: maps `derechoMercado`, `ivaDerechoMercado` and
    `montoInversion`, including values with thousands separators
    (e.g. `"96,395.09"`).

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

[0.1.3]: https://github.com/ezeprimo/py_iol/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/ezeprimo/py_iol/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/ezeprimo/py_iol/compare/v0.1.0...v0.1.1
