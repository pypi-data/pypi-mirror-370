# finalsa-sqs-client

Thin, typed wrapper around AWS SQS using boto3 with a simple in-memory test implementation.

- Python 3.10+
- Adds W3C trace headers to all messages by default (traceparent, tracestate)
- Accepts dict or JSON string payloads
- Returns a convenient `SqsReponse` model with flattened message attributes


## Installation

Using pip or uv:

```bash
pip install finalsa-sqs-client
# or
uv add finalsa-sqs-client
```

Requires valid AWS credentials for the default boto3 client (env vars, config file, or IAM role).


## Quick start

```python
from finalsa.sqs.client import SqsServiceImpl, SqsException

svc = SqsServiceImpl()

# Resolve a queue URL by name (helper)
queue_url = svc.get_queue_url("my-queue")

# Send a JSON payload (dict) with optional custom attributes
svc.send_message(queue_url, {"hello": "world"}, {"tenant": "acme"})

# Receive up to 10 messages and delete them
messages = svc.receive_messages(queue_url, max_number_of_messages=10, wait_time_seconds=1)
for msg in messages:
		print("body:", msg.body)  # raw JSON string
		print("attrs:", msg.message_attributes)  # flattened: {"traceparent": "...", ...}
		svc.delete_message(queue_url, msg.receipt_handle)

# Other helpers
arn = svc.get_queue_arn(queue_url)
attrs = svc.get_queue_attributes(queue_url)
```

Errors are raised as `SqsException` wrapping the underlying boto3 error when applicable.


## Message attributes and tracing

- Custom attributes can be passed as a simple dict of strings: `{"key": "value"}`.
- The client adds two trace headers automatically to every send:
	- `traceparent`
	- `tracestate`
- When receiving messages, attributes are returned flattened into a `dict[str, str]` on `SqsReponse.message_attributes`.

Example sending raw string JSON and custom attributes:

```python
svc.send_raw_message(queue_url, '{"a":1}', {"source": "ingestor"})
```


## In-memory test service

For local tests or offline development, use the built-in, in-memory implementation:

```python
from finalsa.sqs.client import SqsServiceTest

svc = SqsServiceTest()
svc.send_message("test-queue", {"x": 1})
msgs = svc.receive_messages("test-queue")
assert len(msgs) == 1
svc.delete_message("test-queue", msgs[0].receipt_handle)
```

Notes:
- `SqsServiceTest` keeps messages in process memory keyed by the queue URL/name you pass.
- It also injects the same trace attributes as the real client so behavior matches production closely.


## API overview

The primary entry points are exported from `finalsa.sqs.client`:

- `SqsService`: abstract interface
- `SqsServiceImpl`: boto3-backed implementation
- `SqsServiceTest`: in-memory implementation for tests
- `SqsException`: error wrapper

Key methods (see docstrings for details):
- `receive_messages(queue_url, max_number_of_messages=1, wait_time_seconds=1) -> list[SqsReponse]`
- `send_message(queue_url, payload: dict, message_attributes: dict | None = None) -> None`
- `send_raw_message(queue_url, data: dict | str, message_attributes: dict | None = None) -> None`
- `delete_message(queue_url, receipt_handle) -> None`
- `get_queue_arn(queue_url) -> str`
- `get_queue_attributes(queue_url) -> dict`
- `get_queue_url(queue_name) -> str`

Payload handling:
- Dict payloads are serialized with orjson (compact) before sending.
- String payloads are sent as-is.


## Credentials and configuration

`SqsServiceImpl` uses the default `boto3.client('sqs')`. Configure credentials/region via any standard boto3 method:
- Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, ...)
- AWS config/credentials files
- IAM role when running in AWS


## Development

Run tests with uv (recommended):

```bash
uv sync
uv run pytest -q
```

Or with plain pip:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .[test]
pytest -q
```


## License

MIT – see `LICENSE.md`.

