#!/usr/bin/env python3

import time
# import random
# import paho.mqtt.client as mqttc
from key_stroke import KeyStroke


from cb_test_rig import TestRigStatus
from cb_test_rig import TestRigStatusClient
from cb_test_rig import TestRigConfig

cfg = TestRigConfig(test_name='cb_test_rig_pub')

def main():
    c = TestRigStatusClient(test_config=cfg)

    k = KeyStroke()
    print('Press ESC to terminate!')
    while True:
        # c.publish_random_status_for_testing()

        for status in TestRigStatus.list():
            print(f'Publishing status: {status}')
            c.publish_status(status)
            time.sleep(1)


        # check whether a key from the list has been pressed
        if k.check(['\x1b', 'q', 'x']):
            break

        time.sleep(1)


    c.close()


if __name__ == '__main__':
    main()