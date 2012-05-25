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
from pyvttbl.plotting import scatter_matrix
from pyvttbl.misc.support import *

class Test_scatter_matrix(unittest.TestCase):
    def setUp(self):
        self.df = DataFrame()
        self.df.read_tbl('iqbrainsize.txt', delimiter='\t')
        self.df['TOTSA'] = [v*1000 for v in self.df['TOTSA']]
        self.df['HC'] = [v*.0001 for v in self.df['HC']]
        
    def test0(self):
        self.df.scatter_matrix('CCSA FIQ TOTSA TOTVOL'.split(),
                          diagonal=None,
                          fname = 'scatter,4var,diag=None')

    def test1(self):
        self.df.scatter_matrix('CCSA HC FIQ TOTSA TOTVOL'.split(),
                          diagonal=None,
                          fname = 'scatter,5var,diag=None')

    def test2(self):

        self.df.scatter_matrix('CCSA FIQ TOTSA TOTVOL'.split(),
                          diagonal='kde',
                          fname = 'scatter,4var,diag=kde')

    def test3(self):

        self.df.scatter_matrix('CCSA HC FIQ TOTSA TOTVOL'.split(),
                          diagonal='kde',
                          fname = 'scatter,5var,diag=kde')

    def test4(self):
        self.df.scatter_matrix('CCSA FIQ TOTSA TOTVOL'.split(),
                          diagonal='hist',
                          fname = 'scatter,4var,diag=hist')

    def test5(self):
        self.df.scatter_matrix('CCSA HC FIQ TOTSA TOTVOL'.split(),
                          diagonal='hist',
                          fname = 'scatter,5var,diag=hist')

    def test5(self):
        self.df.scatter_matrix('CCSA FIQ TOTSA TOTVOL'.split(),
                          diagonal='kde', alternate_labels=False,
                          fname = 'scatter,4var,diag=kde,alternate_labels=False')

    def test6(self):
        self.df.scatter_matrix('CCSA HC FIQ TOTSA TOTVOL'.split(),
                          diagonal='kde', alternate_labels=False,
                          fname = 'scatter,5var,diag=kde,alternate_labels=False')


def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_scatter_matrix)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
    
