# ha_discovery/publisher.py

"""
High-level Home Assistant MQTT Discovery publisher.

This module provides convenient functions for publishing discovery configurations
to MQTT brokers for Home Assistant auto-discovery.
"""

import json
import time
from typing import Any

from .constants import AvailabilityMode, EntityCategory, SensorStateClass
from .device import Device
from .entity import Button, Entity, Sensor
from .status_sensor import StatusSensor


def _slugify(value: str) -> str:
    """Create a HA-friendly slug: lowercase, alnum+underscore only."""
    import re

    value = value.strip().lower()
    value = re.sub(r"[\s\-]+", "_", value)
    value = re.sub(r"[^a-z0-9_]", "", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "device"


def publish_discovery_configs(
    config,
    publisher,
    entities=None,
    device=None,
    one_time_mode=False,
    *,
    emit_device_bundle: bool = False,
    device_id: str | None = None,
):
    """
    Publishes the MQTT discovery configurations for all defined entities.

    Args:
        config: Configuration object with get() method
        publisher: MQTT publisher instance (must have publish() method)
        entities: Optional list of entities to publish. If None, creates default entities.
        device: Optional Device instance. If None, creates a new device.
        one_time_mode: If True, only publish if not already published (default: False)
    """
    if not config.get("home_assistant.enabled", True):
        return

    # Create a single device instance to be shared by all entities
    if device is None:
        device = Device(config)

    # If no entities provided, create default entities
    if entities is None:
        entities = []

        # Conditionally add the Status Sensor
        if config.get("mqtt.topics.status"):
            entities.append(StatusSensor(config, device))

    # Determine bundle-only behavior (default False for backward compatibility)
    bundle_only_mode = bool(config.get("home_assistant.bundle_only_mode", False))

    # Optionally run a verification pass to heal missing retained configs
    # Only when explicitly enabled and when publisher supports subscriptions.
    ensure_enabled = config.get("home_assistant.ensure_discovery_on_startup", False)
    if (
        ensure_enabled
        and one_time_mode
        and hasattr(publisher, "subscribe")
        and callable(publisher.subscribe)
        and entities
    ):
        try:
            ensure_discovery(
                config=config,
                publisher=publisher,
                entities=entities,
                device=device,
                device_id=device_id,
                timeout=float(
                    config.get("home_assistant.ensure_discovery_timeout", 2.0)
                ),
                one_time_mode=True,
            )
        except Exception as exc:
            print(f"Warning: ensure_discovery failed: {exc}")
    elif (emit_device_bundle or bundle_only_mode) and entities:
        # If ensure_discovery isn't used, optionally emit or always emit device bundle first
        try:
            publish_device_bundle(
                config=config,
                publisher=publisher,
                device=device,
                entities=entities,
                device_id=device_id,
            )
        except Exception as exc:
            print(f"Warning: device bundle publish failed: {exc}")

    # If bundle-only mode, skip per-entity discovery publishes
    if bundle_only_mode:
        if one_time_mode:
            print("One-time discovery mode (bundle-only): Per-entity configs skipped")
        return

    # Track published configs for one-time mode
    published_count = 0
    skipped_count = 0

    # Publish the discovery config for each entity
    for entity in entities:
        config_topic = entity.get_config_topic()
        config_payload = entity.get_config_payload()

        if one_time_mode and _is_discovery_already_published(config_topic, config):
            print(f"Skipping already published discovery config: {config_topic}")
            skipped_count += 1
            continue

        publisher.publish(
            topic=config_topic, payload=json.dumps(config_payload), retain=True
        )
        print(f"Published discovery config to {config_topic}")
        published_count += 1

        # Mark as published for one-time mode
        if one_time_mode:
            _mark_discovery_as_published(config_topic, config)

    if one_time_mode:
        print(
            f"One-time discovery mode: Published {published_count}, Skipped {skipped_count}"
        )


def _is_discovery_already_published(config_topic, config):
    """
    Check if a discovery config has already been published.

    Args:
        config_topic: The MQTT topic for the discovery config
        config: Configuration object

    Returns:
        bool: True if already published, False otherwise
    """
    import json
    import os

    # Get the discovery state file path
    state_file = config.get(
        "home_assistant.discovery_state_file", ".ha_discovery_state.json"
    )

    if not os.path.exists(state_file):
        return False

    try:
        with open(state_file) as f:
            published_configs = json.load(f)
        return config_topic in published_configs.get("published_topics", [])
    except (OSError, json.JSONDecodeError):
        return False


def _mark_discovery_as_published(config_topic, config):
    """
    Mark a discovery config as published.

    Args:
        config_topic: The MQTT topic for the discovery config
        config: Configuration object
    """
    from datetime import datetime
    import json
    import os

    # Get the discovery state file path
    state_file = config.get(
        "home_assistant.discovery_state_file", ".ha_discovery_state.json"
    )

    # Load existing state
    published_configs = {"published_topics": [], "last_updated": None}
    if os.path.exists(state_file):
        try:
            with open(state_file) as f:
                published_configs = json.load(f)
        except (OSError, json.JSONDecodeError):
            pass

    # Add the new topic if not already present
    if config_topic not in published_configs.get("published_topics", []):
        published_configs.setdefault("published_topics", []).append(config_topic)
        published_configs["last_updated"] = datetime.now().isoformat()

        # Save the updated state
        try:
            with open(state_file, "w") as f:
                json.dump(published_configs, f, indent=2)
        except OSError as exc:
            print(f"Warning: Could not save discovery state: {exc}")


def clear_discovery_state(config):
    """
    Clear the discovery state file to force republication of all configs.

    Args:
        config: Configuration object
    """
    import os

    state_file = config.get(
        "home_assistant.discovery_state_file", ".ha_discovery_state.json"
    )

    if os.path.exists(state_file):
        try:
            os.remove(state_file)
            print(f"Cleared discovery state file: {state_file}")
        except OSError as exc:
            print(f"Warning: Could not remove discovery state file: {exc}")
    else:
        print("Discovery state file does not exist")


def force_republish_discovery(config, publisher, entities=None, device=None):
    """
    Force republication of all discovery configs, ignoring one-time mode state.

    Args:
        config: Configuration object with get() method
        publisher: MQTT publisher instance (must have publish() method)
        entities: Optional list of entities to publish
        device: Optional Device instance
    """
    clear_discovery_state(config)
    publish_discovery_configs(config, publisher, entities, device, one_time_mode=False)


def ensure_discovery(
    config,
    publisher,
    entities: list[Entity] | None = None,
    device: Device | None = None,
    *,
    device_id: str | None = None,
    timeout: float = 2.0,
    one_time_mode: bool = False,
):
    """
    Verify retained discovery configs exist; republish any missing.

    - Subscribes to relevant discovery topics (bundle + per-entity).
    - Waits up to `timeout` for retained messages to arrive.
    - Republishes missing topics and optionally marks them "published" when one_time_mode.

    Returns a summary dict: {"seen": set[str], "missing": set[str], "republished": set[str]}.
    """
    discovery_prefix = config.get("home_assistant.discovery_prefix", "homeassistant")

    topics_to_check: list[str] = []

    # Bundle topic (if device provided and bundle-only mode enabled)
    bundle_only_mode = bool(config.get("home_assistant.bundle_only_mode", False))
    bundle_topic: str | None = None
    if device is not None:
        if not device_id:
            if isinstance(device.identifiers, list) and device.identifiers:
                device_id = str(device.identifiers[0])
            else:
                device_id = _slugify(device.name)
        bundle_topic = f"{discovery_prefix}/device/{device_id}/config"
        # Always consider bundle if bundle_only_mode; otherwise we still check per-entity
        if bundle_only_mode:
            topics_to_check.append(bundle_topic)

    # Entity topics
    entities = entities or []
    if entities and not bundle_only_mode:
        topics_to_check.extend([e.get_config_topic() for e in entities])

    if not topics_to_check:
        return {"seen": set(), "missing": set(), "republished": set()}

    seen: set[str] = set()
    republished: set[str] = set()

    # Callback to record seen topics
    def _on_msg(_client, _userdata, msg):  # pragma: no cover - tiny glue
        try:
            seen.add(msg.topic)
        except Exception:
            pass

    # Subscribe to each topic; messages should arrive immediately if retained
    for t in topics_to_check:
        try:
            publisher.subscribe(t, qos=0, callback=_on_msg)
        except Exception:
            # Non-fatal; continue to try others
            pass

    # Wait briefly or until all are seen
    deadline = time.time() + max(0.05, float(timeout))
    while time.time() < deadline and len(seen) < len(topics_to_check):
        time.sleep(0.05)

    # Unsubscribe
    for t in topics_to_check:
        try:
            if hasattr(publisher, "unsubscribe"):
                publisher.unsubscribe(t)
        except Exception:
            pass

    missing = set(topics_to_check) - seen

    # Republish bundle if needed
    if bundle_only_mode and bundle_topic and (bundle_topic in missing) and device:
        try:
            ok = publish_device_bundle(
                config=config,
                publisher=publisher,
                device=device,
                entities=entities,
                device_id=device_id,
            )
            if ok:
                republished.add(bundle_topic)
                if one_time_mode:
                    _mark_discovery_as_published(bundle_topic, config)
        except Exception as exc:
            print(f"Warning: failed to republish bundle discovery: {exc}")

    # Republish missing per-entity topics
    if entities and not bundle_only_mode:
        for e in entities:
            t = e.get_config_topic()
            if t in missing:
                try:
                    payload = e.get_config_payload()
                    publisher.publish(topic=t, payload=json.dumps(payload), retain=True)
                    republished.add(t)
                    if one_time_mode:
                        _mark_discovery_as_published(t, config)
                except Exception as exc:
                    print(f"Warning: failed to republish discovery for {t}: {exc}")

    # Optionally mark seen topics as published in one-time mode
    if one_time_mode:
        for t in seen:
            try:
                _mark_discovery_as_published(t, config)
            except Exception:
                pass

    return {"seen": seen, "missing": missing, "republished": republished}


def publish_device_config(
    config,
    publisher,
    device: Device,
    *,
    device_id: str | None = None,
    retain: bool = True,
) -> bool:
    """
    Publish a device-centric discovery message.

    Topic format: <discovery_prefix>/device/<device_id>/config

    Args:
        config: Configuration object with get() method
        publisher: MQTT publisher instance (must have publish() method)
        device: Device instance to serialize
        device_id: Optional device identifier for the topic. If not provided,
                   uses the first identifier from the device or a slugified name.
        retain: Retain flag for the config message (default True)

    Returns:
        bool: Success status from publisher.publish
    """
    discovery_prefix = config.get("home_assistant.discovery_prefix", "homeassistant")

    # Determine device_id for topic
    if not device_id:
        if isinstance(device.identifiers, list) and device.identifiers:
            device_id = str(device.identifiers[0])
        else:
            device_id = _slugify(device.name)

    topic = f"{discovery_prefix}/device/{device_id}/config"
    payload = device.get_device_info()
    return publisher.publish(topic=topic, payload=json.dumps(payload), retain=retain)


def _entity_to_component_payload(entity: Entity) -> dict:
    """Convert an Entity instance to a compact entity payload for bundle."""
    payload = entity.get_config_payload().copy()

    # Map to compact keys where applicable (aligning with HA docs example terms):
    # - platform -> p (component type)
    # - unique_id kept as unique_id
    # Remove top-level device block; device is represented once in bundle
    payload.pop("device", None)

    # Ensure component type key (p)
    payload["p"] = entity.component
    return payload


def publish_device_bundle(
    config,
    publisher,
    device: Device,
    entities: list[Entity],
    *,
    device_id: str | None = None,
    retain: bool = True,
) -> bool:
    """
    Publish a single device-centric bundled discovery message including all entities.

    Topic: <discovery_prefix>/device/<device_id>/config

    Payload structure:
    {
      "dev": { ...device info... },
      "o":   { ...origin info... },
      "cmps": { <object_id>: { ...component payload... }, ... },
      "qos": <int>,
      "retain": <bool>,
      "state_topic": <optional default>
    }
    Note: Entities still publish state/command at runtime; this replaces per-entity
    config publishes on modern HA versions that support the device bundle.
    """
    discovery_prefix = config.get("home_assistant.discovery_prefix", "homeassistant")

    # Determine device_id for topic
    if not device_id:
        if isinstance(device.identifiers, list) and device.identifiers:
            device_id = str(device.identifiers[0])
        else:
            device_id = _slugify(device.name)

    topic = f"{discovery_prefix}/device/{device_id}/config"

    # Build cmps from entities keyed by their unique_id or object_id
    cmps: dict[str, dict] = {}
    for e in entities:
        comp_payload = _entity_to_component_payload(e)
        # Use the raw entity.unique_id as bundle key to keep keys stable and readable
        key = e.unique_id
        cmps[key] = comp_payload

    # Origin block (optional)
    origin = {
        "name": config.get("app.name", "ha_mqtt_publisher"),
        "sw": config.get("app.sw_version"),
        "url": config.get("app.configuration_url"),
    }
    origin = {k: v for k, v in origin.items() if v}

    bundle: dict[str, Any] = {
        "dev": device.get_device_info(),
        "cmps": cmps,
    }
    if origin:
        bundle["o"] = origin

    # Optional defaults at bundle level
    default_qos = config.get("mqtt.default_qos")
    if default_qos is not None:
        bundle["qos"] = int(default_qos)
    default_retain = config.get("mqtt.default_retain")
    if default_retain is not None:
        bundle["retain"] = bool(default_retain)

    return publisher.publish(topic=topic, payload=json.dumps(bundle), retain=retain)


def create_sensor(
    config,
    device: Device,
    name: str,
    unique_id: str,
    state_topic: str,
    *,
    entity_category: EntityCategory | None = None,
    availability_mode: AvailabilityMode | None = None,
    state_class: SensorStateClass | None = None,
    **kwargs,
):
    """
    Convenience function to create a Sensor entity.

    Args:
        config: Configuration object
        device: Device instance
        name: Display name for the sensor
        unique_id: Unique identifier for the sensor
        state_topic: MQTT topic where sensor publishes its state
        **kwargs: Additional sensor attributes (value_template, icon, etc.)

    Returns:
        Sensor: Configured sensor entity
    """
    return Sensor(
        config=config,
        device=device,
        name=name,
        unique_id=unique_id,
        state_topic=state_topic,
        entity_category=entity_category,
        availability_mode=availability_mode,
        state_class=state_class,
        **kwargs,
    )


def create_status_sensor(config, device):
    """
    Convenience function to create a StatusSensor.

    Args:
        config: Configuration object
        device: Device instance

    Returns:
        StatusSensor: Configured status sensor
    """
    return StatusSensor(config, device)


def publish_command_buttons(
    config,
    publisher,
    device: Device,
    *,
    base_unique_id: str,
    base_name: str,
    command_topic_base: str,
    buttons: dict[str, str],
) -> list[Button]:
    """Publish HA button discovery entries that mirror command topics.

    buttons: mapping of button_key -> human label (e.g., {"refresh": "Refresh"})
    Returns the created Button entities.
    """
    entities: list[Button] = []
    for key, label in buttons.items():
        unique = f"{base_unique_id}_{key}"
        ent = Button(
            config,
            device,
            name=f"{base_name}: {label}",
            unique_id=unique,
            command_topic=f"{command_topic_base}/{key}",
        )
        publisher.publish(
            topic=ent.get_config_topic(),
            payload=json.dumps(ent.get_config_payload()),
            retain=True,
        )
        entities.append(ent)
    return entities


def purge_legacy_discovery(
    config,
    publisher,
    *,
    topics: list[str],
) -> None:
    """Idempotently clear legacy retained discovery configs by publishing empty payloads."""
    for t in topics:
        try:
            publisher.publish(topic=t, payload="", retain=True)
        except Exception:
            pass
