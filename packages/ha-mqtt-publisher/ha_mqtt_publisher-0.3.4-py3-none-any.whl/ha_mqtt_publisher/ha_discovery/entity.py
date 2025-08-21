# ha_discovery/entity.py

"""
Entity classes for Home Assistant MQTT Discovery.

This module provides the base Entity class and specialized entity types
for creating Home Assistant MQTT discovery configurations. The library
supports all Home Assistant entity types through a flexible approach.

Includes light validation for HA-compatible fields to improve
interoperability (entity_category, availability_mode, state_class for sensors,
and device_class for binary_sensors). Validation is non-fatal (warnings only)
by default but can be strict via config.
"""

import logging
import re

from .constants import (
    AVAILABILITY_MODES,
    BINARY_SENSOR_DEVICE_CLASSES,
    ENTITY_CATEGORIES,
    SENSOR_DEVICE_CLASSES,
    SENSOR_STATE_CLASSES,
)
from .device import Device

logger = logging.getLogger(__name__)

"""Allowed values are imported from constants for single source of truth."""


def _slugify_object_id(value: str) -> str:
    """Create a HA-friendly object_id: lowercase, alnum+underscore only."""
    value = value.strip().lower()
    # Replace spaces and separators with underscores
    value = re.sub(r"[\s\-]+", "_", value)
    # Remove invalid chars
    value = re.sub(r"[^a-z0-9_]", "", value)
    # Collapse multiple underscores
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "entity"


class Entity:
    """
    Base class for all Home Assistant entities. It defines the common
    attributes and methods that all entities (sensors, binary_sensors, etc.)
    will use for MQTT discovery.

    This flexible base class allows creating any Home Assistant entity type
    by setting the component type and providing the appropriate fields.
    """

    def __init__(self, config, device: Device, component="sensor", **kwargs):
        """
        Initializes the base Entity.

        Args:
            config: The application's configuration object with get() method.
            device: The Device object representing the physical device.
            component: The Home Assistant component type (sensor, switch, etc.)
            **kwargs: Additional entity attributes (name, unique_id, topics, etc.)
        """
        self._config = config
        self.device = device
        self.component = component
        self.name = kwargs.get("name", "Unnamed")
        self.unique_id = kwargs.get("unique_id", "unnamed")
        self.base_topic = self._config.get("mqtt.base_topic", "mqtt_publisher")

        # Common topics
        self.state_topic = kwargs.get("state_topic", "")
        self.availability_topic = kwargs.get("availability_topic")
        self.command_topic = kwargs.get("command_topic")

        # Common attributes
        self.availability_mode = kwargs.get("availability_mode")
        self.availability_template = kwargs.get("availability_template")
        self.device_class = kwargs.get("device_class")
        self.enabled_by_default = kwargs.get("enabled_by_default")
        self.encoding = kwargs.get("encoding")
        self.entity_category = kwargs.get("entity_category")
        self.icon = kwargs.get("icon")
        self.json_attributes_template = kwargs.get("json_attributes_template")
        self.json_attributes_topic = kwargs.get("json_attributes_topic")
        self.object_id = kwargs.get("object_id")
        self.payload_available = kwargs.get("payload_available", "online")
        self.payload_not_available = kwargs.get("payload_not_available", "offline")
        self.qos = kwargs.get("qos", 0)
        self.retain = kwargs.get("retain", False)
        self.state_class = kwargs.get("state_class")
        self.unit_of_measurement = kwargs.get("unit_of_measurement")
        self.value_template = kwargs.get("value_template")

        # Store any additional attributes
        self.extra_attributes = {}
        for key, value in kwargs.items():
            if not hasattr(self, key) and not key.startswith("_"):
                self.extra_attributes[key] = value

        # Validation for better HA compatibility (strict by default)
        strict = bool(self._config.get("home_assistant.strict_validation", True))

        # Allow users to extend allowed sets via config
        extras = self._config.get("home_assistant.extra_allowed", {}) or {}

        def _to_set(val):
            if isinstance(val, list | set | tuple):
                return set(val)
            return set()

        allowed_entity_categories = ENTITY_CATEGORIES | _to_set(
            extras.get("entity_categories")
        )
        allowed_availability_modes = AVAILABILITY_MODES | _to_set(
            extras.get("availability_modes")
        )
        allowed_sensor_state_classes = SENSOR_STATE_CLASSES | _to_set(
            extras.get("sensor_state_classes")
        )
        allowed_sensor_device_classes = SENSOR_DEVICE_CLASSES | _to_set(
            extras.get("sensor_device_classes")
        )
        allowed_binary_sensor_device_classes = BINARY_SENSOR_DEVICE_CLASSES | _to_set(
            extras.get("binary_sensor_device_classes")
        )

        if (
            self.entity_category
            and self.entity_category not in allowed_entity_categories
        ):
            msg = f"entity_category '{self.entity_category}' is not one of {allowed_entity_categories}"
            if strict:
                raise ValueError(msg)
            logger.warning(msg)
        if (
            self.availability_mode
            and self.availability_mode not in allowed_availability_modes
        ):
            msg = f"availability_mode '{self.availability_mode}' is not one of {allowed_availability_modes}"
            if strict:
                raise ValueError(msg)
            logger.warning(msg)
        if (
            self.component == "sensor"
            and self.state_class
            and self.state_class not in allowed_sensor_state_classes
        ):
            msg = f"sensor.state_class '{self.state_class}' is not one of {allowed_sensor_state_classes}"
            if strict:
                raise ValueError(msg)
            logger.warning(msg)
        if (
            self.component == "sensor"
            and self.device_class
            and self.device_class not in allowed_sensor_device_classes
        ):
            msg = f"sensor.device_class '{self.device_class}' is not one of {allowed_sensor_device_classes}"
            if strict:
                raise ValueError(msg)
            logger.warning(msg)
        if (
            self.component == "binary_sensor"
            and self.device_class
            and self.device_class not in allowed_binary_sensor_device_classes
        ):
            msg = f"binary_sensor.device_class '{self.device_class}' is not one of {allowed_binary_sensor_device_classes}"
            if strict:
                raise ValueError(msg)
            logger.warning(msg)

    def get_config_topic(self) -> str:
        """
        Generates the MQTT topic for publishing the entity's discovery configuration.
        Format: <discovery_prefix>/<component>/<unique_id>/config
        """
        discovery_prefix = self._config.get(
            "home_assistant.discovery_prefix", "homeassistant"
        )
        return f"{discovery_prefix}/{self.component}/{self.unique_id}/config"

    def get_config_payload(self) -> dict:
        """Returns the complete configuration payload for this entity."""
        # Construct a globally unique ID and a clean object ID
        prefix = self._config.get("app.unique_id_prefix", "mqtt_publisher")
        computed_uid = f"{prefix}_{self.unique_id}"
        safe_object_id = _slugify_object_id(computed_uid)

        payload = {
            "name": self.name,
            # Preserve unique_id for registry stability; slugify object_id only
            "unique_id": computed_uid,
            "object_id": safe_object_id,
            "device": self.device.get_device_info(),
        }

        # Add required topics
        if self.state_topic:
            payload["state_topic"] = self.state_topic
        if self.command_topic:
            payload["command_topic"] = self.command_topic

        # Add optional common attributes only if they have values
        optional_attrs = [
            "availability_topic",
            "availability_mode",
            "availability_template",
            "device_class",
            "enabled_by_default",
            "encoding",
            "entity_category",
            "icon",
            "json_attributes_template",
            "json_attributes_topic",
            "payload_available",
            "payload_not_available",
            "qos",
            "retain",
            "state_class",
            "unit_of_measurement",
            "value_template",
        ]

        for attr in optional_attrs:
            value = getattr(self, attr, None)
            if value is not None:
                payload[attr] = value

        # Add any extra attributes
        payload.update(self.extra_attributes)

        return payload


class Sensor(Entity):
    """
    Represents a Home Assistant Sensor entity. Sensors are read-only entities
    that provide state information.
    """

    def __init__(self, config, device: Device, **kwargs):
        super().__init__(config, device, component="sensor", **kwargs)


class BinarySensor(Entity):
    """
    Represents a Home Assistant Binary Sensor entity. Binary sensors provide
    on/off or true/false state information.
    """

    def __init__(self, config, device: Device, **kwargs):
        super().__init__(config, device, component="binary_sensor", **kwargs)


class Switch(Entity):
    """
    Represents a Home Assistant Switch entity. Switches can be turned on/off
    via command topics.
    """

    def __init__(self, config, device: Device, **kwargs):
        # Set common switch defaults
        kwargs.setdefault("payload_on", "ON")
        kwargs.setdefault("payload_off", "OFF")
        super().__init__(config, device, component="switch", **kwargs)


class Light(Entity):
    """
    Represents a Home Assistant Light entity. Lights support various features
    like brightness, color, effects, etc.
    """

    def __init__(self, config, device: Device, **kwargs):
        # Set common light defaults
        kwargs.setdefault("payload_on", "ON")
        kwargs.setdefault("payload_off", "OFF")
        super().__init__(config, device, component="light", **kwargs)


class Cover(Entity):
    """
    Represents a Home Assistant Cover entity. Covers can be opened, closed,
    and positioned (blinds, garage doors, etc.).
    """

    def __init__(self, config, device: Device, **kwargs):
        # Set common cover defaults
        kwargs.setdefault("payload_open", "OPEN")
        kwargs.setdefault("payload_close", "CLOSE")
        kwargs.setdefault("payload_stop", "STOP")
        super().__init__(config, device, component="cover", **kwargs)


class Climate(Entity):
    """
    Represents a Home Assistant Climate entity. Climate entities control
    HVAC systems with temperature, mode, and fan controls.
    """

    def __init__(self, config, device: Device, **kwargs):
        super().__init__(config, device, component="climate", **kwargs)


class Fan(Entity):
    """
    Represents a Home Assistant Fan entity. Fans can be controlled for
    on/off state, speed, oscillation, etc.
    """

    def __init__(self, config, device: Device, **kwargs):
        # Set common fan defaults
        kwargs.setdefault("payload_on", "ON")
        kwargs.setdefault("payload_off", "OFF")
        super().__init__(config, device, component="fan", **kwargs)


class Lock(Entity):
    """
    Represents a Home Assistant Lock entity. Locks can be locked/unlocked
    and report their state.
    """

    def __init__(self, config, device: Device, **kwargs):
        # Set common lock defaults
        kwargs.setdefault("payload_lock", "LOCK")
        kwargs.setdefault("payload_unlock", "UNLOCK")
        super().__init__(config, device, component="lock", **kwargs)


class Number(Entity):
    """
    Represents a Home Assistant Number entity. Numbers allow setting
    numeric values within a defined range.
    """

    def __init__(self, config, device: Device, **kwargs):
        super().__init__(config, device, component="number", **kwargs)


class Select(Entity):
    """
    Represents a Home Assistant Select entity. Selects allow choosing
    from a predefined list of options.
    """

    def __init__(self, config, device: Device, **kwargs):
        super().__init__(config, device, component="select", **kwargs)


class Text(Entity):
    """
    Represents a Home Assistant Text entity. Text entities allow setting
    and reading text values.
    """

    def __init__(self, config, device: Device, **kwargs):
        super().__init__(config, device, component="text", **kwargs)


class Button(Entity):
    """
    Represents a Home Assistant Button entity. Buttons trigger actions
    when pressed.
    """

    def __init__(self, config, device: Device, **kwargs):
        super().__init__(config, device, component="button", **kwargs)


class DeviceTracker(Entity):
    """
    Represents a Home Assistant Device Tracker entity. Device trackers
    report location/presence information.
    """

    def __init__(self, config, device: Device, **kwargs):
        super().__init__(config, device, component="device_tracker", **kwargs)


class AlarmControlPanel(Entity):
    """
    Represents a Home Assistant Alarm Control Panel entity. These entities
    control security/alarm systems.
    """

    def __init__(self, config, device: Device, **kwargs):
        super().__init__(config, device, component="alarm_control_panel", **kwargs)


class Camera(Entity):
    """
    Represents a Home Assistant Camera entity. Cameras provide image/video
    feeds and can be controlled.
    """

    def __init__(self, config, device: Device, **kwargs):
        super().__init__(config, device, component="camera", **kwargs)


class Vacuum(Entity):
    """
    Represents a Home Assistant Vacuum entity. Vacuums can be started,
    stopped, returned to dock, etc.
    """

    def __init__(self, config, device: Device, **kwargs):
        super().__init__(config, device, component="vacuum", **kwargs)


class Scene(Entity):
    """
    Represents a Home Assistant Scene entity. Scenes trigger predefined
    configurations of multiple devices.
    """

    def __init__(self, config, device: Device, **kwargs):
        super().__init__(config, device, component="scene", **kwargs)


class Siren(Entity):
    """
    Represents a Home Assistant Siren entity. Sirens can be turned on/off
    with various tones and volumes.
    """

    def __init__(self, config, device: Device, **kwargs):
        super().__init__(config, device, component="siren", **kwargs)
