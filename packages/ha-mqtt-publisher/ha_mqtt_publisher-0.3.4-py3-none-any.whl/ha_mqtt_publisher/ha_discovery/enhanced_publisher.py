"""Enhanced device discovery with availability and migration support.

This module provides the enhanced publish_device_level_discovery function
originally developed in twickenham_events, with generic patterns for:
- Availability topic configuration
- Per-entity to bundle migration
- Command system patterns
- Rich entity configuration using proper Entity objects
"""

import json

from .device import Device
from .entity import Button, Entity, Sensor


def publish_device_level_discovery(
    config,
    publisher,
    device: Device,
    entities: list[Entity],
    *,
    device_id: str | None = None,
    availability_topic: str | None = None,
    migrate_from_per_entity: bool = False,
    retain: bool = True,
) -> str:
    """
    Publish device-based discovery with full availability and migration support.
    
    This is the enhanced version originally developed in twickenham_events,
    now generalized for any application using proper Entity objects.
    
    Args:
        config: Application config object
        publisher: MQTT publisher instance
        device: Device instance
        entities: List of Entity instances
        device_id: Optional device ID override
        availability_topic: Optional availability topic for online/offline
        migrate_from_per_entity: If True, publishes migration markers and cleanup
        retain: Whether to retain the discovery message
        
    Returns:
        The published device topic string
    """
    from .publisher import _entity_to_component_payload
    
    discovery_prefix = config.get("home_assistant.discovery_prefix", "homeassistant")
    base = config.get("app.unique_id_prefix", config.get("app.name", "mqtt_publisher"))
    
    # Determine device_id for topic
    if not device_id:
        if isinstance(device.identifiers, list) and device.identifiers:
            device_id = str(device.identifiers[0])
        else:
            device_id = base
            
    device_topic = f"{discovery_prefix}/device/{device_id}/config"
    
    # Build origin block
    origin = {
        "name": base,
        "sw": device.get_device_info().get("sw_version", "unknown"),
        "url": device.get_device_info().get("configuration_url"),
    }
    
    # Build cmps from entities using the library's conversion function
    cmps: dict[str, dict] = {}
    state_topics = set()
    
    for entity in entities:
        # Convert Entity to component payload (removes device, adds 'p' for component type)
        comp_payload = _entity_to_component_payload(entity)
        
        # Use unique_id as the key for stable references
        key = entity.unique_id.replace(f"{base}_", "", 1) if entity.unique_id.startswith(f"{base}_") else entity.unique_id
        cmps[key] = comp_payload
        
        # Track state topics for potential common topic detection
        if hasattr(entity, 'state_topic') and entity.state_topic:
            state_topics.add(entity.state_topic)
    
    # Build the device bundle payload
    payload = {
        "dev": device.get_device_info(),
        "o": origin,
        "cmps": cmps,
        "qos": config.get("mqtt.default_qos", 0),
    }
    
    # Add availability configuration if provided
    if availability_topic:
        payload["availability"] = [{"topic": availability_topic}]
        payload["payload_available"] = "online"
        payload["payload_not_available"] = "offline"
        
    # Add common state topic if all entities share the same one
    if len(state_topics) == 1:
        payload["state_topic"] = list(state_topics)[0]
    
    # Handle migration from per-entity discovery
    if migrate_from_per_entity:
        # Publish migration markers first
        for entity in entities:
            marker_topic = f"{discovery_prefix}/{entity.component}/{device_id}/migrate_discovery"
            marker_payload = json.dumps({"migrated_to": device_topic})
            publisher.publish(marker_topic, marker_payload, retain=True)
    
    # Publish the device bundle
    payload_json = json.dumps(payload)
    publisher.publish(device_topic, payload_json, retain=retain)
    
    # Clean up old per-entity topics if migrating
    if migrate_from_per_entity:
        for entity in entities:
            old_topic = entity.get_config_topic()
            publisher.publish(old_topic, "", retain=False)  # Empty payload removes retained
    
    return device_topic


def create_command_entities(config, device: Device, base_prefix: str, command_topics: dict[str, str]) -> list[Entity]:
    """
    Create command system entities (ack, result, last_ack, last_result) as Entity objects.
    
    Args:
        config: Application config
        device: Device instance 
        base_prefix: Base prefix for entity unique_ids
        command_topics: Dict with ack_topic, result_topic, last_ack_topic, last_result_topic
        
    Returns:
        List of Entity objects for command system
    """
    entities = []
    
    # Command acknowledgment sensor
    if "ack_topic" in command_topics:
        entities.append(Sensor(
            config=config,
            device=device,
            name="Command Ack",
            unique_id=f"{base_prefix}_cmd_ack",
            state_topic=command_topics["ack_topic"],
            icon="mdi:check-circle",
            entity_category="diagnostic",
            expire_after=120,
        ))
    
    # Command result sensor  
    if "result_topic" in command_topics:
        entities.append(Sensor(
            config=config,
            device=device,
            name="Command Result", 
            unique_id=f"{base_prefix}_cmd_result",
            state_topic=command_topics["result_topic"],
            icon="mdi:message-text",
            entity_category="diagnostic",
            expire_after=120,
        ))
    
    # Last acknowledgment sensor
    if "last_ack_topic" in command_topics:
        entities.append(Sensor(
            config=config,
            device=device,
            name="Last Ack",
            unique_id=f"{base_prefix}_last_ack",
            state_topic=command_topics["last_ack_topic"],
            icon="mdi:check-circle-outline",
            entity_category="diagnostic",
        ))
    
    # Last result sensor
    if "last_result_topic" in command_topics:
        entities.append(Sensor(
            config=config,
            device=device,
            name="Last Result",
            unique_id=f"{base_prefix}_last_result", 
            state_topic=command_topics["last_result_topic"],
            icon="mdi:message-outline",
            entity_category="diagnostic",
        ))
    
    return entities


def create_standard_buttons(config, device: Device, base_prefix: str, command_topic_base: str, button_names: list[str] | None = None) -> list[Entity]:
    """
    Create standard button entities (refresh, clear_cache, restart) as Entity objects.
    
    Args:
        config: Application config
        device: Device instance
        base_prefix: Base prefix for entity unique_ids
        command_topic_base: Base command topic (e.g., "app/cmd")
        button_names: Optional list of button names (defaults to ["refresh", "clear_cache", "restart"])
        
    Returns:
        List of Button Entity objects
    """
    if button_names is None:
        button_names = ["refresh", "clear_cache", "restart"]
    
    entities = []
    
    for button_name in button_names:
        entities.append(Button(
            config=config,
            device=device,
            name=button_name.replace("_", " ").title(),
            unique_id=f"{base_prefix}_{button_name}",
            command_topic=f"{command_topic_base}/{button_name}",
            icon=_get_button_icon(button_name),
        ))
    
    return entities


def _get_button_icon(button_name: str) -> str:
    """Get appropriate MDI icon for standard button names."""
    icon_map = {
        "refresh": "mdi:refresh",
        "clear_cache": "mdi:delete-sweep",
        "restart": "mdi:restart",
        "reload": "mdi:reload",
        "reset": "mdi:backup-restore",
    }
    return icon_map.get(button_name, "mdi:gesture-tap-button")
