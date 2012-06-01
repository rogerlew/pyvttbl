Quick-Start Guide
=================

pyvttbl has two primary containers for storing data. :class:`DataFrame` objects 
hold tabulated data in a manner similiar to what you would have in a 
spreadsheet. DataFrames are basically dictionary objects. The *keys*
are the names of the columns and the *values* are NumPy arrays or
NumPy MaskedArrays if missing data is specified or encountered when
reading datafiles.

DataFrames can be pivoted to created :class:`PyvtTbl` objects. These are 
subclasses of :class:`NumPy.MaskedArray`. The use of :class:`MaskedArray' helps to make
:class:`PyvtTbl`'s robust to invalid or missing data. 

   
Loading Data into a :class:`DataFrame`
--------------------------------------

Before we can start building contingency tables we need to first load the 
data into a :class:`DataFrame` object. Data can be read from plaintext datafiles 
using the :class:`DataFrame`.:meth:`read_tbl` method or inserted one row at a time using 
:class:`DataFrame`.:meth:`insert`. DataFrames can be attached to one another using 
:class:`DataFrame`.:meth:`attach`. The read_tbl method is looking for comma separated values 
(CSV) files. Other delimited file types should also work; just specify the 
delimiter. You can also specify whether your file has labels (default is 
True) and the number of lines at the beginning to skip (Default is 0).

.. sourcecode:: python

   >>> from __future__ import print_function
   >>> 
   >>> from pyvttbl import DataFrame
   >>> df = DataFrame()
   >>> df.read_tbl('example.csv')
   >>> print(df)
   CASE   TIME    CONDITION    X  
   ==============================
      1   day     A           102 
      2   day     B            70 
      3   night   A            27 
      4   night   B            38 
      5   day     A            67 
      6   day     B           127 
      7   night   A            68 
      8   night   B            49 
      9   day     A            57 
     10   day     B            71 
     11   night   A            40 
     12   night   B            84 
   >>>

Manipulating Data in a :class:`DataFrame`
-----------------------------------------

The :class:`DataFrame` class inherits collections.OrderedDict. The :meth:`__str__` method 
is defined to output pretty looking text tables. Because the :class:`DataFrame` holds
 NumPy arrays manipulating data is fairly straight forward.

.. sourcecode:: python

   >>> import numpy as np
   >>> df['LOG10_X'] = np.log10(df['X'])
   >>> print(df)
   CASE   TIME    CONDITION    X    LOG10_X 
   ========================================
      1   day     A           102     2.009 
      2   day     B            70     1.845 
      3   night   A            27     1.431 
      4   night   B            38     1.580 
      5   day     A            67     1.826 
      6   day     B           127     2.104 
      7   night   A            68     1.833 
      8   night   B            49     1.690 
      9   day     A            57     1.756 
     10   day     B            71     1.851 
     11   night   A            40     1.602 
     12   night   B            84     1.924 
   >>> 
   
Sorting a :class:`DataFrame`
----------------------------

:class:`DataFrame` has an inplace :meth:`sort` method. You just have to specify the 
variables you want to sort by.

.. sourcecode:: python

   >>> df.sort(['TIME','CONDITION'])
   >>> print(df)
   CASE   TIME    CONDITION    X    LOG10_X 
   ========================================
      1   day     A           102     2.009 
      5   day     A            67     1.826 
      9   day     A            57     1.756 
      2   day     B            70     1.845 
      6   day     B           127     2.104 
     10   day     B            71     1.851 
      3   night   A            27     1.431 
      7   night   A            68     1.833 
     11   night   A            40     1.602 
      4   night   B            38     1.580 
      8   night   B            49     1.690 
     12   night   B            84     1.924 
   >>> 

You can also reverse the order by using 'DESC' or 'desc' after the name of 
the variable.

.. sourcecode:: python

   >>> df.sort(['TIME DESC','CONDITION DESC'])
   >>> print(df)
   CASE   TIME    CONDITION    X    LOG10_X 
   ========================================
      4   night   B            38     1.580 
      8   night   B            49     1.690 
     12   night   B            84     1.924 
      3   night   A            27     1.431 
      7   night   A            68     1.833 
     11   night   A            40     1.602 
      2   day     B            70     1.845 
      6   day     B           127     2.104 
     10   day     B            71     1.851 
      1   day     A           102     2.009 
      5   day     A            67     1.826 
      9   day     A            57     1.756 
      
Writing Data from a :class:`DataFrame`
--------------------------------------

Tables can be exported using the write method. If filename is not supplied 
(as a fname keyword argument) a filename will be generated from the column 
labels.

.. sourcecode:: python

   >>> df.write()
   >>> df.read_tbl('caseXtimeXconditionXxXlog0_x.csv')
   >>> print(df)
   CASE   TIME    CONDITION    X    LOG10_X 
   ========================================
      1   day     A           102     2.009 
      2   day     B            70     1.845 
      3   night   A            27     1.431 
      4   night   B            38     1.580 
      5   day     A            67     1.826 
      6   day     B           127     2.104 
      7   night   A            68     1.833 
      8   night   B            49     1.690 
      9   day     A            57     1.756 
     10   day     B            71     1.851 
     11   night   A            40     1.602 
     12   night   B            84     1.924 
   >>> 
   
Pivoting Data
-------------

Once data is in a :class:`DataFrame` pivoting is as simple as:

.. sourcecode:: python

   >>> pt = df.pivot('LOG10_X', ['TIME'], ['CONDITION'])
   >>> print(pt)
   avg(LOG10_X)
   TIME    CONDITION=A   CONDITION=B 
   =================================
   day           1.864         1.933 
   night         1.622         1.731 
   >>>
   
Calling pivot returns a :class:`PyvtTbl` object.
   
Multidimensional Pivoting 
-------------------------

The example above isn't all that impressive. The :class:`PyvtTbl` class can also pivot higher dimensional data.

.. sourcecode:: python

   >>> df.read_tbl('suppression~subjectXgroupXageXcycleXphase.csv')
   >>> pt = df.pivot('SUPPRESSION',
                     rows=['CYCLE', 'PHASE'],
                     cols=['GROUP', 'AGE'])
   >>> print(pt)
   avg(SUPPRESSION)
   CYCLE   PHASE   GROUP=AA,   GROUP=AA,   GROUP=AB,   GROUP=AB,   GROUP=LAB,   GROUP=LAB, 
                    AGE=old    AGE=young    AGE=old    AGE=young    AGE=old     AGE=young  
   =======================================================================================
   1       I          17.750       8.675      12.625       5.525       21.625        7.825 
   1       II         20.875       8.300      22.750       8.675       36.250       13.750 
   2       I          22.375      10.225      23.500       8.825       21.375        9.900 
   2       II         28.125      10.250      41.125      13.100       46.875       14.375 
   3       I          23.125      10.500          20       9.125       23.750        9.500 
   3       II         20.750       9.525      46.125      14.475       50.375       15.575 
   4       I          20.250       9.925      15.625       7.750       26.375        9.650 
   4       II         24.250      11.100      51.750      12.850       46.500       14.425 
   >>> 

Pivot Aggregate Functions 
-------------------------
If no aggregate keyword is supplied the pivoting will result in averages of the underlying
data. A variety of other aggregators can also be applied:

==================   ===========================================================
   Aggregate            Description
==================   ===========================================================
 abs_mean(X)          mean of the absolute values of X	
 avg(X)               average value of all non-NULL X within a group
 arbitrary(X)	      an arbitrary element of X	
 count(X)             count of the number of times that X is not NULL in a group
 ci(X)	              95% confidence interval of X	
 datarange(X)         range of X	
 geometric_mean(X)	  geometric mean of X
 group_concat(X)      concatenates the values of X as elements in a list
 hasinf(X)	          True if X contains any inf values	
 hasnan(X)	          True if X contains any nan values	
 kurt(X)              sample kurtosis estimate of X	
 kurtp(X)             population kurtosis estimate of X	
 median(X)            median of X	
 mode(X)              mode of X	
 prod(X)              product of the elements of X	
 rms(X)               root mean square of X	
 sem(X)               standard error of the mean of X
 skew(X)              sample skewness estimate of X	(N-1)
 skewp(X)	          population skewness estimate of X	(N)
 stdev(X)             standard deviation estimate of the samples in X (N-1)
 stdevp(X)	          standard deviation of the population X	(N)
 var(X)               variance estimate of the samples in X (N-1)
 varp(X)              variance of the population X (N)
==================   ===========================================================

The pyvttbl module takes advantage of aggregate functions in from pystaggrelite3. 
You can also bind your own using :class:`DataFrame`.:meth:`bind_aggregate`.

.. sourcecode:: python

   >>> pt = df.pivot('SUPPRESSION',
                     rows=['CYCLE', 'PHASE'],
                     cols=['GROUP', 'AGE'],
                     aggregate='count')
   >>> print(pt)
   count(SUPPRESSION)
   CYCLE   PHASE   GROUP=AA,   GROUP=AA,   GROUP=AB,   GROUP=AB,   GROUP=LAB,   GROUP=LAB, 
                    AGE=old    AGE=young    AGE=old    AGE=young    AGE=old     AGE=young  
   =======================================================================================
   1       I               8           8           8           8            8            8 
   1       II              8           8           8           8            8            8 
   2       I               8           8           8           8            8            8 
   2       II              8           8           8           8            8            8 
   3       I               8           8           8           8            8            8 
   3       II              8           8           8           8            8            8 
   4       I               8           8           8           8            8            8 
   4       II              8           8           8           8            8            8 
   >>> 
   
Manipulating :class:`PyvtTbl` objects
-------------------------------------

:class:`PyvtTbl` can be added, subtracted, multiplied by constants or other :class:`PyvtTbl` objects 
of equivalent shape. 

.. sourcecode:: python

   >>> df=DataFrame()
   >>> df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
   >>> pt = df.pivot('ERROR', ['TIMEOFDAY'], ['COURSE'])
   >>> print(pt)    
   avg(ERROR)
   TIMEOFDAY   COURSE=C1   COURSE=C2   COURSE=C3   Total 
   =====================================================
   T1              7.167       6.500           4   5.619 
   T2              3.222       2.889       1.556   2.556 
   =====================================================
   Total           4.800       4.333       2.778   3.896 
   >>> pt2=pt+5
   >>> print(pt2)
   avg(ERROR)
   TIMEOFDAY   COURSE=C1   COURSE=C2   COURSE=C3   Total  
   ======================================================
   T1             12.167      11.500           9   10.619 
   T2              8.222       7.889       6.556    7.556 
   ======================================================
   Total           9.800       9.333       7.778    8.896 
   >>> sums = df.pivot('ERROR', ['TIMEOFDAY'], ['COURSE'], 
                       aggregate='sum')
   >>> counts = df.pivot('ERROR', ['TIMEOFDAY'], ['COURSE'], 
                         aggregate='count')
   >>> print(sums/counts.astype(np.float64))   
   N/A(ERROR)
   TIMEOFDAY   COURSE=C1   COURSE=C2   COURSE=C3   Total 
   =====================================================
   T1              7.167       6.500           4   5.619 
   T2              3.222       2.889       1.556   2.556 
   =====================================================
   Total           4.800       4.333       2.778   3.896 

The operrations are applied to the row and column totals when 
possible. However, operations like np.sum behave as expected

.. sourcecode:: python

   >>> import numpy as np
   >>> df=DataFrame()
   >>> df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
   >>> counts = df.pivot('ERROR', ['TIMEOFDAY'], ['COURSE'], 
                         aggregate'count')
   >>> print(counts)   
   >>>
   count(ERROR)
   TIMEOFDAY   COURSE=C1   COURSE=C2   COURSE=C3   Total 
   =====================================================
   T1                  6           6           9      21 
   T2                  9           9           9      27 
   =====================================================
   Total              15          15          18      48 
   >>> print(np.sum(counts))
   48
   
Converting a :class:`PyvtTbl` to a :class:`DataFrame`
-----------------------------------------------------
:class:`PyvtTbl`.:meth:`to_dataframe` will return the pivoted data as a :class:`DataFrame` object

.. sourcecode:: python

   >>> import numpy as np
   >>> from pyvttbl import DataFrame
   >>> df = DataFrame()
   >>> df.read_tbl('example.csv')
   >>> df['LOG10_X'] = np.log10(df['X'])
   >>> pt = df.pivot('LOG10_X', ['TIME'], ['CONDITION'])
   >>> df2 = pt.to_dataframe()
   >>> print(df2)
   TIME    CONDITION=A   CONDITION=B 
   =================================
   day           1.864         1.933 
   night         1.622         1.731 
   