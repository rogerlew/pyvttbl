# Copyright (c) 2011-2024, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.
    
import unittest

from pyvttbl import DataFrame
from pyvttbl.misc.support import *

class Test_df__str__(unittest.TestCase):
    def test0(self):
        R = """SUBJECT   TIMEOFDAY   COURSE   MODEL   ERROR 
============================================
      1   T1          C1       M1         10 
      1   T1          C1       M2          8 
      1   T1          C1       M3          6 
      1   T1          C2       M1          9 
      1   T1          C3       M1          7 
      1   T1          C3       M2          6 
      1   T1          C3       M3          3 
      1   T2          C1       M1          5 
      1   T2          C1       M2          4 
      1   T2          C1       M3          3 
      1   T2          C2       M1          4 
      1   T2          C2       M2          3 
      1   T2          C2       M3          3 
      1   T2          C3       M1          2 
      1   T2          C3       M2          2 
      1   T2          C3       M3          1 
      2   T1          C2       M1         10 
      2   T1          C2       M2          6 
      2   T1          C2       M3          4 
      2   T1          C3       M1          4 
      2   T1          C3       M2          5 
      2   T1          C3       M3          2 
      2   T2          C1       M1          4 
      2   T2          C1       M2          3 
      2   T2          C1       M3          3 
      2   T2          C2       M1          4 
      2   T2          C2       M2          2 
      2   T2          C2       M3          2 
      2   T2          C3       M1          2 
      2   T2          C3       M2          3 
      2   T2          C3       M3          2 
      3   T1          C1       M1          8 
      3   T1          C1       M2          7 
      3   T1          C1       M3          4 
      3   T1          C2       M1          7 
      3   T1          C2       M3          3 
      3   T1          C3       M1          3 
      3   T1          C3       M2          4 
      3   T1          C3       M3          2 
      3   T2          C1       M1          4 
      3   T2          C1       M2          1 
      3   T2          C1       M3          2 
      3   T2          C2       M1          3 
      3   T2          C2       M2          3 
      3   T2          C2       M3          2 
      3   T2          C3       M1          1 
      3   T2          C3       M2          0 
      3   T2          C3       M3          1 """
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')

        self.assertEqual(str(df),R)
        
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_df__str__)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
