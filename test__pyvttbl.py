from __future__ import print_function

# Copyright (c) 2011, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.

import unittest
import warnings
import os

from random import shuffle
from collections import Counter
from dictset import DictSet,_rep_generator
from math import isnan, isinf
import numpy as np
from pprint import pprint as pp
from pyvttbl import PyvtTbl
from pyvttbl import _flatten

def _isfloat(string):
    try:
        float(string)
    except:
        return False
    return True

def fcmp(d,r):
    """
    Compares two files, d and r, cell by cell. Float comparisons 
    are made to seven decimal places. Extending this function could
    be a project in and of itself.
    """
    # we need to compare the files
    dh=open(d,'rb')
    rh=open(r,'rb')
    
    dlines = dh.readlines()
    rlines = rh.readlines()
    boolCounter = Counter()
    for dline, rline in zip(dlines,rlines):
        for dc,rc in zip(dline.split(','),rline.split(',')):
            if _isfloat(dc):
                if round(float(dc),7)!=round(float(rc),7):
                    boolCounter[False] += 1
                else:
                    boolCounter[True] += 1 
            else:
                pass
                if dc!=rc:
                    boolCounter[False]+= 1
                else:
                    boolCounter[True]+= 1    
    dh.close()
    rh.close()

    if False not in boolCounter:
        return True
    else:
        return False

class Test_readTbl(unittest.TestCase):
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
            
        self.df=PyvtTbl()
        self.df.readTbl('skiptest.csv',skip=4)
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
            
        self.df=PyvtTbl()
        self.df.readTbl('test.csv',skip=1,labels=False)
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
            
        self.df=PyvtTbl()
        
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            
            # Trigger a warning.    
            self.df.readTbl('test.csv',skip=1,labels=True)
        
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
            
        self.df=PyvtTbl()
        
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            
            # Trigger a warning.    
            self.df.readTbl('test.csv',skip=1,labels=True)
        
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
            
        self.df=PyvtTbl()
        self.df.readTbl('test.csv',skip=1,labels=True)
        
        D=self.df['x']+self.df['y']+self.df['z']
        R=[1,2,3,4,5,6,7,8,9,'',11,12]
        
        for (d,r) in zip(D,R):
            self.assertAlmostEqual(d,r)

    def tearDown(self):
        os.remove('./test.csv')

class Test__setitem__(unittest.TestCase):
    def setUp(self):
        self.df=PyvtTbl()
        self.df.readTbl('error~subjectXtimeofdayXcourseXmodel_MISSING.csv')

    def test2(self):
        self.df['DUM']=range(48) # Shouldn't complain

    def test3(self):
        self.df['DUM']=range(48)
        self.df['DUM'].pop()

        # user should be able to freely manipulate data, but should
        # complain if the user tries to pivot with unequal columns
        with self.assertRaises(Exception) as cm:
            self.df.pivot('DUM',['COURSE'])

        self.assertEqual(str(cm.exception),
                         'columns have unequal lengths')

class Test__delitem__(unittest.TestCase):
    def setUp(self):
        self.df=PyvtTbl()
        self.df.readTbl('error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        del self.df['COURSE']

    def test0(self):
        self.assertEqual(self.df.names,
                         ['SUBJECT', 'TIMEOFDAY', 'MODEL', 'ERROR'])

    def test1(self):
        self.assertEqual(self.df.types,
                         ['integer', 'text', 'text', 'integer'])

    def test2(self):
        self.assertEqual(self.df.conditions.keys(),
                         ['SUBJECT', 'MODEL', 'TIMEOFDAY', 'ERROR'])

    def test3(self):
        self.assertEqual(self.df.N, 4)
        
class Test_insert(unittest.TestCase):
    def test0(self):
        df=PyvtTbl()
        conditionsDict=DictSet({'A':[10,20,40,80],
                                'B':[100,800],
                              'rep':range(10)})
        for A,B,rep in conditionsDict.unique_combinations():
            df.insert({'A':A, 'B':B,'rep':rep})

        for d,r in zip(df['A'],_rep_generator([10,20,40,80],4,20)):
            self.assertAlmostEqual(d,r)

        for d,r in zip(df['B'],_rep_generator([100,800],8,10)):
            self.assertAlmostEqual(d,r)

        for d,r in zip(df['rep'],_rep_generator(range(10),8,1)):
            self.assertAlmostEqual(d,r)

    def test1(self):
        df=PyvtTbl()

        with self.assertRaises(Exception) as cm:
            df.insert([1,2,3,4])

        self.assertEqual(str(cm.exception),
                         'row must be mappable type')

    def test2(self):
        df=PyvtTbl()
        df.insert({'A':1, 'B':2})

        with self.assertRaises(Exception) as cm:
            df.insert({'A':1, 'B':2, 'C':3})

        self.assertEqual(str(cm.exception),
                         'row must have the same keys as the table')
        
    def test3(self):
        df=PyvtTbl()
        df.insert({'A':1, 'B':2})

        with self.assertRaises(Exception) as cm:
            df.insert({'A':1, 'B':2, 'C':3})

        self.assertEqual(str(cm.exception),
                         'row must have the same keys as the table')

    def test4(self):
        df=PyvtTbl()
        df.insert([('A',1.23), ('B',2), ('C','A')])
        self.assertEqual(df.types, ['real', 'integer', 'text'])
        
class Test_attach(unittest.TestCase):
    def test0(self):
        self.df1=PyvtTbl()
        self.df1.readTbl('words~ageXcondition.csv')

        with self.assertRaises(Exception) as cm:
            self.df1.attach('s')

        self.assertEqual(str(cm.exception),
                         'second argument must be a PyvtTbl')
        
    def test1(self):
        self.df1=PyvtTbl()
        self.df2=PyvtTbl()
        self.df1.readTbl('words~ageXcondition.csv')
        self.df2.readTbl('words~ageXcondition.csv')

        # add an extra key to df1
        self.df1['EXTRA'] = [5 for a in self.df1['AGE']]

        with self.assertRaises(Exception) as cm:
            self.df1.attach(self.df2)

        self.assertEqual(str(cm.exception),
                         'self and other must have the same columns')

    def test2(self):
        df1=PyvtTbl()
        df2=PyvtTbl()
        df1.readTbl('words~ageXcondition.csv')
        df2.readTbl('words~ageXcondition.csv')

        M=df1.M

        # this should work
        df1.attach(df2)

        # df1 should have twice as many rows now
        self.assertEqual(df1.M/2,df2.M)

        # go through and check data
        for i in range(M):
            for n in df1.names:
                if _isfloat(df1[n][i]):
                    self.assertAlmostEqual(df1[n][i],df1[n][M+i])
                else:
                    self.assertEqual(df1[n][i],df1[n][M+i])

class Test_sort(unittest.TestCase):
    def test0(self):
        R={'A': [-10.0, -9.0, -8.0, -7.0, -6.0, -5.0, -4.0, -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0],
           'B': [2.0, 2.0, 1.0, 1.0, 2.0, 2.0, 2.0, 1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 2.0, 1.0]}

        a=[4, 8, 1, 5, -7, -5, 9, 7, -8, -10, -1, -4, 3, 0., -2, 6, 2, -9, -3, -6]
        b=[1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2]

        df=PyvtTbl()
        for A,B in zip(a,b):
            df.insert({'A':A, 'B':B})

        df.sort(['A'])
        
        for d,r in zip(df['A'],R['A']):
            self.assertAlmostEqual(d,r)

        for d,r in zip(df['B'],R['B']):
            self.assertAlmostEqual(d,r)
            
    def test1(self):
        R={'A': [9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.0, -1.0, -2.0, -3.0, -4.0, -5.0, -6.0, -7.0, -8.0, -9.0, -10.0],
           'B': [1.0, 2.0, 2.0, 2.0, 2.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 1.0, 1.0, 2.0, 2.0]}

        a=[4, 8, 1, 5, -7, -5, 9, 7, -8, -10, -1, -4, 3, 0., -2, 6, 2, -9, -3, -6]
        b=[1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2]

        df=PyvtTbl()
        for A,B in zip(a,b):
            df.insert({'A':A, 'B':B})

        df.sort(['A desc',])

        for d,r in zip(df['A'],R['A']):
            self.assertAlmostEqual(d,r)

        for d,r in zip(df['B'],R['B']):
            self.assertAlmostEqual(d,r)

    def test2(self):
        R={'A': [-8.0, -7.0, -3.0, -2.0, -1.0, 1.0, 2.0, 3.0, 4.0, 9.0, -10.0, -9.0, -6.0, -5.0, -4.0, 0.0, 5.0, 6.0, 7.0, 8.0],
           'B': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0]}

        a=[4, 8, 1, 5, -7, -5, 9, 7, -8, -10, -1, -4, 3, 0., -2, 6, 2, -9, -3, -6]
        b=[1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2]

        df=PyvtTbl()
        for A,B in zip(a,b):
            df.insert({'A':A, 'B':B})

        df.sort(['B','A'])

        for d,r in zip(df['A'],R['A']):
            self.assertAlmostEqual(d,r)

        for d,r in zip(df['B'],R['B']):
            self.assertAlmostEqual(d,r)

class Test_pivot_1(unittest.TestCase):
    def setUp(self):
        D={
            'SUBJECT':[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100],
            'AGE':'old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young'.split(','),
            'CONDITION':'counting,counting,counting,counting,counting,counting,counting,counting,counting,counting,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,intention,intention,intention,intention,intention,intention,intention,intention,intention,intention,counting,counting,counting,counting,counting,counting,counting,counting,counting,counting,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,intention,intention,intention,intention,intention,intention,intention,intention,intention,intention'.split(','),
            'WORDS':[9,8,6,8,10,4,6,5,7,7,7,9,6,6,6,11,6,3,8,7,11,13,8,6,14,11,13,13,10,11,12,11,16,11,9,23,12,10,19,11,10,19,14,5,10,11,14,15,11,11,8,6,4,6,7,6,5,7,9,7,10,7,8,10,4,7,10,6,7,7,14,11,18,14,13,22,17,16,12,11,20,16,16,15,18,16,20,22,14,19,21,19,17,15,22,16,22,22,18,21],
           }
        
        self.df=PyvtTbl()
        self.df.readTbl('words~ageXcondition.csv')
        
    def test001(self):
        with self.assertRaises(KeyError) as cm:
            self.df.pivot('NOTAKEY',rows=['AGE'])

        self.assertEqual(str(cm.exception),"'NOTAKEY'")
        
    def test002(self):
        with self.assertRaises(KeyError) as cm:
            self.df.pivot('CONDITION',cols=['NOTAKEY'])

        self.assertEqual(str(cm.exception),"'NOTAKEY'")

    def test003(self):
        with self.assertRaises(KeyError) as cm:
            self.df.pivot('SUBJECT',rows=['NOTAKEY','AGE'])

        self.assertEqual(str(cm.exception),"'NOTAKEY'")

    def test004(self):
        with self.assertRaises(KeyError) as cm:
            self.df.pivot('CONDITION',cols=['NOTAKEY'])

        self.assertEqual(str(cm.exception),"'NOTAKEY'")

    def test005(self):
        with self.assertRaises(TypeError) as cm:
            self.df.pivot('SUBJECT',rows='AGE')

        self.assertEqual(str(cm.exception),
                         "'str' object is not iterable")

    def test0051(self):
        with self.assertRaises(TypeError) as cm:
            self.df.pivot('SUBJECT',rows=42)

        self.assertEqual(str(cm.exception),
                         "'list' object is not iterable")
        
    def test006(self):
        with self.assertRaises(TypeError) as cm:
            self.df.pivot('SUBJECT',cols='AGE')

        self.assertEqual(str(cm.exception),
                         "'str' object is not iterable")
##    def test004(self):
##        # test the exclude parameter checking
##
##        with warnings.catch_warnings(record=True) as w:
##            # Cause all warnings to always be triggered.
##            warnings.simplefilter("always")
##            
##            # Trigger a warning.    
##            self.df.pivot('SUBJECT',
##                          where=[('AGE','not in',['medium',])])
##        
##            assert issubclass(w[-1].category, RuntimeWarning)
    
    def test005(self):
        # test the exclude parameter
        R=np.array([[14.8], [6.5], [17.6], [19.3], [7.6]])
        
        # this one shouldn't raise an Exception
        self.df.pivot('WORDS',rows=['CONDITION'],
                      where=[('AGE','not in',['old',])])
        D=np.array(self.df.Z)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)
        
    def test011(self):
        R=np.array([[25.5], [75.5]])
        
        # aggregate is case-insensitive
        self.df.pivot('SUBJECT',rows=['AGE'],aggregate='AVG')
        D=np.array(self.df.Z)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)
        
    def test0(self):
        R=np.array([[ 11. ,   7. ,  13.4,  12. ,   6.9],
                 [ 14.8,   6.5,  17.6,  19.3,   7.6]])
        
        self.df.pivot('WORDS',rows=['AGE'],cols=['CONDITION'])
        D=np.array(self.df.Z)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

    def test1(self):
        R=np.array([[ 110.,  148.],
                    [  70.,   65.],
                    [ 134.,  176.],
                    [ 120.,  193.],
                    [  69.,   76.]])
        
        self.df.pivot('WORDS',rows=['CONDITION'],cols=['AGE'],aggregate='sum')
        D=np.array(self.df.Z)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

    def test3(self):
        R=np.array([[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  11.0, 13.0, 8.0,  6.0,  14.0, 11.0, 13.0, 13.0, 10.0, 11.0, None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None, None, None, 14.0, 11.0, 18.0, 14.0, 13.0, 22.0, 17.0, 16.0, 12.0, 11.0,
                  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                 [9.0,  8.0,  6.0,  8.0,  10.0, 4.0,  6.0,  5.0,  7.0,  7.0,  None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None, None, None, 8.0,  6.0,  4.0,  6.0,  7.0,  6.0,  5.0,  7.0,  9.0,  7.0,
                  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                 [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None, None, None, 12.0, 11.0, 16.0, 11.0, 9.0, 23.0, 12.0, 10.0, 19.0, 11.0,
                  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  20.0, 16.0, 16.0, 15.0, 18.0, 16.0, 20.0, 22.0, 14.0, 19.0, None, None, None, None, None, None, None, None, None, None],
                 [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  10.0, 19.0, 14.0, 5.0,  10.0, 11.0, 14.0, 15.0, 11.0, 11.0, None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None, None, None, 21.0, 19.0, 17.0, 15.0, 22.0, 16.0, 22.0, 22.0, 18.0, 21.0],
                 [None, None, None, None, None, None, None, None, None, None, 7.0,  9.0,  6.0,  6.0,  6.0,  11.0, 6.0,  3.0,  8.0,  7.0,
                  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  10.0, 7.0,  8.0,  10.0, 4.0,  7.0,  10.0, 6.0,  7.0,  7.0,  None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]], dtype=object)


        # One row and one col factor                     
        self.df.pivot('WORDS',rows=['CONDITION'],cols=['SUBJECT'],aggregate='sum')
        D=np.array(self.df.Z)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

    def test4(self):
        R=np.array([[5.191085988]])

        # No rows or cols        
        self.df.pivot('WORDS',aggregate='stdev')
        D=np.array(self.df.Z)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

    def test5(self):
        # when the tolist aggregate the pivot operation
        # uses eval to unpack the lists
        R=np.array([[[11.0, 13.0, 8.0, 6.0, 14.0, 11.0, 13.0, 13.0, 10.0, 11.0],
                  [9.0, 8.0, 6.0, 8.0, 10.0, 4.0, 6.0, 5.0, 7.0, 7.0],
                  [12.0, 11.0, 16.0, 11.0, 9.0, 23.0, 12.0, 10.0, 19.0, 11.0],
                  [10.0, 19.0, 14.0, 5.0, 10.0, 11.0, 14.0, 15.0, 11.0, 11.0],
                  [7.0, 9.0, 6.0, 6.0, 6.0, 11.0, 6.0, 3.0, 8.0, 7.0]],
                 [[14.0, 11.0, 18.0, 14.0, 13.0, 22.0, 17.0, 16.0, 12.0, 11.0],
                  [8.0, 6.0, 4.0, 6.0, 7.0, 6.0, 5.0, 7.0, 9.0, 7.0],
                  [20.0, 16.0, 16.0, 15.0, 18.0, 16.0, 20.0, 22.0, 14.0, 19.0],
                  [21.0, 19.0, 17.0, 15.0, 22.0, 16.0, 22.0, 22.0, 18.0, 21.0],
                  [10.0, 7.0, 8.0, 10.0, 4.0, 7.0, 10.0, 6.0, 7.0, 7.0]]])

        self.df.pivot('WORDS',
                      rows=['AGE'], cols=['CONDITION'],
                      aggregate='tolist')
        D=np.array(self.df.Z)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

    def test6(self):
        # tolist handles text data differently then integer
        # or float data. We need to test this case as well
        R=np.array([[['L', 'N', 'I', 'G', 'O', 'L', 'N', 'N', 'K', 'L'],
                  ['J', 'I', 'G', 'I', 'K', 'E', 'G', 'F', 'H', 'H'],
                  ['M', 'L', 'Q', 'L', 'J', 'X', 'M', 'K', 'T', 'L'],
                  ['K', 'T', 'O', 'F', 'K', 'L', 'O', 'P', 'L', 'L'],
                  ['H', 'J', 'G', 'G', 'G', 'L', 'G', 'D', 'I', 'H']],
                 [['O', 'L', 'S', 'O', 'N', 'W', 'R', 'Q', 'M', 'L'],
                  ['I', 'G', 'E', 'G', 'H', 'G', 'F', 'H', 'J', 'H'],
                  ['U', 'Q', 'Q', 'P', 'S', 'Q', 'U', 'W', 'O', 'T'],
                  ['V', 'T', 'R', 'P', 'W', 'Q', 'W', 'W', 'S', 'V'],
                  ['K', 'H', 'I', 'K', 'E', 'H', 'K', 'G', 'H', 'H']]])

        # caesar cipher
        num2abc=dict(zip(list(range(26)),'ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
        self.df['ABC']=[num2abc[v%26] for v in self.df['WORDS']]

        self.df.pivot('ABC',
                      rows=['AGE'], cols=['CONDITION'],
                      aggregate='tolist')
        
        D=np.array(self.df.Z)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

    def test7(self):
        # test group_concat
        R=np.array( [[u'11,13,8,6,14,11,13,13,10,11',
                      u'9,8,6,8,10,4,6,5,7,7',
                      u'12,11,16,11,9,23,12,10,19,11',
                      u'10,19,14,5,10,11,14,15,11,11',
                      u'7,9,6,6,6,11,6,3,8,7'],
                     [u'14,11,18,14,13,22,17,16,12,11',
                      u'8,6,4,6,7,6,5,7,9,7',
                      u'20,16,16,15,18,16,20,22,14,19',
                      u'21,19,17,15,22,16,22,22,18,21',
                      u'10,7,8,10,4,7,10,6,7,7']])
        self.df.pivot('WORDS',
                      rows=['AGE'], cols=['CONDITION'],
                      aggregate='group_concat')
        D=np.array(self.df.Z)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessEqual(d,r)
##            
class Test_pivot_2(unittest.TestCase):
    def setUp(self):
        self.df=PyvtTbl()
        self.df.readTbl('error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        
    def test0(self):
              # M 1  2  3
        R=np.array([[2, 2, 2],  # T1 C1
                 [3, 1, 2],  # T1 C2
                 [3, 3, 3],  # T1 C3
                 [3, 3, 3],  # T2 C1
                 [3, 3, 3],  # T2 C2
                 [3, 3, 3]]) # T2 C3
        
        self.df.pivot('ERROR',rows=['TIMEOFDAY','COURSE'],
                      cols=['MODEL'],aggregate='count')
        D=np.array(self.df.Z)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

    def test1(self):
        # check to make sure missing cells are correct
        R=np.array([[1, 1, 1, 1, 1, 1],
                 [1, 1, 0, 1, 0, 1],
                 [1, 1, 1, 1, 1, 1],
                 [0, 1, 0, 1, 0, 1],
                 [1, 1, 1, 1, 1, 1],
                 [1, 1, 1, 1, 1, 1],
                 [1, 1, 1, 1, 1, 1],
                 [1, 1, 0, 1, 1, 1],
                 [1, 1, 1, 1, 1, 1]])
        
        # multiple rows and cols
        self.df.pivot('ERROR',rows=['SUBJECT','COURSE'],
                      cols=['MODEL','TIMEOFDAY'],aggregate='count')
        D=np.array(self.df.Z)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

    def test2(self):          
        R=np.array([[ 0.26882528, -0.06797845]])

        # No row
        self.df.pivot('ERROR',cols=['TIMEOFDAY'],aggregate='skew')
        D=np.array(self.df.Z)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

    def test3(self):              
        R=np.array([[ 0.26882528],
                 [-0.06797845]])

        # No col
        self.df.pivot('ERROR',rows=['TIMEOFDAY'],aggregate='skew')
        D=np.array(self.df.Z)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

class Test_writeTable(unittest.TestCase):
    def setUp(self):
        self.df=PyvtTbl()
        self.df.readTbl('suppression~subjectXgroupXageXcycleXphase.csv')

    def test0(self):
        d='suppression~subjectXgroupXageXcycleXphase.csv'
        r='subjectXsexXageXgroupXcycleXphaseXsuppressionXranddata.csv'
        self.df.writeTable()
        self.assertTrue(fcmp(d,r))

        # clean up
        os.remove('./subjectXsexXageXgroupXcycleXphaseXsuppressionXranddata.csv')        

    def test1(self):
        # with exclusion
        d='suppression~subjectXgroupXageXcycleXphase.csv'
        r='subjectXsexXageXgroupXcycleXphaseXsuppressionXranddata.csv'
        self.df.writeTable(where=[('AGE','not in',['young'])])
        self.assertTrue(fcmp(d,r))

        # clean up
        os.remove('./subjectXsexXageXgroupXcycleXphaseXsuppressionXranddata.csv') 

class Test_selectCol(unittest.TestCase):
    def setUp(self):
        self.df=PyvtTbl()
        self.df.readTbl('suppression~subjectXgroupXageXcycleXphase.csv')
    
    def test0(self):
        R=[33.0, 43.0, 40.0, 52.0, 39.0, 52.0, 38.0, 48.0, 4.0, 35.0, 9.0, 42.0, 4.0, 46.0, 23.0, 51.0, 32.0, 39.0, 38.0, 47.0, 24.0, 44.0, 16.0, 40.0, 17.0, 34.0, 21.0, 41.0, 27.0, 50.0, 13.0, 40.0, 44.0, 52.0, 37.0, 48.0, 33.0, 53.0, 33.0, 43.0, 12.0, 16.0, 9.0, 39.0, 9.0, 59.0, 13.0, 45.0, 18.0, 42.0, 3.0, 62.0, 45.0, 49.0, 60.0, 57.0, 13.0, 29.0, 14.0, 44.0, 9.0, 50.0, 15.0, 48.0]
        D=self.df.selectCol('SUPPRESSION',
                            where=[('AGE','not in',['young']),
                                   ('GROUP','not in',['AB','AA'])])
        for r,d in zip(R,D):
            self.assertAlmostEqual(r,d)
             
class Test_writePivot(unittest.TestCase):
    def setUp(self):
        self.df=PyvtTbl()
        self.df.readTbl('suppression~subjectXgroupXageXcycleXphase.csv')

    def test0(self):
        # self.assertEqual doesn't like really long comparisons
        # so we will break it up into lines
        R=['"avg(SUPPRESSION) where GROUP not in [\'AB\'] and  CYCLE not in [1, 2]"\r\n',
           'GROUP,CYCLE=3_AGE=old,CYCLE=3_AGE=young,CYCLE=4_AGE=old,CYCLE=4_AGE=young\r\n',
           'AA,21.9375,10.0125,22.25,10.5125\r\n',
           'LAB,37.0625,12.5375,36.4375,12.0375\r\n']
        
        self.df.pivot('SUPPRESSION',
                 rows=['GROUP'],
                 cols=['CYCLE','AGE'],
                 aggregate='avg',
                 where=[('GROUP','not in',['AB']),
                        ('CYCLE','not in',[1,2])])
        self.df.writePivot()

        D=[]
        # write pivot should generate this name
                   
        with open('suppression~(group)Z(cycleXage).csv','rb') as f:
            D=f.readlines()

        for d,r in zip(D,R):
            self.failUnlessEqual(d,r)

        # clean up
##        os.remove('./suppression~(group)Z(cycleXage).csv')
            
    def test1(self):
        # same as test0 except we are specifying a filename
        # and specifying the delimiter as \t
        R=['"avg(SUPPRESSION) where GROUP not in [\'AB\'] and  CYCLE not in [1, 2]"\r\n',
           'GROUP\tCYCLE=3.0_AGE=old\tCYCLE=3.0_AGE=young\tCYCLE=4.0_AGE=old\tCYCLE=4.0_AGE=young\r\n',
           'AA\t21.9375\t10.0125\t22.25\t10.5125\r\n',
           'LAB\t37.0625\t12.5375\t36.4375\t12.0375\r\n']
        
        self.df.pivot('SUPPRESSION',
                 rows=['GROUP'],
                 cols=['CYCLE','AGE'],
                 aggregate='avg',
                 where=[('GROUP','not in',['AB']),
                        ('CYCLE','not in',[1,2])])
        self.df.writePivot('myname.dat','\t')

        # clean up
        os.remove('./myname.dat')

    def test2(self):
        # no exclusions this time
        R=['avg(SUPPRESSION)\r\n',
           'GROUP,CYCLE=1_AGE=old,CYCLE=1_AGE=young,CYCLE=2_AGE=old,CYCLE=2_AGE=young,CYCLE=3_AGE=old,CYCLE=3_AGE=young,CYCLE=4_AGE=old,CYCLE=4_AGE=young\r\n',
           'AA,19.3125,8.4875,25.25,10.2375,21.9375,10.0125,22.25,10.5125\r\n',
           'AB,17.6875,7.1,32.3125,10.9625,33.0625,11.8,33.6875,10.3\r\n',
           'LAB,28.9375,10.7875,34.125,12.1375,37.0625,12.5375,36.4375,12.0375\r\n']

        
        self.df.pivot('SUPPRESSION',
                 rows=['GROUP'],
                 cols=['CYCLE','AGE'],
                 aggregate='avg')
        self.df.writePivot('pivot_test2.csv')

        D=[]
        # write pivot should generate this name
        with open('pivot_test2.csv','rb') as f:
            D=f.readlines()

        for d,r in zip(D,R):
            self.failUnlessEqual(d,r)

        # clean up
        os.remove('./pivot_test2.csv')        

    def test3(self):
        # try to write pivot table when table doesn't exist
        with self.assertRaises(Exception) as cm:
            self.df.writePivot('pivot_test3.csv')

        self.assertEqual(str(cm.exception),
                         'must call pivot before writing pivot table')        
        
    def test4(self):
        R = 'avg(SUPPRESSION)\r\nCYCLE=1_AGE=old,CYCLE=1_AGE=young,CYCLE=2_AGE=old,CYCLE=2_AGE=young,CYCLE=3_AGE=old,CYCLE=3_AGE=young,CYCLE=4_AGE=old,CYCLE=4_AGE=young\r\n21.9791666667,8.79166666667,30.5625,11.1125,30.6875,11.45,30.7916666667,10.95\r\n'
        # rows not specified
        self.df.pivot('SUPPRESSION',
                 cols=['CYCLE','AGE'],
                 aggregate='avg')
        self.df.writePivot()

        # write pivot should generate this name
        with open('suppression~()Z(cycleXage).csv','rb') as f:
            D=f.read()

        self.failUnlessEqual(D,R)

        # clean up
        os.remove('./suppression~()Z(cycleXage).csv')

    def test5(self):
        R = 'avg(SUPPRESSION)\r\nCYCLE,AGE,Value\r\n1,old,21.9791666667\r\n1,young,8.79166666667\r\n2,old,30.5625\r\n2,young,11.1125\r\n3,old,30.6875\r\n3,young,11.45\r\n4,old,30.7916666667\r\n4,young,10.95\r\n'
        # cols not specified
        self.df.pivot('SUPPRESSION',
                 rows=['CYCLE','AGE'],
                 aggregate='avg')
        self.df.writePivot()

        # write pivot should generate this name
        with open('suppression~(cycleXage)Z().csv','rb') as f:
            D=f.read()

        self.failUnlessEqual(D,R)

        # clean up
        os.remove('./suppression~(cycleXage)Z().csv')

    def test6(self):
        R = 'count(SUPPRESSION)\r\nValue\r\n384\r\n'
        
        # no rows or cols not specified
        self.df.pivot('SUPPRESSION',
                 aggregate='count')
        self.df.writePivot(delimiter='\t') # check .tsv functionality

        # write pivot should generate this name
        with open('suppression~()Z().tsv','rb') as f:
            D=f.read()

        self.failUnlessEqual(D,R)

        # clean up
        os.remove('./suppression~()Z().tsv')

    def test7(self):        
        # no rows or cols not specified
        self.df.pivot('SUPPRESSION',
                 aggregate='count')
        
        with self.assertRaises(Exception) as cm:
            self.df.writePivot([]) # non-str filename

        self.assertEqual(str(cm.exception),
                         'fname must be a string')
        
class Test_marginals(unittest.TestCase):
    def test0(self):
        self.df=PyvtTbl()
        self.df.readTbl('words~ageXcondition.csv')

        x=self.df.marginals('WORDS',factors=['AGE','CONDITION'])
        [f,dmu,dN,dsem,dlower,dupper]=x

        for d,r in zip(dmu,[11,7,13.4,12,6.9,14.8,6.5,17.6,19.3,7.6]):
            self.failUnlessAlmostEqual(d,r)

        for d,r in zip(dN,[10,10,10,10,10,10,10,10,10,10]):
            self.failUnlessAlmostEqual(d,r)

        for d,r in zip(dsem,[0.788810638,
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

class Test_hist(unittest.TestCase):
    def test0(self):
        R=[[4.0, 14.0, 17.0, 12.0, 15.0, 10.0, 9.0, 5.0, 6.0, 8.0],
           [3.0, 5.0, 7.0, 9.0, 11.0, 13.0, 15.0, 17.0, 19.0, 21.0, 23.0]]
        
        df=PyvtTbl()
        df.readTbl('words~ageXcondition.csv')
        D=df.hist('WORDS')
        D=[D[0],D[1]]

        for (d,r) in zip(_flatten(D),_flatten(R)):
            self.assertAlmostEqual(d,r)

class Test_plotHist(unittest.TestCase):
    def test0(self):
        df=PyvtTbl()
        df.readTbl('words~ageXcondition.csv')
        D=df.plotHist('WORDS')
            
class Test_plotMarginals(unittest.TestCase):
    # TODO: check checking
    def test0(self):
        R = {'aggregate': None,
             'clevels': [1],
             'fname': 'words~ageXcondition',
             'maintitle': 'WORDS by AGE * CONDITION',
             'numcols': 1,
             'numrows': 1,
             'rlevels': [1],
             'subplot_titles': [''],
             'xmaxs': [1.5],
             'xmins': [-0.5],
             'y': [[[11.0, 14.8], [7.0, 6.5], [13.4, 17.6], [12.0, 19.3], [6.9, 7.6]]],
             'yerr': [[]],
             'ymin': 0.0,
             'ymax': 27.183257964740832}
        
        # a simple plot
        df=PyvtTbl()
        df.TESTMODE=True
        df.readTbl('words~ageXcondition.csv')
        D=df.plotMarginals('WORDS','AGE','CONDITION')

        self.assertEqual(D['aggregate'],R['aggregate'])
        self.assertEqual(D['clevels'],R['clevels'])
        self.assertEqual(D['rlevels'],R['rlevels'])
        self.assertEqual(D['numcols'],R['numcols'])
        self.assertEqual(D['numrows'],R['numrows'])
        self.assertEqual(D['fname'],R['fname'])
        self.assertEqual(D['maintitle'],R['maintitle'])
        self.assertEqual(D['subplot_titles'],R['subplot_titles'])
        self.assertAlmostEqual(D['ymin'],R['ymin'])
        self.assertAlmostEqual(D['ymax'],R['ymax'])

        for d,r in zip(np.array(D['y']).flat,np.array(R['y']).flat):
            self.assertAlmostEqual(d,r)

        for d,r in zip(np.array(D['yerr']).flat,np.array(R['yerr']).flat):
            self.assertAlmostEqual(d,r)
        
    def test1(self):
        R = {'aggregate': None,
             'clevels': ['M1', 'M2', 'M3'],
             'fname': 'error~timeofdayXcourseXmodel',
             'maintitle': 'ERROR by TIMEOFDAY * COURSE * MODEL',
             'numcols': 3,
             'numrows': 1,
             'rlevels': [1],
             'subplot_titles': ['M1', 'M2', 'M3'],
             'xmaxs': [1.5, 1.5, 1.5],
             'xmins': [-0.5, -0.5, -0.5],
             'y': [[[7.166666666666667, 3.2222222222222223], [6.5, 2.888888888888889], [4.0, 1.5555555555555556]], [[7.166666666666667, 3.2222222222222223], [6.5, 2.888888888888889], [4.0, 1.5555555555555556]], [[7.166666666666667, 3.2222222222222223], [6.5, 2.888888888888889], [4.0, 1.5555555555555556]]],
             'yerr': [[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]],
             'ymax': 11.119188627248182,
             'ymin': 0.0}
        
        # specify yerr
        df=PyvtTbl()
        df.TESTMODE = True
        df.readTbl('error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        D=df.plotMarginals('ERROR','TIMEOFDAY',
                                seplines='COURSE',
                                sepxplots='MODEL',yerr=1.)

        self.assertEqual(D['aggregate'],R['aggregate'])
        self.assertEqual(D['clevels'],R['clevels'])
        self.assertEqual(D['rlevels'],R['rlevels'])
        self.assertEqual(D['numcols'],R['numcols'])
        self.assertEqual(D['numrows'],R['numrows'])
        self.assertEqual(D['fname'],R['fname'])
        self.assertEqual(D['maintitle'],R['maintitle'])
        self.assertEqual(D['subplot_titles'],R['subplot_titles'])
        self.assertAlmostEqual(D['ymin'],R['ymin'])
        self.assertAlmostEqual(D['ymax'],R['ymax'])

        for d,r in zip(np.array(D['y']).flat,np.array(R['y']).flat):
            self.assertAlmostEqual(d,r)

        for d,r in zip(np.array(D['yerr']).flat,np.array(R['yerr']).flat):
            self.assertAlmostEqual(d,r)

    def test2(self):
        R = {'aggregate': 'ci',
             'clevels': [1],
             'fname': 'suppression~cycleXageXphase',
             'maintitle': 'SUPPRESSION by CYCLE * AGE * PHASE',
             'numcols': 1,
             'numrows': 2,
             'rlevels': ['I', 'II'],
             'subplot_titles': ['I', 'II'],
             'xmaxs': [4.1749999999999998, 4.1749999999999998],
             'xmins': [0.32499999999999996, 0.32499999999999996],
             'y': [[[21.979166666666668, 30.5625, 30.6875, 30.791666666666668], [8.791666666666668, 11.112499999999995, 11.449999999999998, 10.950000000000001]], [[21.979166666666668, 30.5625, 30.6875, 30.791666666666668], [8.791666666666668, 11.112499999999995, 11.449999999999998, 10.950000000000001]]],
             'yerr': [[1.5806317070654425, 1.0647384230760477, 1.3467210191966632, 1.1532196680758091], [1.5806317070654425, 1.0647384230760477, 1.3467210191966632, 1.1532196680758091]],
             'ymax': 64.8719707118471,
             'ymin': 0.0}
        
        # generate yerr
        df=PyvtTbl()
        df.TESTMODE = True
        df.readTbl('suppression~subjectXgroupXageXcycleXphase.csv')

        D = df.plotMarginals('SUPPRESSION','CYCLE',
                            seplines='AGE',
                            sepyplots='PHASE',yerr='ci')

        self.assertEqual(D['aggregate'],R['aggregate'])
        self.assertEqual(D['clevels'],R['clevels'])
        self.assertEqual(D['rlevels'],R['rlevels'])
        self.assertEqual(D['numcols'],R['numcols'])
        self.assertEqual(D['numrows'],R['numrows'])
        self.assertEqual(D['fname'],R['fname'])
        self.assertEqual(D['maintitle'],R['maintitle'])
        self.assertEqual(D['subplot_titles'],R['subplot_titles'])
        self.assertAlmostEqual(D['ymin'],R['ymin'])
        self.assertAlmostEqual(D['ymax'],R['ymax'])
        
        for d,r in zip(np.array(D['y']).flat,np.array(R['y']).flat):
            self.assertAlmostEqual(d,r)

        for d,r in zip(np.array(D['yerr']).flat,np.array(R['yerr']).flat):
            self.assertAlmostEqual(d,r)

    def test3(self):
        R = {'aggregate': 'ci',
             'clevels': ['I', 'II'],
             'fname': 'suppression~cycleXageXphaseXgroup',
             'maintitle': 'SUPPRESSION by CYCLE * AGE * PHASE * GROUP',
             'numcols': 2,
             'numrows': 2,
             'rlevels': ['AA', 'AB'],
             'subplot_titles': ['GROUP = AA, PHASE = AA', 'GROUP = AA, PHASE = AA', 'GROUP = AB, PHASE = AB', 'GROUP = AB, PHASE = AB'],
             'xmaxs': [4.1500000000000004, 4.1500000000000004, 4.1500000000000004, 4.1500000000000004],
             'xmins': [0.84999999999999998, 0.84999999999999998, 0.84999999999999998, 0.84999999999999998],
             'y': [[[18.5, 28.78125, 27.5, 27.96875], [7.793750000000001, 10.599999999999996, 10.90625, 10.406249999999998]],
                   [[18.5, 28.78125, 27.5, 27.96875], [7.793750000000001, 10.599999999999996, 10.90625, 10.406249999999998]],
                   [[18.5, 28.78125, 27.5, 27.96875], [7.793750000000001, 10.599999999999996, 10.90625, 10.406249999999998]],
                   [[18.5, 28.78125, 27.5, 27.96875], [7.793750000000001, 10.599999999999996, 10.90625, 10.406249999999998]]],
             'yerr': [[1.9389820403558615, 1.2681503421608105, 1.691832428382257, 1.2797605110823689], [1.9389820403558615, 1.2681503421608105, 1.691832428382257, 1.2797605110823689], [1.9389820403558615, 1.2681503421608105, 1.691832428382257, 1.2797605110823689], [1.9389820403558615, 1.2681503421608105, 1.691832428382257, 1.2797605110823689]],
             'ymax': 64.8719707118471,
             'ymin': 0.0}
                    
        # separate y plots and separate x plots
        df=PyvtTbl()
        df.TESTMODE = True
        df.readTbl('suppression~subjectXgroupXageXcycleXphase.csv')

        D = df.plotMarginals('SUPPRESSION','CYCLE',
                              seplines='AGE',
                              sepxplots='PHASE',
                              sepyplots='GROUP',yerr='ci',
                              where=[('GROUP','not in',['LAB'])])
   
        self.assertEqual(D['aggregate'],R['aggregate'])
        self.assertEqual(D['clevels'],R['clevels'])
        self.assertEqual(D['rlevels'],R['rlevels'])
        self.assertEqual(D['numcols'],R['numcols'])
        self.assertEqual(D['numrows'],R['numrows'])
        self.assertEqual(D['fname'],R['fname'])
        self.assertEqual(D['maintitle'],R['maintitle'])
        self.assertEqual(D['subplot_titles'],R['subplot_titles'])
        self.assertAlmostEqual(D['ymin'],R['ymin'])
        self.assertAlmostEqual(D['ymax'],R['ymax'])
        
        for d,r in zip(np.array(D['y']).flat,np.array(R['y']).flat):
            self.assertAlmostEqual(d,r)

        for d,r in zip(np.array(D['yerr']).flat,np.array(R['yerr']).flat):
            self.assertAlmostEqual(d,r)



    # the code for when seplines=None is in a different branch
    # these test that code
    def test4(self):
        R = {'aggregate': None,
             'clevels': ['adjective', 'counting', 'imagery', 'intention', 'rhyming'],
             'fname': 'words~ageXcondition',
             'maintitle': 'WORDS by AGE * CONDITION',
             'numcols': 5,
             'numrows': 1,
             'rlevels': [1],
             'subplot_titles': ['adjective', 'counting', 'imagery', 'intention', 'rhyming'],
             'xmaxs': [1.5, 1.5, 1.5, 1.5, 1.5],
             'xmins': [-0.5, -0.5, -0.5, -0.5, -0.5],
             'y': [[10.06, 13.16], [10.06, 13.16], [10.06, 13.16], [10.06, 13.16], [10.06, 13.16]],
             'yerr': [[], [], [], [], []],
             'ymax': 27.183257964740832,
             'ymin': 0.0}
        
        # a simple plot
        df=PyvtTbl()
        df.TESTMODE = True
        df.readTbl('words~ageXcondition.csv')
        D = df.plotMarginals('WORDS','AGE',sepxplots='CONDITION')

        self.assertEqual(D['aggregate'],R['aggregate'])
        self.assertEqual(D['clevels'],R['clevels'])
        self.assertEqual(D['rlevels'],R['rlevels'])
        self.assertEqual(D['numcols'],R['numcols'])
        self.assertEqual(D['numrows'],R['numrows'])
        self.assertEqual(D['fname'],R['fname'])
        self.assertEqual(D['maintitle'],R['maintitle'])
        self.assertEqual(D['subplot_titles'],R['subplot_titles'])
        self.assertAlmostEqual(D['ymin'],R['ymin'])
        self.assertAlmostEqual(D['ymax'],R['ymax'])
        
        for d,r in zip(np.array(D['y']).flat,np.array(R['y']).flat):
            self.assertAlmostEqual(d,r)

        for d,r in zip(np.array(D['yerr']).flat,np.array(R['yerr']).flat):
            self.assertAlmostEqual(d,r)
        
    def test5(self):
        R = {'aggregate': None,
             'clevels': ['M1', 'M2', 'M3'],
             'fname': 'error~timeofdayXmodel',
             'maintitle': 'ERROR by TIMEOFDAY * MODEL',
             'numcols': 3,
             'numrows': 1,
             'rlevels': [1],
             'subplot_titles': ['M1', 'M2', 'M3'],
             'xmaxs': [1.5, 1.5, 1.5],
             'xmins': [-0.5, -0.5, -0.5],
             'y': [[5.619047619047619, 2.5555555555555554], [5.619047619047619, 2.5555555555555554], [5.619047619047619, 2.5555555555555554]],
             'yerr': [[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]],
             'ymax': 11.119188627248182,
             'ymin': 0.0}
                    
        # specify yerr
        df=PyvtTbl()
        df.TESTMODE = True
        df.readTbl('error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        D = df.plotMarginals('ERROR','TIMEOFDAY',
                                sepxplots='MODEL',yerr=1.) 

        self.assertEqual(D['aggregate'],R['aggregate'])
        self.assertEqual(D['clevels'],R['clevels'])
        self.assertEqual(D['rlevels'],R['rlevels'])
        self.assertEqual(D['numcols'],R['numcols'])
        self.assertEqual(D['numrows'],R['numrows'])
        self.assertEqual(D['fname'],R['fname'])
        self.assertEqual(D['maintitle'],R['maintitle'])
        self.assertEqual(D['subplot_titles'],R['subplot_titles'])
        self.assertAlmostEqual(D['ymin'],R['ymin'])
        self.assertAlmostEqual(D['ymax'],R['ymax'])
        
        for d,r in zip(np.array(D['y']).flat,np.array(R['y']).flat):
            self.assertAlmostEqual(d,r)

        for d,r in zip(np.array(D['yerr']).flat,np.array(R['yerr']).flat):
            self.assertAlmostEqual(d,r)
            
    def test6(self):
        R = {'aggregate': 'ci',
             'clevels': [1],
             'fname': 'suppression~cycleXphase',
             'maintitle': 'SUPPRESSION by CYCLE * PHASE',
             'numcols': 1,
             'numrows': 2,
             'rlevels': ['I', 'II'],
             'subplot_titles': ['I', 'II'],
             'xmaxs': [4.1749999999999998, 4.1749999999999998],
             'xmins': [0.82499999999999996, 0.82499999999999996],
             'y': [[15.38541666666667, 20.8375, 21.068749999999998, 20.870833333333326], [15.38541666666667, 20.8375, 21.068749999999998, 20.870833333333326]],
             'yerr': [[2.61145375321679, 2.949214252328975, 3.12200931549039, 3.261774931685317], [2.61145375321679, 2.949214252328975, 3.12200931549039, 3.261774931685317]],
             'ymax': 64.8719707118471,
             'ymin': 0.0}
        
        # generate yerr
        df=PyvtTbl()
        df.TESTMODE = True
        df.readTbl('suppression~subjectXgroupXageXcycleXphase.csv')
        D = df.plotMarginals('SUPPRESSION','CYCLE',
                              sepyplots='PHASE',yerr='ci') 

        self.assertEqual(D['aggregate'],R['aggregate'])
        self.assertEqual(D['clevels'],R['clevels'])
        self.assertEqual(D['rlevels'],R['rlevels'])
        self.assertEqual(D['numcols'],R['numcols'])
        self.assertEqual(D['numrows'],R['numrows'])
        self.assertEqual(D['fname'],R['fname'])
        self.assertEqual(D['maintitle'],R['maintitle'])
        self.assertEqual(D['subplot_titles'],R['subplot_titles'])
        self.assertAlmostEqual(D['ymin'],R['ymin'])
        self.assertAlmostEqual(D['ymax'],R['ymax'])
        
        for d,r in zip(np.array(D['y']).flat,np.array(R['y']).flat):
            self.assertAlmostEqual(d,r)

        for d,r in zip(np.array(D['yerr']).flat,np.array(R['yerr']).flat):
            self.assertAlmostEqual(d,r)

    def test7(self):
        R = {'aggregate': 'ci',
             'clevels': ['I', 'II'],
             'fname': 'suppression~cycleXphaseXgroup',
             'maintitle': 'SUPPRESSION by CYCLE * PHASE * GROUP',
             'numcols': 2,
             'numrows': 2,
             'rlevels': ['AA', 'AB'],
             'subplot_titles': ['GROUP = AA, PHASE = AA', 'GROUP = AA, PHASE = AA', 'GROUP = AB, PHASE = AB', 'GROUP = AB, PHASE = AB'],
             'xmaxs': [4.1500000000000004, 4.1500000000000004, 4.1500000000000004, 4.1500000000000004],
             'xmins': [0.84999999999999998, 0.84999999999999998, 0.84999999999999998, 0.84999999999999998],
             'y': [[13.146875000000005, 19.690624999999997, 19.203124999999996, 19.187500000000004], [13.146875000000005, 19.690624999999997, 19.203124999999996, 19.187500000000004], [13.146875000000005, 19.690624999999997, 19.203124999999996, 19.187500000000004], [13.146875000000005, 19.690624999999997, 19.203124999999996, 19.187500000000004]],
             'yerr': [[2.973964360180699, 3.346152147793127, 3.4887686723195532, 3.8861848793729132], [2.973964360180699, 3.346152147793127, 3.4887686723195532, 3.8861848793729132], [2.973964360180699, 3.346152147793127, 3.4887686723195532, 3.8861848793729132], [2.973964360180699, 3.346152147793127, 3.4887686723195532, 3.8861848793729132]],
             'ymax': 64.8719707118471,
             'ymin': 0.0}
        
        # separate y plots and separate x plots
        df=PyvtTbl()
        df.TESTMODE = True
        df.readTbl('suppression~subjectXgroupXageXcycleXphase.csv')

        D = df.plotMarginals('SUPPRESSION','CYCLE',
                              sepxplots='PHASE',
                              sepyplots='GROUP',yerr='ci',
                              where=[('GROUP','not in',['LAB'])])
        
        self.assertEqual(D['aggregate'],R['aggregate'])
        self.assertEqual(D['clevels'],R['clevels'])
        self.assertEqual(D['rlevels'],R['rlevels'])
        self.assertEqual(D['numcols'],R['numcols'])
        self.assertEqual(D['numrows'],R['numrows'])
        self.assertEqual(D['fname'],R['fname'])
        self.assertEqual(D['maintitle'],R['maintitle'])
        self.assertEqual(D['subplot_titles'],R['subplot_titles'])
        self.assertAlmostEqual(D['ymin'],R['ymin'])
        self.assertAlmostEqual(D['ymax'],R['ymax'])
        
        for d,r in zip(np.array(D['y']).flat,np.array(R['y']).flat):
            self.assertAlmostEqual(d,r)

        for d,r in zip(np.array(D['yerr']).flat,np.array(R['yerr']).flat):
            self.assertAlmostEqual(d,r)
            
class Test_descriptives(unittest.TestCase):
    def test0(self):
        self.df=PyvtTbl()
        self.df.readTbl('words~ageXcondition.csv')

        D=self.df.descriptives('WORDS')
        
        R={}
        R['count']      = 100.
        R['mean']       = 11.61
        R['var']        = 26.94737374
        R['stdev']      = 5.191085988
        R['sem']        = 5.191085988/10.
        R['rms']        = 12.70708464
        R['min']        = 3.
        R['max']        = 23.
        R['range']      = 20.
        R['median']     = 11.
        R['95ci_lower'] = 11.61-.5191085988*1.96
        R['95ci_upper'] = 11.61+.5191085988*1.96

        for k in D.keys():
            self.failUnlessAlmostEqual(D[k],R[k])

class Test_validate(unittest.TestCase):
    def test0(self):
        from pyvttbl import _isint, _isfloat

        df=PyvtTbl()
        df.readTbl('suppression~subjectXgroupXageXcycleXphase.csv')
        df['RANDDATA'][42]='nan'

        R=df.validate({'GROUP' : lambda x: x in ['AA', 'AB', 'LAB'],
                         'SEX' : lambda x: x in [0],
                 'SUPPRESSION' : lambda x: x < 62.,
                    'RANDDATA' : lambda x: _isfloat(x),
                     'SUBJECT' : _isint}, verbose=False, report=False)
        self.assertFalse(R)


    def test1(self):
        from pyvttbl import _isint, _isfloat

        df=PyvtTbl()
        df.readTbl('suppression~subjectXgroupXageXcycleXphase.csv')
        ##df['RANDDATA'][42]='nan'

        R=df.validate({'GROUP' : lambda x: x in ['AA', 'AB', 'LAB'],
                         'SEX' : lambda x: x in [0,1],
                 'SUPPRESSION' : lambda x: x < 1000.,
                    'RANDDATA' : lambda x: _isfloat(x),
                     'SUBJECT' : _isint}, verbose=False, report=False)
        self.assertTrue(R)
        
    def test2(self):
        from pyvttbl import _isint, _isfloat

        df=PyvtTbl()
        df.readTbl('suppression~subjectXgroupXageXcycleXphase.csv')
        ##df['RANDDATA'][42]='nan'

        R=df.validate({'GROUP' : lambda x: x in ['AA', 'AB', 'LAB'],
                         'SEX' : lambda x: x in [0,1],
                 'SUPPRESSION' : lambda x: x < 1000.,
                    'RANDDATA' : lambda x: _isfloat(x) and not isnan(x),
                     'SUBJECT' : _isint(1),
                  'NOT_A_COL1' : _isint,
                  'NOT_A_COL2' : _isint}, verbose=False, report=False)
        self.assertFalse(R)

    def test3(self):
        df=PyvtTbl()
        
        with self.assertRaises(Exception) as cm:
            df.validate({'GROUP' : lambda x: x in ['AA', 'AB', 'LAB']})

        self.assertEqual(str(cm.exception),
                         'table must have data to validate data')

    def test4(self):
        df=PyvtTbl()
        df.insert([('GROUP','AA'),('VAL',1)])
        
        with self.assertRaises(Exception) as cm:
            df.validate(lambda x: x in ['AA', 'AB', 'LAB'])

        self.assertEqual(str(cm.exception),
                         'criteria must be mappable type')

def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_readTbl),
            unittest.makeSuite(Test__setitem__),
            unittest.makeSuite(Test__delitem__),
            unittest.makeSuite(Test_insert),
            unittest.makeSuite(Test_attach),
            unittest.makeSuite(Test_sort),
            unittest.makeSuite(Test_pivot_1),
            unittest.makeSuite(Test_pivot_2),
            unittest.makeSuite(Test_marginals),
            unittest.makeSuite(Test_selectCol),
            unittest.makeSuite(Test_hist),
            unittest.makeSuite(Test_plotHist),
            unittest.makeSuite(Test_plotMarginals),
            unittest.makeSuite(Test_writeTable),
            unittest.makeSuite(Test_writePivot),
            unittest.makeSuite(Test_descriptives),
            unittest.makeSuite(Test_validate),
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
    
