# Copyright (c) 2011-2024, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.

import unittest
import difflib

from collections import Counter

from pyvttbl import DataFrame, PyvtTbl
from pyvttbl.plotting import *
from pyvttbl.stats import *
from pyvttbl.misc.support import *


class Test_chisquare2way(unittest.TestCase):
    def test0(self):
        R="""\
Chi-Square: two Factor

SUMMARY
         Guilty     NotGuilty   Total
=====================================
High          157          24     181
        (130.441)    (50.559)
Low           101          76     177
        (127.559)    (49.441)
=====================================
Total         258         100     358

SYMMETRIC MEASURES
                          Value    Approx.
                                    Sig.
===========================================
Cramer's V                0.331   1.390e-10
Contingency Coefficient   0.314   1.244e-09
N of Valid Cases            358

CHI-SQUARE TESTS
                        Value    df   P
=======================================
Pearson Chi-Square      39.155    1   0
Continuity Correction   37.695    1   0
Likelihood Ratio        40.621    1   0
N of Valid Cases           358

CHI-SQUARE POST-HOC POWER
       Measure
==============================
Effect size w            0.331
Non-centrality lambda   39.155
Critical Chi-Square      3.841
Power                    1.000
"""
        df=DataFrame()
        df['FAULTS']=list(Counter(Low=177,High=181).elements())
        df['FAULTS']=df['FAULTS'][::-1] # reverse 'FAULT' data
        df['VERDICT']=list(Counter(Guilty=153, NotGuilty=24).elements()) + \
                      list(Counter(Guilty=105, NotGuilty=76).elements())

        x2= df.chisquare2way('FAULTS','VERDICT')

        diff = difflib.ndiff(str(x2).splitlines(keepends=True),
                             R.splitlines(keepends=True))
        print(''.join(diff))


    def test1(self):
        """chi-square 2-way"""
        R="""\
Chi-Square: two Factor

SUMMARY
            Litter      Removed    Trash Can   Total 
====================================================
Countrol         385         477          41     903 
           (343.976)   (497.363)    (61.661)         
Message          290         499          80     869 
           (331.024)   (478.637)    (59.339)         
====================================================
Total            675         976         121    1772 

SYMMETRIC MEASURES
                          Value    Approx.  
                                    Sig.    
===========================================
Cramer's V                0.121   3.510e-07 
Contingency Coefficient   0.120   4.263e-07 
N of Valid Cases           1772             

CHI-SQUARE TESTS
                     Value    df       P     
============================================
Pearson Chi-Square   25.794    2   2.506e-06 
Likelihood Ratio     26.056    2   2.198e-06 
N of Valid Cases       1772                  

CHI-SQUARE POST-HOC POWER
       Measure                 
==============================
Effect size w            0.121 
Non-centrality lambda   25.794 
Critical Chi-Square      5.991 
Power                    0.997 """
        
        df=DataFrame()
        rfactors= ['Countrol']*903 + ['Message']*869
        cfactors= ['Trash Can']*41 + ['Litter']*385 + ['Removed']*477
        cfactors+=['Trash Can']*80 + ['Litter']*290 + ['Removed']*499
        
        x2= ChiSquare2way()
        x2.run(rfactors, cfactors)

        diff = difflib.ndiff(str(x2).splitlines(keepends=True),
                             R.splitlines(keepends=True))
        print(''.join(diff))

    def test2(self):
        """chi-square 2-way"""
        R="""ChiSquare2way([('chisq', 25.79364579345589), ('p', 2.5059995107347527e-06), ('df', 2), ('lnchisq', 26.055873891205664), ('lnp', 2.1980566132523407e-06), ('ccchisq', None), ('ccp', None), ('N', 1772.0), ('C', 0.11978058926585373), ('CramerV', 0.12064921681366868), ('CramerV_prob', 3.50998747929475e-07), ('C_prob', 4.26267335738495e-07), ('w', 0.12064921681366868), ('lambda', 25.79364579345589), ('crit_chi2', 5.991464547107979), ('power', 0.9972126130834689)], counter=Counter({('Message', 'Removed'): 499.0, ('Countrol', 'Removed'): 477.0, ('Countrol', 'Litter'): 385.0, ('Message', 'Litter'): 290.0, ('Message', 'Trash Can'): 80.0, ('Countrol', 'Trash Can'): 41.0}), row_counter=Counter({'Countrol': 903.0, 'Message': 869.0}), col_counter=Counter({'Removed': 976.0, 'Litter': 675.0, 'Trash Can': 121.0}), N_r=2, N_c=3)"""

        rfactors=['Countrol']*903 + ['Message']*869
        cfactors=['Trash Can']*41 + ['Litter']*385 + ['Removed']*477
        cfactors+=['Trash Can']*80 + ['Litter']*290 + ['Removed']*499
        
        x2= ChiSquare2way()
        x2.run(rfactors, cfactors)

        self.assertEqual(repr(x2), R)
            
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_chisquare2way)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
    
