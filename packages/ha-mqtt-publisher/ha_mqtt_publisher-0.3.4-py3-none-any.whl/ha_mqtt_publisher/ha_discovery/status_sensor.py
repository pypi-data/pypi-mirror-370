# ha_discovery/status_sensor.py

"""
Status sensor for Home Assistant MQTT Discovery.

This module provides the StatusSensor class which creates a binary sensor
for monitoring the health/status of the MQTT publishing system.
"""

from .entity import BinarySensor


class StatusSensor(BinarySensor):
    """
    Represents the status binary_sensor in Home Assistant.
    This creates a binary sensor that indicates whether the system is running
    correctly (OFF) or has encountered an error (ON).
    """

    def __init__(self, config, device):
        """
        Initializes the StatusSensor.

        Args:
            config: The application's configuration object with get() method.
            device: The Device object for HA discovery.
        """
        base_topic = config.get("mqtt.base_topic", "mqtt_publisher")

        super().__init__(
            config,
            device,
            unique_id="status",
            name="Status",
            device_class="problem",
            state_topic=f"{base_topic}/status",
            value_template="{{ 'ON' if value_json.status == 'error' else 'OFF' }}",
            json_attributes_topic=f"{base_topic}/status",
            json_attributes_template="{{ value_json | tojson }}",
        )
