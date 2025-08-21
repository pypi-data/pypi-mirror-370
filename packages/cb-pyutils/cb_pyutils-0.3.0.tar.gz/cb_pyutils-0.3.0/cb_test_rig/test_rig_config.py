import configparser

CONFIG_FILE_NAME = 'test_rig.conf'


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

    def read_config(self, conf_file_name=CONFIG_FILE_NAME):
        config = configparser.ConfigParser()

        config.read(conf_file_name)

        self.mqtt_broker = config.get(
            'MQTT-BROKER', 'host', fallback=self.mqtt_broker)
        self.mqtt_broker_port = config.getint(
            'MQTT-BROKER', 'port', fallback=self.mqtt_broker_port)

    def write_config(self, conf_file_name=CONFIG_FILE_NAME):
        config = configparser.ConfigParser()

        config['MQTT-BROKER'] = {'host': self.mqtt_broker,
                                 'port': str(self.mqtt_broker_port)}

        config['TEST'] = {'name': self.test_name}

        with open(conf_file_name, 'w') as configfile:
            config.write(configfile)


def write_base_config():
    config = configparser.ConfigParser()
    config['MQTT-BROKER'] = {'host': 'localhost',
                             'port': '1883'}

    with open(CONFIG_FILE_NAME, 'w') as configfile:
        config.write(configfile)
