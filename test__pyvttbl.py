from __future__ import print_function

import unittest
import warnings

from numpy import array
from pprint import pprint as pp
from pyvttbl import PyvtTbl


class Test_readTbl(unittest.TestCase):
    def test01(self):

        # skip 4 lines
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


class Test__setitem__(unittest.TestCase):
    def setUp(self):
        self.df=PyvtTbl()
        self.df.readTbl('error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        
    def test1(self):
        with self.assertRaises(Exception) as cm:
            self.df['DUM']=range(49)

        self.assertEqual(str(cm.exception),
                         'columns have unequal lengths')

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
        
class Test_pivot_1(unittest.TestCase):
    def setUp(self):
        D={
            'SUBJECT':[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100],
            'AGE':'old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young'.split(','),
            'CONDITION':'counting,counting,counting,counting,counting,counting,counting,counting,counting,counting,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,intention,intention,intention,intention,intention,intention,intention,intention,intention,intention,counting,counting,counting,counting,counting,counting,counting,counting,counting,counting,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,intention,intention,intention,intention,intention,intention,intention,intention,intention,intention'.split(','),
            'WORDS':[9,8,6,8,10,4,6,5,7,7,7,9,6,6,6,11,6,3,8,7,11,13,8,6,14,11,13,13,10,11,12,11,16,11,9,23,12,10,19,11,10,19,14,5,10,11,14,15,11,11,8,6,4,6,7,6,5,7,9,7,10,7,8,10,4,7,10,6,7,7,14,11,18,14,13,22,17,16,12,11,20,16,16,15,18,16,20,22,14,19,21,19,17,15,22,16,22,22,18,21],
           }
        
        self.df=PyvtTbl(D)
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
                         'rows should be a list')
        
    def test006(self):
        with self.assertRaises(TypeError) as cm:
            self.df.pivot('SUBJECT',cols='AGE')

        self.assertEqual(str(cm.exception),
                         'cols should be a list')
    def test004(self):
        # test the exclude parameter checking

        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            
            # Trigger a warning.    
            self.df.pivot('SUBJECT',exclude={'AGE':['medium',]})
        
            assert issubclass(w[-1].category, RuntimeWarning)
    
    def test005(self):
        # test the exclude parameter
        R=array([[14.8], [6.5], [17.6], [19.3], [7.6]])
        
        # this one shouldn't raise an Exception
        self.df.pivot('WORDS',rows=['CONDITION'],exclude={'AGE':['old',]})
        D=array(self.df.Z)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)
        
    def test011(self):
        R=array([[25.5], [75.5]])
        
        # aggregate is case-insensitive
        self.df.pivot('SUBJECT',rows=['AGE'],aggregate='AVG')
        D=array(self.df.Z)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)
        
    def test0(self):
        R=array([[ 11. ,   7. ,  13.4,  12. ,   6.9],
                 [ 14.8,   6.5,  17.6,  19.3,   7.6]])
        
        self.df.pivot('WORDS',rows=['AGE'],cols=['CONDITION'])
        D=array(self.df.Z)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

    def test1(self):
        R=array([[ 110.,  148.],
                 [  70.,   65.],
                 [ 134.,  176.],
                 [ 120.,  193.],
                 [  69.,   76.]])
        
        self.df.pivot('WORDS',rows=['CONDITION'],cols=['AGE'],aggregate='sum')
        D=array(self.df.Z)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

    def test3(self):
        R=array([[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
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
        D=array(self.df.Z)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

    def test4(self):
        R=array([[5.191085988]])

        # No rows or cols        
        self.df.pivot('WORDS',aggregate='stdev')
        D=array(self.df.Z)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)
            
class Test_pivot_2(unittest.TestCase):
    def setUp(self):
        self.df=PyvtTbl()
        self.df.readTbl('error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        
    def test0(self):
              # M 1  2  3
        R=array([[2, 2, 2],  # T1 C1
                 [3, 1, 2],  # T1 C2
                 [3, 3, 3],  # T1 C3
                 [3, 3, 3],  # T2 C1
                 [3, 3, 3],  # T2 C2
                 [3, 3, 3]]) # T2 C3
        
        self.df.pivot('ERROR',rows=['TIMEOFDAY','COURSE'],
                      cols=['MODEL'],aggregate='count')
        D=array(self.df.Z)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

    def test1(self):
        # check to make sure missing cells are correct
        R=array([[1, 1, 1, 1, 1, 1],
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
        D=array(self.df.Z)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

    def test2(self):          
        R=array([[ 0.26882528, -0.06797845]])

        # No row
        self.df.pivot('ERROR',cols=['TIMEOFDAY'],aggregate='skew')
        D=array(self.df.Z)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

    def test3(self):              
        R=array([[ 0.26882528],
                 [-0.06797845]])

        # No col
        self.df.pivot('ERROR',rows=['TIMEOFDAY'],aggregate='skew')
        D=array(self.df.Z)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

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

class Test_plotMarginals(unittest.TestCase):
    def test0(self):
        self.df=PyvtTbl()
        self.df.readTbl('words~ageXcondition.csv')

        R=self.df.plotMarginals('WORDS','AGE','CONDITION')
        self.assertTrue(R)
        
    def test1(self):
        self.df=PyvtTbl()
        self.df.readTbl('error~subjectXtimeofdayXcourseXmodel_MISSING.csv')

        R=self.df.plotMarginals('ERROR','TIMEOFDAY',
                                seplines='COURSE',
                                sepxplots='MODEL',yerr=1.)
        self.assertTrue(R)

    def test2(self):
        self.df=PyvtTbl()
        self.df.readTbl('error~subjectXtimeofdayXcourseXmodel_MISSING.csv')

        with self.assertRaises(Exception) as cm:
            self.df.plotMarginals('ERROR','TIMEOFDAY',
                                seplines='COURSE',
                                sepxplots='MODEL',yerr='ci')

        self.assertEqual(str(cm.exception),
                         'cell count too low to calculate ci')

        
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
            
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_readTbl),
            unittest.makeSuite(Test__setitem__),
            unittest.makeSuite(Test_pivot_1),
            unittest.makeSuite(Test_pivot_2),
            unittest.makeSuite(Test_marginals),
            unittest.makeSuite(Test_plotMarginals),
            unittest.makeSuite(Test_descriptives),
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
    
