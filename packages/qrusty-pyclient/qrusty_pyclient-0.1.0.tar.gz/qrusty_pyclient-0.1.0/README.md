# qrusty_pyclient

A Python client wrapper for the qrusty API.

## Features

- Connect to a qrusty server
- Publish, consume, ack, and purge messages
- List and manage queues

## Installation

```bash
pip install qrusty_pyclient
```

## Usage

```python
from qrusty_pyclient import QrustyClient

client = QrustyClient(base_url="http://localhost:3000")
client.publish(queue="orders", priority=100, payload={"order_id": 123})
message = client.consume(queue="orders", consumer_id="worker-1")
client.ack(queue="orders", message_id=message["id"], consumer_id="worker-1")
```
