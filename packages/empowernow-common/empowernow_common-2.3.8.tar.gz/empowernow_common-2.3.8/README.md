# EmpowerNow Common SDK

![PyPI](https://img.shields.io/pypi/v/empowernow-common?logo=pypi)
![CI](https://github.com/empowernow/empowernow-common/actions/workflows/ci.yml/badge.svg)

The **EmpowerNow Common SDK** provides authentication helpers, configuration management and utilities shared across EmpowerNow micro-services and platform integrations.

```bash
pip install "empowernow-common[fastapi]"
```

## Quick-start

### Async OAuth
```python
from empowernow_common import async_oauth

cfg = {
    "client_id": "svc",
    "client_secret": "***",
    "token_url": "https://auth.empowernow.io/oauth/token",
    "authorization_url": "https://auth.empowernow.io/oauth/authorize",
}

async with async_oauth(**cfg) as oauth:
    token = await oauth.get_token()
    print(token.access_token)
```

### FastAPI integration
```python
from empowernow_common.fastapi import build_auth_dependency, init
from empowernow_common.settings import EmpowerNowSettings

settings = EmpowerNowSettings.from_env()  # or from_yaml()
init(settings=settings)

app = FastAPI()
app.dependency_overrides[build_auth_dependency()] = lambda: {"sub": "demo"}
```

See the `docs/` folder for full guides.

## Optional extras
* `redis` – distributed caches
* `kafka` – log sink and event bus
* `metrics` – Prometheus client
* `fastapi` – web-framework helpers

## Development
```bash
git clone https://github.com/empowernow/empowernow-common.git
cd empowernow-common
pip install -e .[dev]
pre-commit install
pytest -q
```

## Secret Loader

`empowernow_common` provides a zero-dependency helper to resolve secrets delivered as Docker/K8s secrets or environment variables.

```python
from empowernow_common import load_secret

# read from /run/secrets/primary/db-password
password = load_secret("file:primary:db-password")

# read environment variable MY_API_KEY (dev only)
api_key = load_secret("env:MY_API_KEY")
```

Pointer grammar:

* `file:<instance>:<id>` – Reads `<mount>/<instance>/<id>` where `mount` defaults to `/run/secrets` or `$FILE_MOUNT_PATH`.
* `filex:<instance>:<id>` – Same as `file:` but returns rich structures: JSON objects or line-based `key=value` pairs are parsed into a dict.
* `env:<VAR>` – Returns the environment variable value.

Providers are pluggable:

```python
from empowernow_common.secret_loader import register_provider

def vault_provider(path: str):
    ...
register_provider("vault", vault_provider)
```

Audit: pass `audit_hook` to `load_secret` to stream access events to Kafka/SIEM.

## Shared Kafka Producer

The SDK includes an **optional**, zero-config Kafka helper so services can publish
structured events without re-implementing connection logic.

```python
from empowernow_common.kafka.platform_producer import publish_structured
from empowernow_common.kafka.topics import TOPICS

await publish_structured(
    "pdp.decisions",                     # event_type
    {"decision": "allow", "id": "123"},  # payload (JSON-serialisable)
    topic=TOPICS["pdp.decisions"],       # canonical topic
    key="123"                            # partition key (optional)
)
```

Key points:
* **Optional dependency** – install with `pip install empowernow-common[kafka]`.
* Reads `KAFKA_BOOTSTRAP_SERVERS`, `SERVICE_NAME`, `KAFKA_ENABLED` env vars.
* No-ops automatically if Kafka is disabled or `aiokafka` isn’t installed.
* `empowernow_common.kafka.topics` provides a central map so topic names evolve
  without touching every service.
* Secret-access audit hook already uses the shared producer; you can register
  additional hooks via:
  ```python
  from empowernow_common.kafka.platform_producer import publish
  ```

See `kafka/platform_producer.py` for full documentation and
`kafka/topics.py` for the canonical topic list.

---
© EmpowerNow, Inc. MIT License 