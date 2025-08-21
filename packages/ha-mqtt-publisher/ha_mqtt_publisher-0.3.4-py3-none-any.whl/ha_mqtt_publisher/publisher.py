import json
import logging
import ssl
import time
from typing import Any

import paho.mqtt.client as mqtt

from ha_mqtt_publisher.mqtt_utils import (
    safe_on_connect,
    safe_on_disconnect,
    safe_on_publish,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class MQTTPublisher:
    """An MQTT publisher class for sending messages to an MQTT broker.

    Supports MQTT 3.1, 3.1.1, and 5.0 protocols with modern paho-mqtt 2.1.0+ features.

    Args:
        broker_url: URL of the MQTT broker
        broker_port: Port number for the broker
        client_id: Unique client identifier
        security: Security mechanism to use
            Options: 'none', 'username', 'tls', 'tls_with_client_cert'
        auth: Authentication credentials
        tls: TLS configuration settings
        max_retries: Maximum connection attempts
        last_will: Last Will and Testament settings
        config: Complete configuration dictionary (alternative to individual params)
        protocol: MQTT protocol version ('MQTTv31', 'MQTTv311', 'MQTTv5')
        properties: MQTT 5.0 properties for connection
        default_qos: Default QoS level for publish operations (0-2)
        default_retain: Default retain flag for publish operations
        logging_config: Enhanced logging configuration with levels for different modules
            Example: {
                "connection_level": "DEBUG",
                "publish_level": "INFO",
                "discovery_level": "WARNING",
                "topic_specific": {
                    "sensors/*": "DEBUG",
                    "status": "INFO"
                }
            }
    """

    def _convert_port(self, port: int | str | None) -> int:
        """Convert port to integer, handling string conversion."""
        if port is None:
            return 1883  # Default MQTT port
        if isinstance(port, str):
            try:
                return int(port)
            except ValueError as e:
                raise ValueError(
                    f"Invalid port value: {port}. Must be a valid integer."
                ) from e
        return port

    def _validate_config(self) -> None:
        """Validate MQTT configuration and provide helpful error messages."""
        errors = []
        warnings = []

        if not self.broker_url:
            errors.append("broker_url is required")

        if not isinstance(self.broker_port, int) or not (
            1 <= self.broker_port <= 65535
        ):
            errors.append(
                f"broker_port must be integer 1-65535, got: {self.broker_port}"
            )

        if not self.client_id:
            errors.append("client_id is required")

        if self.security == "username":
            user = self.auth.get("username") if self.auth else None
            pwd = self.auth.get("password") if self.auth else None
            if not (user and pwd):
                errors.append("username and password required when security='username'")

        if self.security in ["tls", "tls_with_client_cert"]:
            if not self.tls:
                errors.append(
                    f"TLS configuration required when security='{self.security}'"
                )
            elif self.security == "tls_with_client_cert":
                if not all(self.tls.get(key) for key in ["client_cert", "client_key"]):
                    errors.append(
                        "client_cert and client_key required for tls_with_client_cert"
                    )

        # Port/TLS consistency warnings (warnings, not errors)
        if self.tls and self.broker_port == 1883:
            warnings.append(
                "TLS enabled but using non-TLS port 1883. Consider port 8883 for TLS"
            )

        if not self.tls and self.broker_port == 8883:
            warnings.append(
                "TLS disabled but using TLS port 8883. Consider port 1883 for non-TLS"
            )

        # Log warnings but don't fail
        if warnings:
            import logging

            for warning in warnings:
                logging.warning(f"MQTT configuration warning: {warning}")

        # Only fail on actual errors
        if errors:
            raise ValueError(
                "MQTT configuration errors:\n"
                + "\n".join(f"- {error}" for error in errors)
            )

    def _setup_enhanced_logging(self) -> None:
        """Set up enhanced logging based on configuration."""
        # Get logging configuration with defaults
        connection_level = self.logging_config.get("connection_level", "INFO")
        publish_level = self.logging_config.get("publish_level", "INFO")
        discovery_level = self.logging_config.get("discovery_level", "INFO")
        topic_specific = self.logging_config.get("topic_specific", {})

        # Create module-specific loggers if configured
        if connection_level != "INFO":
            self.connection_logger = logging.getLogger(f"{__name__}.connection")
            self.connection_logger.setLevel(getattr(logging, connection_level.upper()))
        else:
            self.connection_logger = logging.getLogger(__name__)

        if publish_level != "INFO":
            self.publish_logger = logging.getLogger(f"{__name__}.publish")
            self.publish_logger.setLevel(getattr(logging, publish_level.upper()))
        else:
            self.publish_logger = logging.getLogger(__name__)

        if discovery_level != "INFO":
            self.discovery_logger = logging.getLogger(f"{__name__}.discovery")
            self.discovery_logger.setLevel(getattr(logging, discovery_level.upper()))
        else:
            self.discovery_logger = logging.getLogger(__name__)

        # Store topic-specific logging configuration
        self.topic_loggers = {}
        for topic_pattern, level in topic_specific.items():
            logger = logging.getLogger(f"{__name__}.topic.{topic_pattern}")
            logger.setLevel(getattr(logging, level.upper()))
            self.topic_loggers[topic_pattern] = logger

    def _get_topic_logger(self, topic: str) -> logging.Logger:
        """Get appropriate logger for a specific topic."""
        # Check for exact match first
        if topic in self.topic_loggers:
            return self.topic_loggers[topic]

        # Check for pattern matches (simple wildcard support)
        for pattern, logger in self.topic_loggers.items():
            if "*" in pattern:
                # Simple wildcard matching
                pattern_regex = pattern.replace("*", ".*")
                import re

                if re.match(pattern_regex, topic):
                    return logger

        # Default to publish logger
        return self.publish_logger

    def __init__(
        self,
        broker_url: str | None = None,
        broker_port: int | str | None = None,
        client_id: str | None = None,
        security: str = "none",
        auth: dict | None = None,
        tls: dict | None = None,
        max_retries: int = 3,
        last_will: dict | None = None,
        config: dict | None = None,
        protocol: str = "MQTTv311",  # New: Support for MQTT protocol version
        properties: dict | None = None,  # New: MQTT 5.0 properties
        default_qos: int = 0,  # New: Default QoS for publish operations
        default_retain: bool = False,  # New: Default retain flag for publish operations
        logging_config: dict | None = None,  # New: Enhanced logging configuration
    ):
        # Handle config dict parameter
        if config:
            self.broker_url = config["broker_url"]
            self.broker_port = self._convert_port(config.get("broker_port"))
            self.client_id = config["client_id"]
            security = config.get("security", "none")
            auth = config.get("auth")
            tls = config.get("tls")
            max_retries = config.get("max_retries", 3)
            last_will = config.get("last_will")
            self.protocol = config.get("protocol", protocol)
            self.properties = config.get("properties", properties)
            self.default_qos = config.get("default_qos", default_qos)
            self.default_retain = config.get("default_retain", default_retain)
            self.logging_config = config.get("logging_config", logging_config or {})
        else:
            # Use individual parameters (existing behavior)
            self.broker_url = broker_url
            self.broker_port = self._convert_port(broker_port)
            self.client_id = client_id
            self.protocol = protocol
            self.properties = properties or {}
            self.default_qos = default_qos
            self.default_retain = default_retain
            self.logging_config = logging_config or {}

        self.security = security
        self.auth = auth or {}
        self.tls = tls
        self.max_retries = max_retries
        self._connected = False
        self._loop_running = False  # Track background loop state

        # Validate configuration
        self._validate_config()

        # Set up enhanced logging
        self._setup_enhanced_logging()

        # Validate default QoS
        if not (0 <= self.default_qos <= 2):
            raise ValueError(f"default_qos must be 0, 1, or 2, got: {self.default_qos}")

        # Validate default retain
        if not isinstance(self.default_retain, bool):
            raise ValueError(
                f"default_retain must be boolean, got: {self.default_retain}"
            )  # Type assertions for type checker (validation ensures these are not None)
        assert self.broker_url is not None, "broker_url validated to be not None"
        assert self.client_id is not None, "client_id validated to be not None"

        # Map protocol string to paho-mqtt constants
        protocol_map = {
            "MQTTv31": mqtt.MQTTv31,
            "MQTTv311": mqtt.MQTTv311,
            "MQTTv5": mqtt.MQTTv5,
        }

        protocol_version = protocol_map.get(self.protocol, mqtt.MQTTv311)

        # Create MQTT client with backwards compatibility
        if hasattr(mqtt, "CallbackAPIVersion"):
            # Choose callback API version consistent with chosen MQTT protocol
            try:
                if protocol_version == mqtt.MQTTv5:
                    cb = mqtt.CallbackAPIVersion.VERSION2
                else:
                    cb = mqtt.CallbackAPIVersion.VERSION1
            except Exception:
                cb = mqtt.CallbackAPIVersion.VERSION2

            self.client = mqtt.Client(
                callback_api_version=cb,
                client_id=self.client_id,
                protocol=protocol_version,
            )
        else:
            # paho-mqtt < 2.0.0 - use legacy API
            self.client = mqtt.Client(
                client_id=self.client_id,
                protocol=protocol_version,
            )

        # Configure Last Will and Testament
        if last_will:
            self.client.will_set(
                last_will["topic"],
                last_will["payload"],
                qos=last_will["qos"],
                retain=last_will["retain"],
            )

        # Configure security based on type
        # Always apply username/password if provided
        user = self.auth.get("username") if self.auth else None
        pwd = self.auth.get("password") if self.auth else None
        if user and pwd:
            self.client.username_pw_set(user, pwd)

        # Enable TLS whenever TLS configuration is present (regardless of 'security'
        # string). Previously TLS was only applied when security=='tls' which caused
        # clients that supplied TLS settings with security='username' to attempt a
        # non-TLS connect to a TLS port (causing broker disconnects).
        if self.tls:
            self.client.tls_set(
                ca_certs=self.tls.get("ca_cert"),
                certfile=self.tls.get("client_cert"),
                keyfile=self.tls.get("client_key"),
                cert_reqs=(
                    ssl.CERT_REQUIRED if self.tls.get("verify") else ssl.CERT_NONE
                ),
                tls_version=ssl.PROTOCOL_TLS,
            )
            self.client.tls_insecure_set(not self.tls.get("verify", True))

        # Set up callbacks
        # Wrap connect/disconnect/publish handlers to normalize v1/v2 signatures
        try:
            self.client.on_connect = safe_on_connect(self._on_connect)
        except Exception:
            self.client.on_connect = self._on_connect
        # Wrap disconnect/publish handlers to be tolerant of v1/v2 signatures from paho
        try:
            self.client.on_disconnect = safe_on_disconnect(self._on_disconnect)
        except Exception:
            self.client.on_disconnect = self._on_disconnect

        try:
            self.client.on_publish = safe_on_publish(self._on_publish)
        except Exception:
            self.client.on_publish = self._on_publish

    def _get_connection_error_message(self, error_code) -> str:
        """Provide helpful error messages for common connection issues."""
        # Handle both integer (v1) and ReasonCode (v2) formats
        error_code_int = (
            int(error_code) if hasattr(error_code, "__int__") else error_code
        )

        error_messages = {
            0: "Connection successful",
            1: "Connection refused - unacceptable protocol version",
            2: "Connection refused - identifier rejected",
            3: "Connection refused - server unavailable",
            4: "Connection refused - bad username or password",
            5: "Connection refused - not authorized",
        }

        base_message = error_messages.get(
            error_code_int, f"Unknown connection error: {error_code}"
        )

        # Add specific guidance for common misconfigurations
        if error_code_int == 1:  # Connection refused
            if self.tls and self.broker_port == 1883:
                return f"{base_message}. TLS enabled but using non-TLS port 1883. Try port 8883."
            elif not self.tls and self.broker_port == 8883:
                return f"{base_message}. TLS disabled but using TLS port 8883. Try port 1883 or enable TLS."

        return base_message

    def _on_connect(self, client, userdata, *args):
        """Normalized and tolerant on_connect handler.

        Supports both older paho signatures (client, userdata, flags, rc, props)
        and modern signatures (client, userdata, rc, props). We extract the
        reason_code and properties from the positional args and then reuse the
        existing success/error handling logic.
        """
        # Extract reason_code and properties from possible arg shapes
        reason_code = None
        properties = None
        try:
            if len(args) == 2:
                # (reason_code, properties)
                reason_code, properties = args
            elif len(args) == 3:
                # (flags, reason_code, properties)
                _, reason_code, properties = args
            elif len(args) == 1:
                # (reason_code,) - best-effort
                reason_code = args[0]
        except Exception:
            reason_code = None
            properties = None

        # Accept multiple forms of success: int-like 0, ReasonCode objects that
        # cast to 0, or missing reason_code accompanied by v5 properties (ConnAck).
        success = False
        try:
            if reason_code is None:
                # If properties present (MQTTv5 ConnAck properties) assume success
                success = properties is not None
            else:
                # Try numeric conversion where possible
                success = (
                    int(reason_code) == 0
                    if hasattr(reason_code, "__int__")
                    else reason_code == 0
                )
        except Exception:
            success = False

        if success:
            self._connected = True
            self.connection_logger.info("Connected to MQTT broker")
            return

        # Not successful - log helpful guidance
        try:
            error_msg = self._get_connection_error_message(reason_code)
        except Exception:
            error_msg = f"Unknown connection error: {reason_code}"
        self.connection_logger.error(error_msg)

    def _on_disconnect(self, client, userdata, *args):
        """Tolerant on_disconnect handler supporting multiple callback shapes.

        Supports: (client, userdata, rc, props) and (client, userdata, flags, rc, props)
        """
        self._connected = False

        # Extract reason_code and properties from args
        reason_code = None
        properties = None
        try:
            if len(args) == 2:
                reason_code, properties = args
            elif len(args) == 3:
                _, reason_code, properties = args
            elif len(args) == 1:
                reason_code = args[0]
        except Exception:
            reason_code = None
            properties = None

        # Best-effort numeric reason code for uniform handling
        try:
            rc_int = (
                int(reason_code) if hasattr(reason_code, "__int__") else reason_code
            )
        except Exception:
            rc_int = reason_code

        if rc_int != 0:
            # Extract useful properties where available to aid debugging
            prop_repr = None
            try:
                if properties is None:
                    prop_repr = None
                else:
                    props = {}
                    for attr in (
                        "ReasonString",
                        "ServerReference",
                        "UserProperty",
                        "SessionExpiryInterval",
                        "AuthenticationMethod",
                    ):
                        if hasattr(properties, attr):
                            try:
                                props[attr] = getattr(properties, attr)
                            except Exception:
                                props[attr] = repr(getattr(properties, attr))
                    if not props:
                        try:
                            prop_items = {}
                            for k in dir(properties):
                                if k.startswith("_"):
                                    continue
                                try:
                                    v = getattr(properties, k)
                                except Exception:
                                    continue
                                if callable(v):
                                    continue
                                prop_items[k] = v
                            prop_repr = prop_items
                        except Exception:
                            prop_repr = repr(properties)
                    else:
                        prop_repr = props
            except Exception:
                prop_repr = repr(properties)

            self.connection_logger.warning(
                "Unexpected disconnection rc=%r rc_int=%s properties=%s",
                reason_code,
                rc_int,
                prop_repr,
            )

    def _on_publish(self, client, userdata, *args):
        """Tolerant on_publish handler that accepts legacy and v5 signatures.

        Common shapes: (client, userdata, mid) or (client, userdata, mid, reason_codes, properties)
        """
        mid = None
        try:
            if len(args) >= 1:
                mid = args[0]
        except Exception:
            mid = None

        self.publish_logger.debug(f"Message published with ID: {mid}")

    def connect(self) -> bool:
        """Connect to the MQTT broker with exponential backoff retry logic."""
        # Type assertions for type checker (validation ensures these are not None)
        assert self.broker_url is not None
        assert isinstance(self.broker_port, int)

        retries = 0
        base_delay = 1  # Start with 1 second delay
        max_delay = 60  # Maximum delay of 60 seconds

        while retries < self.max_retries:
            try:
                self.connection_logger.info(
                    "Attempting connection to %s:%d (attempt %d/%d)",
                    self.broker_url,
                    self.broker_port,
                    retries + 1,
                    self.max_retries,
                )
                result = self.client.connect(
                    self.broker_url, self.broker_port, keepalive=60
                )

                # Check if connect call itself failed
                if result != 0:
                    raise Exception(f"MQTT connect() returned error code: {result}")

                self.client.loop_start()

                # If already connected (mock scenario or immediate connection), return success
                if self._connected:
                    self.connection_logger.info("Successfully connected to MQTT broker")
                    return True

                # Wait for connection callback
                timeout = 5
                start_time = time.time()
                while not self._connected and (time.time() - start_time) < timeout:
                    time.sleep(0.1)
                if self._connected:
                    self.connection_logger.info("Successfully connected to MQTT broker")
                    return True
                self.connection_logger.warning(
                    "Connection timeout after %d seconds", timeout
                )
            except Exception as e:
                self.connection_logger.error(
                    "Connection attempt %d/%d failed: %s",
                    retries + 1,
                    self.max_retries,
                    e,
                    exc_info=True,
                )

            retries += 1
            if retries < self.max_retries:
                # Exponential backoff with jitter
                delay = min(base_delay * (2 ** (retries - 1)), max_delay)
                # Add some jitter (±25% of the delay)
                import random

                jitter = delay * 0.25 * (random.random() * 2 - 1)
                actual_delay = max(0.5, delay + jitter)

                self.connection_logger.info(
                    "Retrying in %.1f seconds (exponential backoff)...", actual_delay
                )
                time.sleep(actual_delay)

        self.connection_logger.error(
            "Failed to connect after %d attempts with exponential backoff",
            self.max_retries,
        )
        return False

    def disconnect(self) -> None:
        """Disconnect from the MQTT broker."""
        if self._connected:
            self.client.loop_stop()
            self._loop_running = False
            self.client.disconnect()
            self._connected = False
            self.connection_logger.info("Disconnected from MQTT broker")

    def publish(
        self,
        topic: str,
        payload: Any,
        qos: int | None = None,
        retain: bool | None = None,
        properties: dict | None = None,
    ) -> bool:
        """Publish a payload to a topic.

        Args:
            topic: The MQTT topic
            payload: The message payload
            qos: Quality of service (0-2). If None, uses default_qos
            retain: Whether to retain the message. If None, uses default_retain
            properties: MQTT 5.0 properties (only used with MQTTv5)

        Returns:
            bool: Success status
        """
        if not self._connected:
            topic_logger = self._get_topic_logger(topic)
            topic_logger.error(f"Not connected to broker when publishing to {topic}")
            return False

        # Use defaults if not specified
        if qos is None:
            qos = self.default_qos
        if retain is None:
            retain = self.default_retain

        topic_logger = self._get_topic_logger(topic)

        try:
            if isinstance(payload, dict | list):
                payload = json.dumps(payload)

            # Use MQTT 5.0 properties if provided and using MQTTv5
            if (
                properties
                and self.protocol == "MQTTv5"
                and hasattr(mqtt, "Properties")
                and hasattr(mqtt, "PacketTypes")
            ):
                mqtt_properties = mqtt.Properties(mqtt.PacketTypes.PUBLISH)
                for key, value in properties.items():
                    setattr(mqtt_properties, key, value)
                result = self.client.publish(
                    topic, payload, qos=qos, retain=retain, properties=mqtt_properties
                )
            else:
                result = self.client.publish(topic, payload, qos=qos, retain=retain)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.publish_logger.info(
                    f"Published message to topic '{topic}' (QoS: {qos}, Retain: {retain})"
                )
                return True
            else:
                topic_logger.error(f"Failed to publish message to {topic}: {result.rc}")
                return False
        except Exception as e:
            topic_logger.error(f"Error publishing message to {topic}: {e}")
            return False

    def subscribe(
        self,
        topic: str,
        qos: int = 0,
        callback=None,
        properties: dict | None = None,
    ) -> bool:
        """Subscribe to an MQTT topic.

        Args:
            topic: The MQTT topic to subscribe to
            qos: Quality of service (0-2)
            callback: Optional callback function for this specific topic
            properties: MQTT 5.0 properties (only used with MQTTv5)

        Returns:
            bool: Success status
        """
        if not self._connected:
            logging.error("Not connected to broker")
            return False

        try:
            # Add topic-specific callback if provided
            if callback:
                self.client.message_callback_add(topic, callback)

            # Use MQTT 5.0 properties if provided and using MQTTv5
            if (
                properties
                and self.protocol == "MQTTv5"
                and hasattr(mqtt, "Properties")
                and hasattr(mqtt, "PacketTypes")
            ):
                mqtt_properties = mqtt.Properties(mqtt.PacketTypes.SUBSCRIBE)
                for key, value in properties.items():
                    setattr(mqtt_properties, key, value)
                result = self.client.subscribe(
                    topic, qos=qos, properties=mqtt_properties
                )
            else:
                result = self.client.subscribe(topic, qos=qos)

            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                logging.info(f"Subscribed to topic '{topic}'")
                return True
            else:
                logging.error(f"Failed to subscribe to topic: {result[0]}")
                return False
        except Exception as e:
            logging.error(f"Error subscribing to topic: {e}")
            return False

    def unsubscribe(self, topic: str, properties: dict | None = None) -> bool:
        """Unsubscribe from an MQTT topic.

        Args:
            topic: The MQTT topic to unsubscribe from
            properties: MQTT 5.0 properties (only used with MQTTv5)

        Returns:
            bool: Success status
        """
        if not self._connected:
            logging.error("Not connected to broker")
            return False

        try:
            # Remove topic-specific callback
            self.client.message_callback_remove(topic)

            # Use MQTT 5.0 properties if provided and using MQTTv5
            if (
                properties
                and self.protocol == "MQTTv5"
                and hasattr(mqtt, "Properties")
                and hasattr(mqtt, "PacketTypes")
            ):
                mqtt_properties = mqtt.Properties(mqtt.PacketTypes.UNSUBSCRIBE)
                for key, value in properties.items():
                    setattr(mqtt_properties, key, value)
                result = self.client.unsubscribe(topic, properties=mqtt_properties)
            else:
                result = self.client.unsubscribe(topic)

            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                logging.info(f"Unsubscribed from topic '{topic}'")
                return True
            else:
                logging.error(f"Failed to unsubscribe from topic: {result[0]}")
                return False
        except Exception as e:
            logging.error(f"Error unsubscribing from topic: {e}")
            return False

    def set_message_callback(self, callback) -> None:
        """Set the default message callback for all subscribed topics.

        Args:
            callback: Function to call when a message is received
                     Signature: callback(client, userdata, message)
        """
        self.client.on_message = callback

    def add_topic_callback(self, topic_filter: str, callback) -> None:
        """Add a callback for a specific topic filter.

        Args:
            topic_filter: MQTT topic filter (can include wildcards)
            callback: Function to call when a message matching the filter is received
        """
        self.client.message_callback_add(topic_filter, callback)

    def remove_topic_callback(self, topic_filter: str) -> None:
        """Remove a callback for a specific topic filter.

        Args:
            topic_filter: MQTT topic filter to remove callback for
        """
        self.client.message_callback_remove(topic_filter)

    def is_loop_running(self) -> bool:
        """Check if the background loop is currently running.

        Returns:
            True if background loop is active, False otherwise
        """
        # Since paho-mqtt doesn't provide a direct way to check loop status,
        # we'll track it ourselves using a simple instance variable
        if not hasattr(self, "_loop_running"):
            self._loop_running = False
        return self._loop_running

    def loop_start(self) -> None:
        """Start the network loop in a background thread for non-blocking operation.

        This allows the MQTT client to process network traffic (publish/subscribe)
        in the background without blocking the main application thread.
        """
        try:
            self.client.loop_start()
            self._loop_running = True
            self.connection_logger.info("Started MQTT background loop")
        except Exception as e:
            self.connection_logger.error(f"Failed to start MQTT loop: {e}")
            raise

    def loop_stop(self) -> None:
        """Stop the background network loop.

        This stops the background thread and forces all network operations
        to be processed synchronously (blocking).
        """
        try:
            self.client.loop_stop()
            self._loop_running = False
            self.connection_logger.info("Stopped MQTT background loop")
        except Exception as e:
            self.connection_logger.error(f"Failed to stop MQTT loop: {e}")
            raise

    def __enter__(self):
        if not self.connect():
            raise ConnectionError("Failed to connect to MQTT broker")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
