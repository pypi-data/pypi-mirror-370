#!/usr/bin/env python3
"""
Home Assistant MQTT Discovery Topic Generator.
Processes YAML configuration for Home Assistant MQTT discovery messages.
"""

import json
import logging
from pathlib import Path
import uuid

import yaml

# Set up logging
logging.basicConfig(level=logging.DEBUG)


class HADiscoveryProcessor:
    """Processes Home Assistant MQTT Discovery configuration."""

    def __init__(self, config_file: str):
        """Initialize with path to YAML config file."""
        self.config_path = Path(config_file)
        self.config = self._load_config()
        self.generate_uuids = (
            str(self.config.get("generate_uuids", "false")).lower() == "true"
        )
        self._uuid = str(uuid.uuid4()) if self.generate_uuids else ""

    def _load_config(self) -> dict:
        """Load and validate the YAML configuration file."""
        logging.debug("Loading configuration file: %s", self.config_path)
        try:
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
            logging.debug("Configuration loaded: %s", config)

            # Basic validation of required fields
            required_fields = ["discovery_topic", "device", "components"]
            missing = [field for field in required_fields if field not in config]
            if missing:
                raise ValueError(
                    f"Missing required fields in config: {', '.join(missing)}"
                )

            return config
        except (yaml.YAMLError, OSError) as e:
            logging.error("Error loading config file: %s", e)
            raise RuntimeError(f"Error loading config file: {e}") from e

    def _append_uuid(self, value: str) -> str:
        """Append UUID to a string if UUID generation is enabled."""
        return f"{value}-{self._uuid}" if self.generate_uuids else value

    def get_discovery_topic(self, component_name: str) -> str:
        """Generate discovery topic for a component."""
        logging.debug("Generating discovery topic for component: %s", component_name)
        topic_config = self.config["discovery_topic"]
        discovery_prefix = topic_config["discovery_prefix"]
        component = topic_config["component"]
        node_id = topic_config.get("node_id", "")
        object_id = self._append_uuid(f"{topic_config['object_id']}_{component_name}")

        # Build topic parts
        parts = [discovery_prefix, component]
        if node_id:
            parts.append(node_id)
        parts.append(object_id)
        parts.append("config")

        topic = "/".join(parts)
        logging.debug("Generated discovery topic: %s", topic)
        return topic

    def discovery_topic(self, component: str, object_id: str) -> str:
        """Generate discovery topic for a component."""
        logging.debug(
            "Generating discovery topic for component: %s, object_id: %s",
            component,
            object_id,
        )
        topic_config = self.config["discovery_topic"]
        discovery_prefix = topic_config["discovery_prefix"]
        node_id = topic_config.get("node_id", "")
        object_id = self._append_uuid(object_id)

        # Build topic parts
        parts = [discovery_prefix, component]
        if node_id:
            parts.append(node_id)
        parts.append(object_id)
        parts.append("config")

        topic = "/".join(parts)
        logging.debug("Generated discovery topic: %s", topic)
        return topic

    def get_component_payload(self, component_name: str) -> dict:
        """Generate discovery payload for a component."""
        logging.debug("Generating component payload for: %s", component_name)
        if component_name not in self.config["components"]:
            raise ValueError(f"Component {component_name} not found in configuration")

        # Get base component configuration
        component = self.config["components"][component_name]

        # Get and process device configuration
        device = self.config["device"].copy()
        if isinstance(device.get("identifiers"), list):
            device["identifiers"] = [
                self._append_uuid(i) for i in device["identifiers"]
            ]
        elif isinstance(device.get("identifiers"), str):
            device["identifiers"] = self._append_uuid(device["identifiers"])

        # Build payload with proper structure
        payload = {
            # Component specific configuration
            **component,  # Spread operator to include all component fields
            # Required fields
            "platform": component.get("platform", "sensor"),
            "unique_id": self._append_uuid(component["unique_id"]),
            # Device and origin information
            "device": device,
            "origin": self.config.get("origin", {}),
        }

        # Add topic defaults if present
        topic_defaults = self.get_topic_defaults()
        if topic_defaults:
            payload.update(
                {k: v for k, v in topic_defaults.items() if k not in payload}
            )

        logging.debug("Generated component payload: %s", payload)
        return payload

    def get_topic_defaults(self) -> dict:
        """Return topic defaults from configuration."""
        return self.config.get("topic_defaults", {})

    def process_component(self, component_name: str) -> tuple[str, str]:
        """Process a component and return its discovery topic and payload."""
        topic = self.get_discovery_topic(component_name)
        payload = self.get_component_payload(component_name)
        return topic, json.dumps(payload)

    def get_device_discovery_message(self) -> tuple[str, str]:
        """
        Generate Home Assistant device discovery topic and payload.
        Uses device config directly from YAML without field restrictions.
        Returns a tuple of (topic, payload_json_string).
        """
        logging.debug("Generating device discovery message")
        object_id = self._append_uuid(self.config["discovery_topic"]["object_id"])
        topic = f"homeassistant/device/{object_id}/config"

        # Use device configuration as-is
        payload = self.config["device"].copy()

        # Process identifiers with UUID if needed
        if isinstance(payload.get("identifiers"), list):
            payload["identifiers"] = [
                self._append_uuid(i) for i in payload["identifiers"]
            ]
        elif isinstance(payload.get("identifiers"), str):
            payload["identifiers"] = self._append_uuid(payload["identifiers"])

        logging.debug("Generated device discovery message: %s", payload)
        return topic, json.dumps(payload)


def main():
    """Main function when script is run directly."""
    # Find config file relative to script location
    script_dir = Path(__file__).parent
    config_file = script_dir.parent / "ha_mqtt_config" / "ha_mqtt_discovery.yaml"

    try:
        processor = HADiscoveryProcessor(config_file)

        # Process device discovery first
        device_topic, device_payload = processor.get_device_discovery_message()
        print("\nDevice Discovery:")
        print(f"Topic: {device_topic}")
        print(f"Payload:\n{json.dumps(json.loads(device_payload), indent=2)}")

        # Process each component
        for component_name in processor.config["components"]:
            try:
                topic, payload = processor.process_component(component_name)
                print(f"\nComponent: {component_name}")
                print(f"Discovery Topic: {topic}")
                print(f"Payload:\n{json.dumps(json.loads(payload), indent=2)}")
            except Exception as e:
                print(f"Error processing component {component_name}: {e}")

        # Print topic defaults
        print("\nTopic Defaults:")
        print(json.dumps(processor.get_topic_defaults(), indent=2))

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
else:
    pass
