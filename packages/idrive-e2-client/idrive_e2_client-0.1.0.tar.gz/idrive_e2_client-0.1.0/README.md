# idrive-e2-client

[![PyPI version](https://img.shields.io/pypi/v/idrive-e2-client.svg)](https://pypi.org/project/idrive-e2-client/)
[![Python versions](https://img.shields.io/pypi/pyversions/idrive-e2-client.svg)](https://pypi.org/project/idrive-e2-client/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Async Python client for the  
[IDrive e2 Get Region Endpoint API](https://www.idrive.com/s3-storage-e2/guides/get_region_endpoint).

This library provides a minimal, typed wrapper around the IDrive e2 region lookup call:

- 🔑 Fetch the correct **endpoint URL** for an access key  
- 🚦 Handle invalid credentials and network errors with clean exceptions  
- ⚡ Async-first design, built on `aiohttp`  

It is lightweight, minimal, and used by the [Home Assistant](https://www.home-assistant.io/) backup integration for IDrive e2.

---

## Install

```bash
pip install idrive-e2-client
```

---

## Quick Start

```python
import asyncio
import aiohttp
from idrive_e2 import IDriveE2Client, InvalidAuth, CannotConnect

ACCESS_KEY = "..."

async def main():
    async with aiohttp.ClientSession() as session:
        client = IDriveE2Client(session)
        try:
            endpoint = await client.get_region_endpoint(ACCESS_KEY)
            print("Resolved endpoint:", endpoint)
        except InvalidAuth:
            print("Invalid credentials")
        except CannotConnect:
            print("Cannot connect to IDrive e2")

asyncio.run(main())
```

---

## Why?

Before you can connect to IDrive e2 with standard S3 tools,  
you must call the **Get Region Endpoint** API to determine the correct regional endpoint.  

This client wraps that step into a reusable Python package with a simple, async method.

---

## Installation

```bash
pip install idrive-e2-client
```

### For development

```bash
git clone https://github.com/patrickvorgers/idrive-e2-client.git
cd idrive-e2-client
pip install -e .[dev]
```
---

## API

### `IDriveE2Client(session: aiohttp.ClientSession)`

Create a new client instance using an aiohttp session.

### `await client.get_region_endpoint(access_key: str) -> str`

Resolve and return the correct endpoint URL for the given access key.  
The returned string is normalized to include a scheme (e.g., `https://...`).

**Raises**  
- `InvalidAuth` → credentials not valid  
- `CannotConnect` → API not reachable/bad response/malformed data  

---

## Exceptions

- `InvalidAuth` -> credentials not valid  
- `CannotConnect` -> API not reachable or bad response  
- `IDriveE2Error` -> base class for all errors  

---

## Contributing

Contributions are welcome! Please open an [issue](../../issues) or [pull request](../../pulls).

---

## License

MIT © 2025 Patrick Vorgers
