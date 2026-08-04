# pyIOL Agent Guide

This guide is for programming agents building applications with `pyiol-client`. It describes the stable entry points visible in the repository, not undocumented IOL API behavior.

## Quick Path

1. Install `pyiol-client` and keep credentials outside source control.
2. Create one `IOLClient` for a unit of work and use it as a context manager.
3. Start with read-only methods and typed results.
4. Add explicit validation, confirmation, logging, and limits before any money-moving method.

```python
from pyIol import IOLClient

with IOLClient(username, password) as client:
    quote = client.get_stock_quote("GGAL")
    print(quote.ultimo_precio)
```

## Installation and Credentials

```bash
python -m pip install pyiol-client
```

For repository development:

```bash
uv sync
```

The runtime package requires Python `>=3.8`, `httpx`, and `cachetools`. The optional `dev` extra adds notebooks, dotenv support, Ruff, and pytest. Pass credentials to `IOLClient(username, password)`; the client sends them to IOL only when it obtains an access token.

Never place credentials in source, prompts, logs, notebooks, test fixtures, or command history. Prefer environment variables or a secret manager. The repository's `.env` is for local use and must not be committed.

## Authentication and Lifecycle

`IOLClient` creates an `httpx.Client`, authenticates lazily on the first authenticated request, and caches the access token for 870 seconds. `test_authentication()` returns `True` or `False`; normal methods raise `IOLAPIError` when authentication or an API request fails.

```python
with IOLClient(username, password) as client:
    if not client.test_authentication():
        raise RuntimeError("IOL authentication failed")
    profile = client.get_profile_data()
```

The context manager closes the HTTP session. Call `close()` when managing the lifecycle manually.

## Typed and Raw Methods

Most endpoint methods have a matching `_raw()` method.

- Typed methods convert API dictionaries into exported dataclasses such as `CotizacionTitulo`, `Portafolio`, and `ResultadoOrden`.
- Raw methods return dictionaries or lists shaped for that endpoint and are useful when an application needs fields not represented by a model.
- Do not assume every raw method is the untouched HTTP top-level response. Several methods normalize list/object responses, for example FCI, options, instruments, operations, and CPD methods.
- Typed model fields use Python names such as `ultimo_precio`; raw payloads preserve API names such as `ultimoPrecio`.

Choose typed methods at application boundaries when the expected contract is known. Choose raw methods only at an integration boundary that intentionally owns API-shape handling.

## Selecting Endpoints

Use [`api-reference.md`](./api-reference.md) as the source of truth for method names, parameters, and return types.

Common selection rules:

- A single security quote: `get_stock_quote()`.
- Security metadata: `get_stock_data()`.
- Options for a security: `get_stock_options()`.
- Instrument discovery: `get_market_instruments()`.
- Broad or panel market data: `get_massive_quotes()` or `get_panel_quotes()`.
- Account and holdings: `get_account_status()` and `get_portfolio()`.
- Historical orders: `get_operations()` and `get_operation_detail()`.
- FCI discovery: `get_fci_list()`, `get_fci_detail()`, and related catalog methods.
- MEP planning: estimate and validation methods before `buy_mep_simplified()`.
- CPD planning: `can_operate_cpd()`, `get_cpd_list()`, and `get_cpd_commissions()` before `operate_cpd()`.

Use exported constants instead of repeating protocol values:

```python
from pyIol import Countries, Markets, OperationStates, SettlementTerms

market = Markets.BCBA
term = SettlementTerms.T1
country = Countries.ARGENTINA
state = OperationStates.ALL
```

`Markets`, `SettlementTerms`, `OperationStates`, `Countries`, `CPDStates`, and `CPDSegments` are available from `pyIol`. Their values and defaults are listed in the API reference.

## Error Handling

Catch `IOLAPIError` around authentication and network/API operations. `redeem_fci()` and `redeem_fci_raw()` also raise `ValueError` when neither, or both, of `cantidad` and `monto` are supplied.

Do not treat an empty list as proof that an account or market has no data without considering the endpoint behavior. Some read methods return empty collections for a `404` response. Keep the request inputs and endpoint name in application logs, but redact credentials and access tokens.

## Financial Safety Rules

The following methods submit or modify financial operations and must be treated as side-effecting:

- `buy()`, `sell()`, `buy_dollar_bond()`, `sell_dollar_bond()`
- `cancel_operation()`
- `subscribe_fci()`, `redeem_fci()`
- `buy_mep_simplified()`
- `operate_cpd()`
- `save_investor_profile()`
- `advisor_sell_dollar_bond()`

Before enabling one in an application:

- Verify the symbol, country, market, settlement term, quantity, price, currency, and account.
- Fetch current account/portfolio state and display a human-readable confirmation.
- Use estimate, validation, permission, and commission methods where available.
- Supply an explicit ISO `validez` when the application needs a deliberate expiry; when omitted, order methods generate a validity time three UTC hours in the future.
- Make retries conservative. A network error after submission does not prove that no order was created; query the operation history before retrying.
- Store operation identifiers and response payloads securely for reconciliation.
- Start with mocked tests and the IOL sandbox where available. The repository does not provide a separate runtime sandbox configuration.

The library is an unofficial client. It does not provide transaction guarantees, idempotency keys, portfolio suitability advice, or a dry-run mode for ordinary orders. `solo_validar=True` is supported by FCI subscription/redemption; MEP and CPD expose separate planning/validation methods.

## Application Architecture

Keep pyIOL behind an application adapter instead of importing it throughout business logic:

- **Infrastructure adapter:** owns `IOLClient`, credentials, request lifecycle, timeout policy, and translation of `IOLAPIError`.
- **Application services:** select endpoints, apply business rules, enforce limits, and require confirmation for side effects.
- **Domain models:** store the small set of values the application needs; do not leak raw API dictionaries into the domain.
- **Presentation/jobs:** render quotes or submit approved commands; never let a UI retry a failed order blindly.
- **Persistence/audit:** record timestamps, inputs, operation IDs, and sanitized responses for reconciliation.

Use dependency injection for the adapter so tests can use fakes without network access. Keep read and write capabilities separate when possible. A service that only displays prices should not receive an object capable of submitting orders.

## Distribution Boundary

The repository documentation is canonical for agents working from source. `pyproject.toml` excludes `/doc` from source distributions and configures the wheel to package only `pyIol`; installed `pyiol-client` distributions therefore do not include these Markdown files. This documentation change intentionally does not alter packaging.

## Further Reading

- [`api-reference.md`](./api-reference.md): method-by-method public client reference.
- [`recipes/`](./recipes/): small read-only scripts.
- [`iol_api_doc.MD`](./iol_api_doc.MD): repository endpoint notes and examples.
- [`notebooks/`](./notebooks/): interactive examples; mutating examples are commented out for safety.
- [`../SECURITY.md`](../SECURITY.md): security reporting policy.
