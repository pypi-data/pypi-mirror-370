# ha_discovery/device.py

"""
Device representation for Home Assistant MQTT Discovery.

This module provides the Device class which represents a physical or logical
device in Home Assistant that groups multiple entities together.
"""


class Device:
    """
    Represents a Home Assistant device. This class is used to create a device
    that groups multiple entities (sensors, binary_sensors, etc.) together.

    Supports all Home Assistant device fields as documented at:
    https://www.home-assistant.io/integrations/mqtt/#device-registry
    """

    def __init__(self, config, **kwargs):
        """
        Initializes the Device object.

        Args:
            config: The application's configuration object with get() method.
            **kwargs: Additional device attributes that override config values
        """
        self._config = config

        # Required fields
        self.identifiers = kwargs.get(
            "identifiers", [self._config.get("app.unique_id_prefix", "mqtt_publisher")]
        )
        self.name = kwargs.get("name", self._config.get("app.name", "MQTT Publisher"))

        # Optional fields with config fallbacks
        self.manufacturer = kwargs.get(
            "manufacturer",
            self._config.get("app.manufacturer", "Generic MQTT Publisher"),
        )
        self.model = kwargs.get("model", self._config.get("app.model", "MQTT-Pub-Py"))
        self.sw_version = kwargs.get("sw_version", self._config.get("app.sw_version"))
        self.hw_version = kwargs.get("hw_version", self._config.get("app.hw_version"))
        self.configuration_url = kwargs.get(
            "configuration_url", self._config.get("app.configuration_url")
        )
        self.connections = kwargs.get(
            "connections", self._config.get("app.connections")
        )
        self.suggested_area = kwargs.get(
            "suggested_area", self._config.get("app.suggested_area")
        )
        self.via_device = kwargs.get("via_device", self._config.get("app.via_device"))
        self.model_id = kwargs.get("model_id", self._config.get("app.model_id"))
        self.serial_number = kwargs.get(
            "serial_number", self._config.get("app.serial_number")
        )

    def get_device_info(self) -> dict:
        """
        Returns a dictionary containing the device information, which is used
        in the discovery payload for each entity. Only includes fields that
        have been set (not None).
        """
        device_info = {
            "identifiers": self.identifiers,
            "name": self.name,
        }

        # Add optional fields only if they have values
        optional_fields = [
            "manufacturer",
            "model",
            "sw_version",
            "hw_version",
            "configuration_url",
            "connections",
            "suggested_area",
            "via_device",
            "model_id",
            "serial_number",
        ]

        for field in optional_fields:
            value = getattr(self, field, None)
            if value is not None:
                device_info[field] = value

        return device_info
