#!/usr/bin/env python

import unittest
#import TestBabyGPT
import TestDecoderInstall

class babyGPTInstallTestCase( unittest.TestCase ):
    def checkVersion(self):
        import babyGPT

testSuites = [unittest.makeSuite(babyGPTInstallTestCase, 'test')] 

for test_type in [
            TestDecoderInstall,
    ]:
    testSuites.append(test_type.getTestSuites('test'))


def getTestDirectory():
    try:
        return os.path.abspath(os.path.dirname(__file__))
    except:
        return '.'

import os
os.chdir(getTestDirectory())

runner = unittest.TextTestRunner()
runner.run(unittest.TestSuite(testSuites))
