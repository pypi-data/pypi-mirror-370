import yaml


class MQTTConfig:
    """
    MQTT configuration builder and validator utility.

    Provides convenient methods to build and validate MQTT configuration
    dictionaries with proper type conversion and validation.
    """

    @staticmethod
    def build_config(**kwargs) -> dict:
        """Build and validate complete MQTT configuration with defaults.

        Args:
            broker_url: MQTT broker URL (required)
            broker_port: MQTT broker port (default: 1883)
            client_id: MQTT client ID (default: "mqtt_client")
            security: Security mode (default: "none")
            username: Username for authentication
            password: Password for authentication
            tls: TLS configuration dictionary
            max_retries: Maximum connection retries (default: 3)
            last_will: Last Will and Testament configuration
            default_qos: Default QoS level for publish operations (default: 0)
            default_retain: Default retain flag for publish operations (default: False)
            logging_config: Enhanced logging configuration dictionary

        Returns:
            Complete MQTT configuration dictionary

        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Handle port conversion with proper defaults
        broker_port = kwargs.get("broker_port")
        if broker_port is None:
            broker_port = 1883
        else:
            broker_port = int(broker_port)

        # Handle max_retries conversion with proper defaults
        max_retries = kwargs.get("max_retries")
        if max_retries is None:
            max_retries = 3
        else:
            max_retries = int(max_retries)

        # Handle default_qos conversion with proper defaults
        default_qos = kwargs.get("default_qos")
        if default_qos is None:
            default_qos = 0
        else:
            default_qos = int(default_qos)
            if not (0 <= default_qos <= 2):
                raise ValueError(f"default_qos must be 0, 1, or 2, got: {default_qos}")

        # Handle default_retain conversion with proper defaults
        default_retain = kwargs.get("default_retain", False)
        if isinstance(default_retain, str):
            default_retain = default_retain.lower() in ("true", "1", "yes", "on")

        config = {
            "broker_url": kwargs.get("broker_url"),
            "broker_port": broker_port,
            "client_id": kwargs.get("client_id") or "mqtt_client",
            "security": kwargs.get("security") or "none",
            "max_retries": max_retries,
            "default_qos": default_qos,
            "default_retain": default_retain,
        }

        # Handle authentication
        username = kwargs.get("username")
        password = kwargs.get("password")
        if username or password:
            config["auth"] = {
                "username": username,
                "password": password,
            }

        # Handle TLS configuration
        tls = kwargs.get("tls")
        if tls:
            config["tls"] = tls

        # Handle Last Will and Testament
        last_will = kwargs.get("last_will")
        if last_will:
            config["last_will"] = last_will

        # Handle logging configuration
        logging_config = kwargs.get("logging_config")
        if logging_config:
            config["logging_config"] = logging_config

        # Validate required fields
        if not config["broker_url"]:
            raise ValueError("broker_url is required")

        return config

    @staticmethod
    def from_dict(config_dict: dict) -> dict:
        """Build MQTT config from nested dictionary (like YAML config).

        Args:
            config_dict: Nested configuration dictionary with 'mqtt' section

        Returns:
            Complete MQTT configuration dictionary suitable for MQTTPublisher

        Example:
            config_dict = {
                "mqtt": {
                    "broker_url": "mqtt.example.com",
                    "broker_port": 8883,
                    "client_id": "my_client",
                    "security": "username",
                    "auth": {
                        "username": "user",
                        "password": "pass"
                    },
                    "tls": {
                        "verify": True
                    }
                }
            }
            mqtt_config = MQTTConfig.from_dict(config_dict)
        """
        mqtt_section = config_dict.get("mqtt", {})
        auth_section = mqtt_section.get("auth", {})

        return MQTTConfig.build_config(
            broker_url=mqtt_section.get("broker_url"),
            broker_port=mqtt_section.get("broker_port"),
            client_id=mqtt_section.get("client_id"),
            security=mqtt_section.get("security"),
            username=auth_section.get("username"),
            password=auth_section.get("password"),
            tls=mqtt_section.get("tls"),
            max_retries=mqtt_section.get("max_retries"),
            last_will=mqtt_section.get("last_will"),
            default_qos=mqtt_section.get("default_qos"),
            default_retain=mqtt_section.get("default_retain"),
            logging_config=mqtt_section.get("logging_config"),
        )

    @staticmethod
    def from_mapping(mapping: dict, *, section: str = "mqtt") -> dict:
        """Build config from a flat or nested mapping.

        Supports keys like 'mqtt.broker_url' or nested mapping under 'mqtt'.
        """

        def _get(key: str, default=None):
            if f"{section}.{key}" in mapping:
                return mapping.get(f"{section}.{key}")
            if section in mapping and isinstance(mapping[section], dict):
                return mapping[section].get(key, default)
            return mapping.get(key, default)

        auth = _get("auth") or {}
        return MQTTConfig.build_config(
            broker_url=_get("broker_url"),
            broker_port=_get("broker_port"),
            client_id=_get("client_id"),
            security=_get("security"),
            username=auth.get("username") or _get("username"),
            password=auth.get("password") or _get("password"),
            tls=_get("tls"),
            max_retries=_get("max_retries"),
            last_will=_get("last_will"),
            default_qos=_get("default_qos"),
            default_retain=_get("default_retain"),
            logging_config=_get("logging_config"),
        )

    @staticmethod
    def to_publisher_kwargs(config: dict) -> dict:
        """Convert validated config dict to kwargs for MQTTPublisher."""
        out = {
            "broker_url": config.get("broker_url"),
            "broker_port": config.get("broker_port"),
            "client_id": config.get("client_id"),
            "security": config.get("security"),
            "auth": config.get("auth"),
            "tls": config.get("tls"),
            "max_retries": config.get("max_retries"),
            "last_will": config.get("last_will"),
            "default_qos": config.get("default_qos"),
            "default_retain": config.get("default_retain"),
            "logging_config": config.get("logging_config"),
        }
        return out

    @staticmethod
    def validate_config(config: dict) -> None:
        """Validate an MQTT configuration dictionary.

        Args:
            config: MQTT configuration dictionary to validate

        Raises:
            ValueError: If configuration is invalid with detailed error messages
        """
        errors = []

        # Check required fields
        if not config.get("broker_url"):
            errors.append("broker_url is required")

        # Validate port
        broker_port = config.get("broker_port")
        if not isinstance(broker_port, int) or not (1 <= broker_port <= 65535):
            errors.append(f"broker_port must be integer 1-65535, got: {broker_port}")

        # Validate client_id
        if not config.get("client_id"):
            errors.append("client_id is required")

        # Validate security-specific requirements
        security = config.get("security", "none")
        if security in ["username", "tls", "tls_with_client_cert"]:
            auth = config.get("auth", {})
            if not (auth.get("username") and auth.get("password")):
                errors.append(
                    f"username and password required when security='{security}'"
                )

        if security in ["tls", "tls_with_client_cert"]:
            if not config.get("tls"):
                errors.append(f"TLS configuration required when security='{security}'")
            elif security == "tls_with_client_cert":
                tls = config.get("tls", {})
                if not all(tls.get(key) for key in ["client_cert", "client_key"]):
                    errors.append(
                        "client_cert and client_key required for tls_with_client_cert"
                    )

        # Configuration consistency warnings
        tls = config.get("tls")
        if tls and broker_port == 1883:
            errors.append(
                "Warning: TLS enabled but using non-TLS port 1883. Consider port 8883 for TLS"
            )

        if not tls and broker_port == 8883:
            errors.append(
                "Warning: TLS disabled but using TLS port 8883. Consider port 1883 for non-TLS"
            )

        if errors:
            raise ValueError(
                "MQTT configuration errors:\n"
                + "\n".join(f"- {error}" for error in errors)
            )


class Config:
    """
    Enhanced configuration class with support for nested key access.

    Supports both dot notation (config.get("mqtt.broker_url")) and
    underscore notation (config.mqtt_broker_url) for accessing nested values.
    """

    def __init__(self, config_path):
        with open(config_path) as config_file:
            self.config = yaml.safe_load(config_file)

    def __getattr__(self, name):
        # First try to get directly from top level
        if name in self.config:
            return self.config[name]

        # If not found, try nested dictionary lookup
        keys = name.split("_")
        value = self.config
        for key in keys:
            if not isinstance(value, dict) or key not in value:
                raise AttributeError(f"Configuration key '{name}' not found")
            value = value[key]
        return value

    def get(self, name, default=None):
        """
        Get configuration value with optional default.

        Supports dot notation: config.get("mqtt.broker_url")
        And underscore notation: config.get("mqtt_broker_url")

        Args:
            name: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        try:
            # Try dot notation first
            if "." in name:
                keys = name.split(".")
                value = self.config
                for key in keys:
                    if not isinstance(value, dict) or key not in value:
                        return default
                    value = value[key]
                return value
            # Fall back to underscore notation
            return self.__getattr__(name)
        except AttributeError:
            return default
