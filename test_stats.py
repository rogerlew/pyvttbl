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
from math import isnan, isinf
import numpy as np
from pprint import pprint as pp
from pyvttbl import DataFrame, PyvtTbl, Descriptives,  Marginals, Histogram, \
     Ttest, Ttest1sample, _flatten, _isfloat, _isint

class Test_ttest1sample(unittest.TestCase):
    def test0(self):
        """1 sample ttest"""
        R=OrderedDict([('t', -17.797126310672542), ('p2tail', 1.0172137120313963e-07), ('p1tail', 5.086068560156982e-08), ('n', 9), ('df', 8), ('mu', 4.555555555555555), ('pop_mu', 20), ('var', 6.777777777777778), ('tc2tail', 2.3060059174895287), ('tc1tail', 1.8595485016703606)])
        A=[3,4, 5,8,9, 1,2,4, 5]
        pop_mu=20
      
        D=Ttest1sample()
        D.run(A,pop_mu)

        for k in R.keys():
            self.assertTrue(D[k],R[k])

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

    def test__repr__(self):
        R="Ttest([('t', 2.310889197854228), ('p2tail', 0.026382412254338405), ('p1tail', 0.013191206127169203), ('n1', 21), ('n2', 23), ('df', 37.855400659439084), ('mu1', 51.476190476190474), ('mu2', 41.52173913043478), ('var1', 121.16190476190475), ('var2', 294.0790513833993), ('tc2tail', 2.0246487110853195), ('tc1tail', 1.6861152835190296)], equal_variance=False, aname='A', bname='B')"
        
        A=[24,61,59,46,43,44,52,43,58,67,62,57,71,49,54,43,53,57,49,56,33]
        B=[42,33,46,37,43,41,10,42,55,19,17,55,26,54,60,28,62,20,53,48,37,85,42]
        
        D=Ttest()
        D.run(A,B,equal_variance=False)
        self.assertEqual(repr(D),R)
        
            
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_ttest1sample),
            unittest.makeSuite(Test_ttest)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
    
