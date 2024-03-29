# Copyright (c) 2011-2024, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.

import unittest

import difflib


from pyvttbl import DataFrame, PyvtTbl
from pyvttbl.misc.support import *

class Test_pivot_1(unittest.TestCase):
    def setUp(self):
        D={
            'SUBJECT':[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100],
            'AGE':'old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young'.split(','),
            'CONDITION':'counting,counting,counting,counting,counting,counting,counting,counting,counting,counting,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,intention,intention,intention,intention,intention,intention,intention,intention,intention,intention,counting,counting,counting,counting,counting,counting,counting,counting,counting,counting,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,intention,intention,intention,intention,intention,intention,intention,intention,intention,intention'.split(','),
            'WORDS':[9,8,6,8,10,4,6,5,7,7,7,9,6,6,6,11,6,3,8,7,11,13,8,6,14,11,13,13,10,11,12,11,16,11,9,23,12,10,19,11,10,19,14,5,10,11,14,15,11,11,8,6,4,6,7,6,5,7,9,7,10,7,8,10,4,7,10,6,7,7,14,11,18,14,13,22,17,16,12,11,20,16,16,15,18,16,20,22,14,19,21,19,17,15,22,16,22,22,18,21],
           }
        
        self.df=DataFrame()
        self.df.read_tbl('data/words~ageXcondition.csv')
        
    def test0(self):
        R="""\
avg(WORDS)
 AGE    CONDITION=adjective   CONDITION=counting   CONDITION=imagery   CONDITION=intention   CONDITION=rhyming   Total  
=======================================================================================================================
old                      11                    7              13.400                    12               6.900   10.060 
young                14.800                6.500              17.600                19.300               7.600   13.160 
=======================================================================================================================
Total                12.900                6.750              15.500                15.650               7.250   11.610 """
        
        D = self.df.pivot('WORDS',rows=['AGE'],cols=['CONDITION'])

##        print(repr(D))

        # verify the values in the table
        self.failUnlessEqual(str(D),R)

    def test2(self):
        R="""\
avg(WORDS)
CONDITION=adjective   CONDITION=counting   CONDITION=imagery   CONDITION=intention   CONDITION=rhyming   Total  
===============================================================================================================
             12.900                6.750              15.500                15.650               7.250   11.610 """
        
        D = self.df.pivot('WORDS', cols=['CONDITION'])
        
        # verify the values in the table
        self.failUnlessEqual(str(D),R)

    def test3(self):
        R="""\
avg(WORDS)
CONDITION   Value  
==================
adjective   12.900 
counting     6.750 
imagery     15.500 
intention   15.650 
rhyming      7.250 
==================
Total       11.610 """
        
        D = self.df.pivot('WORDS', rows=['CONDITION'])
        
        # verify the values in the table
        self.failUnlessEqual(str(D),R)
        
    def test4(self):
        R="""\
stdev(WORDS)
Value 
=====
5.191 """

        # No rows or cols        
        D = self.df.pivot('WORDS',aggregate='stdev')
        
        # verify the values in the table
        self.failUnlessEqual(str(D),R)

    def test6(self):
        # tolist handles text data differently then integer
        # or float data. We need to test this case as well
        R="""\
tolist(ABC)
 AGE                   CONDITION=adjective                                   CONDITION=counting                                   CONDITION=imagery                                   CONDITION=intention                                   CONDITION=rhyming
==============================================================================================================================================================================================================================================================================
old     ['L', 'N', 'I', 'G', 'O', 'L', 'N', 'N', 'K', 'L']   ['J', 'I', 'G', 'I', 'K', 'E', 'G', 'F', 'H', 'H']   ['M', 'L', 'Q', 'L', 'J', 'X', 'M', 'K', 'T', 'L']   ['K', 'T', 'O', 'F', 'K', 'L', 'O', 'P', 'L', 'L']   ['H', 'J', 'G', 'G', 'G', 'L', 'G', 'D', 'I', 'H']
young   ['O', 'L', 'S', 'O', 'N', 'W', 'R', 'Q', 'M', 'L']   ['I', 'G', 'E', 'G', 'H', 'G', 'F', 'H', 'J', 'H']   ['U', 'Q', 'Q', 'P', 'S', 'Q', 'U', 'W', 'O', 'T']   ['V', 'T', 'R', 'P', 'W', 'Q', 'W', 'W', 'S', 'V']   ['K', 'H', 'I', 'K', 'E', 'H', 'K', 'G', 'H', 'H'] """

        # caesar cipher
        num2abc=dict(zip(list(range(26)),'ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
        self.df['ABC']=[num2abc[v%26] for v in self.df['WORDS']]

        D = self.df.pivot('ABC',
                      rows=['AGE'], cols=['CONDITION'],
                      aggregate='tolist')


        diff = difflib.ndiff(str(D).splitlines(keepends=True),
                            R.splitlines(keepends=True))
        print(''.join(diff))

    def test7(self):
        # test group_concat
        R="""\
group_concat(WORDS)
 AGE         CONDITION=adjective         CONDITION=counting          CONDITION=imagery              CONDITION=intention          CONDITION=rhyming    
=====================================================================================================================================================
old       11,13,8,6,14,11,13,13,10,11   9,8,6,8,10,4,6,5,7,7    12,11,16,11,9,23,12,10,19,11    10,19,14,5,10,11,14,15,11,11     7,9,6,6,6,11,6,3,8,7 
young   14,11,18,14,13,22,17,16,12,11    8,6,4,6,7,6,5,7,9,7   20,16,16,15,18,16,20,22,14,19   21,19,17,15,22,16,22,22,18,21   10,7,8,10,4,7,10,6,7,7 """

        D=self.df.pivot('WORDS',
                      rows=['AGE'], cols=['CONDITION'],
                      aggregate='group_concat')

        # verify the values in the table

        diff = difflib.ndiff(str(D).splitlines(keepends=True),
                            R.splitlines(keepends=True))
        print(''.join(diff))



    def test8(self):
        # tolist handles text data differently then integer
        # or float data. We need to test this case as well
        R="""\
tolist(ABC)
                                                  CONDITION=adjective                                                                                                         CONDITION=counting                                                                                                         CONDITION=imagery                                                                                                         CONDITION=intention                                                                                                         CONDITION=rhyming                                                     
====================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
['L', 'N', 'I', 'G', 'O', 'L', 'N', 'N', 'K', 'L', 'O', 'L', 'S', 'O', 'N', 'W', 'R', 'Q', 'M', 'L']   ['J', 'I', 'G', 'I', 'K', 'E', 'G', 'F', 'H', 'H', 'I', 'G', 'E', 'G', 'H', 'G', 'F', 'H', 'J', 'H']   ['M', 'L', 'Q', 'L', 'J', 'X', 'M', 'K', 'T', 'L', '', 'Q', 'Q', 'P', 'S', 'Q', '', 'W', 'O', 'T']   ['K', 'T', 'O', 'F', 'K', 'L', 'O', 'P', 'L', 'L', 'V', 'T', 'R', 'P', 'W', 'Q', 'W', 'W', 'S', 'V']   ['H', 'J', 'G', 'G', 'G', 'L', 'G', 'D', 'I', 'H', 'K', 'H', 'I', 'K', 'E', 'H', 'K', 'G', 'H', 'H'] """

        # caesar cipher
        num2abc=dict(zip(list(range(26)),'ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
        self.df['ABC']=[num2abc[v%26] for v in self.df['WORDS']]

        D = self.df.pivot('ABC',
                      cols=['CONDITION'],
                      aggregate='tolist')
        
        # verify the values in the table

        diff = difflib.ndiff(str(D).splitlines(keepends=True),
                            R.splitlines(keepends=True))
        print(''.join(diff))


    def test9(self):
        # tolist handles text data differently then integer
        # or float data. We need to test this case as well
        R="""\
tolist(ABC)
CONDITION                                                            Value                                                           
====================================================================================================================================
adjective   ['L', 'N', 'I', 'G', 'O', 'L', 'N', 'N', 'K', 'L', 'O', 'L', 'S', 'O', 'N', 'W', 'R', 'Q', 'M', 'L'] 
counting    ['J', 'I', 'G', 'I', 'K', 'E', 'G', 'F', 'H', 'H', 'I', 'G', 'E', 'G', 'H', 'G', 'F', 'H', 'J', 'H'] 
imagery     ['M', 'L', 'Q', 'L', 'J', 'X', 'M', 'K', 'T', 'L', '', 'Q', 'Q', 'P', 'S', 'Q', '', 'W', 'O', 'T'] 
intention   ['K', 'T', 'O', 'F', 'K', 'L', 'O', 'P', 'L', 'L', 'V', 'T', 'R', 'P', 'W', 'Q', 'W', 'W', 'S', 'V'] 
rhyming     ['H', 'J', 'G', 'G', 'G', 'L', 'G', 'D', 'I', 'H', 'K', 'H', 'I', 'K', 'E', 'H', 'K', 'G', 'H', 'H'] """
        
        # caesar cipher
        num2abc=dict(zip(list(range(26)),'ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
        self.df['ABC']=[num2abc[v%26] for v in self.df['WORDS']]

        D = self.df.pivot('ABC',
                      rows=['CONDITION'],
                      aggregate='tolist')

        # verify the values in the table

        diff = difflib.ndiff(str(D).splitlines(keepends=True),
                            R.splitlines(keepends=True))
        print(''.join(diff))


    def test10(self):
        # test group_concat
        R="""\
group_concat(WORDS)
                                                            AGE=old                                                                                                                            AGE=young                                                               
======================================================================================================================================================================================================================================================================
9,8,6,8,10,4,6,5,7,7,7,9,6,6,6,11,6,3,8,7,11,13,8,6,14,11,13,13,10,11,12,11,16,11,9,23,12,10,19,11,10,19,14,5,10,11,14,15,11,11   8,6,4,6,7,6,5,7,9,7,10,7,8,10,4,7,10,6,7,7,14,11,18,14,13,22,17,16,12,11,20,16,16,15,18,16,20,22,14,19,21,19,17,15,22,16,22,22,18,21 """

        D=self.df.pivot('WORDS',
                      cols=['AGE'],
                      aggregate='group_concat')

        # verify the values in the table

        diff = difflib.ndiff(str(D).splitlines(keepends=True),
                            R.splitlines(keepends=True))
        print(''.join(diff))



    def test11(self):
        # test group_concat
        R="""\
group_concat(WORDS)
 AGE                                                                   Value                                                                 
============================================================================================================================================
old          9,8,6,8,10,4,6,5,7,7,7,9,6,6,6,11,6,3,8,7,11,13,8,6,14,11,13,13,10,11,12,11,16,11,9,23,12,10,19,11,10,19,14,5,10,11,14,15,11,11 
young   8,6,4,6,7,6,5,7,9,7,10,7,8,10,4,7,10,6,7,7,14,11,18,14,13,22,17,16,12,11,20,16,16,15,18,16,20,22,14,19,21,19,17,15,22,16,22,22,18,21 """
        D=self.df.pivot('WORDS',
                      rows=['AGE'],
                      aggregate='group_concat')
        
        # verify the values in the table

        diff = difflib.ndiff(str(D).splitlines(keepends=True),
                            R.splitlines(keepends=True))
        print(''.join(diff))


class Test_pivot_2(unittest.TestCase):
    def setUp(self):
        D={
            'SUBJECT':[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100],
            'AGE':'old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young'.split(','),
            'CONDITION':'counting,counting,counting,counting,counting,counting,counting,counting,counting,counting,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,intention,intention,intention,intention,intention,intention,intention,intention,intention,intention,counting,counting,counting,counting,counting,counting,counting,counting,counting,counting,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,intention,intention,intention,intention,intention,intention,intention,intention,intention,intention'.split(','),
            'WORDS':[9,8,6,8,10,4,6,5,7,7,7,9,6,6,6,11,6,3,8,7,11,13,8,6,14,11,13,13,10,11,12,11,16,11,9,23,12,10,19,11,10,19,14,5,10,11,14,15,11,11,8,6,4,6,7,6,5,7,9,7,10,7,8,10,4,7,10,6,7,7,14,11,18,14,13,22,17,16,12,11,20,16,16,15,18,16,20,22,14,19,21,19,17,15,22,16,22,22,18,21],
           }
        
        self.df=DataFrame()
        self.df.read_tbl('data/words~ageXcondition.csv')
        
    def test12(self):
        R="""\
avg(WORDS)
CONDITION    AGE    Value  
==========================
adjective   old         11 
adjective   young   14.800 
counting    old          7 
counting    young    6.500 
imagery     old     13.400 
imagery     young   17.600 
intention   old         12 
intention   young   19.300 
rhyming     old      6.900 
rhyming     young    7.600 
==========================
Total               11.610 """
        
        D = self.df.pivot('WORDS', rows=['CONDITION','AGE'])
        list(D)
        
        
        # verify the values in the table

        diff = difflib.ndiff(str(D).splitlines(keepends=True),
                            R.splitlines(keepends=True))
        print(''.join(diff))

                
    def test13(self):
        R="""\
avg(WORDS)
CONDITION=adjective,   CONDITION=adjective,   CONDITION=counting,   CONDITION=counting,   CONDITION=imagery,   CONDITION=imagery,   CONDITION=intention,   CONDITION=intention,   CONDITION=rhyming,   CONDITION=rhyming,   Total  
      AGE=old               AGE=young               AGE=old              AGE=young             AGE=old             AGE=young              AGE=old               AGE=young              AGE=old             AGE=young               
==================================================================================================================================================================================================================================
                  11                 14.800                     7                 6.500               13.400               17.600                     12                 19.300                6.900                7.600   11.610 """
        
        D = self.df.pivot('WORDS', cols=['CONDITION','AGE'])
        
        # verify the values in the table

        diff = difflib.ndiff(str(D).splitlines(keepends=True),
                            R.splitlines(keepends=True))
        print(''.join(diff))

        
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_pivot_1),
            unittest.makeSuite(Test_pivot_2)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
