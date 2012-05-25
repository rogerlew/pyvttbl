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
##from pyvttbl.plotting import box_plot
from pyvttbl.misc.support import *

class Test_marginals(unittest.TestCase):
    def test0(self):
        df=DataFrame()
        df.read_tbl('words~ageXcondition.csv')

        x=df.marginals('WORDS',factors=['AGE','CONDITION'])

        for d,r in zip(x['dmu'],[11,7,13.4,12,6.9,14.8,6.5,17.6,19.3,7.6]):
            self.failUnlessAlmostEqual(d,r)

        for d,r in zip(x['dN'],[10,10,10,10,10,10,10,10,10,10]):
            self.failUnlessAlmostEqual(d,r)

        for d,r in zip(x['dsem'],[0.788810638,
                                  0.577350269,
                                  1.423610434,
                                  1.183215957,
                                  0.674124947,
                                  1.103529690,
                                  0.453382350,
                                  0.819213715,
                                  0.843932593,
                                  0.618241233]):
            self.failUnlessAlmostEqual(d,r)

    def test02(self):
        df=DataFrame()
        df.read_tbl('words~ageXcondition.csv')
        D = str(df.marginals('WORDS',factors=['AGE','CONDITION']))
        R = """ AGE    CONDITION    Mean    Count   Std.    95% CI   95% CI 
                                     Error   lower    upper  
============================================================
old     adjective   11.000   10      0.789    9.454   12.546 
old     counting     7.000   10      0.577    5.868    8.132 
old     imagery     13.400   10      1.424   10.610   16.190 
old     intention   12.000   10      1.183    9.681   14.319 
old     rhyming      6.900   10      0.674    5.579    8.221 
young   adjective   14.800   10      1.104   12.637   16.963 
young   counting     6.500   10      0.453    5.611    7.389 
young   imagery     17.600   10      0.819   15.994   19.206 
young   intention   19.300   10      0.844   17.646   20.954 
young   rhyming      7.600   10      0.618    6.388    8.812 """
        self.assertEqual(D, R)

    def test03(self):
        df=DataFrame()
        df.read_tbl('words~ageXcondition.csv')
        D = repr(df.marginals('WORDS',factors=['AGE','CONDITION']))
        R = "Marginals([('factorials', OrderedDict([('AGE', [u'old', u'old', u'old', u'old', u'old', u'young', u'young', u'young', u'young', u'young']), ('CONDITION', [u'adjective', u'counting', u'imagery', u'intention', u'rhyming', u'adjective', u'counting', u'imagery', u'intention', u'rhyming'])])), ('dmu', PyvtTbl([11.0, 7.0, 13.4, 12.0, 6.9, 14.8, 6.5, 17.6, 19.3, 7.6], val='WORDS', grand_tot=11.61, rnames=[[('AGE', u'old'), ('CONDITION', u'adjective')], [('AGE', u'old'), ('CONDITION', u'counting')], [('AGE', u'old'), ('CONDITION', u'imagery')], [('AGE', u'old'), ('CONDITION', u'intention')], [('AGE', u'old'), ('CONDITION', u'rhyming')], [('AGE', u'young'), ('CONDITION', u'adjective')], [('AGE', u'young'), ('CONDITION', u'counting')], [('AGE', u'young'), ('CONDITION', u'imagery')], [('AGE', u'young'), ('CONDITION', u'intention')], [('AGE', u'young'), ('CONDITION', u'rhyming')]], cnames=[1], flatten=True)), ('dN', PyvtTbl([10, 10, 10, 10, 10, 10, 10, 10, 10, 10], val='WORDS', grand_tot=100, rnames=[[('AGE', u'old'), ('CONDITION', u'adjective')], [('AGE', u'old'), ('CONDITION', u'counting')], [('AGE', u'old'), ('CONDITION', u'imagery')], [('AGE', u'old'), ('CONDITION', u'intention')], [('AGE', u'old'), ('CONDITION', u'rhyming')], [('AGE', u'young'), ('CONDITION', u'adjective')], [('AGE', u'young'), ('CONDITION', u'counting')], [('AGE', u'young'), ('CONDITION', u'imagery')], [('AGE', u'young'), ('CONDITION', u'intention')], [('AGE', u'young'), ('CONDITION', u'rhyming')]], cnames=[1], aggregate='count', flatten=True)), ('dsem', PyvtTbl([0.7888106377466154, 0.5773502691896257, 1.4236104336041748, 1.1832159566199232, 0.6741249472052228, 1.103529690483123, 0.4533823502911814, 0.8192137151629671, 0.8439325934114773, 0.6182412330330468], val='WORDS', grand_tot=0.5191085988246943, rnames=[[('AGE', u'old'), ('CONDITION', u'adjective')], [('AGE', u'old'), ('CONDITION', u'counting')], [('AGE', u'old'), ('CONDITION', u'imagery')], [('AGE', u'old'), ('CONDITION', u'intention')], [('AGE', u'old'), ('CONDITION', u'rhyming')], [('AGE', u'young'), ('CONDITION', u'adjective')], [('AGE', u'young'), ('CONDITION', u'counting')], [('AGE', u'young'), ('CONDITION', u'imagery')], [('AGE', u'young'), ('CONDITION', u'intention')], [('AGE', u'young'), ('CONDITION', u'rhyming')]], cnames=[1], aggregate='sem', flatten=True)), ('dlower', PyvtTbl([9.453931150016635, 5.868393472388334, 10.609723550135818, 9.680896725024951, 5.578715103477764, 12.637081806653079, 5.611370593429284, 15.994341118280586, 17.645892116913505, 6.388247183255228], val='WORDS', grand_tot=100, rnames=[[('AGE', u'old'), ('CONDITION', u'adjective')], [('AGE', u'old'), ('CONDITION', u'counting')], [('AGE', u'old'), ('CONDITION', u'imagery')], [('AGE', u'old'), ('CONDITION', u'intention')], [('AGE', u'old'), ('CONDITION', u'rhyming')], [('AGE', u'young'), ('CONDITION', u'adjective')], [('AGE', u'young'), ('CONDITION', u'counting')], [('AGE', u'young'), ('CONDITION', u'imagery')], [('AGE', u'young'), ('CONDITION', u'intention')], [('AGE', u'young'), ('CONDITION', u'rhyming')]], cnames=[1], aggregate='count', flatten=True)), ('dupper', PyvtTbl([12.546068849983365, 8.131606527611666, 16.190276449864182, 14.319103274975049, 8.221284896522237, 16.962918193346923, 7.388629406570716, 19.205658881719415, 20.954107883086497, 8.811752816744772], val='WORDS', grand_tot=100, rnames=[[('AGE', u'old'), ('CONDITION', u'adjective')], [('AGE', u'old'), ('CONDITION', u'counting')], [('AGE', u'old'), ('CONDITION', u'imagery')], [('AGE', u'old'), ('CONDITION', u'intention')], [('AGE', u'old'), ('CONDITION', u'rhyming')], [('AGE', u'young'), ('CONDITION', u'adjective')], [('AGE', u'young'), ('CONDITION', u'counting')], [('AGE', u'young'), ('CONDITION', u'imagery')], [('AGE', u'young'), ('CONDITION', u'intention')], [('AGE', u'young'), ('CONDITION', u'rhyming')]], cnames=[1], aggregate='count', flatten=True))], val='WORDS', factors=['AGE', 'CONDITION'])"
        self.assertEqual(D, R)

    def test04(self):
        df=DataFrame()
        df.read_tbl('words~ageXcondition.csv')
        D = str(df.marginals('WORDS',
                              factors=['AGE','CONDITION'],
                              where='AGE == "old"'))
        R = """AGE   CONDITION    Mean    Count   Std.    95% CI   95% CI 
                                   Error   lower    upper  
==========================================================
old   adjective   11.000   10      0.789    9.454   12.546 
old   counting     7.000   10      0.577    5.868    8.132 
old   imagery     13.400   10      1.424   10.610   16.190 
old   intention   12.000   10      1.183    9.681   14.319 
old   rhyming      6.900   10      0.674    5.579    8.221 """
        self.assertEqual(D, R)

    def test05(self):
        df=DataFrame()
        df.read_tbl('words~ageXcondition.csv')
        D = df.marginals('WORDS',
                              factors=['AGE','CONDITION'],
                              where='AGE == "old"')
        R = """Marginals([('factorials', OrderedDict([('AGE', [u'old', u'old', u'old', u'old', u'old']), ('CONDITION', [u'adjective', u'counting', u'imagery', u'intention', u'rhyming'])])), ('dmu', PyvtTbl([11.0, 7.0, 13.4, 12.0, 6.9], val='WORDS', grand_tot=10.06, rnames=[[('AGE', u'old'), ('CONDITION', u'adjective')], [('AGE', u'old'), ('CONDITION', u'counting')], [('AGE', u'old'), ('CONDITION', u'imagery')], [('AGE', u'old'), ('CONDITION', u'intention')], [('AGE', u'old'), ('CONDITION', u'rhyming')]], cnames=[1], flatten=True, where='AGE == "old"')), ('dN', PyvtTbl([10, 10, 10, 10, 10], val='WORDS', grand_tot=50, rnames=[[('AGE', u'old'), ('CONDITION', u'adjective')], [('AGE', u'old'), ('CONDITION', u'counting')], [('AGE', u'old'), ('CONDITION', u'imagery')], [('AGE', u'old'), ('CONDITION', u'intention')], [('AGE', u'old'), ('CONDITION', u'rhyming')]], cnames=[1], aggregate='count', flatten=True, where='AGE == "old"')), ('dsem', PyvtTbl([0.7888106377466154, 0.5773502691896257, 1.4236104336041748, 1.1832159566199232, 0.6741249472052228], val='WORDS', grand_tot=0.5667018796582233, rnames=[[('AGE', u'old'), ('CONDITION', u'adjective')], [('AGE', u'old'), ('CONDITION', u'counting')], [('AGE', u'old'), ('CONDITION', u'imagery')], [('AGE', u'old'), ('CONDITION', u'intention')], [('AGE', u'old'), ('CONDITION', u'rhyming')]], cnames=[1], aggregate='sem', flatten=True, where='AGE == "old"')), ('dlower', PyvtTbl([9.453931150016635, 5.868393472388334, 10.609723550135818, 9.680896725024951, 5.578715103477764], val='WORDS', grand_tot=50, rnames=[[('AGE', u'old'), ('CONDITION', u'adjective')], [('AGE', u'old'), ('CONDITION', u'counting')], [('AGE', u'old'), ('CONDITION', u'imagery')], [('AGE', u'old'), ('CONDITION', u'intention')], [('AGE', u'old'), ('CONDITION', u'rhyming')]], cnames=[1], aggregate='count', flatten=True, where='AGE == "old"')), ('dupper', PyvtTbl([12.546068849983365, 8.131606527611666, 16.190276449864182, 14.319103274975049, 8.221284896522237], val='WORDS', grand_tot=50, rnames=[[('AGE', u'old'), ('CONDITION', u'adjective')], [('AGE', u'old'), ('CONDITION', u'counting')], [('AGE', u'old'), ('CONDITION', u'imagery')], [('AGE', u'old'), ('CONDITION', u'intention')], [('AGE', u'old'), ('CONDITION', u'rhyming')]], cnames=[1], aggregate='count', flatten=True, where='AGE == "old"'))], val='WORDS', factors=['AGE', 'CONDITION'], where='AGE == "old"')"""
        self.assertEqual(repr(D), R)


def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_marginals)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
