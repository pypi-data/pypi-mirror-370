#!/usr/bin/env python3

import sys
import time

from busylight_core import KuandoLights
from busylight_core.exceptions import NoLightsFoundError

from key_stroke import KeyStroke

from cb_test_rig import TestRigStatusClient
from cb_test_rig import TestRigStatus
from cb_test_rig import TestRigConfig

cfg = TestRigConfig(test_name = 'cb_test_rig_lighthouse')
cfg.read_config()

verbose = False  # Set to True to enable verbose output

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    msg_payload = msg.payload.decode('utf-8')

    topic_base = msg.topic.split('/')[0]
    test_name = msg.topic.split('/')[1]
    test_topic = msg.topic.split('/')[2]


    if topic_base in cfg.mqtt_topic_base and test_topic == 'status':

        try:
            # Convert string to TestRigStatus enum
            rx_status = TestRigStatus[msg_payload.replace('TestRigStatus.', '')]
        except KeyError:
            print(f"ERROR: Invalid status message: {msg_payload}")
            rx_status = TestRigStatus.IDLE  # Reset to undefined status
            return

        if userdata.value.rank <= rx_status.value.rank:
            if userdata.name != rx_status.name:
                print(f'current status: {userdata.name}, received status: {test_name}/{rx_status.name}')
            userdata = rx_status
        elif rx_status == TestRigStatus.CLEAR:
            print(f'current status: {userdata.name}, received status: {test_name}/{rx_status.name}, resetting to CLEAR.')
            userdata = TestRigStatus.CLEAR
        else:
            print(f"Info: Received status {test_name} {rx_status.name} with lower rank than current status {userdata.name}, ignoring.")

        client.user_data_set(userdata)


def main():
    # Get first Kuando device
    try:
        light = KuandoLights.first_light()
    except NoLightsFoundError:
        print("No lighthouse devices found")
        sys.exit(-1)


    light.off()  # Turn off the light

    status = TestRigStatus.IDLE  # Default status

    cbtc = TestRigStatusClient(test_config=cfg,
                               on_message_callback=on_message,
                               verbose=verbose)

    cbtc.mqtt_client.user_data_set(status)

    k = KeyStroke()
    print('Press ESC to terminate!')

    while True:
        status = cbtc.mqtt_client.user_data_get()
        light.on(status.value.color)

        # check whether a key from the list has been pressed
        if k.check(['\x1b', 'q', 'x']):
            break

        time.sleep(0.1)


    cbtc.close()
    light.off()  # Turn off the light


if __name__ == '__main__':
    main()