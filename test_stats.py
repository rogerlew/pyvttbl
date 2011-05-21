from __future__ import print_function

# Copyright (c) 2011, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.

import unittest
import warnings
import os
import math

from random import shuffle
from collections import Counter,OrderedDict
from dictset import DictSet,_rep_generator
from math import isnan, isinf, floor
import numpy as np
from pprint import pprint as pp
from pyvttbl import DataFrame, PyvtTbl, Descriptives,  Marginals, Histogram, \
     Ttest, Anova1way, _flatten, _isfloat, _isint

class Test_anova1way(unittest.TestCase):
    def test0(self):
        """1 way anova"""
        R="Anova1way([('f', 16.70726997413529), ('p', 4.5885798225758395e-06), ('ns', [14, 15, 16]), ('mus', [62.142857142857146, 57.2, 94.375]), ('vars', [202.13186813186815, 584.7428571428571, 339.5833333333333]), ('ssbn', 12656.046825396828), ('sswn', 15907.864285714284), ('dfbn', 2), ('dfwn', 42), ('msbn', 6328.023412698414), ('mswn', 378.7586734693877)], conditions_list=['A', 'B', 'C'])"
        listOflists=[[42,52,55,59,75,40,79,79,44,56,68,77,75,69],
                     [29,36,29,31,97,88,27,57,54,77,54,52,58,91,78],
                     [91,79,73,75,99,66,114,120,102,68,114,79,115,104,107,104]]

        D=Anova1way()
        D.run(listOflists)
        self.assertEqual(repr(D),R)

    def test1(self):
        """1 way anova"""

        R="""Anova: Single Factor on Measure

SUMMARY
Groups   Count   Sum    Average   Variance 
==========================================
A           14    870    62.143    202.132 
B           15    858    57.200    584.743 
C           16   1510    94.375    339.583 

ANOVA
Source of Variation      SS       df      MS        F       P-value  
====================================================================
Treatments            12656.047    2   6328.023   16.707   4.589e-06 
Error                 15907.864   42    378.759                      
====================================================================
Total                 28563.911   44                                 """
        listOflists=[[42,52,55,59,75,40,79,79,44,56,68,77,75,69],
                     [29,36,29,31,97,88,27,57,54,77,54,52,58,91,78],
                     [91,79,73,75,99,66,114,120,102,68,114,79,115,104,107,104]]

        D=Anova1way()
        D.run(listOflists)
        self.assertEqual(str(D),R)

    def test2(self):
        R="""Anova: Single Factor on SUPPRESSION

SUMMARY
Groups   Count     Sum      Average   Variance 
==============================================
AA         128       2048        16    148.792 
AB         128   2510.600    19.614    250.326 
LAB        128   2945.000    23.008    264.699 

ANOVA
Source of Variation      SS       df       MS        F      P-value  
====================================================================
Treatments             3144.039     2   1572.020   7.104   9.348e-04 
Error                 84304.687   381    221.272                     
====================================================================
Total                 87448.726   383                                """
        
        df = DataFrame()
        df.read_tbl('suppression~subjectXgroupXageXcycleXphase.csv')
        aov=df.anova1way('SUPPRESSION','GROUP')
        self.assertEqual(str(aov),R)
        
class Test_ttest1sample(unittest.TestCase):
    def test0(self):
        """1 sample ttest"""
        R=OrderedDict([('t', -17.797126310672542), ('p2tail', 1.0172137120313963e-07), ('p1tail', 5.086068560156982e-08), ('n', 9), ('df', 8), ('mu', 4.555555555555555), ('pop_mean', 20), ('var', 6.777777777777778), ('tc2tail', 2.3060059174895287), ('tc1tail', 1.8595485016703606)])
        A=[3,4, 5,8,9, 1,2,4, 5]
        pop_mean=20
      
        D=Ttest()
        D.run(A, pop_mean=pop_mean)
        
        for k in R.keys():
            self.assertTrue(D[k],R[k])

    def test1(self):
        R="""t-Test: One Sample for means

                         SUPPRESSION 
====================================
Sample Mean                   19.541 
Hypothesized Pop. Mean             0 
Variance                     228.326 
Observations                     384 
df                               383 
t Stat                        25.341 
P(T<=t) one-tail           3.347e-84 
t Critical one-tail            1.649 
P(T<=t) two-tail           6.694e-84 
t Critical two-tail            1.966 """
        df = DataFrame()
        df.read_tbl('suppression~subjectXgroupXageXcycleXphase.csv')
        ttest=df.ttest('SUPPRESSION')
        self.assertEqual(str(ttest),R)       

class Test_ttest(unittest.TestCase):
    def test0(self):
        """paired ttest"""
        R=OrderedDict([('t', -1.4106912317171967), ('p2tail', 0.19601578492449323), ('p1tail', 0.09800789246224662), ('n1', 9), ('n2', 9), ('df', 8), ('mu1', 4.555555555555555), ('mu2', 7.888888888888889), ('var1', 6.777777777777778), ('var2', 47.111111111111114), ('tc2tail', 2.3060059174895287), ('tc1tail', 1.8595485016703606)])

        A=[3,4, 5,8,9, 1,2,4, 5]
        B=[6,19,3,2,14,4,5,17,1]
      
        D=Ttest()
        D.run(A,B,paired=True)

        for k in R.keys():
            self.assertTrue(D[k],R[k])
            
    def test01(self):
        """paired ttest"""
        R="""t-Test: Paired Two Sample for means
                        A        B    
=====================================
Mean                   4.556    7.889 
Variance               6.778   47.111 
Observations               9        9 
Pearson Correlation    0.102          
df                         8          
t Stat                -1.411          
P(T<=t) one-tail       0.098          
t Critical one-tail    1.860          
P(T<=t) two-tail       0.196          
t Critical two-tail    2.306          """
        
        A=[3,4, 5,8,9, 1,2,4, 5]
        B=[6,19,3,2,14,4,5,17,1]
      
        D=Ttest()
        D.run(A,B,paired=True)

        self.assertEqual(str(D),R)

    def test1(self):
        """independent equal variance ttest"""
        R=OrderedDict([('t', -1.712764845721259), ('p2tail', 0.10493320627442616), ('p1tail', 0.05246660313721308), ('n1', 9), ('n2', 10), ('df', 17), ('mu1', 4.555555555555555), ('mu2', 9.0), ('var1', 6.777777777777777), ('var2', 54.22222222222222), ('vpooled', 31.895424836601304), ('tc2tail', 2.1098158322274685), ('tc1tail', 1.7396057955920696)])

        A=[3,4, 5,8,9, 1,2,4, 5]
        B=[6,19,3,2,14,4,5,17,1,19]
      
        D=Ttest()
        D.run(A,B,equal_variance=True)

        for k in R.keys():
            self.assertTrue(D[k],R[k])

    def test11(self):
        """independent equal variance ttest"""
        R="""t-Test: Two-Sample Assuming Equal Variances
                        A        B    
=====================================
Mean                   4.556        9 
Variance               6.778   54.222 
Observations               9       10 
Pooled Variance       31.895          
df                        17          
t Stat                -1.713          
P(T<=t) one-tail       0.052          
t Critical one-tail    1.740          
P(T<=t) two-tail       0.105          
t Critical two-tail    2.110          """
        
        A=[3,4, 5,8,9, 1,2,4, 5]
        B=[6,19,3,2,14,4,5,17,1,19]
      
        D=Ttest()
        D.run(A,B,equal_variance=True)
        
        self.assertEqual(str(D),R)

    def test2(self):
        """independent unequal variance ttest"""
        R=OrderedDict([('t', -1.7884967184189302), ('p2tail', 0.1002162848567985), ('p1tail', 0.05010814242839925), ('n1', 9), ('n2', 10), ('df', 11.425658453695835), ('mu1', 4.555555555555555), ('mu2', 9.0), ('var1', 6.777777777777777), ('var2', 54.22222222222222), ('tc2tail', 2.1910201758146286), ('tc1tail', 1.789783127605915)])

        A=[3,4, 5,8,9, 1,2,4, 5]
        B=[6,19,3,2,14,4,5,17,1,19]
      
        D=Ttest()
        D.run(A,B,equal_variance=False)

        for k in R.keys():
            self.assertTrue(D[k],R[k])

    def test21(self):
        """independent unequal variance ttest"""
        R="""t-Test: Two-Sample Assuming Unequal Variances
                        A        B    
=====================================
Mean                   4.556        9 
Variance               6.778   54.222 
Observations               9       10 
df                    11.426          
t Stat                -1.788          
P(T<=t) one-tail       0.050          
t Critical one-tail    1.790          
P(T<=t) two-tail       0.100          
t Critical two-tail    2.191          """
        
        A=[3,4, 5,8,9, 1,2,4, 5]
        B=[6,19,3,2,14,4,5,17,1,19]
      
        D=Ttest()
        D.run(A,B,equal_variance=False)

        self.assertEqual(str(D),R)

    def test3(self):
        """independent unequal variance ttest
        http://alamos.math.arizona.edu/~rychlik/math263/class_notes/Chapter7/R/"""
        R=OrderedDict([('t', 2.310889197854228), ('p2tail', 0.026382412254338405), ('p1tail', 0.013191206127169203), ('n1', 21), ('n2', 23), ('df', 37.855400659439084), ('mu1', 51.476190476190474), ('mu2', 41.52173913043478), ('var1', 121.16190476190475), ('var2', 294.0790513833993), ('tc2tail', 2.0246487110853195), ('tc1tail', 1.6861152835190296)])

        A=[24,61,59,46,43,44,52,43,58,67,62,57,71,49,54,43,53,57,49,56,33]
        B=[42,33,46,37,43,41,10,42,55,19,17,55,26,54,60,28,62,20,53,48,37,85,42]
      
        D=Ttest()
        D.run(A,B,equal_variance=False)

        for k in R.keys():
            self.assertTrue(D[k],R[k])

    def test31(self):
        """independent unequal variance ttest
        http://alamos.math.arizona.edu/~rychlik/math263/class_notes/Chapter7/R/"""
        R="""t-Test: Two-Sample Assuming Unequal Variances
                         A         B    
=======================================
Mean                   51.476    41.522 
Variance              121.162   294.079 
Observations               21        23 
df                     37.855           
t Stat                  2.311           
P(T<=t) one-tail        0.013           
t Critical one-tail     1.686           
P(T<=t) two-tail        0.026           
t Critical two-tail     2.025           """
        
        A=[24,61,59,46,43,44,52,43,58,67,62,57,71,49,54,43,53,57,49,56,33]
        B=[42,33,46,37,43,41,10,42,55,19,17,55,26,54,60,28,62,20,53,48,37,85,42]
      
        D=Ttest()
        D.run(A,B,equal_variance=False)

        self.assertEqual(str(D),R)

    def test4(self):
        R="""t-Test: Paired Two Sample for means
                        PRE        POST   
=========================================
Mean                    87.250     87.083 
Variance              1207.659   1166.629 
Observations                12         12 
Pearson Correlation      0.995            
df                          11            
t Stat                   0.163            
P(T<=t) one-tail         0.437            
t Critical one-tail      1.796            
P(T<=t) two-tail         0.873            
t Critical two-tail      2.201            """
        df = DataFrame()
        df.read_tbl('example2_prepost.csv')
        ttest = df.ttest('PRE','POST',paired=True)
        self.assertEqual(str(ttest),R)
        
    def test__repr__(self):
        R="Ttest([('t', 2.310889197854228), ('p2tail', 0.026382412254338405), ('p1tail', 0.013191206127169203), ('n1', 21), ('n2', 23), ('df', 37.855400659439084), ('mu1', 51.476190476190474), ('mu2', 41.52173913043478), ('var1', 121.16190476190475), ('var2', 294.0790513833993), ('tc2tail', 2.0246487110853195), ('tc1tail', 1.6861152835190296)], equal_variance=False, aname='A', bname='B', type='t-Test: Two-Sample Assuming Unequal Variances')"
        
        A=[24,61,59,46,43,44,52,43,58,67,62,57,71,49,54,43,53,57,49,56,33]
        B=[42,33,46,37,43,41,10,42,55,19,17,55,26,54,60,28,62,20,53,48,37,85,42]
        
        D=Ttest()
        D.run(A,B,equal_variance=False)
        self.assertEqual(repr(D),R)
        
            
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_anova1way),
            unittest.makeSuite(Test_ttest1sample),
            unittest.makeSuite(Test_ttest)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
    
