# Copyright (c) 2011-2024, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.

import unittest

import numpy as np
from pyvttbl import DataFrame
from pyvttbl.misc.support import *

class Test_plotHist(unittest.TestCase):
    def test0(self):
        R = {'bins': np.array([ 4, 14, 17, 12, 15, 10,  9,  5,  6,  8]),
             'counts': np.array([  3.,   5.,   7.,   9.,  11.,  13.,  15.,  17.,  19.,  21.,  23.]),
             'fname': 'output\\hist(WORDS).png'}
        df=DataFrame()
        df.TESTMODE=True
        df.read_tbl('data/words~ageXcondition.csv')
        D=df.histogram_plot('WORDS', output_dir='output')

        self.assertEqual(D['fname'],R['fname'])
        
        for d,r in zip(D['bins'].flat,R['bins'].flat):
            self.assertAlmostEqual(d,r)

        for d,r in zip(D['counts'].flat,R['counts'].flat):
            self.assertAlmostEqual(d,r)
            
    def test1(self):
        
        df=DataFrame()
        df.TESTMODE=True
        df.read_tbl('data/words~ageXcondition.csv')
        D=df.histogram_plot('WORDS', cumulative=True, output_dir='output')

        self.assertEqual(D['fname'],'output\\hist(WORDS,cumulative=True).png')
        
            
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_plotHist)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
    
