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
from pyvttbl.plotting import scatter_plot
from pyvttbl.misc.support import *

class Test_scatter_plot(unittest.TestCase):
    def test01(self):
        df=DataFrame()
        df.read_tbl('iqbrainsize.txt', delimiter='\t')
        df.scatter_plot('TOTVOL','FIQ')
        
    def test02(self):
        df=DataFrame()
        df.read_tbl('iqbrainsize.txt', delimiter='\t')
        df.scatter_plot('TOTVOL','FIQ', trend='power')
            
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_scatter_plot),
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
    
