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

class Test_read_tbl(unittest.TestCase):
    def test01(self):

        # skip 4 lines
        # DON'T MESS WITH THE SPACING
        with open('test.csv','wb') as f:
            f.write("""



x,y,z
1,5,9
2,6,10
3,7,11
4,8,12""")
            
        self.df=DataFrame()
        self.df.read_tbl('skiptest.csv',skip=4)
        D=self.df['x']+self.df['y']+self.df['z']
        R=range(1,13)
        
        for (d,r) in zip(D,R):
            self.assertAlmostEqual(d,r)

    def test01(self):

        # no labels
        with open('test.csv','wb') as f:
            f.write("""
1,5,9
2,6,10
3,7,11
4,8,12""")
            
        self.df=DataFrame()
        self.df.read_tbl('test.csv',skip=1,labels=False)
        D=self.df['COL_1']+self.df['COL_2']+self.df['COL_3']
        R=range(1,13)
        
        for (d,r) in zip(D,R):
            self.assertAlmostEqual(d,r)

    def test03(self):

        # duplicate labels
        with open('test.csv','wb') as f:
            f.write("""
x,x,x
1,5,9
2,6,10
3,7,11
4,8,12""")
            
        self.df=DataFrame()
        
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            
            # Trigger a warning.    
            self.df.read_tbl('test.csv',skip=1,labels=True)
        
            assert issubclass(w[-1].category, RuntimeWarning)
            
        D=self.df['x']+self.df['x_2']+self.df['x_3']
        R=range(1,13)
        
        for (d,r) in zip(D,R):
            self.assertAlmostEqual(d,r)

    def test04(self):

        # line missing data, no comma after 6
        with open('test.csv','wb') as f:
            f.write("""
x,y,z
1,5,9
2,6
3,7,11
4,8,12""")
            
        self.df=DataFrame()
        
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            
            # Trigger a warning.    
            self.df.read_tbl('test.csv',skip=1,labels=True)
        
            assert issubclass(w[-1].category, RuntimeWarning)
            
        D=self.df['x']+self.df['y']+self.df['z']
        R=[1,3,4,5,7,8,9,11,12]
        
        for (d,r) in zip(D,R):
            self.assertAlmostEqual(d,r)

    def test05(self):

        # cell has empty string, comma after 6
        with open('test.csv','wb') as f:
            f.write("""
x,y,z
1,5,9
2,6,
3,7,11
4,8,12""")
            
        self.df=DataFrame()
        self.df.read_tbl('test.csv',skip=1,labels=True)
        
        D=self.df['x']+self.df['y']+self.df['z']
        R=[1,2,3,4,5,6,7,8,9,'',11,12]
        
        for (d,r) in zip(D,R):
            self.assertAlmostEqual(d,r)

    def test06(self):

        # labels have spaces
        with open('test.csv','wb') as f:
            f.write("""
y 1,y 2,y 3
1,5,9
2,6,
3,7,11
4,8,12""")
            
        self.df=DataFrame()
        self.df.read_tbl('test.csv',skip=1,labels=True)
        
        D=self.df['y_1']+self.df['y_2']+self.df['y_3']
        R=[1,2,3,4,5,6,7,8,9,'',11,12]
        
        for (d,r) in zip(D,R):
            self.assertAlmostEqual(d,r)


    def test07(self):

        # labels have spaces
        with open('test.csv','wb') as f:
            f.write("""
y 1,   y 2   ,   y 3
1,5,9
2,6,
3,7,11
4,8,12""")
            
        self.df=DataFrame()
        self.df.read_tbl('test.csv',skip=1,labels=True)
        
        D=self.df['y_1']+self.df['y_2']+self.df['y_3']
        R=[1,2,3,4,5,6,7,8,9,'',11,12]
        
        for (d,r) in zip(D,R):
            self.assertAlmostEqual(d,r)
            
    def tearDown(self):
        os.remove('./test.csv')

class Test__setitem__(unittest.TestCase):
    def test1(self):
        df=DataFrame()
        df.read_tbl('error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        df['DUM']=range(48) # Shouldn't complain
                
    def test11(self):
        df=DataFrame()
        df['DUM']=range(48) # Shouldn't complain
        self.assertEqual(df.keys(),[('DUM','integer')])
        
        df['DUM']=['A' for i in range(48)] # Shouldn't complain
        self.assertEqual(df.keys(),[('DUM','text')])

    def test21(self):
        df=DataFrame()
        df[1]=range(48) # 1 becomes a string
        self.assertEqual(df.keys(),[('1','integer')])

    def test2(self):
        df=DataFrame()
        with self.assertRaises(TypeError) as cm:
            df['DUM']=42

        self.assertEqual(str(cm.exception),
                         "'int' object is not iterable")

    def test4(self):
        df=DataFrame()
        df['DUM']=[42]
        with self.assertRaises(Exception) as cm:
            df['dum']=[42]

        self.assertEqual(str(cm.exception),
                         "a case variant of 'dum' already exists")

    def test_kn(self):
        df = DataFrame()
        df.read_tbl('example.csv')
        y = [23]*len(df['X'])
        df['X'] = y
        
        self.assertEqual(df.names(), ('CASE', 'TIME', 'CONDITION', 'X'))
        

def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_read_tbl)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
