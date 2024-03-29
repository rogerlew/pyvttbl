# Copyright (c) 2011-2024, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.
    
import unittest
from random import shuffle

import numpy as np

from pyvttbl import DataFrame
from pyvttbl.misc.support import *

class Test__build_sqlite3_tbl(unittest.TestCase):

    def test00(self):
        """test with empty DataFrame"""
        df = DataFrame()
        df.PRINTQUERIES = True
        df._build_sqlite3_tbl(df.keys())
        

    def test03(self):
        """test with mixed data types"""
        df = DataFrame()
        df['1'] = [1, 2, 3, 4, 5]
        df['2'] = ['a', 'b', 'c', 'd', 'e']
        df['3'] = [1.1, 2.2, 3.3, 4.4, 5.5]
        df['4'] = [True, False, True, False, True]

        df._build_sqlite3_tbl(df.keys())
        
        df._execute('select * from TBL')
        for i, (a, b, c, d) in enumerate(df.cur):
            self.assertEqual(a, df['1'][i])
            self.assertEqual(b, df['2'][i])
            self.assertEqual(c, df['3'][i])
            self.assertEqual(d, df['4'][i])

    def test04(self):
        """test with missing values"""
        df = DataFrame()
        df['1'] = [1, 2, None, 4, 5]
        df['2'] = ['a', 'b', 'c', None, 'e']
        df['3'] = [1.1, None, 3.3, 4.4, 5.5]
        df['4'] = [True, False, None, False, True]

        df._build_sqlite3_tbl(df.keys())
        
        df._execute('select * from TBL')
        for i, (a, b, c, d) in enumerate(df.cur):
            self.assertEqual(a, df['1'][i])
            self.assertEqual(b, df['2'][i])
            self.assertEqual(c, df['3'][i])
            self.assertEqual(d, str(df['4'][i]))
        """test with string keys"""
        df=DataFrame()
##        df.PRINTQUERIES=True
        df['1']=list(range(100))
        df['2']=['bob' for i in range(100)]
        df['3']=[i*1.234232 for i in range(100)]
        df['4']=['bob' for i in range(50)]+list(range(50))

        df['5']= np.sqrt(df['3'] *100.)
##        print(df)

        shuffle(df['1'])
        shuffle(df['2'])
        shuffle(df['3'])

        df._build_sqlite3_tbl(df.keys())
        
        df._execute('select * from TBL')
        for i,(a,b,c,d,e) in enumerate(df.cur):
            print(i, a,b,c,d,e)
            self.assertEqual(a,df['1'][i])
            self.assertEqual(b,df['2'][i])
            self.assertEqual(c,df['3'][i])
            self.assertEqual(d,str(df['4'][i]))  
            
    def test01(self):
        """test with integer keys"""
        df = DataFrame()
        df[1] = list(range(100))
        df[2] = ['bob' for i in range(100)]
        df[3] = [i*1.234232 for i in range(100)]
        df[4] = ['bob' for i in range(50)] + list(range(50))

        shuffle(df[1])
        shuffle(df[2])
        shuffle(df[3])
        shuffle(df[4])

        df._build_sqlite3_tbl(df.keys())
        
        df._execute('select * from TBL')
        for i,(a,b,c,d) in enumerate(df.cur):
            self.assertEqual(a,df[1][i])
            self.assertEqual(b,df[2][i])
            self.assertEqual(c,df[3][i])
            self.assertEqual(d,str(df[4][i]))

    def test02(self):
        """test with tuple keys"""
        df=DataFrame()
##        df.PRINTQUERIES = True
        df[(1,)] = list(range(100))
        df[(2,)] = ['bob' for i in range(100)]
        df[(3,)] = [i*1.234232 for i in range(100)]
        df[(4,)] = ['bob' for i in range(50)] + list(range(50))

        shuffle(df[(1,)])
        shuffle(df[(2,)])
        shuffle(df[(3,)])
        shuffle(df[(4,)])

        df._build_sqlite3_tbl(df.keys())
        
        df._execute('select * from TBL')
        for i,(a,b,c,d) in enumerate(df.cur):
            self.assertEqual(a,df[(1,)][i])
            self.assertEqual(b,df[(2,)][i])
            self.assertEqual(c,df[(3,)][i])
            self.assertEqual(d,str(df[(4,)][i]))
            
    def test1(self):
        """test with integer keys subset of table"""
        df=DataFrame()
        df[1]=list(range(100))
        df[2]=['bob' for i in range(100)]
        df[3]=[i*1.234232 for i in range(100)]
        df[4]=['bob' for i in range(50)] + list(range(50))

        shuffle(df[1])
        shuffle(df[2])
        shuffle(df[3])
        shuffle(df[4])

        df._build_sqlite3_tbl(list(df.keys())[:2])
        
        df._execute('select * from TBL')
        for i,(a,b) in enumerate(df.cur):
            self.assertEqual(a,df[1][i])
            self.assertEqual(b,df[2][i])

    def test2(self):
        """test with string keys and tuple where condition"""
        df=DataFrame()
        df['1']=list(range(100))
        df['2']=['bob' for i in range(100)]
        df['3']=[i*1.234232 for i in range(100)]
        df['4']=['bob' for i in range(50)] + list(range(50))

        shuffle(df['1'])
        shuffle(df['2'])
        shuffle(df['3'])

        df._build_sqlite3_tbl(list(df.keys())[:2], [('4','not in',['bob'])])
        
        df._execute('select * from TBL')
        for i,(a,b) in enumerate(df.cur):
            self.assertEqual(a,df['1'][i+50])
            self.assertEqual(b,df['2'][i+50])

    def test21(self):
        """test with string keys and tuple where condition"""
        df=DataFrame()
        df[1]=list(range(100))
        df[2]=['bob' for i in range(100)]
        df[3]=[i*1.234232 for i in range(100)]
        df[4]=['bob' for i in range(50)] + list(range(50))

        shuffle(df[1])
        shuffle(df[2])
        shuffle(df[3])

        df._build_sqlite3_tbl(list(df.keys())[:2], [(4,'not in',['bob'])])
        
        df._execute('select * from TBL')
        for i,(a,b) in enumerate(df.cur):
            self.assertEqual(a,df[1][i+50])
            self.assertEqual(b,df[2][i+50])

    def test22(self):
        """test with string keys and where condition"""
        df=DataFrame()
        df['1']=list(range(100))
        df['2']=['bob' for i in range(100)]
        df['3']=[i*1.234232 for i in range(100)]
        df['4']=['bob' for i in range(50)] + list(range(50))

        shuffle(df['1'])
        shuffle(df['2'])
        shuffle(df['3'])

        df._build_sqlite3_tbl(list(df.keys())[:2], ['4 not in ("bob")'])
        
        df._execute('select * from TBL')
        for i,(a,b) in enumerate(df.cur):
            self.assertEqual(a,df['1'][i+50])
            self.assertEqual(b,df['2'][i+50])
            
    def test3(self):
        """test with string keys and tuple where condition"""
        df=DataFrame()
        df[1]=list(range(100))
        df[2]=['bob' for i in range(100)]
        df[3]=[i*1.234232 for i in range(100)]
        df[4]=['bob' for i in range(50)] + list(range(50))

        shuffle(df[1])
        shuffle(df[2])
        shuffle(df[3])

        df._build_sqlite3_tbl(list(df.keys())[:2], [(4,'!=','bob')])
        
        df._execute('select * from TBL')
        for i,(a,b) in enumerate(df.cur):
            self.assertEqual(a,df[1][i+50])
            self.assertEqual(b,df[2][i+50])

    def test31(self):
        df=DataFrame()
        df[1]=list(range(100))
        df[2]=['bob' for i in range(100)]
        df[3]=[i*1.234232 for i in range(100)]
        df[4]=['bob' for i in range(50)] + list(range(50))

        shuffle(df[1])
        shuffle(df[2])
        shuffle(df[3])

        with self.assertRaises(KeyError) as cm:
            df._build_sqlite3_tbl(list(df.keys())[:2], ['4 != "bob"'])
        
        self.assertEqual(str(cm.exception),
                         "'4'")
            
    def test4(self):
        df=DataFrame()
        df[1]=list(range(100))
        df[2]=['bob' for i in range(100)]
        df[3]=[i*1.234232 for i in range(100)]
        df[4]=['bob' for i in range(50)] + list(range(50))

        with self.assertRaises(TypeError) as cm:
            df._build_sqlite3_tbl(list(df.keys())[:2], 42)
        
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
