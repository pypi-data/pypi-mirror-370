#!/usr/bin/env python3

import sys
import time
import argparse
import socket
from ping3 import ping
from cb_logging import CBLogger
from cb_test_rig import TestRigStatusClient
from cb_test_rig import TestRigStatus
from cb_test_rig import TestRigConfig
from key_stroke import KeyStroke

# Default values
DEFAULT_HOST = '192.168.55.100'
DEFAULT_INTERVAL = 0.1
DEFAULT_TIMEOUT = 3
DEFAULT_SIZE = 64
TTL = 64
LOG_FILE_NAME = 'cb_pingy.log'


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Special ping utility for emc testing')
    parser.add_argument('host',
                        help='Target host to ping')
    parser.add_argument('--interval', '-i',
                        type=float, default=DEFAULT_INTERVAL,
                        help=f'Interval between pings in seconds (default: {DEFAULT_INTERVAL})')  # noqa: E501
    parser.add_argument('--timeout', '-t',
                        type=float, default=DEFAULT_TIMEOUT,
                        help=f'Timeout for each ping in seconds (default: {DEFAULT_TIMEOUT})')  # noqa: E501
    parser.add_argument('--size', '-s',
                        type=int, default=DEFAULT_SIZE,
                        help=f'Packet size in bytes (default: {DEFAULT_SIZE})')  # noqa: E501
    parser.add_argument('--log', '-l',
                        action='store_true',
                        help=f'Enable logging to file ({LOG_FILE_NAME})')
    return parser.parse_args()


def main():
    args = parse_arguments()

    host = args.host
    interval = args.interval
    timeout = args.timeout
    size = args.size
    ttl = TTL
    do_log = args.log

    # Set up logging
    log = CBLogger(do_file_logging=do_log,
                   log_file_name=LOG_FILE_NAME)

    log.info(f'Start pinging {host}')
    log.info(f'Interval: {interval} s, '
             f'Timeout: {timeout} s, '
             f'Data Size: {size} bytes')

    ip_addr = socket.gethostbyname(host)
    if host != ip_addr:
        host_display = f'{host} ({ip_addr})'
    else:
        host_display = host

    cfg = TestRigConfig(test_name='cb_pingy')
    cfg.read_config()

    c = TestRigStatusClient(test_config=cfg)

    c.publish_status(TestRigStatus.CLEAR)

    print('\nPress ESC to terminate! \n')
    k = KeyStroke()

    while True:
        try:
            ret = ping(ip_addr,
                       unit='ms',
                       timeout=timeout,
                       size=size,
                       ttl=ttl)
        except PermissionError as e:
            c.publish_status(TestRigStatus.FAIL)
            log.error(f'{e}')
            print('On Linux, you need to run this script with root privileges to allow pinging.')  # noqa: E501
            print('You can use "sudo" to run this script with root privileges.')  # noqa: E501
            print('If you want to allow all users to create ICMP sockets, you can set the sysctl parameter:')  # noqa: E501
            print('To permanently set this parameter by adding it to /etc/sysctl.conf:')   # noqa: E501
            print('echo -e "# allow all users to create icmp sockets\\nnet.ipv4.ping_group_range=0 2147483647" | sudo tee -a /etc/sysctl.conf')  # noqa: E501
            sys.exit(-e.errno)
        except Exception as e:
            c.publish_status(TestRigStatus.FAIL)
            log.error(f'undefined error occured: {e}')
            break

        if isinstance(ret, float):
            c.publish_status(TestRigStatus.PASS)
            log.info(
                f'ping to {host_display} successful. '
                f'Round trip time: {ret:8.3f} ms')
        elif isinstance(ret, bool):
            c.publish_status(TestRigStatus.WARNING)
            log.warning(f'Host unknown (cannot resolve): {host_display}')
            break
        elif ret is None:
            c.publish_status(TestRigStatus.FAIL)
            log.error('ping timed out!')
        else:
            c.publish_status(TestRigStatus.FAIL)
            log.error(f'undefined return value: {ret}!')
            break

        time.sleep(interval)

        # check whether a key from the list has been pressed
        if k.check(['\x1b', 'q', 'x']):
            break

    c.close()

    log.info('Ping test completed.')


if __name__ == '__main__':
    main()
