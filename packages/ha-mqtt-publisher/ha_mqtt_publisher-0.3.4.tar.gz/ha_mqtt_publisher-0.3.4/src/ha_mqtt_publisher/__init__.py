"""An MQTT publisher package with Home Assistant Discovery support"""

__version__ = "0.3.4"
__author__ = "ronschaeffer"

# Import main components for easy access (sorted)
from .availability import AvailabilityPublisher, install_signal_handlers
from .commands import CommandProcessor, Executor
from .config import Config, MQTTConfig
from .ha_discovery import (
    Device,
    DiscoveryManager,
    Entity,
    StatusSensor,
    publish_discovery_configs,
)
from .json_publish import publish_json, publish_many
from .publisher import MQTTPublisher
from .service_runner import run_service_loop, run_service_once
from .status import StatusError, StatusPayload
from .topic_map import TopicMap
from .validator import validate_retained

__all__ = [
    "AvailabilityPublisher",
    "CommandProcessor",
    "Config",
    "Device",
    "DiscoveryManager",
    "Entity",
    "Executor",
    "MQTTConfig",
    "MQTTPublisher",
    "StatusError",
    "StatusPayload",
    "StatusSensor",
    "TopicMap",
    "install_signal_handlers",
    "publish_discovery_configs",
    "publish_json",
    "publish_many",
    "run_service_loop",
    "run_service_once",
    "validate_retained",
]
