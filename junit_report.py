#!/usr/bin/env python

"""
Run tests and generate JUnit formatted test report for gw provisioning tests
"""
import unittest
import xmlrunner
import gw_provision as t
from test_config import *


class GwTestCases(unittest.TestCase):
    def test_basic(self):
        self.assertTrue(t.run_test('basic'), msg='Basic provisioning test failed')

    @unittest.skip('Test scenario not supported yet')
    def test_Telstra(self):
        self.assertTrue(t.run_test('Telstra'), msg='Telstra provsioning test failed')

    @unittest.expectedFailure
    def test_other(self):
        self.assertTrue(t.run_test('other'), msg='Other provisioning test failed')


if __name__ == '__main__':
    test_runner = xmlrunner.XMLTestRunner(output=xml_report_dir)
    unittest.main(testRunner=test_runner)
