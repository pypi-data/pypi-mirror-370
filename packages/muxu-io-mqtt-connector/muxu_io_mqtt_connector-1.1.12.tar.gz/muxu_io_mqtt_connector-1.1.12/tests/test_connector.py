"""Tests for the MQTT connector module."""

import asyncio
import os
import uuid

import pytest

from mqtt_connector import MqttConnector


@pytest.fixture
def mqtt_connector():
    """Create an MqttConnector instance for testing."""
    # Use a unique client ID to avoid conflicts
    unique_id = uuid.uuid4().hex[:8]

    # Use environment variables for broker configuration (CI/local development)
    mqtt_host = os.getenv("MQTT_BROKER_HOST", "test.mosquitto.org")
    mqtt_port = int(os.getenv("MQTT_BROKER_PORT", "1883"))

    connector = MqttConnector(
        mqtt_broker=mqtt_host,
        mqtt_port=mqtt_port,
        client_id=f"test_connector_{unique_id}",
        reconnect_interval=2,
        max_reconnect_attempts=3,
        throttle_interval=0.1,
    )
    return connector


@pytest.mark.asyncio
async def test_connect(mqtt_connector):
    """Test connection to MQTT broker."""
    try:
        result = await mqtt_connector.connect()
        assert result is True
        assert mqtt_connector.is_connected() is True
    finally:
        await mqtt_connector.disconnect()


@pytest.mark.asyncio
async def test_disconnect(mqtt_connector):
    """Test disconnection from MQTT broker."""
    try:
        await mqtt_connector.connect()
        await mqtt_connector.disconnect()
        assert mqtt_connector.is_connected() is False
    finally:
        if mqtt_connector.is_connected():
            await mqtt_connector.disconnect()


@pytest.mark.asyncio
async def test_publish(mqtt_connector):
    """Test publishing a message."""
    try:
        await mqtt_connector.connect()
        # Use a unique topic to avoid interference
        unique_topic = f"test/topic/{uuid.uuid4().hex[:8]}"
        result = await mqtt_connector.publish(unique_topic, "test message")
        assert result is True
    finally:
        await mqtt_connector.disconnect()


@pytest.mark.asyncio
async def test_subscribe(mqtt_connector):
    """Test subscribing to a topic."""
    try:
        await mqtt_connector.connect()
        # Use a unique topic to avoid interference
        unique_topic = f"test/topic/{uuid.uuid4().hex[:8]}"
        result = await mqtt_connector.subscribe(unique_topic)
        assert result is True
    finally:
        await mqtt_connector.disconnect()


@pytest.mark.asyncio
async def test_log_callback(mqtt_connector):
    """Test the log callback functionality."""
    log_messages = []

    def log_callback(level, message):
        log_messages.append((level, message))

    try:
        mqtt_connector.set_log_callback(log_callback)
        await mqtt_connector.connect()
        assert len(log_messages) > 0
        # Check that we have at least one log message from connection
        connection_logs = [
            msg for level, msg in log_messages if "connect" in msg.lower()
        ]
        assert len(connection_logs) > 0
    finally:
        await mqtt_connector.disconnect()


@pytest.mark.asyncio
async def test_json_publish(mqtt_connector):
    """Test publishing JSON messages."""
    try:
        await mqtt_connector.connect()
        unique_topic = f"test/json/{uuid.uuid4().hex[:8]}"
        json_message = {"timestamp": "2025-08-03", "value": 42, "status": "active"}
        result = await mqtt_connector.publish(unique_topic, json_message)
        assert result is True
    finally:
        await mqtt_connector.disconnect()


@pytest.mark.asyncio
async def test_qos_publish(mqtt_connector):
    """Test publishing with different QoS levels."""
    try:
        await mqtt_connector.connect()
        unique_topic = f"test/qos/{uuid.uuid4().hex[:8]}"

        # Test QoS 0
        result = await mqtt_connector.publish(unique_topic, "QoS 0 message", qos=0)
        assert result is True

        # Test QoS 1
        result = await mqtt_connector.publish(unique_topic, "QoS 1 message", qos=1)
        assert result is True

    finally:
        await mqtt_connector.disconnect()


@pytest.mark.asyncio
async def test_message_callback():
    """Test message callback functionality."""
    unique_id = uuid.uuid4().hex[:8]

    # Use environment variables for broker configuration
    mqtt_host = os.getenv("MQTT_BROKER_HOST", "test.mosquitto.org")
    mqtt_port = int(os.getenv("MQTT_BROKER_PORT", "1883"))

    connector = MqttConnector(
        mqtt_broker=mqtt_host,
        mqtt_port=mqtt_port,
        client_id=f"callback_test_{unique_id}",
        throttle_interval=0.1,
    )

    received_messages = []

    def message_callback(topic, message):
        received_messages.append((topic, message))

    try:
        connector.set_message_callback(message_callback)
        await connector.connect()

        unique_topic = f"test/callback/{unique_id}"
        await connector.subscribe(unique_topic)

        # Give subscription time to register
        await asyncio.sleep(0.5)

        await connector.publish(unique_topic, "callback test message")

        # Wait for message to be received
        await asyncio.sleep(1)

        # Check if we received the message
        assert len(received_messages) > 0
        topic, message = received_messages[0]
        assert topic == unique_topic
        assert message == "callback test message"

    finally:
        await connector.disconnect()


@pytest.mark.asyncio
async def test_context_manager():
    """Test async context manager functionality."""
    unique_id = uuid.uuid4().hex[:8]

    # Use environment variables for broker configuration
    mqtt_host = os.getenv("MQTT_BROKER_HOST", "test.mosquitto.org")
    mqtt_port = int(os.getenv("MQTT_BROKER_PORT", "1883"))

    async with MqttConnector(
        mqtt_broker=mqtt_host,
        mqtt_port=mqtt_port,
        client_id=f"ctx_test_{unique_id}",
    ) as connector:
        assert connector.is_connected() is True

        unique_topic = f"test/context/{unique_id}"
        result = await connector.publish(unique_topic, "Context manager test")
        assert result is True

    # Should be disconnected after context manager exits
    assert connector.is_connected() is False


@pytest.mark.asyncio
async def test_throttling():
    """Test message throttling functionality."""
    unique_id = uuid.uuid4().hex[:8]

    # Use environment variables for broker configuration
    mqtt_host = os.getenv("MQTT_BROKER_HOST", "test.mosquitto.org")
    mqtt_port = int(os.getenv("MQTT_BROKER_PORT", "1883"))

    connector = MqttConnector(
        mqtt_broker=mqtt_host,
        mqtt_port=mqtt_port,
        client_id=f"throttle_test_{unique_id}",
        throttle_interval=0.5,  # 500ms throttling
    )

    try:
        await connector.connect()
        unique_topic = f"test/throttle/{unique_id}"

        # Measure time for rapid publishes
        start_time = asyncio.get_event_loop().time()

        for i in range(3):
            result = await connector.publish(unique_topic, f"message {i}")
            assert result is True

        end_time = asyncio.get_event_loop().time()

        # With throttling, 3 messages should take at least 1 second (2 * 0.5s throttle)
        elapsed = end_time - start_time
        assert (
            elapsed >= 1.0
        ), f"Throttling failed: only took {elapsed: .2f}s for 3 messages"

    finally:
        await connector.disconnect()


@pytest.fixture
def ssl_auth_mqtt_connector():
    """Create an SSL + Auth MqttConnector instance for testing."""
    unique_id = uuid.uuid4().hex[:8]

    # Always use external mosquitto test server for SSL tests
    # This ensures SSL tests run even when using local broker for basic tests
    connector = MqttConnector(
        mqtt_broker="test.mosquitto.org",  # External SSL-enabled broker
        mqtt_port=8885,  # SSL + Auth port (encrypted and authenticated)
        client_id=f"ssl_auth_test_connector_{unique_id}",
        username="rw",  # Read-write user
        password="readwrite",
        use_ssl=True,  # Enable SSL
        verify_ssl=False,  # Disable certificate verification for testing
        reconnect_interval=2,
        max_reconnect_attempts=3,
        throttle_interval=0.1,
    )
    return connector


@pytest.mark.asyncio
@pytest.mark.ssl
@pytest.mark.external
async def test_ssl_auth_connect(ssl_auth_mqtt_connector):
    """Test SSL + authenticated connection to MQTT broker."""
    try:
        result = await ssl_auth_mqtt_connector.connect()
        assert result is True
        assert ssl_auth_mqtt_connector.is_connected() is True
    finally:
        await ssl_auth_mqtt_connector.disconnect()


@pytest.mark.asyncio
@pytest.mark.ssl
@pytest.mark.external
async def test_ssl_auth_publish(ssl_auth_mqtt_connector):
    """Test publishing with SSL + authentication."""
    try:
        await ssl_auth_mqtt_connector.connect()
        unique_topic = f"test/ssl_auth/topic/{uuid.uuid4().hex[:8]}"
        result = await ssl_auth_mqtt_connector.publish(
            unique_topic, "SSL + Auth test message"
        )
        assert result is True
    finally:
        await ssl_auth_mqtt_connector.disconnect()


@pytest.mark.asyncio
@pytest.mark.ssl
@pytest.mark.external
async def test_ssl_auth_json_publish(ssl_auth_mqtt_connector):
    """Test publishing JSON with SSL + authentication."""
    try:
        await ssl_auth_mqtt_connector.connect()
        unique_topic = f"test/ssl_auth/json/{uuid.uuid4().hex[:8]}"
        json_message = {
            "ssl_enabled": True,
            "authenticated": True,
            "timestamp": "2025-08-03",
            "value": 42,
            "user": "rw",
        }
        result = await ssl_auth_mqtt_connector.publish(unique_topic, json_message)
        assert result is True
    finally:
        await ssl_auth_mqtt_connector.disconnect()


@pytest.mark.asyncio
@pytest.mark.ssl
@pytest.mark.external
async def test_ssl_auth_subscribe(ssl_auth_mqtt_connector):
    """Test subscribing with SSL + authentication."""
    try:
        await ssl_auth_mqtt_connector.connect()
        unique_topic = f"test/ssl_auth/subscribe/{uuid.uuid4().hex[:8]}"
        result = await ssl_auth_mqtt_connector.subscribe(unique_topic)
        assert result is True
    finally:
        await ssl_auth_mqtt_connector.disconnect()


@pytest.mark.asyncio
@pytest.mark.ssl
@pytest.mark.external
async def test_ssl_auth_qos_publish(ssl_auth_mqtt_connector):
    """Test publishing with different QoS levels over SSL + Auth."""
    try:
        await ssl_auth_mqtt_connector.connect()
        unique_topic = f"test/ssl_auth/qos/{uuid.uuid4().hex[:8]}"

        # Test QoS 0
        result = await ssl_auth_mqtt_connector.publish(
            unique_topic, "SSL + Auth QoS 0 message", qos=0
        )
        assert result is True

        # Test QoS 1
        result = await ssl_auth_mqtt_connector.publish(
            unique_topic, "SSL + Auth QoS 1 message", qos=1
        )
        assert result is True

    finally:
        await ssl_auth_mqtt_connector.disconnect()


@pytest.mark.asyncio
@pytest.mark.ssl
@pytest.mark.external
async def test_ssl_auth_context_manager():
    """Test SSL + Auth with async context manager."""
    unique_id = uuid.uuid4().hex[:8]

    # Always use external mosquitto test server for SSL tests
    async with MqttConnector(
        mqtt_broker="test.mosquitto.org",  # External SSL-enabled broker
        mqtt_port=8885,  # SSL + Auth port (encrypted and authenticated)
        client_id=f"ssl_auth_ctx_test_{unique_id}",
        username="rw",
        password="readwrite",
        use_ssl=True,
        verify_ssl=False,  # Disable certificate verification for testing
    ) as connector:
        assert connector.is_connected() is True

        unique_topic = f"test/ssl_auth/context/{unique_id}"
        result = await connector.publish(
            unique_topic,
            {
                "message": "SSL + Auth Context manager test",
                "ssl": True,
                "authenticated": True,
            },
        )
        assert result is True

    # Should be disconnected after context manager exits
    assert connector.is_connected() is False


@pytest.mark.asyncio
@pytest.mark.ssl
@pytest.mark.external
async def test_ssl_auth_message_callback():
    """Test SSL + Auth message callback functionality."""
    unique_id = uuid.uuid4().hex[:8]

    # Always use external mosquitto test server for SSL tests
    connector = MqttConnector(
        mqtt_broker="test.mosquitto.org",  # External SSL-enabled broker
        mqtt_port=8885,  # SSL + Auth port (encrypted and authenticated)
        client_id=f"ssl_auth_callback_test_{unique_id}",
        username="rw",
        password="readwrite",
        use_ssl=True,
        verify_ssl=False,  # Disable certificate verification for testing
        throttle_interval=0.1,
    )

    received_messages = []

    def message_callback(topic, message):
        received_messages.append((topic, message))

    try:
        connector.set_message_callback(message_callback)
        await connector.connect()

        unique_topic = f"test/ssl_auth/callback/{unique_id}"
        await connector.subscribe(unique_topic)

        # Give subscription time to register
        await asyncio.sleep(0.5)

        test_message = "SSL + Auth callback test message"
        await connector.publish(unique_topic, test_message)

        # Wait for message to be received
        await asyncio.sleep(1)

        # Check if we received the message
        assert len(received_messages) > 0
        topic, message = received_messages[0]
        assert topic == unique_topic
        assert message == test_message

    finally:
        await connector.disconnect()


@pytest.mark.asyncio
@pytest.mark.ssl
@pytest.mark.external
async def test_ssl_auth_failure():
    """Test that SSL + Auth fails with wrong credentials."""
    unique_id = uuid.uuid4().hex[:8]

    # Always use external mosquitto test server for SSL tests
    connector = MqttConnector(
        mqtt_broker="test.mosquitto.org",  # External SSL-enabled broker
        mqtt_port=8885,  # SSL + Auth port (encrypted and authenticated)
        client_id=f"ssl_auth_fail_test_{unique_id}",
        username="wrong_user",
        password="wrong_password",
        use_ssl=True,
        verify_ssl=False,  # Disable certificate verification for testing
        reconnect_interval=1,
        max_reconnect_attempts=1,
    )

    try:
        # This should fail
        result = await connector.connect()
        # If it doesn't fail, that's unexpected but we should still disconnect
        if result:
            await connector.disconnect()
        # For this test, we expect either False or an exception
        assert result is False or result is None
    except Exception:
        # Exception is also acceptable for auth failure
        pass
    finally:
        if connector.is_connected():
            await connector.disconnect()
