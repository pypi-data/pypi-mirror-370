
import random
import paho.mqtt.client as client

from cb_test_rig.test_rig_status import TestRigStatus
from cb_test_rig.test_rig_config import TestRigConfig


class TestRigStatusClient():
    def __init__(self,
                 test_config=None,
                 on_message_callback=None,
                 verbose=False):

        self.cfg = test_config if test_config else TestRigConfig(
            test_name='Default_Test')

        self.on_message_callback = on_message_callback
        self.verbose = verbose

        if self.verbose:
            print(
                'Connecting to MQTT broker at ',
                f'{self.cfg.mqtt_broker}:{self.cfg.mqtt_broker_port}...')

        self.mqtt_client = self.connect_to_mqtt_server()
        self.mqtt_client.loop_start()

    def close(self):
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        if self.verbose:
            print("Disconnected from MQTT broker.")

    def connect_to_mqtt_server(self):
        def on_connect(client, userdata, flags, reason_code, properties):
            if self.verbose:
                print(f"Connected with result code {reason_code}")
            # Subscribing in on_connect() means that if we lose the
            # connection and reconnect then subscriptions will be renewed.
            client.subscribe(self.cfg.mqtt_subscribe_topic)

        def on_message(client, userdata, msg):
            if self.verbose:
                print(f'Received message {msg.topic}: {msg.payload}')

        mqttc = client.Client(client.CallbackAPIVersion.VERSION2)
        mqttc.on_connect = on_connect

        # connect the on_message callback
        if self.on_message_callback is not None:
            mqttc.on_message = self.on_message_callback
        else:
            mqttc.on_message = on_message

        # finally connect to the MQTT broker
        mqttc.connect(self.cfg.mqtt_broker, self.cfg.mqtt_broker_port)

        return mqttc

    def publish_status(self, status: TestRigStatus):
        msg = f'{status}'
        result = self.mqtt_client.publish(self.cfg.mqtt_status_topic, msg)
        if result[0] == 0:
            if self.verbose:
                print(f"Send `{msg}` to topic `{self.cfg.mqtt_status_topic}`")
        else:
            print('Failed to send message to topic ',
                  f'{self.cfg.mqtt_status_topic}')
            print(f"Result: {result}")

    def publish_random_status_for_testing(self):
        """Publish a random status for testing purposes."""
        status = random.choice(TestRigStatus.list())  # nosec -  B311

        self.publish_status(status)

        return status
