# finalsa SNS client

Lightweight AWS SNS client for Python with:

- Topic discovery/creation and basic subscription helpers
- Single and batch message publishing
- Default W3C trace headers and produced-at timestamp on messages
- Minimal test client for local/testing (`SnsClientTest`)

## Install

Requires Python 3.10+.

```bash
uv add finalsa-sns-client
```

## Quick start

```python
from finalsa.sns.client import SnsClientImpl

client = SnsClientImpl()

# Ensure a topic exists
client.get_or_create_topic("orders")

# Publish a string payload
client.publish("orders", "hello world")

# Publish a dict payload with default trace headers
client.publish_message("orders", {"id": 1, "status": "created"})

# Publish in batch (up to 10 per batch)
client.publish_messages_batch("orders", [{"id": i} for i in range(5)])
```

## Testing locally

Use the in-memory client:

```python
from finalsa.sns.client import SnsClientTest

client = SnsClientTest()
client.publish_message("test", {"ok": True})
assert client.messages("test")[0] == {"ok": True}
```

Run tests:

```bash
uv run -m pytest -q
```

## License

MIT
