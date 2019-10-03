#!/usr/bin/env python

"""
CTS GW provisioning test.

Usage:
    python(python3) gw_provision.py <test_case>
"""

import sys, os, time
from pyHS100 import SmartPlug
from test_config import *


def basic_test():
    """ Execute a basic provisioning test.

    Args: none
    Returns: none
    """
    print('Step 1: power off DUT')
    p = SmartPlug(smart_plug_ip)
    #p.state = 'OFF'
    time.sleep(3)

    print('Step 2: power on DUT')
    #p.state = 'ON'
    #time.sleep(120)

    print('Step 3: GW controller action')
    shell_cmd = 'cd %s; %s %s H1.1 xDSL1 on' % (gw_controller_dir, gw_controller_exe, gw_controller_ip)
    print(shell_cmd)
    #os.system(shell_cmd)
    #time.sleep(120)

    print('Step 4: Run speed test')
    shell_cmd = 'cd %s; %s' % (speed_test_dir, speed_test_cmd)
    print(shell_cmd)
    #os.system(shell_cmd)
    #time.sleep(60)

    print('Test completed')


def run_test(case):
    """
    Main entry for GW provisioning tests.

    :param test: test case selection
    :return: none
    """
    if 'basic' == case:
        print('Run basic test')
        basic_test()
    elif 'Telstra' == case:
        print('Test case to be done')
    else:
        print('Test case', case, 'is not defined')


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('No test case specified.')
        exit(0)
    run_test(sys.argv[1])