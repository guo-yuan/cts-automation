#!/usr/bin/env python

"""
CTS GW provisioning test.

Usage:
    python(python3) gw_provision.py <test_case>
"""

import sys, os, time, json, datetime
# import paramiko
from pyHS100 import SmartPlug
from test_config import *

report = {'case': '', 'result': '', 'reason': '', 'timestamp': ''}


def basic_test():
    """ Execute a basic provisioning test.

    Args: none
    Returns: none
    """

    global report
    report['case'] = 'basic'

    print('Step 1: toggle DUT power')
    p = SmartPlug(smart_plug_ip)
    try:
        p.state = 'OFF'
        time.sleep(3)
        p.state = 'ON'
    except Exception:
        print('Fail to toggle DUT power')
        report['result'] = 'Aborted'
        report['reason'] = 'Fail to toggle DUT power'
        return

    # time.sleep(120)
    print('Wait and allow DUT to boot')

    print('Step 2: GW controller action')
    shell_cmd = 'cd %s; %s %s H1.1 xDSL1 on' % (gw_controller_dir, gw_controller_exe, gw_controller_ip)
    print(shell_cmd)
    ret = os.system(shell_cmd)
    if ret != 0:
        print('Fail to run GW controller')
        report['result'] = 'Aborted'
        report['reason'] = 'Fail to run GW controller'
        return

    # time.sleep(120)
    print('Wait and allow DUT WAN connection to connect')

    print('Step 3: Check Internet connection on a CPE connected to DUT')
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(cpe_ip, username=cpe_ssh_username, password=cpe_ssh_passwd)
    except Exception:
        print('Fail to connect to test CPE')
        report['result'] = 'Failed'
        report['reason'] = 'Fail to connect test CPE'
        return

    shell_cmd = 'ping 8.8.8.8 -c 5'
    _, ssh_stdout, _ = ssh.exec_command(shell_cmd)
    if ssh_stdout.find('0% packet loss') == -1:
        print('Fail to ping Internet from test CPE')
        report['result'] = 'Failed'
        report['reason'] = 'Fail to ping Internet from test CPE'
        return

    print('Test successfully completed')
    report['result'] = 'Success'


def run_test(case):
    """
    Main entry for GW provisioning tests.

    :param case: test case selection
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
    test_timestamp = str(datetime.datetime.now())
    report['timestamp'] = test_timestamp
    json_report = json.dumps(report, indent=4, separators=(', ', ': '))
    print(json_report)

    fh = open('gw_provision_report.txt', 'w')
    fh.write('GW provisioning test report generated at ' + test_timestamp + '\n\n')
    fh.write(json_report)
    fh.close()
