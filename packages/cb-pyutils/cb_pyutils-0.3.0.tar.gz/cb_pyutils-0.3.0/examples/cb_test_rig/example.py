#!/usr/bin/env python3

import time
from key_stroke import KeyStroke

from cb_test_rig import TestRigStatus
from cb_test_rig import TestRigStatusClient
from cb_test_rig import TestRigConfig


def main():
    # configuration
    cfg = TestRigConfig(test_name='example')
    cfg.read_config()

    # Create the test rig status client
    test_rig = TestRigStatusClient(test_config=cfg,
                                   verbose=False)

    # toggle all test statuses
    print('Publishing all test statuses:')
    for status in TestRigStatus.list():
        print(f'Publishing status: {status.name}')
        test_rig.publish_status(status)
        time.sleep(1)

    # run the test rig status randomly
    print('Publishing test statuses randomly:')
    k = KeyStroke()
    print('Press ESC to terminate!')
    while True:
        status = test_rig.publish_random_status_for_testing()
        print(f'Publishing status: {status.name}')

        # check whether a key from the list has been pressed
        if k.check(['\x1b', 'q', 'x']):
            break

        time.sleep(1)

    test_rig.close()


if __name__ == '__main__':
    main()
