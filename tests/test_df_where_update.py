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

from pyvttbl import DataFrame
from pyvttbl.misc.support import *

class Test_where_update(unittest.TestCase):
    def test0(self):
        df=DataFrame()
        df.read_tbl('error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        df.where_update('ERROR = 10')
        self.assertEqual(repr(df),"DataFrame([(('SUBJECT', 'integer'), [1, 2]), (('TIMEOFDAY', 'text'), [u'T1', u'T1']), (('COURSE', 'text'), [u'C1', u'C2']), (('MODEL', 'text'), [u'M1', u'M1']), (('ERROR', 'integer'), [10, 10])])")

    def test1(self):
        df=DataFrame()
        df.read_tbl('error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        df.where_update(['ERROR = 10'])
        self.assertEqual(repr(df),"DataFrame([(('SUBJECT', 'integer'), [1, 2]), (('TIMEOFDAY', 'text'), [u'T1', u'T1']), (('COURSE', 'text'), [u'C1', u'C2']), (('MODEL', 'text'), [u'M1', u'M1']), (('ERROR', 'integer'), [10, 10])])")

    def test2(self):
        df=DataFrame()
        df.read_tbl('error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        df.where_update([('ERROR', '=', 10)])
        self.assertEqual(repr(df),"DataFrame([(('SUBJECT', 'integer'), [1, 2]), (('TIMEOFDAY', 'text'), [u'T1', u'T1']), (('COURSE', 'text'), [u'C1', u'C2']), (('MODEL', 'text'), [u'M1', u'M1']), (('ERROR', 'integer'), [10, 10])])")

    def test3(self):
        df=DataFrame()
        df.read_tbl('error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        df.where_update('COURSE = "C1" and TIMEOFDAY in ("T1", "T2")')
        self.assertEqual(repr(df),"DataFrame([(('SUBJECT', 'integer'), [1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 3, 3]), (('TIMEOFDAY', 'text'), [u'T1', u'T1', u'T1', u'T2', u'T2', u'T2', u'T2', u'T2', u'T2', u'T1', u'T1', u'T1', u'T2', u'T2', u'T2']), (('COURSE', 'text'), [u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1']), (('MODEL', 'text'), [u'M1', u'M2', u'M3', u'M1', u'M2', u'M3', u'M1', u'M2', u'M3', u'M1', u'M2', u'M3', u'M1', u'M2', u'M3']), (('ERROR', 'integer'), [10, 8, 6, 5, 4, 3, 4, 3, 3, 8, 7, 4, 4, 1, 2])])")

    def test5(self):
        df=DataFrame()
        df.read_tbl('error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        df.where_update(['COURSE = "C1"','TIMEOFDAY in ("T1", "T2")'])
        self.assertEqual(repr(df),"DataFrame([(('SUBJECT', 'integer'), [1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 3, 3]), (('TIMEOFDAY', 'text'), [u'T1', u'T1', u'T1', u'T2', u'T2', u'T2', u'T2', u'T2', u'T2', u'T1', u'T1', u'T1', u'T2', u'T2', u'T2']), (('COURSE', 'text'), [u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1']), (('MODEL', 'text'), [u'M1', u'M2', u'M3', u'M1', u'M2', u'M3', u'M1', u'M2', u'M3', u'M1', u'M2', u'M3', u'M1', u'M2', u'M3']), (('ERROR', 'integer'), [10, 8, 6, 5, 4, 3, 4, 3, 3, 8, 7, 4, 4, 1, 2])])")

    def test6(self):
        df=DataFrame()
        df.read_tbl('error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        df.where_update([('COURSE','=',['C1']),('TIMEOFDAY','in',["T1", "T2"])])
        self.assertEqual(repr(df),"DataFrame([(('SUBJECT', 'integer'), [1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 3, 3]), (('TIMEOFDAY', 'text'), [u'T1', u'T1', u'T1', u'T2', u'T2', u'T2', u'T2', u'T2', u'T2', u'T1', u'T1', u'T1', u'T2', u'T2', u'T2']), (('COURSE', 'text'), [u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1']), (('MODEL', 'text'), [u'M1', u'M2', u'M3', u'M1', u'M2', u'M3', u'M1', u'M2', u'M3', u'M1', u'M2', u'M3', u'M1', u'M2', u'M3']), (('ERROR', 'integer'), [10, 8, 6, 5, 4, 3, 4, 3, 3, 8, 7, 4, 4, 1, 2])])")

        
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_where_update)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
