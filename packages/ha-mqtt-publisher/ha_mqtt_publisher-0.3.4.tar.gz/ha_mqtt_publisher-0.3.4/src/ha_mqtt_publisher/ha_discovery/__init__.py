"""
Home Assistant MQTT Discovery module.

Provides Home Assistant MQTT Discovery support: entity classes, device
management, and discovery publishing helpers.
"""

from .device import Device
from .discovery_manager import DiscoveryManager
from .entity import (
    AlarmControlPanel,
    BinarySensor,
    Button,
    Camera,
    Climate,
    Cover,
    DeviceTracker,
    Entity,
    Fan,
    Light,
    Lock,
    Number,
    Select,
    Sensor,
    Switch,
    Text,
)
from .publisher import (
    AvailabilityMode,
    EntityCategory,
    SensorStateClass,
    StatusSensor,
    create_sensor,
    create_status_sensor,
    ensure_discovery,
    publish_command_buttons,
    publish_device_bundle,
    publish_device_config,
    publish_discovery_configs,
    purge_legacy_discovery,
)
from .enhanced_publisher import (
    create_command_entities,
    create_standard_buttons,
    publish_device_level_discovery,
)

__all__ = [
    "AlarmControlPanel",
    "AvailabilityMode",
    "BinarySensor",
    "Button",
    "Camera",
    "Climate",
    "Cover",
    "Device",
    "DeviceTracker",
    "DiscoveryManager",
    "Entity",
    "EntityCategory",
    "Fan",
    "Light",
    "Lock",
    "Number",
    "Select",
    "Sensor",
    "SensorStateClass",
    "StatusSensor",
    "Switch",
    "Text",
    "create_command_entities",
    "create_sensor",
    "create_standard_buttons",
    "create_status_sensor",
    "ensure_discovery",
    "publish_command_buttons",
    "publish_device_bundle",
    "publish_device_config",
    "publish_device_level_discovery",
    "publish_discovery_configs",
    "purge_legacy_discovery",
]
