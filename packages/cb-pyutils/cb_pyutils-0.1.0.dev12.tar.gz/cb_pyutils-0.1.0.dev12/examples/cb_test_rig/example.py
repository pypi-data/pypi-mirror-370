#!/usr/bin/env python3

import time
from key_stroke import Key_Stroke

from cb_test_rig import TestRigStatus
from cb_test_rig import TestRigStatusClient
from cb_test_rig import TestRigConfig


def main():
    # configuration
    cfg = TestRigConfig(test_name='example')

    # Create the test rig status client
    test_rig = TestRigStatusClient(test_config=cfg,
                                   verbose=True)

    # toggle all test statuses
    for status in TestRigStatus.list():
        test_rig.publish_status(status)
        time.sleep(1)

    # run the test rig status randomly
    k = Key_Stroke()
    print('Press ESC to terminate!')
    while True:
        test_rig.publish_random_status_for_testing()

        # check whether a key from the list has been pressed
        if k.check(['\x1b', 'q', 'x']):
            break

        time.sleep(1)

    test_rig.close()


if __name__ == '__main__':
    main()
