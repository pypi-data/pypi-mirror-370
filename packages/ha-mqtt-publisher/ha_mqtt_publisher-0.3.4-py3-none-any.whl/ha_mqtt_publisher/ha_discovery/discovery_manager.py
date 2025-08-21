# ha_discovery/discovery_manager.py

"""
Discovery Manager for Home Assistant MQTT Discovery.

This module provides advanced discovery lifecycle management including
entity removal, updates, and discovery scanning.
"""

import json
import logging
from typing import Any

from .device import Device
from .entity import Entity


class DiscoveryManager:
    """
    Manages Home Assistant MQTT Discovery configurations.

    Provides methods for creating, updating, removing, and managing
    discovery configurations for entities and devices.
    """

    def __init__(self, config, publisher):
        """
        Initialize the Discovery Manager.

        Args:
            config: Configuration object with get() method
            publisher: MQTT publisher instance
        """
        self.config = config
        self.publisher = publisher
        self.entities: dict[str, Entity] = {}
        self.devices: dict[str, Device] = {}
        self.discovery_prefix = config.get(
            "home_assistant.discovery_prefix", "homeassistant"
        )

    def add_entity(self, entity: Entity) -> bool:
        """
        Add an entity and publish its discovery configuration.

        Args:
            entity: Entity to add

        Returns:
            bool: Success status
        """
        try:
            # Store entity
            self.entities[entity.unique_id] = entity

            # Publish discovery configuration
            config_topic = entity.get_config_topic()
            config_payload = entity.get_config_payload()

            success = self.publisher.publish(
                topic=config_topic, payload=json.dumps(config_payload), retain=True
            )

            if success:
                logging.info(f"Added entity '{entity.name}' ({entity.unique_id})")
            else:
                logging.error(f"Failed to add entity '{entity.name}'")

            return success

        except Exception as e:
            logging.error(f"Error adding entity: {e}")
            return False

    def remove_entity(self, unique_id: str) -> bool:
        """
        Remove an entity by publishing an empty discovery configuration.

        Args:
            unique_id: Unique ID of the entity to remove

        Returns:
            bool: Success status
        """
        try:
            entity = self.entities.get(unique_id)
            if not entity:
                logging.warning(f"Entity '{unique_id}' not found")
                return False

            # Publish empty payload to remove entity
            config_topic = entity.get_config_topic()
            success = self.publisher.publish(
                topic=config_topic, payload="", retain=True
            )

            if success:
                # Remove from local tracking
                del self.entities[unique_id]
                logging.info(f"Removed entity '{entity.name}' ({unique_id})")
            else:
                logging.error(f"Failed to remove entity '{entity.name}'")

            return success

        except Exception as e:
            logging.error(f"Error removing entity: {e}")
            return False

    def update_entity(self, unique_id: str, **kwargs) -> bool:
        """
        Update an entity's configuration and republish discovery.

        Args:
            unique_id: Unique ID of the entity to update
            **kwargs: Fields to update

        Returns:
            bool: Success status
        """
        try:
            entity = self.entities.get(unique_id)
            if not entity:
                logging.warning(f"Entity '{unique_id}' not found")
                return False

            # Update entity attributes
            for key, value in kwargs.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
                else:
                    entity.extra_attributes[key] = value

            # Republish discovery configuration
            return self.add_entity(entity)

        except Exception as e:
            logging.error(f"Error updating entity: {e}")
            return False

    def add_device(self, device: Device) -> bool:
        """
        Add a device to tracking.

        Args:
            device: Device to add

        Returns:
            bool: Success status
        """
        try:
            device_id = device.identifiers[0] if device.identifiers else device.name
            self.devices[device_id] = device
            logging.info(f"Added device '{device.name}' ({device_id})")
            return True

        except Exception as e:
            logging.error(f"Error adding device: {e}")
            return False

    def remove_device(self, device_id: str) -> bool:
        """
        Remove a device and all its entities.

        Args:
            device_id: Device identifier

        Returns:
            bool: Success status
        """
        try:
            device = self.devices.get(device_id)
            if not device:
                logging.warning(f"Device '{device_id}' not found")
                return False

            # Remove all entities belonging to this device
            entities_to_remove = [
                uid for uid, entity in self.entities.items() if entity.device == device
            ]

            success = True
            for uid in entities_to_remove:
                if not self.remove_entity(uid):
                    success = False

            # Remove device from tracking
            if success:
                del self.devices[device_id]
                logging.info(f"Removed device '{device.name}' ({device_id})")

            return success

        except Exception as e:
            logging.error(f"Error removing device: {e}")
            return False

    def get_device_entities(self, device_id: str) -> list[Entity]:
        """
        Get all entities belonging to a device.

        Args:
            device_id: Device identifier

        Returns:
            List of entities
        """
        device = self.devices.get(device_id)
        if not device:
            return []

        return [entity for entity in self.entities.values() if entity.device == device]

    def publish_all_discoveries(self) -> bool:
        """
        Publish discovery configurations for all tracked entities.

        Returns:
            bool: Success status
        """
        success = True
        for entity in self.entities.values():
            if not self.add_entity(entity):
                success = False
        return success

    def clear_all_discoveries(self) -> bool:
        """
        Remove all discovery configurations.

        Returns:
            bool: Success status
        """
        success = True
        entity_ids = list(self.entities.keys())

        for uid in entity_ids:
            if not self.remove_entity(uid):
                success = False

        return success

    def get_entity_status(self, unique_id: str) -> dict[str, Any] | None:
        """
        Get status information for an entity.

        Args:
            unique_id: Unique ID of the entity

        Returns:
            Dictionary with entity status or None if not found
        """
        entity = self.entities.get(unique_id)
        if not entity:
            return None

        return {
            "unique_id": entity.unique_id,
            "name": entity.name,
            "component": entity.component,
            "device": entity.device.name,
            "config_topic": entity.get_config_topic(),
            "state_topic": getattr(entity, "state_topic", None),
            "command_topic": getattr(entity, "command_topic", None),
            "availability_topic": getattr(entity, "availability_topic", None),
        }

    def list_entities(self) -> list[dict[str, Any]]:
        """
        List all tracked entities with their status.

        Returns:
            List of entity status dictionaries
        """
        return [
            status
            for status in (self.get_entity_status(uid) for uid in self.entities.keys())
            if status is not None
        ]

    def list_devices(self) -> list[dict[str, Any]]:
        """
        List all tracked devices with their information.

        Returns:
            List of device information dictionaries
        """
        devices = []
        for device_id, device in self.devices.items():
            entity_count = len(self.get_device_entities(device_id))
            devices.append(
                {
                    "device_id": device_id,
                    "name": device.name,
                    "manufacturer": getattr(device, "manufacturer", None),
                    "model": getattr(device, "model", None),
                    "sw_version": getattr(device, "sw_version", None),
                    "entity_count": entity_count,
                }
            )
        return devices
