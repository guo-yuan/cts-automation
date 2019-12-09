#!/usr/bin/env python3

"""
CTS GW provisioning test.

Usage:
    python(python3) gw_provision.py <test_case>
"""

import sys, os, time, json, datetime, logging
import unittest
import cpeTest
from pyHS100 import SmartPlug
from test_config import *

if __name__ == "__main__":
    logger = logging.getLogger("GW Test")
else:
    logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt='%d-%b-%y %H:%M:%S')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

#logging.basicConfig(format='%(asctime)s CTS Test: %(message)s', level=logging.INFO, datefmt='%d-%b-%y %H:%M:%S')

def basic_test():
    """ Execute a basic provisioning test.

    Args: none
    Returns: none
    """

    global report
    report['case'] = 'basic'

    logger.info('Step 1 - toggle DUT power...')
    p = SmartPlug(smart_plug_ip)
    try:
#        p.state = 'OFF'
        time.sleep(3)
#        p.state = 'ON'
    except Exception:
        logger.info('Fail to toggle DUT power.')
        report['result'] = 'Aborted'
        report['reason'] = 'Fail to toggle DUT power'
        return

    # time.sleep(120)
    logger.info('Wait and allow DUT to boot...')

    logger.info('Step 2 - GW controller action...')
    shell_cmd = 'cd %s; %s %s H1.1 xDSL1 on' % (gw_controller_dir, gw_controller_exe, gw_controller_ip)
    logger.info(shell_cmd)
#    ret = os.system(shell_cmd)
#    if ret != 0:
#        logger.info('Fail to run GW controller.')
#        report['result'] = 'Aborted'
#        report['reason'] = 'Fail to run GW controller'
#        return

    # time.sleep(120)
    logger.info('Wait and allow DUT WAN connection to connect...')

    logger.info('Step 3 - Check Internet connection on a CPE connected to DUT...')
    try:
        cpeTest.clientInit(cpeTest.checkOutcome)
        cpeTest.requestTest("8.8.8.8")
        cpeTest.testConcluded.wait(timeout=10)
    except Exception:
        logger.info('Fail to initiate CPE connectivity test.')
        report['result'] = 'Failed'
        report['reason'] = 'Fail to initiate CPE connectivity test'
        return

    if not cpeTest.testSucceed:
        report['result'] = 'Failed'
        report['reason'] = 'CPE device has no Internet connectivity.'
        return False

    report['result'] = 'Success'
    return True


def run_test(case):
    """
    Main entry for GW provisioning tests.

    Args: case: test case selection
    Return: True if test case pass 
    """
    global report
    report = {'case': '', 'result': '', 'reason': '', 'timestamp': ''}
    result = False

    if 'basic' == case:
        print('Run basic test...')
        result = basic_test()
    elif 'Telstra' == case:
        logger.info('Test case %s to be supported.' % case)
    else:
        logger.info('Test scenario %s is invalid. Please use scenario: [Basic|Telstra].' % case)

    print('Test report: ', report)
    return result


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('No test case specified. Available cases: basic, Telstra.')
        sys.argv.append('basic')

    run_test(sys.argv[1])
    test_timestamp = str(datetime.datetime.now())
    report['timestamp'] = test_timestamp
    json_report = json.dumps(report, indent=4, separators=(', ', ': '))
    logger.info(json_report)

    fh = open('gw_provision_report.txt', 'w')
    fh.write('GW provisioning test report generated at ' + test_timestamp + '\n\n')
    fh.write(json_report)
    fh.close()
