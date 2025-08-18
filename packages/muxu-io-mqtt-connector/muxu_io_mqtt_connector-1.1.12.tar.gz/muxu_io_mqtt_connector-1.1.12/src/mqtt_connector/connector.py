"""MQTT connector module for robust MQTT communication."""

import asyncio
import json
import threading
import time
import uuid
from typing import Any, Awaitable, Callable, Dict, Optional, Union

import paho.mqtt.client as mqtt


class MqttConnector:
    """Handles connection to the MQTT broker."""

    def __init__(
        self,
        mqtt_broker: str,
        mqtt_port: int,
        client_id: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_ssl: bool = False,
        ca_cert: Optional[str] = None,
        cert_file: Optional[str] = None,
        key_file: Optional[str] = None,
        verify_ssl: bool = True,
        reconnect_interval: int = 5,
        max_reconnect_attempts: int = -1,
        throttle_interval: float = 0.1,
    ):
        """Initialize the MqttConnector.

        Args:
            mqtt_broker (str): The MQTT broker's address.
            mqtt_port (int): The MQTT broker's port.
            client_id (str, optional): Client ID for the MQTT connection. If None, a random ID is generated.
            username (str, optional): Username for MQTT authentication.
            password (str, optional): Password for MQTT authentication.
            use_ssl (bool): Whether to use SSL/TLS encryption.
            ca_cert (str, optional): Path to CA certificate file for SSL.
            cert_file (str, optional): Path to client certificate file for SSL.
            key_file (str, optional): Path to client private key file for SSL.
            verify_ssl (bool): Whether to verify SSL certificates (set to False for testing).
            reconnect_interval (int): Seconds between reconnection attempts.
            max_reconnect_attempts (int): Maximum number of reconnection attempts (-1 for infinite).
            throttle_interval (float): Minimum seconds between MQTT publishes.
        """
        import logging
        import os

        # Map string log level to integer, default INFO
        self.level_map = {
            "CRITICAL": logging.CRITICAL,
            "ERROR": logging.ERROR,
            "WARNING": logging.WARNING,
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
            "NOTSET": logging.NOTSET,
        }
        env_level = os.environ.get("LOG_LEVEL", "INFO").upper()
        self.log_level = self.level_map.get(env_level, logging.INFO)
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.client_id = (
            client_id if client_id else f"mqtt_connector_{uuid.uuid4().hex[:8]}"
        )
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.ca_cert = ca_cert
        self.cert_file = cert_file
        self.key_file = key_file
        self.verify_ssl = verify_ssl
        self.reconnect_interval = reconnect_interval
        self.max_reconnect_attempts = max_reconnect_attempts
        self.throttle_interval = throttle_interval
        self.connected = False
        self.reconnect_attempts = 0

        # Message handling and callbacks
        self._last_publish_time = 0.0
        self._log_callback = None
        self._message_callback = None

        # MQTT client - use VERSION2 callback API to avoid deprecation warning
        self.client = mqtt.Client(
            client_id=self.client_id,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        )
        self._setup_client()
        self._setup_callbacks()

        # Threading event for connection status
        self._connection_event = threading.Event()
        self._disconnect_event = threading.Event()
        self._auto_reconnect = True
        self._reconnect_task = None

    def _setup_client(self) -> None:
        """Configure the MQTT client with SSL and authentication settings."""
        # Set up authentication if provided
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
            self._log("INFO", f"Authentication configured for user: {self.username}")

        # Set up SSL/TLS if requested
        if self.use_ssl:
            import ssl

            try:
                if self.verify_ssl:
                    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)

                    if self.ca_cert:
                        context.load_verify_locations(self.ca_cert)

                    if self.cert_file and self.key_file:
                        context.load_cert_chain(self.cert_file, self.key_file)

                    self.client.tls_set_context(context)
                    self._log(
                        "INFO",
                        "SSL/TLS encryption enabled with certificate verification",
                    )
                else:
                    # For testing - disable certificate verification
                    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE

                    if self.cert_file and self.key_file:
                        context.load_cert_chain(self.cert_file, self.key_file)

                    self.client.tls_set_context(context)
                    self._log(
                        "INFO",
                        "SSL/TLS encryption enabled WITHOUT certificate verification (testing mode)",
                    )

            except Exception as e:
                self._log("ERROR", f"Failed to set up SSL/TLS: {e}")
                # Fallback to simpler SSL setup
                try:
                    self.client.tls_set()
                    self._log("INFO", "SSL/TLS encryption enabled (fallback)")
                except Exception as e2:
                    self._log("ERROR", f"Failed to set up SSL/TLS fallback: {e2}")
                    raise

    def set_log_callback(self, callback: Callable[[str, str], None]) -> None:
        """Set a callback function for logging messages from the connector.

        Args:
            callback (Callable[[str, str], None]): The callback function to handle log messages.
        """
        self._log_callback = callback

    def _schedule_async_callback(self, topic: str, message: str) -> None:
        """Schedule an async callback to run in the event loop thread-safely."""
        try:
            # Try to get the running event loop
            loop = asyncio.get_running_loop()
            # Use call_soon_threadsafe to schedule from Paho's background thread
            loop.call_soon_threadsafe(
                lambda: asyncio.create_task(self._message_callback(topic, message))
            )
        except RuntimeError:
            # No running event loop - log error
            self._log(
                "ERROR",
                f"Cannot execute async callback for topic {topic} - no running event loop",
            )

    def _log(self, level: str, message: str) -> None:
        """Internal logging method that uses the callback if available and respects log_level"""
        module_name = __name__.split(".")[0]
        level_int = self.level_map.get(level.upper(), 20)  # Default to INFO if unknown
        if level_int < self.log_level:
            return
        log_message = f"[{module_name}] {message}"
        if self._log_callback:
            self._log_callback(level, log_message)
        else:
            import sys

            print(f"[{level}] {log_message}", file=sys.stderr)

    def _setup_callbacks(self) -> None:
        """Set up MQTT client callbacks."""

        def on_connect(client, userdata, flags, reason_code, properties=None):
            if reason_code == 0:
                self.connected = True
                self.reconnect_attempts = 0
                self._connection_event.set()
                self._disconnect_event.clear()
                self._log("INFO", "Successfully connected to MQTT broker")
            else:
                self.connected = False
                self._connection_event.clear()
                self._log(
                    "ERROR",
                    f"Failed to connect to MQTT broker with reason code {reason_code}",
                )

        def on_disconnect(client, userdata, flags, reason_code, properties=None):
            self.connected = False
            self._connection_event.clear()
            self._disconnect_event.set()
            if reason_code != 0:
                self._log(
                    "WARNING",
                    f"Unexpected disconnection from MQTT broker (reason: {reason_code})",
                )
                # Start auto-reconnection if enabled
                if self._auto_reconnect and not self._reconnect_task:
                    try:
                        loop = asyncio.get_event_loop()
                        self._reconnect_task = loop.create_task(
                            self._auto_reconnect_loop()
                        )
                    except RuntimeError:
                        # No event loop running, auto-reconnection will need to be handled manually
                        self._log(
                            "WARNING", "No event loop available for auto-reconnection"
                        )
            else:
                self._log("INFO", "Disconnected from MQTT broker")

        def on_publish(client, userdata, mid, reason_code=None, properties=None):
            # Topic is not directly available in on_publish, but you can log the mid
            self._log("DEBUG", f"Message published with id: {mid}")

        def on_subscribe(client, userdata, mid, reason_codes, properties=None):
            self._log(
                "INFO", f"Subscribed with mid: {mid}, reason codes: {reason_codes}"
            )

        def on_message(client, userdata, msg):
            self._log(
                "DEBUG",
                f"Received message on topic {msg.topic}: {msg.payload.decode()}",
            )

        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.on_publish = on_publish
        self.client.on_subscribe = on_subscribe
        self.client.on_message = on_message

    async def connect(self, force_reconnect: bool = False) -> bool:
        """Connect to the MQTT broker.

        Args:
            force_reconnect (bool): Force a reconnection attempt even if already connected.

        Returns:
            bool: True if connection succeeded, False otherwise.
        """
        if self.connected and not force_reconnect:
            return True

        # Print version information on first connection
        if not hasattr(self, "_version_logged"):
            from . import __version__

            self._log("INFO", f"MqttConnector v{__version__} initializing...")
            self._version_logged = True

        attempts = 0
        while (
            self.max_reconnect_attempts == -1 or attempts < self.max_reconnect_attempts
        ):
            self._log(
                "INFO",
                f"Connecting to MQTT broker {self.mqtt_broker}: {self.mqtt_port} (attempt {attempts + 1})",
            )

            try:
                # Reset connection event
                self._connection_event.clear()

                # Connect to the broker
                result = self.client.connect(
                    self.mqtt_broker, self.mqtt_port, keepalive=60
                )
                if result == mqtt.MQTT_ERR_SUCCESS:
                    # Start the network loop in a separate thread
                    self.client.loop_start()

                    # Wait for connection to be established (up to 10 seconds)
                    connected = await asyncio.get_event_loop().run_in_executor(
                        None, self._connection_event.wait, 10.0
                    )

                    if connected:
                        self.reconnect_attempts = 0
                        return True
                    else:
                        self._log(
                            "ERROR", "Connection timeout - broker did not respond"
                        )
                        self.client.loop_stop()

                else:
                    self._log(
                        "ERROR",
                        f"Failed to initiate connection to MQTT broker (error code: {result})",
                    )

            except Exception as e:
                self._log("ERROR", f"Failed to connect to MQTT broker: {e}")

            attempts += 1
            self.reconnect_attempts = attempts

            if (
                self.max_reconnect_attempts != -1
                and attempts >= self.max_reconnect_attempts
            ):
                self._log(
                    "ERROR",
                    f"Maximum reconnection attempts ({self.max_reconnect_attempts}) reached",
                )
                break

            self._log(
                "INFO", f"Retrying connection in {self.reconnect_interval} seconds..."
            )
            await asyncio.sleep(self.reconnect_interval)

        self.connected = False
        return False

    async def disconnect(self) -> None:
        """Disconnect from the MQTT broker."""
        if self.connected:
            self._log("INFO", "Disconnecting from MQTT broker")
            try:
                # Disable auto-reconnection before disconnecting
                self._auto_reconnect = False
                if self._reconnect_task:
                    self._reconnect_task.cancel()
                    self._reconnect_task = None

                self._disconnect_event.clear()
                self.client.disconnect()

                # Wait for disconnection to complete (up to 5 seconds)
                await asyncio.get_event_loop().run_in_executor(
                    None, self._disconnect_event.wait, 5.0
                )

                self.client.loop_stop()
                self.connected = False
            except Exception as e:
                self._log("ERROR", f"Error during disconnection: {e}")
                self.connected = False

    async def publish(
        self,
        topic: str,
        message: Union[str, Dict[str, Any], bytes],
        qos: int = 0,
        retain: bool = False,
    ) -> bool:
        """Publish a message to the specified MQTT topic.

        Args:
            topic (str): The MQTT topic to publish to.
            message (Union[str, Dict[str, Any], bytes]): The message to publish.
            qos (int): Quality of Service level (0, 1, or 2).
            retain (bool): Whether to retain the message on the broker.

        Returns:
            bool: True if publish succeeded, False otherwise.
        """
        if not self.connected:
            success = await self.connect()
            if not success:
                self._log("ERROR", "Failed to publish - not connected to broker")
                return False

        # Throttle publishing if needed
        now = time.time()
        if now - self._last_publish_time < self.throttle_interval:
            await asyncio.sleep(
                self.throttle_interval - (now - self._last_publish_time)
            )

        # Ensure payload is a valid type for MQTT publish
        if isinstance(message, dict):
            payload = json.dumps(message)
        elif isinstance(message, (str, bytes, bytearray)):
            payload = message
        else:
            payload = str(message)

        try:
            # Publish the message
            result = self.client.publish(topic, payload, qos=qos, retain=retain)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                if qos > 0:
                    # For QoS > 0, wait for the message to be delivered
                    try:
                        result.wait_for_publish(timeout=5.0)
                        success = True
                    except RuntimeError:
                        self._log("WARNING", f"Publish timeout for message to {topic}")
                        success = False
                else:
                    success = True
            else:
                self._log(
                    "ERROR",
                    f"Failed to publish message to {topic} (error code: {result.rc})",
                )
                success = False

        except Exception as e:
            self._log("ERROR", f"Exception during publish: {e}")
            success = False

        if success:
            self._last_publish_time = time.time()
            self._log("DEBUG", f"Published message to {topic}: {str(payload)}")
        else:
            self._log("ERROR", f"Failed to publish message to {topic}")

        return success

    def is_connected(self) -> bool:
        """Check if the MQTT connector is connected.

        Returns:
            bool: True if connected, False otherwise.
        """
        return self.connected

    async def subscribe(self, topic: str, qos: int = 0) -> bool:
        """Subscribe to a topic.

        Args:
            topic (str): The topic to subscribe to.
            qos (int): Quality of Service level (0, 1, or 2).

        Returns:
            bool: True if subscription succeeded, False otherwise.
        """
        if not self.connected:
            success = await self.connect()
            if not success:
                self._log("ERROR", "Failed to subscribe - not connected to broker")
                return False

        try:
            # Subscribe to the topic
            result = self.client.subscribe(topic, qos)
            success = result[0] == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            self._log("ERROR", f"Exception during subscription: {e}")
            success = False

        if success:
            self._log("INFO", f"Subscribed to topic: {topic}")
        else:
            self._log("ERROR", f"Failed to subscribe to topic: {topic}")

        return success

    def set_message_callback(
        self,
        callback: Union[
            Callable[[str, str], None], Callable[[str, str], Awaitable[None]]
        ],
    ) -> None:
        """Set a callback function for handling received messages.

        Args:
            callback: Callback function that takes (topic, message) as parameters.
                     Can be either sync or async.
        """
        self._message_callback = callback

        def on_message_wrapper(client, userdata, msg):
            try:
                message = msg.payload.decode("utf-8")

                # Check if callback is async and handle appropriately
                import inspect

                if inspect.iscoroutinefunction(callback):
                    self._schedule_async_callback(msg.topic, message)
                else:
                    callback(msg.topic, message)
            except Exception as e:
                self._log("ERROR", f"Error in message callback: {e}")

        self.client.on_message = on_message_wrapper

    async def _auto_reconnect_loop(self) -> None:
        """Auto-reconnection loop that runs in the background."""
        self._log("INFO", "Starting auto-reconnection loop")

        while self._auto_reconnect and not self.connected:
            try:
                self._log("INFO", "Attempting auto-reconnection...")
                success = await self.connect()
                if success:
                    self._log("INFO", "Auto-reconnection successful")
                    break
                else:
                    await asyncio.sleep(self.reconnect_interval)
            except Exception as e:
                self._log("ERROR", f"Error during auto-reconnection: {e}")
                await asyncio.sleep(self.reconnect_interval)

        self._reconnect_task = None

    def set_auto_reconnect(self, enabled: bool) -> None:
        """Enable or disable automatic reconnection.

        Args:
            enabled (bool): Whether to enable automatic reconnection.
        """
        self._auto_reconnect = enabled
        if not enabled and self._reconnect_task:
            self._reconnect_task.cancel()
            self._reconnect_task = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self.set_auto_reconnect(False)
        await self.disconnect()
