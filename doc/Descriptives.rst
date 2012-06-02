:class:`pyvttbl.stats.Descriptives` Overview
==============================================

This class calculates, reports, and stores summary statistics.

Using class directly
-------------------------

Here we examine data sampled from a normal distribution with
a mean of 0 and a standard deviation of 1.

::

    >>> from pyvttbl.stats import Descriptives
    >>> from random import normalvariate
    >>> desc = Descriptives()
    >>> desc.run([normalvariate(mu=0,sigma=1) for i in xrange(1000)])
    >>> print(desc)
    Descriptive Statistics
      
    ==========================
     count        1000.000 
     mean            0.025 
     mode           -0.182 
     var             0.934 
     stdev           0.967 
     sem             0.031 
     rms             0.966 
     min            -2.863 
     Q1             -0.589 
     median          0.004 
     Q3              0.681 
     max             3.467 
     range           6.330 
     95ci_lower     -0.035 
     95ci_upper      0.085 
     
:class:`Descriptives` objects inherent :mod:`collections`. :class:`OrderedDict`

::

    >>> desc
    Descriptives([('count', 1000.0), 
                  ('mean', 0.025036481568892106), 
                  ('mode', -0.18188273915666869), 
                  ('var', 0.93438245182138646), 
                  ('stdev', 0.9666346009849774), 
                  ('sem', 0.030567670042405695), 
                  ('rms', 0.9664755013857896), 
                  ('min', -2.8632575029784033), 
                  ('Q1', -0.58880378505312103), 
                  ('median', 0.0040778734181358472), 
                  ('Q3', 0.68105047745497083), 
                  ('max', 3.4671371053896305), 
                  ('range', 6.3303946083680334), 
                  ('95ci_lower', -0.034876151714223057), 
                  ('95ci_upper', 0.084949114852007263)], 
                  cname='')
                  
This means data can be accessed as if the descriptive statistics were stored in a dict.

::          

    >>> desc['var']
    0.93438245182138646
    >>> 
    
    
Using DataFrame wrapper
-------------------------

::

    >>> df = DataFrame()
    >>> df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
    >>> desc = df.descriptives('ERROR')
    >>> print(desc)
    Descriptive Statistics
      ERROR
    ==========================
     count        48.000 
     mean          3.896 
     mode          3.000 
     var           5.797 
     stdev         2.408 
     sem           0.348 
     rms           4.567 
     min           0.000 
     Q1            2.000 
     median        3.000 
     Q3            5.000 
     max          10.000 
     range        10.000 
     95ci_lower    3.215 
     95ci_upper    4.577