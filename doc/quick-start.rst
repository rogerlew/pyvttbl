Quick-Start Guide
=================

pyvttbl has two primary containers for storing data. :class:`DataFrame` objects 
hold tabulated data in a manner similiar to what you would have in a 
spreadsheet. DataFrames are basically dictionary objects. The *keys*
are the names of the columns and the *values* are NumPy arrays or
NumPy MaskedArrays if missing data is specified or encountered when
reading datafiles.

DataFrames can be pivoted to created :class:`PyvtTbl` objects. These are 
subclasses of :class:`NumPy.MaskedArray`. The use of :class:`MaskedArray` helps to make
:class:`PyvtTbl` objects robust to invalid or missing data. 

   
Loading Data into a :class:`DataFrame`
--------------------------------------

Before we can start building contingency tables we need to first load the 
data into a :class:`DataFrame` object. Data can be read from plaintext datafiles 
using the :class:`DataFrame`. :meth:`read_tbl` method or inserted one row at a time using 
:class:`DataFrame`. :meth:`insert`. DataFrames can be attached to one another using 
:class:`DataFrame`. :meth:`attach`. The read_tbl method is looking for comma separated values 
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
 stdevp(X)	          standard deviation of the population X (N)
 tolist(X)            puts the values of X in a list (as 3 dimensional PyvtTbl)
 var(X)               variance estimate of the samples in X (N-1)
 varp(X)              variance of the population X (N)
==================   ===========================================================

The pyvttbl module takes advantage of aggregate functions in from pystaggrelite3. 
You can also bind your own using :class:`DataFrame`. :meth:`bind_aggregate`.

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
   
Example using the 'tolist' aggregator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    >>> pt = df.pivot('SUPPRESSION',
                      rows=['CYCLE', 'PHASE','GROUP', 'AGE'],
                      aggregate='tolist')
    >>> print(pt)
    tolist(SUPPRESSION)
    CYCLE   PHASE   GROUP    AGE                         Value                       
    ================================================================================
    1       I       AA      old        [1.0, 37.0, 18.0, 1.0, 44.0, 15.0, 0.0, 26.0] 
    1       I       AA      young       [6.2, 16.4, 7.6, 1.2, 13.8, 13.0, 1.0, 10.2] 
    1       I       AB      old        [1.0, 21.0, 15.0, 30.0, 11.0, 16.0, 7.0, 0.0] 
    1       I       AB      young          [3.2, 9.2, 3.0, 9.0, 6.2, 11.2, 2.4, 0.0] 
    1       I       LAB     old      [33.0, 4.0, 32.0, 17.0, 44.0, 12.0, 18.0, 13.0] 
    1       I       LAB     young          [15.6, 8.8, 7.4, 4.4, 8.8, 5.4, 4.6, 7.6] 
    1       II      AA      old        [6.0, 59.0, 43.0, 2.0, 25.0, 14.0, 3.0, 15.0] 
    1       II      AA      young        [4.2, 21.8, 15.6, 0.4, 6.0, 12.8, 0.6, 5.0] 
    1       II      AB      old     [28.0, 21.0, 17.0, 34.0, 23.0, 11.0, 26.0, 22.0] 
    1       II      AB      young        [5.6, 14.2, 5.4, 15.8, 5.6, 4.2, 5.2, 13.4] 
    1       II      LAB     old     [43.0, 35.0, 39.0, 34.0, 52.0, 16.0, 42.0, 29.0] 
    1       II      LAB     young    [14.6, 15.0, 13.8, 14.8, 20.4, 3.2, 16.4, 11.8] 
    2       I       AA      old       [16.0, 28.0, 38.0, 9.0, 28.0, 22.0, 7.0, 31.0] 
    2       I       AA      young      [11.2, 10.6, 14.6, 7.8, 10.6, 5.4, 7.4, 14.2] 
    2       I       AB      old     [22.0, 16.0, 13.0, 55.0, 12.0, 18.0, 29.0, 23.0] 
    2       I       AB      young       [12.4, 9.2, 2.6, 12.0, 11.4, 3.6, 14.8, 4.6] 
    2       I       LAB     old        [40.0, 9.0, 38.0, 21.0, 37.0, 9.0, 3.0, 14.0] 
    2       I       LAB     young         [12.0, 7.8, 16.6, 6.2, 9.4, 9.8, 8.6, 8.8] 
    2       II      AA      old       [8.0, 36.0, 50.0, 8.0, 42.0, 32.0, 17.0, 32.0] 
    2       II      AA      young        [7.6, 10.2, 19.0, 8.6, 9.4, 8.4, 11.4, 7.4] 
    2       II      AB      old     [48.0, 40.0, 35.0, 54.0, 33.0, 34.0, 40.0, 45.0] 
    2       II      AB      young   [14.6, 11.0, 15.0, 13.8, 11.6, 11.8, 13.0, 14.0] 
    2       II      LAB     old     [52.0, 42.0, 47.0, 41.0, 48.0, 39.0, 62.0, 44.0] 
    2       II      LAB     young    [17.4, 17.4, 14.4, 8.2, 14.6, 17.8, 12.4, 12.8] 
    3       I       AA      old        [9.0, 34.0, 39.0, 6.0, 47.0, 16.0, 6.0, 28.0] 
    3       I       AA      young      [6.8, 13.8, 13.8, 6.2, 19.4, 12.2, 1.2, 10.6] 
    3       I       AB      old     [22.0, 15.0, 22.0, 37.0, 10.0, 11.0, 25.0, 18.0] 
    3       I       AB      young        [4.4, 9.0, 9.4, 14.4, 3.0, 12.2, 12.0, 8.6] 
    3       I       LAB     old        [39.0, 4.0, 24.0, 27.0, 33.0, 9.0, 45.0, 9.0] 
    3       I       LAB     young         [12.8, 7.8, 8.8, 8.4, 9.6, 6.8, 13.0, 8.8] 
    3       II      AA      old       [14.0, 32.0, 15.0, 5.0, 46.0, 23.0, 9.0, 22.0] 
    3       II      AA      young       [9.8, 10.4, 6.0, 2.0, 17.2, 6.6, 11.8, 12.4] 
    3       II      AB      old     [50.0, 39.0, 45.0, 57.0, 50.0, 40.0, 50.0, 38.0] 
    3       II      AB      young    [10.0, 8.8, 14.0, 21.4, 14.0, 18.0, 16.0, 13.6] 
    3       II      LAB     old     [52.0, 46.0, 44.0, 50.0, 53.0, 59.0, 49.0, 50.0] 
    3       II      LAB     young   [20.4, 12.2, 17.8, 10.0, 16.6, 19.8, 10.8, 17.0] 
    4       I       AA      old      [11.0, 26.0, 29.0, 5.0, 33.0, 32.0, 10.0, 16.0] 
    4       I       AA      young      [3.2, 14.2, 11.8, 10.0, 8.6, 13.4, 5.0, 13.2] 
    4       I       AB      old        [14.0, 11.0, 1.0, 57.0, 8.0, 5.0, 14.0, 15.0] 
    4       I       AB      young         [6.8, 6.2, 5.2, 11.4, 4.6, 6.0, 9.8, 12.0] 
    4       I       LAB     old     [38.0, 23.0, 16.0, 13.0, 33.0, 13.0, 60.0, 15.0] 
    4       I       LAB     young         [7.6, 7.6, 10.2, 9.6, 7.6, 6.6, 21.0, 7.0] 
    4       II      AA      old     [33.0, 37.0, 18.0, 15.0, 35.0, 26.0, 15.0, 15.0] 
    4       II      AA      young       [10.6, 16.4, 9.6, 9.0, 16.0, 8.2, 8.0, 11.0] 
    4       II      AB      old     [48.0, 56.0, 43.0, 68.0, 53.0, 40.0, 56.0, 50.0] 
    4       II      AB      young    [15.6, 14.2, 10.6, 15.6, 11.6, 8.0, 16.2, 11.0] 
    4       II      LAB     old     [48.0, 51.0, 40.0, 40.0, 43.0, 45.0, 57.0, 48.0] 
    4       II      LAB     young    [11.6, 16.2, 8.0, 17.0, 12.6, 18.0, 16.4, 15.6] 
    >>> pt[0,0,0]
    1.0
    >>> pt[-1,-1,-1]
    15.6
    >>> 

.. note:: Numpy ndarray objects and their subclasses need to have an equal number of elements at their
          greatest depth. If more elements meet the contingency criteria in one cell compared to another
          the cells are padded with masked values to the dimension with the greatest number of elements.
         
            for example:
         
            .. sourcecode:: python
            
                [[1, 2],
                 [3, 4, 5]]
                 
            would become:

            .. sourcecode:: python
            
                [[1, 2, --],
                 [3, 4, 5]]
   
Manipulating :class:`PyvtTbl` objects
-------------------------------------

Mathematical Operations
^^^^^^^^^^^^^^^^^^^^^^^^

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

The operations are applied to the row and column totals when 
possible. However, operations like np.sum behave as expected.


.. sourcecode:: python

   >>> import numpy as np
   >>> df=DataFrame()
   >>> df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
   >>> counts = df.pivot('ERROR', ['TIMEOFDAY'], ['COURSE'], 
                         aggregate='count')
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
   

:class:`PyvtTbl`. :meth:`transpose`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:meth:`transpose` returns a transposed copy of the table

.. sourcecode:: python

    >>> df=DataFrame()
    >>> df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
    >>> pt = df.pivot('ERROR', ['TIMEOFDAY'], ['COURSE'], 
                      aggregate='count')
    >>> print(pt)
    count(ERROR)
    TIMEOFDAY   COURSE=C1   COURSE=C2   COURSE=C3   Total 
    =====================================================
    T1                  6           6           9      21 
    T2                  9           9           9      27 
    =====================================================
    Total              15          15          18      48 
    >>> print(pt.transpose())
    count(ERROR)
    COURSE   TIMEOFDAY=T1   TIMEOFDAY=T2   Total 
    ============================================
    C1                  6              9      15 
    C2                  6              9      15 
    C3                  9              9      18 
    ============================================
    Total              21             27      48 
    >>> 
  
:class:`PyvtTbl`. :meth:`flatten`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:meth:`flatten` returns a flattened copy of the table
as a :class:`MaskedArray`

.. sourcecode:: python

    >>> # continued from above
    >>> print(pt.flatten())
    [6 9 6 9 9 9]
    >>> print(type(pt.flatten()))
    <class 'numpy.ma.core.MaskedArray'>
    
Iterating over :class:`PyvtTbl` objects
---------------------------------------

The default iteration method iterates over the first index of the PyvtTbl

::
  
    for L in pt <==> for pt[i] in xrange(pt.shape[0])

:class:`PyvtTbl`. :meth:`__iter__`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. sourcecode:: python

    >>> from __future__ import print_function
    >>> df=DataFrame()
    >>> df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
    >>> pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])
    >>> for L in pt:
            print(L)
            print()
        
    avg(ERROR)
    TIMEOFDAY   COURSE=C1   COURSE=C2   COURSE=C3 
    =============================================
    T1              7.167       6.500           4 

    avg(ERROR)
    TIMEOFDAY   COURSE=C1   COURSE=C2   COURSE=C3 
    =============================================
    T2              3.222       2.889       1.556 

    >>> 

:class:`PyvtTbl`. `flat`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`flat` is technically a property and not method so it is called 
without the "()"

.. sourcecode:: python

    >>> from __future__ import print_function
    >>> df=DataFrame()
    >>> df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
    >>> pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])
    >>> for L in pt.flat:
            print(L)

    7.16666666667
    6.5
    4.0
    3.22222222222
    2.88888888889
    1.55555555556
    >>> 

:class:`PyvtTbl`. :meth:`ndenumerate`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:meth:`ndenumerate` returns an iterator yielding pairs of array coordinates and values.

.. sourcecode:: python

    >>> from __future__ import print_function
    >>> df=DataFrame()
    >>> df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
    >>> pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])
    >>> for (rind,cind),L in pt.ndenumerate():
            print((rind,cind), L)

    (0, 0) 7.16666666667
    (0, 1) 6.5
    (0, 2) 4.0
    (1, 0) 3.22222222222
    (1, 1) 2.88888888889
    (1, 2) 1.55555555556
    >>> 
    
These indices can be used to lookup the row and column labels

.. sourcecode:: python

    >>> from __future__ import print_function
    >>> df=DataFrame()
    >>> df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
    >>> pt = df.pivot('ERROR', ['TIMEOFDAY','MODEL'],['COURSE'])
    >>> print(pt)
    avg(ERROR)
    TIMEOFDAY   MODEL   COURSE=C1   COURSE=C2   COURSE=C3   Total 
    =============================================================
    T1          M1              9       8.667       4.667   7.250 
    T1          M2          7.500           6           5       6 
    T1          M3              5       3.500       2.333   3.429 
    T2          M1          4.333       3.667       1.667   3.222 
    T2          M2          2.667       2.667       1.667   2.333 
    T2          M3          2.667       2.333       1.333   2.111 
    =============================================================
    Total                   4.800       4.333       2.778   3.896 
    >>> for (rind,cind),L in pt.ndenumerate():
            rlabel = ', '.join('%s=%s'%(k,v) for k,v in pt.rnames[rind])
            clabel = ', '.join('%s=%s'%(k,v) for k,v in pt.cnames[cind])
            print(rlabel, '\t', clabel, '\t', L)

        
    TIMEOFDAY=T1, MODEL=M1	 COURSE=C1 	 9.0
    TIMEOFDAY=T1, MODEL=M1	 COURSE=C2 	 8.66666666667
    TIMEOFDAY=T1, MODEL=M1	 COURSE=C3 	 4.66666666667
    TIMEOFDAY=T1, MODEL=M2	 COURSE=C1 	 7.5
    TIMEOFDAY=T1, MODEL=M2	 COURSE=C2 	 6.0
    TIMEOFDAY=T1, MODEL=M2	 COURSE=C3 	 5.0
    TIMEOFDAY=T1, MODEL=M3	 COURSE=C1 	 5.0
    TIMEOFDAY=T1, MODEL=M3	 COURSE=C2 	 3.5
    TIMEOFDAY=T1, MODEL=M3	 COURSE=C3 	 2.33333333333
    TIMEOFDAY=T2, MODEL=M1	 COURSE=C1 	 4.33333333333
    TIMEOFDAY=T2, MODEL=M1	 COURSE=C2 	 3.66666666667
    TIMEOFDAY=T2, MODEL=M1	 COURSE=C3 	 1.66666666667
    TIMEOFDAY=T2, MODEL=M2	 COURSE=C1 	 2.66666666667
    TIMEOFDAY=T2, MODEL=M2	 COURSE=C2 	 2.66666666667
    TIMEOFDAY=T2, MODEL=M2	 COURSE=C3 	 1.66666666667
    TIMEOFDAY=T2, MODEL=M3	 COURSE=C1 	 2.66666666667
    TIMEOFDAY=T2, MODEL=M3	 COURSE=C2 	 2.33333333333
    TIMEOFDAY=T2, MODEL=M3	 COURSE=C3 	 1.33333333333
    >>> 
    
.. note:: Unlike :mod:`numpy`. :meth:`ndenumerate`, :mod:`pyvttbl`. :meth:`ndenumerate`
          will only return the first two indices regardless of the number of dimensions
          in the table.
    
.. sourcecode:: python

    >>> pt = df.pivot('ERROR', ['TIMEOFDAY','MODEL'],['COURSE'], 
                      aggregate='tolist')
    >>> for (rind,cind),L in pt.ndenumerate():
            rlabel = ', '.join('%s=%s'%(k,v) for k,v in pt.rnames[rind])
            clabel = ', '.join('%s=%s'%(k,v) for k,v in pt.cnames[cind])
            print(rlabel, '\t', clabel, '\t', L.flatten())
        
    TIMEOFDAY=T1 	 COURSE=C1 	 [10.0 8.0 6.0 8.0 7.0 4.0 -- -- --]
    TIMEOFDAY=T1 	 COURSE=C2 	 [9.0 10.0 6.0 4.0 7.0 3.0 -- -- --]
    TIMEOFDAY=T1 	 COURSE=C3 	 [7.0 6.0 3.0 4.0 5.0 2.0 3.0 4.0 2.0]
    TIMEOFDAY=T2 	 COURSE=C1 	 [5.0 4.0 3.0 4.0 3.0 3.0 4.0 1.0 2.0]
    TIMEOFDAY=T2 	 COURSE=C2 	 [4.0 3.0 3.0 4.0 2.0 2.0 3.0 3.0 2.0]
    TIMEOFDAY=T2 	 COURSE=C3 	 [2.0 2.0 1.0 2.0 3.0 2.0 1.0 0.0 1.0]
    >>> 

Converting a :class:`PyvtTbl` to a :class:`DataFrame`
-----------------------------------------------------
:class:`PyvtTbl`. :meth:`to_dataframe` will return the pivoted data as a :class:`DataFrame` object

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
   