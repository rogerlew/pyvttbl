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

class Test_writepivot(unittest.TestCase):
    def setUp(self):
        self.df=DataFrame()
        self.df.read_tbl('suppression~subjectXgroupXageXcycleXphase.csv')

    def test0(self):
        # self.assertEqual doesn't like really long comparisons
        # so we will break it up into lines
        R=['avg(SUPPRESSION)\r\n',
           'GROUP,CYCLE=3_AGE=old,CYCLE=3_AGE=young,CYCLE=4_AGE=old,CYCLE=4_AGE=young\r\n',
           'AA,21.9375,10.0125,22.25,10.5125\r\n',
           'LAB,37.0625,12.5375,36.4375,12.0375\r\n']
        
        myPyvtTbl = self.df.pivot('SUPPRESSION',
                               rows=['GROUP'],
                               cols=['CYCLE','AGE'],
                               aggregate='avg',
                               where=[('GROUP','not in',['AB']),
                                      ('CYCLE','not in',[1,2])])
        myPyvtTbl.write()

        D=[]
        # write pivot should generate this name
                   
        with open('suppression~(group)Z(cycleXage).csv','rb') as f:
            D=f.readlines()

        for d,r in zip(D,R):
            self.failUnlessEqual(d,r)

        # clean up
        os.remove('./suppression~(group)Z(cycleXage).csv')
            
    def test1(self):
        # same as test0 except we are specifying a filename
        # and specifying the delimiter as \t
        R=['"avg(SUPPRESSION) where GROUP not in [\'AB\'] and  CYCLE not in [1, 2]"\r\n',
           'GROUP\tCYCLE=3.0_AGE=old\tCYCLE=3.0_AGE=young\tCYCLE=4.0_AGE=old\tCYCLE=4.0_AGE=young\r\n',
           'AA\t21.9375\t10.0125\t22.25\t10.5125\r\n',
           'LAB\t37.0625\t12.5375\t36.4375\t12.0375\r\n']
        
        myPyvtTbl = self.df.pivot('SUPPRESSION',
                               rows=['GROUP'],
                               cols=['CYCLE','AGE'],
                               aggregate='avg',
                               where=[('GROUP','not in',['AB']),
                                      ('CYCLE','not in',[1,2])])
        
        myPyvtTbl.write('myname.dat','\t')

        # clean up
        os.remove('./myname.dat')

    def test2(self):
        # no exclusions this time
        R=['avg(SUPPRESSION)\r\n',
           'GROUP,CYCLE=1_AGE=old,CYCLE=1_AGE=young,CYCLE=2_AGE=old,CYCLE=2_AGE=young,CYCLE=3_AGE=old,CYCLE=3_AGE=young,CYCLE=4_AGE=old,CYCLE=4_AGE=young\r\n',
           'AA,19.3125,8.4875,25.25,10.2375,21.9375,10.0125,22.25,10.5125\r\n',
           'AB,17.6875,7.1,32.3125,10.9625,33.0625,11.8,33.6875,10.3\r\n',
           'LAB,28.9375,10.7875,34.125,12.1375,37.0625,12.5375,36.4375,12.0375\r\n']

        
        myPyvtTbl = self.df.pivot('SUPPRESSION',
                               rows=['GROUP'],
                               cols=['CYCLE','AGE'],
                               aggregate='avg')
        
        myPyvtTbl.write('pivot_test2.csv')

        D=[]
        # write pivot should generate this name
        with open('pivot_test2.csv','rb') as f:
            D=f.readlines()

        for d,r in zip(D,R):
            self.failUnlessEqual(d,r)

        # clean up
        os.remove('./pivot_test2.csv')        

    def test3(self):
        from pyvttbl import PyvtTbl
        myPyvtTbl = PyvtTbl()
        # try to write pivot table when table doesn't exist
        with self.assertRaises(Exception) as cm:
            myPyvtTbl.write('pivot_test3.csv')

        self.assertEqual(str(cm.exception),
                         'must call pivot before writing pivot table')        
        
    def test4(self):
        R = 'avg(SUPPRESSION)\r\nCYCLE=1_AGE=old,CYCLE=1_AGE=young,CYCLE=2_AGE=old,CYCLE=2_AGE=young,CYCLE=3_AGE=old,CYCLE=3_AGE=young,CYCLE=4_AGE=old,CYCLE=4_AGE=young\r\n21.9791666667,8.79166666667,30.5625,11.1125,30.6875,11.45,30.7916666667,10.95\r\n'
        # rows not specified
        myPyvtTbl = self.df.pivot('SUPPRESSION',
                               cols=['CYCLE','AGE'],
                               aggregate='avg')

        myPyvtTbl.write()

        # write pivot should generate this name
        with open('suppression~()Z(cycleXage).csv','rb') as f:
            D=f.read()

        self.failUnlessEqual(D,R)

        # clean up
        os.remove('./suppression~()Z(cycleXage).csv')

    def test5(self):
        R = 'avg(SUPPRESSION)\r\nCYCLE,AGE,Value\r\n1,old,21.9791666667\r\n1,young,8.79166666667\r\n2,old,30.5625\r\n2,young,11.1125\r\n3,old,30.6875\r\n3,young,11.45\r\n4,old,30.7916666667\r\n4,young,10.95\r\n'
        # cols not specified
        myPyvtTbl = self.df.pivot('SUPPRESSION',
                               rows=['CYCLE','AGE'],
                               aggregate='avg')
        myPyvtTbl.write()

        # write pivot should generate this name
        with open('suppression~(cycleXage)Z().csv','rb') as f:
            D=f.read()

        self.failUnlessEqual(D,R)

        # clean up
        os.remove('./suppression~(cycleXage)Z().csv')

    def test6(self):
        R = 'count(SUPPRESSION)\r\nValue\r\n384\r\n'
        
        # no rows or cols not specified
        myPyvtTbl = self.df.pivot('SUPPRESSION',
                 aggregate='count')
        myPyvtTbl.write(delimiter='\t') # check .tsv functionality

        # write pivot should generate this name
        with open('suppression~()Z().tsv','rb') as f:
            D=f.read()

        self.failUnlessEqual(D,R)

        # clean up
        os.remove('./suppression~()Z().tsv')

    def test7(self):        
        # no rows or cols not specified
        myPyvtTbl = self.df.pivot('SUPPRESSION',
                               aggregate='count')
        
        with self.assertRaises(Exception) as cm:
            myPyvtTbl.write([]) # non-str filename

        self.assertEqual(str(cm.exception),
                         'fname must be a string')

        
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_writepivot)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
