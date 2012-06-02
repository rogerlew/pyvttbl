:class:`pyvttbl.stats.Marginals` Overview
==============================================

Used to calculate marginal descriptive statistics.

Example
--------------------------

To calculate marginals we first need to get data into a :class:`DataFrame`

::

    >>> df=DataFrame()
    >>> df.read_tbl('data/words~ageXcondition.csv')
    >>> D = df.marginals('WORDS',factors=['AGE','CONDITION'])
    >>> print(D)
    AGE    CONDITION    Mean    Count   Std.    95% CI   95% CI 
                                        Error   lower    upper  
    ============================================================
    old     adjective   11.000   10      0.789    9.454   12.546 
    old     counting     7.000   10      0.577    5.868    8.132 
    old     imagery     13.400   10      1.424   10.610   16.190 
    old     intention   12.000   10      1.183    9.681   14.319 
    old     rhyming      6.900   10      0.674    5.579    8.221 
    young   adjective   14.800   10      1.104   12.637   16.963 
    young   counting     6.500   10      0.453    5.611    7.389 
    young   imagery     17.600   10      0.819   15.994   19.206 
    young   intention   19.300   10      0.844   17.646   20.954 
    young   rhyming      7.600   10      0.618    6.388    8.812 
