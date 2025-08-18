# MQTT Connector

A robust MQTT connector for asynchronous MQTT communication.

## Features

- Asynchronous API using Python's asyncio
- **Async and sync message callbacks** - Native support for both sync and async message handlers
- Automatic reconnection handling
- Message throttling to avoid flooding the broker
- Supports both string and JSON message formats
- Thread-safe async callback scheduling from MQTT background threads
- Customizable logging via callback function

## Installation

```bash
pip install mqtt-connector
```

## Basic Usage

```python
import asyncio
from mqtt_connector import MqttConnector

async def main():
    # Create a connector instance
    connector = MqttConnector(
        mqtt_broker="mqtt.example.com",
        mqtt_port=1883,
        client_id="example_client"
    )

    # Set up message callback (supports both sync and async)
    async def message_handler(topic: str, message: str):
        print(f"Received: {topic} -> {message}")
        # Async operations are supported
        await asyncio.sleep(0.01)

    connector.set_message_callback(message_handler)

    # Connect to the broker
    connected = await connector.connect()

    # Subscribe to a topic
    await connector.subscribe("example/incoming")

    # Publish a message
    await connector.publish(
        topic="example/outgoing",
        message={"status": "online", "timestamp": "2025-08-03T12:00:00Z"}
    )

    # Let messages process for a bit
    await asyncio.sleep(2)

    # Disconnect
    await connector.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

## Message Callbacks

The connector supports both synchronous and asynchronous message callbacks:

### Async Callback Example

```python
async def async_message_handler(topic: str, message: str):
    """Async handler can perform I/O operations."""
    print(f"Processing: {topic}")

    # Async operations like database writes, file I/O, etc.
    await process_message_async(message)
    await save_to_database(topic, message)

connector.set_message_callback(async_message_handler)
```

### Sync Callback Example

```python
def sync_message_handler(topic: str, message: str):
    """Sync handler for simple processing."""
    print(f"Received: {topic} -> {message}")

    # Synchronous operations only
    process_message_sync(message)

connector.set_message_callback(sync_message_handler)
```

### Thread Safety

The connector automatically handles thread-safe execution of async callbacks using `call_soon_threadsafe()`, ensuring proper integration with the asyncio event loop even when MQTT messages arrive on background threads.

## Advanced Usage

For more advanced usage examples, check the `examples` directory in the repository.

## API Reference

### MqttConnector

```python
connector = MqttConnector(
    mqtt_broker="mqtt.example.com",  # Broker address
    mqtt_port=1883,                  # Broker port
    client_id=None,                  # Client ID (auto-generated if None)
    reconnect_interval=5,            # Seconds between reconnection attempts
    max_reconnect_attempts=-1,       # Maximum reconnection attempts (-1 = infinite)
    throttle_interval=0.1            # Minimum seconds between publishes
)
```

### Methods

- `await connector.connect(force_reconnect=False)` - Connect to the broker
- `await connector.disconnect()` - Disconnect from the broker
- `await connector.publish(topic, message, qos=0, retain=False)` - Publish a message
- `await connector.subscribe(topic, qos=0)` - Subscribe to a topic
- `connector.is_connected()` - Check connection status
- `connector.set_message_callback(callback)` - Set message callback (sync or async)
- `connector.set_log_callback(callback)` - Set logging callback function

### Message Callback Signature

```python
# Sync callback
def callback(topic: str, message: str) -> None:
    pass

# Async callback
async def callback(topic: str, message: str) -> None:
    pass
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for detailed instructions on:

- Development setup and workflow
- Commit message conventions
- Pre-submission validation checklist
- CI/CD pipeline overview
- Pull request process

## License

This project is licensed under the MIT License - see the LICENSE file for details.
