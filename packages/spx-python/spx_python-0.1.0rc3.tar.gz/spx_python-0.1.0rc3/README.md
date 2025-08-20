# spx-python &mdash; Quick‑Start Guide
Lightweight Python wrapper for the **SPX server** — model, simulate and test devices through the SPX REST API.  
Designed for effortless use in **local development**, **CI pipelines**, and **unit‑testing suites**.

---

## Table of Contents
1. [Requirements](#requirements)  
2. [Installation](#installation)  
3. [Running an SPX server](#running-an-spx-server)  
4. [Connecting from Python](#connecting-from-python)  
5. [Common operations (step‑by‑step)](#common-operations-step-by-step)  
6. [Full‑system example](#full-system-example)  
7. [Using the client in unit tests](#using-the-client-in-unit-tests)  
8. [CI integration (GitHub Actions)](#ci-integration-github-actions)  
9. [FAQ](#faq)  
10. [License](#license)  

---

## Requirements
| Requirement | Notes |
|-------------|-------|
| Python ≥ 3.7 | Officially tested on 3.9 – 3.12 |
| Docker & Docker Compose | To launch **spx‑server** locally |
| `SPX_PRODUCT_KEY` | Export in your shell or set as a CI secret |

---

## Installation
```bash
pip install spx-python                         # or add to poetry/requirements.txt
```

If you develop the package locally:
```bash
poetry add --dev spx-python pytest pytest-cov coverage
```

---

## Running an SPX server
1. Create **docker‑compose.yml** (minimal):
```yaml
services:
  spx-server:
    image: simplephysx/spx-server:latest
    ports: ["8000:8000"]
    environment:
      SPX_PRODUCT_KEY: ${SPX_PRODUCT_KEY}
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8000/ || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5
```
2. Start it:
```bash
export SPX_PRODUCT_KEY="YOUR_REAL_KEY"
docker compose up -d         # server listens on :8000
```

---

## Connecting from Python
```python
import os, spx_python
from spx_python.client import SpxClient

client: SpxClient = spx_python.init(
    address     = "http://localhost:8000",   # default
    product_key = os.environ["SPX_PRODUCT_KEY"],
)
```
`client` now represents the **root** of the SPX system and behaves like a dictionary plus convenience helpers.

---

## Common operations (step‑by‑step)

### 1&nbsp;· Inspect an empty system
```python
print(client.keys())      # ['models', 'instances', 'timer', 'polling']
```

### 2&nbsp;· Add a model
```python
client["models"]["TemperatureSensor"] = {
    "attributes": {"temperature": 25.0, "heating_power": 0.0}
}
```

### 3&nbsp;· Create an instance
```python
client["instances"]["sensor"] = "TemperatureSensor"
sensor = client["instances"]["sensor"]
```

### 4&nbsp;· Read / write an attribute
```python
temp_attr = sensor["attributes"]["temperature"]
print(temp_attr.internal_value)      # 25.0
temp_attr.internal_value = 30.0      # update
```

### 5&nbsp;· Delete things
```python
del client["instances"]["sensor"]
del client["models"]["TemperatureSensor"]
```

---

## Full‑system example
The unit‑tests (`tests/test_full_spx_python.py`) show a PID loop built from
three models (`TemperatureSensor`, `PowerSupply`, `PIDController`).  
Load the YAML, create instances, wire connections, then run `prepare()` and `run()` to watch values propagate.

---

## Using the client in unit tests
```python
def test_attribute_roundtrip():
    key = os.environ["SPX_PRODUCT_KEY"]
    w   = spx_python.init(product_key=key)

    w["models"]["Foo"] = {"attributes": {"x": 1}}
    w["instances"]["foo1"] = "Foo"
    inst = w["instances"]["foo1"]

    inst["attributes"]["x"].internal_value = 42
    assert inst["attributes"]["x"].internal_value == 42
```

---

## CI integration (GitHub Actions)
```yaml
env:
  SPX_PRODUCT_KEY: ${{ secrets.SPX_PRODUCT_KEY }}

steps:
  - uses: actions/checkout@v3
  - uses: actions/setup-python@v4
    with: { python-version: "3.10" }

  - run: |
      python -m pip install poetry
      poetry install

  - run: docker compose up -d        # start server
  - run: |                           # wait until healthy
      for i in {1..10}; do
        curl -fs http://localhost:8000/ && break
        echo "waiting…"; sleep 5
      done
  - run: |                           # run unit tests + coverage
      poetry run python -m unittest discover -s tests
  - if: always()
    run: docker compose down
```

---

## FAQ
| Question | Answer |
|----------|--------|
| *Why not use `str\|None` type‑hints?* | `Optional[str]` keeps compatibility with Python 3.7 – 3.8. |
---

## License
SPX‑Python is released under the MIT License – see [LICENSE](LICENSE).