# Copyright (C) 2024 Gilles Degottex <contact@pitchmeld.ing> All Rights Reserved.

import unittest

import sys
import os

sys.path.append(os.path.dirname(__file__)+'/../..') # Ensure this package is being tested
import pitchmeld.tests.nolicense_test as nolicense_test
import pitchmeld.tests.license_test as license_test

def run():
    testSuite = unittest.TestSuite()
    testLoader = unittest.TestLoader()
    testSuite.addTest(testLoader.loadTestsFromModule(nolicense_test))
    testSuite.addTest(testLoader.loadTestsFromModule(license_test))

    testRunner = unittest.runner.TextTestRunner(verbosity=3)
    ret = testRunner.run(testSuite)
    assert len(ret.failures) == 0
