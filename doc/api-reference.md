# pyIOL API Reference

This is a source-derived reference for the public `IOLClient` methods in `pyIol/client.py`. Unless marked `raw`, methods return exported dataclasses or booleans. Network, authentication, and API failures normally raise `IOLAPIError`.

## Client

| Method | Parameters | Returns and behavior |
|---|---|---|
| `IOLClient(username, password)` | IOL credentials | Creates an HTTP client; authentication is lazy. |
| `test_authentication()` | none | `bool`; returns `False` instead of raising for `IOLAPIError`. |
| `close()` | none | Closes the HTTP session. Also available through `with`. |

Use `with IOLClient(...) as client:` whenever possible.

## Profile and Market Data

| Typed method | Parameters | Return |
|---|---|---|
| `get_profile_data()` | none | `DatosPerfil` |
| `get_mep_dollar_rate(symbol="AL30")` | `symbol: str` | `dict` |
| `get_stock_quote(symbol, market=Markets.BCBA, settlement_term=SettlementTerms.T1)` | symbol, market, settlement term | `CotizacionTitulo` |
| `get_stock_data(symbol, market=Markets.BCBA)` | symbol, market | `DatosTitulo` |
| `get_stock_options(symbol, market=Markets.BCBA)` | underlying symbol, market | `list[OpcionTitulo]`; returns an empty list for a missing options endpoint. |
| `get_market_instruments(pais="argentina")` | country string | `list[InstrumentoPais]`; normalizes supported list/object responses. |
| `get_massive_quotes(instrumento, pais="argentina")` | instrument, country | `CotizacionesMasivas`; aliases `stocks`, `bonds`, `options`, and `futures` are mapped. |
| `get_panel_quotes(instrumento, panel, pais="argentina")` | instrument, panel, country | `CotizacionesMasivas`; the same four aliases are mapped. |
| `get_stock_quote_detailed(simbolo, mercado="bCBA")` | symbol, market | `CotizacionDetallada` |

The raw counterparts are `get_profile_data_raw()`, `get_stock_quote_raw()`, `get_stock_data_raw()`, `get_stock_options_raw()`, `get_market_instruments_raw()`, `get_massive_quotes_raw()`, `get_panel_quotes_raw()`, and `get_stock_quote_detailed_raw()`. They return the corresponding JSON dictionary/list shape; list-oriented methods may normalize a wrapped response.

## Account and Operations

| Typed method | Parameters | Return |
|---|---|---|
| `get_account_status()` | none | `EstadoCuenta` |
| `get_portfolio(pais="argentina")` | `argentina` or `estados_Unidos` | `Portafolio` |
| `get_operations(estado=None, fecha_desde=None, fecha_hasta=None, pais=None, numero=None)` | optional state, `YYYY-MM-DD` dates, country, operation number | `list[Operacion]`; empty when the response has no recognized operation collection. |
| `get_operation_detail(numero)` | operation number | `OperacionDetalle` |
| `cancel_operation(numero)` | operation number | `True` after a successful DELETE; side effect. |

Raw counterparts: `get_account_status_raw()`, `get_portfolio_raw()`, `get_operations_raw()` (returns a normalized list), `get_operation_detail_raw()`, and `cancel_operation_raw()`.

## Orders and Trading

| Method | Parameters | Return |
|---|---|---|
| `buy` / `buy_raw` | `simbolo, cantidad, precio, mercado=Markets.BCBA, plazo=SettlementTerms.T1, validez=None` | `ResultadoOrden` / raw `dict`; submits a buy order. |
| `sell` / `sell_raw` | same as `buy` | `ResultadoOrden` / raw `dict`; submits a sell order. |
| `buy_dollar_bond` / `buy_dollar_bond_raw` | same as `buy`; symbol is a dollar-species bond | `ResultadoOrden` / raw `dict`; submits a buy order. |
| `sell_dollar_bond` / `sell_dollar_bond_raw` | same as `buy`; symbol is a dollar-species bond | `ResultadoOrden` / raw `dict`; submits a sell order. |

For all four order families, omitted `validez` is generated as an ISO timestamp three UTC hours in the future. `validez` is sent when non-empty. Verify all values before calling these methods.

## FCI

| Typed method | Parameters | Return |
|---|---|---|
| `get_fci_list()` | none | `list[FondoComunInversion]` |
| `get_fci_detail(simbolo)` | FCI symbol | `FCIDetalle` |
| `get_fci_types()` | none | `list[TipoFondo]` |
| `get_fci_managers()` | none | `list[AdministradoraFCI]` |
| `get_fci_types_by_manager(administradora)` | manager name or ID | `list[TipoFondo]` |
| `subscribe_fci(simbolo, monto, solo_validar=False)` | FCI symbol, amount in pesos, optional validation-only flag | `ResultadoFCI`; side effect unless validation-only. |
| `redeem_fci(simbolo, cantidad=None, monto=None, solo_validar=False)` | symbol and exactly one of units or pesos | `ResultadoFCI`; raises `ValueError` if neither or both amount selectors are supplied. |

Each FCI method has a `_raw` counterpart with the same parameters and a raw dictionary/list return: `get_fci_list_raw`, `get_fci_detail_raw`, `get_fci_types_raw`, `get_fci_managers_raw`, `get_fci_types_by_manager_raw`, `subscribe_fci_raw`, and `redeem_fci_raw`.

## Simplified MEP

| Method | Parameters | Return and behavior |
|---|---|---|
| `get_mep_buy_estimate(monto)` | pesos to invest | `EstimacionMEP`; calculation only. |
| `get_mep_sell_estimate(monto)` | dollars to sell | `EstimacionMEP`; calculation only. |
| `get_mep_parameters(id_tipo_operatoria=1)` | operation type ID | `ParametrosMEP`. |
| `validate_mep_operation(monto, id_tipo_operatoria=1)` | pesos and operation type ID | `ValidacionMEP`; validation only. |
| `buy_mep_simplified(monto, id_tipo_operatoria=1)` | pesos and operation type ID | `ResultadoMEP`; submits a real operation. |

Raw counterparts are `get_mep_buy_estimate_raw`, `get_mep_sell_estimate_raw`, `get_mep_parameters_raw`, `validate_mep_operation_raw`, and `buy_mep_simplified_raw`.

## CPD

| Method | Parameters | Return and behavior |
|---|---|---|
| `can_operate_cpd()` | none | `PuedeOperarCPD`. |
| `get_cpd_list(estado="vigentes", segmento="avalados")` | CPD state and segment | `list[ChequeCPD]`. |
| `get_cpd_commissions(importe, plazo, tasa)` | nominal pesos, days, annual discount rate | `ComisionesCPD`; calculation only. |
| `operate_cpd(numero_cheque, precio, cantidad=1)` | cheque number, purchase price, quantity | `ResultadoCPD`; submits a purchase. |

Raw counterparts are `can_operate_cpd_raw`, `get_cpd_list_raw`, `get_cpd_commissions_raw`, and `operate_cpd_raw`.

## Advisor Methods

These methods require the account to have the relevant advisor permissions.

| Method | Parameters | Return and behavior |
|---|---|---|
| `get_advisor_movements(fecha_desde=None, fecha_hasta=None, id_cliente=None, pagina=1, registros_por_pagina=50)` | optional dates/client and pagination | `MovimientosAsesor`. |
| `get_investor_test_questions()` | none | `TestInversor`. |
| `calculate_investor_profile(respuestas)` | list of `{"idPregunta": int, "idRespuesta": int}` | `PerfilInversor`; calculates but does not save. |
| `save_investor_profile(id_cliente, respuestas)` | client ID and answer list | `PerfilInversor`; saves the client's profile. |
| `advisor_sell_dollar_bond(id_cliente, simbolo, cantidad, precio, mercado=Markets.BCBA, plazo=SettlementTerms.T1, validez=None)` | client and order fields | `ResultadoOperacionAsesor`; submits a sale in the client's account. |

Raw counterparts are `get_advisor_movements_raw`, `get_investor_test_questions_raw`, `calculate_investor_profile_raw`, `save_investor_profile_raw`, and `advisor_sell_dollar_bond_raw`.

## Constants and Models

All constants and models below are exported by `pyIol` through `__init__.py`.

| Name | Values or role |
|---|---|
| `Markets` | `BCBA="bCBA"`, `NYSE="nYSE"`, `NASDAQ="nASDAQ"`, `AMEX="aMEX"`, `BCS="bCS"`, `ROFX="rOFX"`. |
| `SettlementTerms` | `T0="t0"`, `T1="t1"`, `T2="t2"`, `T3="t3"`; default is `T1`. |
| `OperationStates` | `ALL="todas"`, `PENDING="pendientes"`, `FINISHED="terminadas"`, `CANCELLED="canceladas"`. |
| `Countries` | `ARGENTINA="argentina"`, `USA="estados_Unidos"`. |
| `CPDStates` | `VIGENTES`, `VENCIDOS`, `TODOS`. |
| `CPDSegments` | `AVALADOS`, `PATROCINADOS`, `GARANTIZADOS`, `TODOS`. |

For the complete exported model list, inspect `pyIol.__all__`; representative response models include `CotizacionTitulo`, `DatosTitulo`, `OpcionTitulo`, `CotizacionesMasivas`, `EstadoCuenta`, `Portafolio`, `Operacion`, `ResultadoOrden`, `ResultadoFCI`, `ResultadoMEP`, `ResultadoCPD`, and `PerfilInversor`.
