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

from random import shuffle

import numpy as np

from pyvttbl import DataFrame
from pyvttbl.misc.support import *

class Test__build_sqlite3_tbl(unittest.TestCase):
    def test0(self):
        df=DataFrame()
        df[1]=range(100)
        df[2]=['bob' for i in range(100)]
        df[3]=[i*1.234232 for i in range(100)]
        df[4]=['bob' for i in range(50)]+range(50)

        shuffle(df[1])
        shuffle(df[2])
        shuffle(df[3])
        shuffle(df[4])

        df._build_sqlite3_tbl(df.names())
        
        df._execute('select * from TBL')
        for i,(a,b,c,d) in enumerate(df.cur):
            self.assertEqual(a,df[1][i])
            self.assertEqual(b,df[2][i])
            self.assertEqual(c,df[3][i])
            self.assertEqual(d,str(df[4][i]))
            
    def test1(self):
        df=DataFrame()
        df[1]=range(100)
        df[2]=['bob' for i in range(100)]
        df[3]=[i*1.234232 for i in range(100)]
        df[4]=['bob' for i in range(50)]+range(50)

        shuffle(df[1])
        shuffle(df[2])
        shuffle(df[3])
        shuffle(df[4])

        df._build_sqlite3_tbl(df.names()[:2])
        
        df._execute('select * from TBL')
        for i,(a,b) in enumerate(df.cur):
            self.assertEqual(a,df[1][i])
            self.assertEqual(b,df[2][i])

    def test2(self):
        df=DataFrame()
        df['1']=range(100)
        df['2']=['bob' for i in range(100)]
        df['3']=[i*1.234232 for i in range(100)]
        df['4']=['bob' for i in range(50)]+range(50)

        shuffle(df['1'])
        shuffle(df['2'])
        shuffle(df['3'])

        df._build_sqlite3_tbl(df.names()[:2], [('4','not in',['bob'])])
        
        df._execute('select * from TBL')
        for i,(a,b) in enumerate(df.cur):
            self.assertEqual(a,df[1][i+50])
            self.assertEqual(b,df[2][i+50])

    def test21(self):
        df=DataFrame()
        df[1]=range(100)
        df[2]=['bob' for i in range(100)]
        df[3]=[i*1.234232 for i in range(100)]
        df[4]=['bob' for i in range(50)]+range(50)

        shuffle(df[1])
        shuffle(df[2])
        shuffle(df[3])

        df._build_sqlite3_tbl(df.names()[:2], ['4 not in ("bob")'])
        
        df._execute('select * from TBL')
        for i,(a,b) in enumerate(df.cur):
            self.assertEqual(a,df[1][i+50])
            self.assertEqual(b,df[2][i+50])
            
    def test3(self):
        df=DataFrame()
        df[1]=range(100)
        df[2]=['bob' for i in range(100)]
        df[3]=[i*1.234232 for i in range(100)]
        df[4]=['bob' for i in range(50)]+range(50)

        shuffle(df[1])
        shuffle(df[2])
        shuffle(df[3])

        df._build_sqlite3_tbl(df.names()[:2], [(4,'!=','bob')])
        
        df._execute('select * from TBL')
        for i,(a,b) in enumerate(df.cur):
            self.assertEqual(a,df[1][i+50])
            self.assertEqual(b,df[2][i+50])

    def test31(self):
        df=DataFrame()
        df[1]=range(100)
        df[2]=['bob' for i in range(100)]
        df[3]=[i*1.234232 for i in range(100)]
        df[4]=['bob' for i in range(50)]+range(50)

        shuffle(df[1])
        shuffle(df[2])
        shuffle(df[3])

        df._build_sqlite3_tbl(df.names()[:2], ['4 != "bob"'])
        
        df._execute('select * from TBL')
        for i,(a,b) in enumerate(df.cur):
            self.assertEqual(a,df[1][i+50])
            self.assertEqual(b,df[2][i+50])
            
    def test4(self):
        df=DataFrame()
        df[1]=range(100)
        df[2]=['bob' for i in range(100)]
        df[3]=[i*1.234232 for i in range(100)]
        df[4]=['bob' for i in range(50)]+range(50)

        with self.assertRaises(TypeError) as cm:
            df._build_sqlite3_tbl(df.names()[:2], 42)
        
        self.assertEqual(str(cm.exception),
                         "'int' object is not iterable")
        
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test__build_sqlite3_tbl)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
