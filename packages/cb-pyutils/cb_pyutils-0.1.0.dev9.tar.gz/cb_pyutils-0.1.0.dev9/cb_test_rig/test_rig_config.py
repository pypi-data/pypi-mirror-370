

class TestRigConfig():
    def __init__(self, mqtt_broker='localhost', mqtt_broker_port=1883,
                 test_name=''):
        self.mqtt_broker = mqtt_broker
        self.mqtt_broker_port = mqtt_broker_port

        self.test_name = test_name

        self.mqtt_topic_base = '$TESTING/'  # Subscribe to all testing topics

        self.mqtt_subscribe_topic = self.mqtt_topic_base + '#'

        self.mqtt_status_topic = self.mqtt_topic_base + \
            f'{self.test_name}/' + \
            'status'
