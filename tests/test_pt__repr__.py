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

class Test_pt__repr__(unittest.TestCase):
    def test0(self):
        
        R = "PyvtTbl([[7.166666666666667, 6.5, 4.0], [3.2222222222222223, 2.888888888888889, 1.5555555555555556]], val='ERROR', row_tots=[5.619047619047619, 2.5555555555555554], col_tots=[4.8, 4.333333333333333, 2.7777777777777777], grand_tot=3.8958333333333335, rnames=[[('TIMEOFDAY', u'T1')], [('TIMEOFDAY', u'T2')]], cnames=[[('COURSE', u'C1')], [('COURSE', u'C2')], [('COURSE', u'C3')]])"
        df=DataFrame()
        df.read_tbl('error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])
        self.assertEqual(repr(pt),R)

    def test1(self):
        
        R = "PyvtTbl([[9.0, 8.666666666666666, 4.666666666666667], [7.5, 6.0, 5.0], [5.0, 3.5, 2.3333333333333335], [4.333333333333333, 3.6666666666666665, 1.6666666666666667], [2.6666666666666665, 2.6666666666666665, 1.6666666666666667], [2.6666666666666665, 2.3333333333333335, 1.3333333333333333]], val='ERROR', row_tots=[7.25, 6.0, 3.4285714285714284, 3.2222222222222223, 2.3333333333333335, 2.111111111111111], col_tots=[4.8, 4.333333333333333, 2.7777777777777777], grand_tot=3.8958333333333335, rnames=[[('TIMEOFDAY', u'T1'), ('MODEL', u'M1')], [('TIMEOFDAY', u'T1'), ('MODEL', u'M2')], [('TIMEOFDAY', u'T1'), ('MODEL', u'M3')], [('TIMEOFDAY', u'T2'), ('MODEL', u'M1')], [('TIMEOFDAY', u'T2'), ('MODEL', u'M2')], [('TIMEOFDAY', u'T2'), ('MODEL', u'M3')]], cnames=[[('COURSE', u'C1')], [('COURSE', u'C2')], [('COURSE', u'C3')]])"
        df=DataFrame()
        df.read_tbl('error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY','MODEL'],['COURSE'])
        self.assertEqual(repr(pt),R)

    def test2(self):
        
        R = "PyvtTbl([[8.0, 8.5, 3.5], [4.0, 3.5, 1.5], [7.0, 6.0, 4.5], [2.0, 2.5, 1.5], [4.0, 3.5, 2.0], [2.5, 2.0, 1.5]], val='ERROR', row_tots=[6.4, 3.0, 5.5, 2.0, 3.0, 2.0], col_tots=[4.0, 4.181818181818182, 2.4166666666666665], grand_tot=3.46875, rnames=[[('MODEL', u'M1'), ('TIMEOFDAY', u'T1')], [('MODEL', u'M1'), ('TIMEOFDAY', u'T2')], [('MODEL', u'M2'), ('TIMEOFDAY', u'T1')], [('MODEL', u'M2'), ('TIMEOFDAY', u'T2')], [('MODEL', u'M3'), ('TIMEOFDAY', u'T1')], [('MODEL', u'M3'), ('TIMEOFDAY', u'T2')]], cnames=[[('COURSE', u'C1')], [('COURSE', u'C2')], [('COURSE', u'C3')]], where=['SUBJECT != 1'])"

        df=DataFrame()
        df.read_tbl('error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['MODEL','TIMEOFDAY'],['COURSE'],where=['SUBJECT != 1'])
        self.assertEqual(repr(pt),R)
        
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_pt__repr__)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
