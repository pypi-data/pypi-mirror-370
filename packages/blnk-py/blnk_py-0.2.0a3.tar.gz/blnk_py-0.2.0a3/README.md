# blnk-py (async)

Typed **async** Python SDK for a Blnk-style ledger & reconciliation API.

- ✅ Pydantic models for requests/responses (transactions, balances, ledgers, reconciliation, search)
- ✅ Idempotency key on mutating calls
- ✅ Structured errors (401/404/429/5xx), retries with backoff
- ✅ Clean resource groups: `transactions`, `balances`, `ledgers`, `reconciliation`, `search`
- ✅ In-app **ASGI transport** for testing against a FastAPI app without real network I/O

> This SDK is API-shape compatible with typical Blnk deployments. Adjust `base_url` and any field names to your tenant as needed.

## Install

### From source (editable)
```bash
pip install -e .[dev]
```

### From wheel/sdist
```bash
pip install blnk-py-0.2.0a3-py3-none-any.whl
# or
pip install dist/blnk-py-0.2.0a3.tar.gz
```

## Quick start (async)

```python
import asyncio
from blnk_py import AsyncBlnkClient
from blnk_py.models.ledgers import CreateLedger
from blnk_py.models.balances import CreateBalance
from blnk_py.models.transactions import TransactionCreate, Destination

async def main():
    client = AsyncBlnkClient(api_key="BLNK_API_KEY", base_url="https://your-tenant.blnk.example")
    ledger = await client.ledgers.create(CreateLedger(name="Wallets", currency="GHS", precision=100))
    wallet = await client.balances.create(CreateBalance(ledger_id=ledger.id, currency="GHS", precision=100))

    # Top-up (inflight -> commit)
    topup = await client.transactions.create(TransactionCreate(
        source="@WorldGHS",
        destination=wallet.id,
        amount=150.00,
        precision=100,
        currency="GHS",
        reference="dep_001",
        inflight=True,
        meta_data={"provider":"Transact"}
    ))
    await client.transactions.commit_inflight(topup.id)

    # Withdraw with a revenue fee via multi-destination
    wd = await client.transactions.create(TransactionCreate(
        source=wallet.id,
        amount=101.00,
        reference="wd_001",
        destinations=[
            Destination(identifier="@WorldGHS",      distribution="100.00"),
            Destination(identifier="@RevenueGHS",    distribution="1.00")
        ],
        currency="GHS", precision=100, inflight=True
    ))
    await client.transactions.commit_inflight(wd.id)

    await client.aclose()

asyncio.run(main())
```

## API Map

| Resource        | Methods (async)                                                                       |
|-----------------|----------------------------------------------------------------------------------------|
| `transactions`  | `create(body, *, idempotency_key=None)`, `commit_inflight(id)`, `void_inflight(id)`, `refund(transaction_id, body=None)` |
| `balances`      | `create(body)`, `get(balance_id, with_queued=True)`, `get_at(balance_id, iso_timestamp)` |
| `ledgers`       | `create(body)`                                                                         |
| `reconciliation`| `upload(req)`, `create_rule(rule)`, `start(req)`, `start_instant(external_payload)`    |
| `search`        | `transactions(q='*', filter_by=None, per_page=50)`, `balances(q='*', per_page=50)`     |

### Important models
- `TransactionCreate`: supports `source+destination`, or `sources`, or `destinations` (for splits).
- `Destination`/`Source`: `identifier` (balance id or `@internal`), `distribution` (amount or `"10%"`).
- `InflightUpdate`: `status` = `"commit"` or `"void"`.

## Idempotency

All `POST`/`PUT`/`PATCH` calls set `Idempotency-Key` automatically. Pass your own via `idempotency_key=` if you want to control it.

## Error handling

- `AuthError` for 401
- `NotFoundError` for 404
- `RateLimitError` for 429 (with `retry_after`)
- `ApiError` for other non-2xx responses
- Retries with exponential backoff for 429/5xx on the default `AsyncHttp`

## Testing without network (ASGI transport)

Use `InAppAsyncHttp` to point the client at a local FastAPI app:

```python
from blnk_py.http import InAppAsyncHttp
from blnk_py.config import Config
from some_fastapi_app import app

cfg = Config(api_key="test", base_url="http://in-app")
client = AsyncBlnkClient(api_key="test", http=InAppAsyncHttp(cfg, app, base_prefix="/blnk"))
```

## Versioning

Pre-release (alpha) tags: `0.2.0aN`. API may evolve—pin to a version in production.

## License

MIT
