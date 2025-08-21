# home_assistant_mqtt/discovery.py

from ha_mqtt_publisher.publisher import MQTTPublisher


class HomeAssistantMQTTDiscovery:
    def __init__(self, mqtt_config):
        self.publisher = MQTTPublisher(**mqtt_config)

    def publish_discovery_message(self, topic, payload):
        if self.publisher.connect():
            self.publisher.publish(topic, payload)
            self.publisher.disconnect()
