from __future__ import print_function

# Copyright (c) 2011, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.

# Python 2 to 3 workarounds
import sys
if sys.version_info[0] == 2:
    _strobj = basestring
    _xrange = xrange
elif sys.version_info[0] == 3:
    _strobj = str
    _xrange = range
    
import unittest
import warnings
import os

import numpy as np

from dictset import DictSet,_rep_generator

from pyvttbl import DataFrame
from pyvttbl.misc.support import *

class Test_insert(unittest.TestCase):
    def test0(self):
        df=DataFrame()
        conditionsDict=DictSet({'A':[10,20,40,80],
                                'B':[100,800],
                              'rep':range(10)})
        for A,B,rep in conditionsDict.unique_combinations():
            df.insert({'A':A, 'B':B,'rep':rep})

        for d,r in zip(df['A'],_rep_generator([10,20,40,80],4,20)):
            self.assertAlmostEqual(d,r)

        for d,r in zip(df['B'],_rep_generator([100,800],8,10)):
            self.assertAlmostEqual(d,r)

        for d,r in zip(df['rep'],_rep_generator(range(10),8,1)):
            self.assertAlmostEqual(d,r)

    def test1(self):
        df=DataFrame()

        with self.assertRaises(Exception) as cm:
            df.insert([1,2,3,4])

        self.assertEqual(str(cm.exception),
                         'row must be mappable type')

    def test2(self):
        df=DataFrame()
        df.insert({'A':1, 'B':2})

        with self.assertRaises(Exception) as cm:
            df.insert({'A':1, 'B':2, 'C':3})

        self.assertEqual(str(cm.exception),
                         'row must have the same keys as the table')
        
    def test3(self):
        df=DataFrame()
        df.insert({'A':1, 'B':2})

        with self.assertRaises(Exception) as cm:
            df.insert({'A':1, 'B':2, 'C':3})

        self.assertEqual(str(cm.exception),
                         'row must have the same keys as the table')

    def test4(self):
        df=DataFrame()
        df.insert([('A',1.23), ('B',2), ('C','A')])
        self.assertEqual(df.types(), ('real', 'integer', 'text'))
        
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_insert)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
