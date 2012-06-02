:class:`pyvttbl.stats.ChiSquare1way` Overview
==========================================

:class:`ChiSquare1way` conducts a chi-squared test on a list of frequencies.

A simple example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    >>> from pyvttbl.stats import ChiSquare1way
    >>> x2 = ChiSquare1way()
    >>> x2.run([17, 19, 18, 20, 32, 20])
    >>> print(x2)
    Chi-Square: Single Factor

    SUMMARY
               A    B    C    D    E    F  
    ======================================
    Observed   17   19   18   20   32   20 
    Expected   21   21   21   21   21   21 

    CHI-SQUARE TESTS
                         Value   df     P   
    =======================================
    Pearson Chi-Square   7.238    5   0.204 
    Likelihood Ratio     6.517    5   0.259 
    Observations           126              

    POST-HOC POWER
           Measure                 
    ==============================
    Effect size w            0.240 
    Non-centrality lambda    7.238 
    Critical Chi-Square     11.070 
    Power                    0.516 
    
If only one argument is provided the expected counts are assumed to be
evenly distributed amongst the possible outcomes. Unequal expected outcomes 
can be specified using the `expected` keyword.

::

    >>> x2.run([17, 19, 18, 20, 32, 20], expected=[10,10,10,10,10,102])
    >>> print(x2)
    Chi-Square: Single Factor

    SUMMARY
               A    B    C    D    E     F  
    =======================================
    Observed   17   19   18   20   32    20 
    Expected   10   10   10   10   10   102 

    CHI-SQUARE TESTS
                          Value    df   P 
    =====================================
    Pearson Chi-Square   143.722    5   0 
    Likelihood Ratio     100.590    5   0 
    Observations             126          

    POST-HOC POWER
           Measure                  
    ===============================
    Effect size w             1.068 
    Non-centrality lambda   143.722 
    Critical Chi-Square      11.070 
    Power                         1 
    >>> 
    
Meaningful column labels can also be supplied to the analysis.

::

>>> x2.run([17, 19, 18, 20, 32, 20], conditions_list=[1,2,3,4,5,6])
>>> print(x2)
Chi-Square: Single Factor

SUMMARY
           1    2    3    4    5    6  
======================================
Observed   17   19   18   20   32   20 
Expected   21   21   21   21   21   21 

CHI-SQUARE TESTS
                     Value   df     P   
=======================================
Pearson Chi-Square   7.238    5   0.204 
Likelihood Ratio     6.517    5   0.259 
Observations           126              

POST-HOC POWER
       Measure                 
==============================
Effect size w            0.240 
Non-centrality lambda    7.238 
Critical Chi-Square     11.070 
Power                    0.516 
>>>

Running analysis from a DataFrame
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:class:`DataFrame` has a wrapper method for conducting a one-way chi-squared
analysis. It assumes the data is denote individual categorical events and
will calculate the frequencies for the user.

::

    >>> from pyvttbl import DataFrame
    >>> from random import randint # simulate a 6-sided die
    >>> df = DataFrame()
    >>> for i in _xrange(1000):
        df.insert([('roll',i), ('outcome', randint(1,6))])
    ...
    SyntaxError: invalid syntax
    >>> for i in _xrange(1000):
        df.insert([('roll',i), ('outcome', randint(1,6))])

    >>> print(df.descriptives('outcome'))
    Descriptive Statistics
      outcome
    ==========================
     count        1000.000 
     mean            3.536 
     mode            5.000 
     var             2.960 
     stdev           1.720 
     sem             0.054 
     rms             3.932 
     min             1.000 
     Q1              2.000 
     median          4.000 
     Q3              5.000 
     max             6.000 
     range           5.000 
     95ci_lower      3.429 
     95ci_upper      3.643 
    >>> x2 = df.chisquare1way('outcome')
    >>> print(x2)
    Chi-Square: Single Factor

    SUMMARY
                  1         2         3         4         5         6    
    ====================================================================
    Observed       164       172       147       169       177       171 
    Expected   166.667   166.667   166.667   166.667   166.667   166.667 

    CHI-SQUARE TESTS
                         Value   df     P   
    =======================================
    Pearson Chi-Square   3.320    5   0.651 
    Likelihood Ratio     3.402    5   0.638 
    Observations          1000              

    POST-HOC POWER
           Measure                 
    ==============================
    Effect size w            0.058 
    Non-centrality lambda    3.320 
    Critical Chi-Square     11.070 
    Power                    0.244 

And we fail to reject the null.
    
Direct access to results
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Like many of the :mod:`pyvttbl.stats` objects :class:`ChiSquare1way`
inherents an :class:`OrderedDict`.
::

    ChiSquare1way([('chisq', 7.238095238095238), 
                   ('p', 0.20352651555710358), 
                   ('df', 5), 
                   ('lnchisq', 6.517343547697185), 
                   ('lnp', 0.25907994276152624), 
                   ('lndf', 5), 
                   ('N', 126), 
                   ('w', 0.23967728365938887), 
                   ('lambda', 7.238095238095237), 
                   ('crit_chi2', 11.070497693516351), 
                   ('power', 0.51617215660330651)], 
                   conditions_list=[1, 2, 3, 4, 5, 6])
                   