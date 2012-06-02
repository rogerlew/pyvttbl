:class:`pyvttbl.stats.Histogram` Overview
==============================================

Used to calculate histogram counts (no plotting).

Example using :class:`DataFrame` wrapper
----------------------------------------

::

    >>> df=DataFrame()
    >>> df.read_tbl('data/words~ageXcondition.csv')
    >>> D = df.histogram('WORDS')
    >>> print(D)
    Cumulative Histogram for WORDS
     Bins    Values  
    ================
     3.000     4.000 
     5.000    18.000 
     7.000    35.000 
     9.000    47.000 
    11.000    62.000 
    13.000    72.000 
    15.000    81.000 
    17.000    86.000 
    19.000    92.000 
    21.000   100.000 
    23.000           
    
Example using :class:`Histogram` directly
---------------------------------

::

    >>> from pyvttbl.stats import Histogram
    >>> form random import normalvariate
    >>> data = [normalvariate(mu=0,sigma=1) for i in xrange(1000)]
    >>> hist = Histogram()
    >>> hist.run(data, bins=20)
    >>> print(hist)
    Histogram for 
     Bins    Values  
    ================
    -2.562     4.000 
    -2.280    11.000 
    -1.999    25.000 
    -1.717    21.000 
    -1.435    40.000 
    -1.153    90.000 
    -0.872    93.000 
    -0.590    84.000 
    -0.308   107.000 
    -0.027   121.000 
     0.255   101.000 
     0.537    88.000 
     0.819    87.000 
     1.100    39.000 
     1.382    38.000 
     1.664    26.000 
     1.945    10.000 
     2.227     8.000 
     2.509     4.000 
     2.791     3.000 
     3.072           
    >>> hist.run(data, bins=20, cumulative=True)
    >>> print(hist)
    Cumulative Histogram for 
     Bins     Values  
    =================
    -2.562      4.000 
    -2.280     15.000 
    -1.999     40.000 
    -1.717     61.000 
    -1.435    101.000 
    -1.153    191.000 
    -0.872    284.000 
    -0.590    368.000 
    -0.308    475.000 
    -0.027    596.000 
     0.255    697.000 
     0.537    785.000 
     0.819    872.000 
     1.100    911.000 
     1.382    949.000 
     1.664    975.000 
     1.945    985.000 
     2.227    993.000 
     2.509    997.000 
     2.791   1000.000 
     3.072        