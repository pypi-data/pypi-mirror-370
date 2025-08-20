# Fostrom Device SDK for Python

[Fostrom](https://fostrom.io) is an IoT Cloud Platform built for developers. Monitor and control your fleet of devices, from microcontrollers to industrial IoT. Designed to be simple, secure, and fast. Experience first-class tooling with Device SDKs, type-safe schemas, programmable actions, and more.

The Fostrom Device SDK for Python works with Python 3.8+ and helps you quickly integrate, start monitoring, and controlling your IoT devices in just a few lines of code.

## Installation

```bash
pip install fostrom
```

## Quick Start

```python
from fostrom import Fostrom

# Create SDK instance
fostrom = Fostrom({
    "fleet_id": "<your-fleet-id>",
    "device_id": "<your-device-id>",
    "device_secret": "<your-device-secret>",
})

# Setup mail handler for incoming messages
def handle_mail(mail):
    print(f"Received: {mail.name} ({mail.id})")
    mail.ack()  # Acknowledge the message

fostrom.on_mail = handle_mail

# Connect and start sending data
if fostrom.connect():
    print("Connected successfully!")
else:
    print("Connection failed - check event handlers for details")
    return

# Send sensor data
fostrom.send_datapoint("sensors", {
    "temperature": 23.5,
    "humidity": 65,
    "timestamp": time.time()
})

# Send status messages
fostrom.send_msg("status", {"online": True})

# Keep running to receive events
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping...")
```

## Features

- **Simple API**: Clean, Pythonic interface with full type annotations
- **Real-time Events**: Automatic event streaming for instant mail delivery
- **Background Agent**: Handles connection management and reconnection automatically
- **Error Handling**: Comprehensive error handling with detailed error messages
- **Mail System**: Send and receive messages with ack/reject/requeue operations
- **Type Safety**: Full typing support with mypy compatibility

## Event Handlers

The SDK provides several event handlers you can customize:

```python
fostrom = Fostrom(config)

# Handle incoming mail
fostrom.on_mail = lambda mail: (
    print(f"Mail: {mail.name}"),
    mail.ack()
)

# Handle connection events
fostrom.on_connected = lambda: print("Connected to Fostrom!")
fostrom.on_unauthorized = lambda reason, after: print(f"Auth failed: {reason}")
fostrom.on_reconnecting = lambda reason, after: print(f"Reconnecting: {reason}")
```

## API Reference

### Fostrom Class

#### `__init__(config)`
Create a new Fostrom instance.

**Parameters:**
- `config` (dict): Configuration dictionary with:
  - `fleet_id` (str): Your fleet ID
  - `device_id` (str): Your device ID
  - `device_secret` (str): Your device secret
  - `log` (bool, optional): Enable logging (default: True)

#### `connect() -> bool`
Connect to Fostrom and start the event stream. Returns True on success, False on failure.
On failure, calls appropriate event handlers (`on_unauthorized` or `on_reconnecting`) instead of raising exceptions.

#### `send_datapoint(name: str, payload: dict) -> None`
Send a datapoint to Fostrom.

#### `send_msg(name: str, payload: dict) -> None`
Send a message to Fostrom.

#### `mailbox_status() -> dict`
Get current mailbox status.

#### `next_mail() -> Mail | None`
Get the next mail from the mailbox.



### Mail Class

#### Properties
- `id` (str): Mail ID
- `name` (str): Mail name/type
- `payload` (dict): Mail payload data
- `mailbox_size` (int): Current mailbox size

#### Methods
- `ack()`: Acknowledge the mail
- `reject()`: Reject the mail
- `requeue()`: Requeue the mail

## Error Handling

The SDK uses `FostromError` for all Fostrom-related errors:

```python
from fostrom import Fostrom, FostromError

try:
    fostrom.connect()
except FostromError as e:
    print(f"Error [{e.atom}]: {e.message}")
```

## Complete Example

```python
import time
import random
from fostrom import Fostrom, FostromError

def main():
    fostrom = Fostrom({
        "fleet_id": "your-fleet-id",
        "device_id": "your-device-id",
        "device_secret": "your-device-secret",
    })

    # Event handlers
    fostrom.on_mail = lambda mail: (
        print(f"📧 Mail: {mail.name}"),
        mail.ack()
    )

    fostrom.on_connected = lambda: print("🟢 Connected!")
    fostrom.on_unauthorized = lambda r, a: print(f"🔒 Auth failed: {r}")

    print("Connecting to Fostrom...")
    if fostrom.connect():
        # Send periodic sensor data
        try:
            while True:
                data = {
                    "temperature": round(random.uniform(20, 25), 1),
                    "humidity": random.randint(40, 80),
                    "timestamp": time.time()
                }

                fostrom.send_datapoint("sensors", data)
                print(f"Sent: {data}")

                time.sleep(10)

        except KeyboardInterrupt:
            print("🛑 Stopping...")
    else:
        print("❌ Failed to connect - check event handlers for details")

if __name__ == "__main__":
    try:
        main()
    except FostromError as e:
        print(f"❌ Error: [{e.atom}] {e.message}")
```

## Device Agent

The Fostrom Device SDK downloads and runs the Fostrom Device Agent in the background. The Agent is downloaded automatically when the package is installed. The Device Agent starts when `fostrom.connect()` is called and handles all communication with the Fostrom platform.

The Agent runs continuously in the background for optimal reconnection performance. To stop the Agent completely:

```python
Fostrom.stop_agent()
```

**Note**: Your Python program will continue running to receive real-time events from the Agent. Use Ctrl+C to stop your program gracefully.

## Requirements

- Python 3.8+
- Linux or macOS
- Network connectivity

## Links

- **Fostrom Platform**: [https://fostrom.io](https://fostrom.io)
- **Documentation**: [https://docs.fostrom.io/sdk/py](https://docs.fostrom.io/sdk/py)
- **Python SDK**: [https://pypi.org/project/fostrom/](https://pypi.org/project/fostrom/)

## License

Apache 2.0
