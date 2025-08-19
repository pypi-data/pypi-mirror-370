[![release](https://github.com/MarcoMiano/cocon_client/actions/workflows/release.yml/badge.svg)](https://github.com/MarcoMiano/cocon_client/actions/workflows/release.yml)
# Televic CoCon Client

> An asynchronous Python client for interacting with the Televic CoCon REST API.

This library provides a type-safe interface for communicating with a Televic CoCon
server. It supports long-polling for event notifications, command dispatching with
automatic retries and clean shutdown of background tasks.

---

## ✨ Features

- Async-friendly with `async with` support
- Long-polling notification handling
- Automatic command retries with exponential backoff
- Configurable behaviour (timeouts, polling interval, retries)
- Typed and documented public API
- Minimal external dependencies

---

## 📦 Installation

The project requires **Python 3.11+**.

```bash
pip install cocon_client
```

To work on the library locally:

```bash
git clone https://github.com/MarcoMiano/cocon_client.git
cd cocon_client
pip install -e .
```

---

## 🚀 Usage

### Creating a client and subscribing to models

```python
import asyncio
from cocon_client import CoConClient, Model

async def handle_notification(data: dict) -> None:
    print("Received:", data)

async def main() -> None:
    async with CoConClient("192.168.1.100", handler=handle_notification) as client:
        await client.subscribe([Model.DELEGATE, Model.MICROPHONE])
        await asyncio.sleep(10)

asyncio.run(main())
```

### Sending commands

Commands are queued and retried automatically:

```python
response = await client.send("SomeCommand", {"param": "value"})
```

### Parsing raw notifications

The helper `parse_notification` converts raw payloads into typed data classes
defined in `parser.py`:

```python
from cocon_client import parse_notification, Delegates

async def handle_notification(data: dict) -> None:
    model = parse_notification(data)
    if isinstance(model, Delegates):
        print("Delegates:", model.delegates)
```

---

## ⚙️ Configuration

You can override default behaviour using the `Config` dataclass:

```python
from cocon_client import Config, CoConClient

custom_config = Config(
    poll_interval=2.0,
    max_retries=10,
    session_timeout=10.0,
)

client = CoConClient("host", config=custom_config)
```

---

## 🧰 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on how to report issues,
submit patches and extend the parser with new models.

---

## 📄 License

This project is licensed under the **GNU AGPL v3 or later**. See [LICENSE](./LICENSE)
for details.

---

## Disclaimer

See [NOTICE.md](NOTICE.md) for disclaimers regarding Televic CoCon.

---

## 🛠 Maintainers

Developed and maintained by **3P Technologies Srl**.