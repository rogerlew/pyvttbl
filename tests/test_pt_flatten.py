# Copyright (c) 2011-2024, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.

import unittest

from pyvttbl import DataFrame
from pyvttbl.misc.support import *

class Test_pt_flatten(unittest.TestCase):
    def test0(self):
        R =[7.16666666667, 6.5, 4.0, 3.22222222222, 2.88888888889, 1.55555555556]
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])        
        pt_flat = pt.flatten()

        for r,d in zip(R,pt_flat):
            self.assertAlmostEqual(r,d)
        
    def test1(self):
        R =[7.16666666667, 6.5, 4.0, 3.22222222222, 2.88888888889, 1.55555555556]
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', rows=['TIMEOFDAY','COURSE'])        
        pt_flat = pt.flatten()

        for r,d in zip(R,pt_flat):
            self.assertAlmostEqual(r,d)
        
    def test2(self):
        R =[7.16666666667, 6.5, 4.0, 3.22222222222, 2.88888888889, 1.55555555556]
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', cols=['TIMEOFDAY','COURSE'])        
        pt_flat = pt.flatten()

        for r,d in zip(R,pt_flat):
            self.assertAlmostEqual(r,d)
        
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_pt_flatten)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
