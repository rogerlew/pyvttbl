Anova
======================================

:class:`Anova` is capable of performing multiple factor between, within, and 
mixed analyses of variance. Within and mixed analyses of variance provide 
corrections for violations of sphericity (Huynh-Feldt, Greenhouse-Geisser, Box). 
The Anova objects also have a convenience method that aids in creating interaction 
plots once an analysis has been run.

If you would like to run multiple factor ANOVAs but don't want the hassle of coding 
your analyses you might want to check out .. _GUANO: http://sourceforge.net/projects/guano/ GUANO. 
It uses `pyvttbl` and `Anova` behind the scenes but provides a point-and-click interface. 

Running an ANOVA
----------------

The recommended way to run an ANOVA is to first load data into a `DataFrame` and use 
`DataFrame.anova` to run the analysis. Calling `DataFrame.anova` will return an `Anova` object.

Example Within-Subjects ANOVA
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    >>> from __future__ import print_function
    >>>
    >>> df = DataFrame()
    >>> fname = 'error~subjectXtimeofdayXcourseXmodel.csv'
    >>> df.read_tbl(fname)
    >>> aov = df.anova('ERROR',
                       wfactors=['TIMEOFDAY','COURSE','MODEL'])
    >>> print(type(aov))
    <class 'anova.Anova'>

Example Between-Subjects ANOVA
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^      

    >>> df=DataFrame()
    >>> fname='words~ageXcondition.csv'
    >>> df.read_tbl(fname)
    >>> aov=Anova()
    >>> aov.run(df, 'WORDS', bfactors=['AGE','CONDITION'])

Notice in this case we are not using `DataFrame.anova`. We are initializing an `Anova` 
object and passing a `DataFrame` instance to it. 


Example Mixed-Subjects ANOVA
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^      

To run a mixed ANOVA we just have to specify both `wfactors` and `bfactors`.


.. note:: Both `wfactors` and `bfactors` must be iterable (lists of labels).

    >>> df = DataFrame()
    >>> fname = 'suppression~subjectXgroupXcycleXphase.csv'
    >>> df.read_tbl(fname)
    >>> aov = df.anova('SUPPRESSION',
                       wfactors=['CYCLE','PHASE'],
                       bfactors=['GROUP'])
    
Specifying a Data Transformation
--------------------------------- 

The analysis is also capable of applying log10, square-root, arc-sine, reciprocal, 
an Windsoring data transforms. These are specified with the `transform` keyword. 

    ==========================  ====================  ==========
    transform keyword           Transform             Comments
    ==========================  ====================  ==========
    ''                          X                     default
    'log' or 'log10'            numpy.log10(X)       
    'reciprocal' or  'inverse'  1/X                  
    'square-root' or 'sqrt'     numpy.sqrt(X)  
    'arcsine' or 'arcsin'       numpy.arcsin(X)
    'windsor01'                 anova.windsor(X, 1)   1% trim    
    'windsor05'                 anova.windsor(X, 5)   5% trim    
    'windsor10'                 anova.windsor(X, 10)  10% trim  
    ==========================  ====================  ========== 

Printing a Summary
------------------- 

Once an analysis is ran the results can be viewed by printing the object. By default estimated marginal means are also provided.

    >>> from __future__ import print_function
    >>>
    >>> df = DataFrame()
    >>> fname = 'error~subjectXtimeofdayXcourseXmodel.csv'
    >>> df.read_tbl(fname)
    >>> aov = df.anova('ERROR',
                       wfactors=['TIMEOFDAY','COURSE','MODEL'])
    >>> print(aov)

::

    ERROR ~ TIMEOFDAY * COURSE * MODEL

    TESTS OF WITHIN SUBJECTS EFFECTS

    Measure: ERROR
         Source                              Type III    eps     df       MS         F         Sig.      et2_G   Obs.    SE     95% CI    lambda    Obs.  
                                                SS                                                                                                  Power 
    =====================================================================================================================================================
    TIMEOFDAY           Sphericity Assumed    140.167       -       1   140.167    120.143       0.008   3.391     27   0.456    0.894   1621.929       1 
                        Greenhouse-Geisser    140.167       1       1   140.167    120.143       0.008   3.391     27   0.456    0.894   1621.929       1 
                        Huynh-Feldt           140.167       1       1   140.167    120.143       0.008   3.391     27   0.456    0.894   1621.929       1 
                        Box                   140.167       1       1   140.167    120.143       0.008   3.391     27   0.456    0.894   1621.929       1 
    -----------------------------------------------------------------------------------------------------------------------------------------------------
    Error(TIMEOFDAY)    Sphericity Assumed      2.333       -       2     1.167                                                                           
                        Greenhouse-Geisser      2.333       1       2     1.167                                                                           
                        Huynh-Feldt             2.333       1       2     1.167                                                                           
                        Box                     2.333       1       2     1.167                                                                           
    -----------------------------------------------------------------------------------------------------------------------------------------------------
    COURSE              Sphericity Assumed     56.778       -       2    28.389   1022.000   3.815e-06   1.374     18   0.056    0.109   9198.000       1 
                        Greenhouse-Geisser     56.778   0.501   1.002    56.667   1022.000   9.664e-04   1.374     18   0.056    0.109   9198.000       1 
                        Huynh-Feldt            56.778   0.504   1.008    56.336   1022.000   9.349e-04   1.374     18   0.056    0.109   9198.000       1 
                        Box                    56.778   0.500       1    56.778   1022.000   9.770e-04   1.374     18   0.056    0.109   9198.000       1 
    -----------------------------------------------------------------------------------------------------------------------------------------------------
    Error(COURSE)       Sphericity Assumed      0.111       -       4     0.028                                                                           
                        Greenhouse-Geisser      0.111   0.501   2.004     0.055                                                                           
                        Huynh-Feldt             0.111   0.504   2.016     0.055                                                                           
                        Box                     0.111   0.500       2     0.056                                                                           
    -----------------------------------------------------------------------------------------------------------------------------------------------------
    MODEL               Sphericity Assumed     51.444       -       2    25.722     92.600   4.470e-04   1.245     18   0.176    0.345    833.400       1 
                        Greenhouse-Geisser     51.444   0.507   1.013    50.770     92.600       0.010   1.245     18   0.176    0.345    833.400   1.000 
                        Huynh-Feldt            51.444   0.527   1.054    48.817     92.600       0.009   1.245     18   0.176    0.345    833.400   1.000 
                        Box                    51.444   0.500       1    51.444     92.600       0.011   1.245     18   0.176    0.345    833.400   1.000 
    -----------------------------------------------------------------------------------------------------------------------------------------------------
    Error(MODEL)        Sphericity Assumed      1.111       -       4     0.278                                                                           
                        Greenhouse-Geisser      1.111   0.507   2.027     0.548                                                                           
                        Huynh-Feldt             1.111   0.527   2.108     0.527                                                                           
                        Box                     1.111   0.500       2     0.556                                                                           
    -----------------------------------------------------------------------------------------------------------------------------------------------------
    TIMEOFDAY *         Sphericity Assumed      5.444       -       2     2.722      2.085       0.240   0.132      9   0.540    1.057      9.383   0.446 
    COURSE              Greenhouse-Geisser      5.444   0.814   1.628     3.345      2.085       0.255   0.132      9   0.540    1.057      9.383   0.373 
                        Huynh-Feldt             5.444       1       2     2.722      2.085       0.240   0.132      9   0.540    1.057      9.383   0.446 
                        Box                     5.444   0.500       1     5.444      2.085       0.286   0.132      9   0.540    1.057      9.383   0.244 
    -----------------------------------------------------------------------------------------------------------------------------------------------------
    Error(TIMEOFDAY *   Sphericity Assumed      5.222       -       4     1.306                                                                           
    COURSE)             Greenhouse-Geisser      5.222   0.814   3.255     1.604                                                                           
                        Huynh-Feldt             5.222       1       4     1.306                                                                           
                        Box                     5.222   0.500       2     2.611                                                                           
    -----------------------------------------------------------------------------------------------------------------------------------------------------
    TIMEOFDAY *         Sphericity Assumed     16.778       -       2     8.389     37.750       0.003   0.406      9   0.223    0.436    169.875   1.000 
    MODEL               Greenhouse-Geisser     16.778   0.540   1.079    15.545     37.750       0.021   0.406      9   0.223    0.436    169.875   0.993 
                        Huynh-Feldt            16.778   0.571   1.142    14.697     37.750       0.018   0.406      9   0.223    0.436    169.875   0.996 
                        Box                    16.778   0.500       1    16.778     37.750       0.025   0.406      9   0.223    0.436    169.875   0.985 
    -----------------------------------------------------------------------------------------------------------------------------------------------------
    Error(TIMEOFDAY *   Sphericity Assumed      0.889       -       4     0.222                                                                           
    MODEL)              Greenhouse-Geisser      0.889   0.540   2.159     0.412                                                                           
                        Huynh-Feldt             0.889   0.571   2.283     0.389                                                                           
                        Box                     0.889   0.500       2     0.444                                                                           
    -----------------------------------------------------------------------------------------------------------------------------------------------------
    COURSE *            Sphericity Assumed      8.778       -       4     2.194      3.762       0.052   0.212      6   0.367    0.719     11.286   0.504 
    MODEL               Greenhouse-Geisser      8.778   0.354   1.415     6.204      3.762       0.157   0.212      6   0.367    0.719     11.286   0.223 
                        Huynh-Feldt             8.778   0.354   1.415     6.204      3.762       0.157   0.212      6   0.367    0.719     11.286   0.223 
                        Box                     8.778   0.500       2     4.389      3.762       0.120   0.212      6   0.367    0.719     11.286   0.292 
    -----------------------------------------------------------------------------------------------------------------------------------------------------
    Error(COURSE *      Sphericity Assumed      4.667       -       8     0.583                                                                           
    MODEL)              Greenhouse-Geisser      4.667   0.354   2.830     1.649                                                                           
                        Huynh-Feldt             4.667   0.354   2.830     1.649                                                                           
                        Box                     4.667   0.500       4     1.167                                                                           
    -----------------------------------------------------------------------------------------------------------------------------------------------------
    TIMEOFDAY *         Sphericity Assumed      2.778       -       4     0.694      1.923       0.200   0.067      3   0.408    0.800      2.885   0.152 
    COURSE *            Greenhouse-Geisser      2.778   0.290   1.159     2.397      1.923       0.293   0.067      3   0.408    0.800      2.885   0.087 
    MODEL               Huynh-Feldt             2.778   0.290   1.159     2.397      1.923       0.293   0.067      3   0.408    0.800      2.885   0.087 
                        Box                     2.778   0.500       2     1.389      1.923       0.260   0.067      3   0.408    0.800      2.885   0.109 
    -----------------------------------------------------------------------------------------------------------------------------------------------------
    Error(TIMEOFDAY *   Sphericity Assumed      2.889       -       8     0.361                                                                           
    COURSE *            Greenhouse-Geisser      2.889   0.290   2.318     1.246                                                                           
    MODEL)              Huynh-Feldt             2.889   0.290   2.318     1.246                                                                           
                        Box                     2.889   0.500       4     0.722                                                                           

    TABLES OF ESTIMATED MARGINAL MEANS

    Estimated Marginal Means for TIMEOFDAY
    TIMEOFDAY   Mean    Std. Error   95% Lower Bound   95% Upper Bound 
    ==================================================================
    T1          5.778        0.457             4.882             6.674 
    T2          2.556        0.229             2.108             3.003 

    Estimated Marginal Means for COURSE
    COURSE   Mean    Std. Error   95% Lower Bound   95% Upper Bound 
    ===============================================================
    C1       5.222        0.608             4.031             6.414 
    C2       4.500        0.562             3.399             5.601 
    C3       2.778        0.432             1.931             3.625 

    Estimated Marginal Means for MODEL
    MODEL   Mean    Std. Error   95% Lower Bound   95% Upper Bound 
    ==============================================================
    M1      5.333        0.686             3.989             6.678 
    M2      4.222        0.558             3.129             5.315 
    M3      2.944        0.328             2.301             3.588 

    Estimated Marginal Means for TIMEOFDAY * COURSE
    TIMEOFDAY   COURSE   Mean    Std. Error   95% Lower Bound   95% Upper Bound 
    ===========================================================================
    T1          C1       7.222        0.641             5.966             8.478 
    T1          C2       6.111        0.790             4.564             7.659 
    T1          C3           4        0.577             2.868             5.132 
    T2          C1       3.222        0.401             2.437             4.007 
    T2          C2       2.889        0.261             2.378             3.400 
    T2          C3       1.556        0.294             0.979             2.132 

    Estimated Marginal Means for TIMEOFDAY * MODEL
    TIMEOFDAY   MODEL   Mean    Std. Error   95% Lower Bound   95% Upper Bound 
    ==========================================================================
    T1          M1      7.444        0.835             5.807             9.081 
    T1          M2      6.111        0.512             5.107             7.115 
    T1          M3      3.778        0.465             2.867             4.689 
    T2          M1      3.222        0.434             2.372             4.073 
    T2          M2      2.333        0.408             1.533             3.133 
    T2          M3      2.111        0.261             1.600             2.622 

    Estimated Marginal Means for COURSE * MODEL
    COURSE   MODEL   Mean    Std. Error   95% Lower Bound   95% Upper Bound 
    =======================================================================
    C1       M1      6.667        1.085             4.540             8.794 
    C1       M2      5.167        1.195             2.825             7.509 
    C1       M3      3.833        0.601             2.656             5.011 
    C2       M1      6.167        1.195             3.825             8.509 
    C2       M2      4.167        0.792             2.614             5.720 
    C2       M3      3.167        0.477             2.231             4.102 
    C3       M1      3.167        0.872             1.457             4.877 
    C3       M2      3.333        0.882             1.605             5.062 
    C3       M3      1.833        0.307             1.231             2.436 

    Estimated Marginal Means for TIMEOFDAY * COURSE * MODEL
    TIMEOFDAY   COURSE   MODEL   Mean    Std. Error   95% Lower Bound   95% Upper Bound 
    ===================================================================================
    T1          C1       M1          9        0.577             7.868            10.132 
    T1          C1       M2      7.667        0.333             7.013             8.320 
    T1          C1       M3          5        0.577             3.868             6.132 
    T1          C2       M1      8.667        0.882             6.938            10.395 
    T1          C2       M2      5.667        0.882             3.938             7.395 
    T1          C2       M3          4        0.577             2.868             5.132 
    T1          C3       M1      4.667        1.202             2.311             7.022 
    T1          C3       M2          5        0.577             3.868             6.132 
    T1          C3       M3      2.333        0.333             1.680             2.987 
    T2          C1       M1      4.333        0.333             3.680             4.987 
    T2          C1       M2      2.667        0.882             0.938             4.395 
    T2          C1       M3      2.667        0.333             2.013             3.320 
    T2          C2       M1      3.667        0.333             3.013             4.320 
    T2          C2       M2      2.667        0.333             2.013             3.320 
    T2          C2       M3      2.333        0.333             1.680             2.987 
    T2          C3       M1      1.667        0.333             1.013             2.320 
    T2          C3       M2      1.667        0.882            -0.062             3.395 
    T2          C3       M3      1.333        0.333             0.680             1.987 
    }}}

Writing Summary to File
-------------------------

If you are familiar with Python it should be obvious that the class essential 
has a :meth:`__str__` method that generates the above output. If you are not as familiar 
with Python all you need to know is that turning the object into a string (via `str(aov)`) 
yields the summary as a big string. This means that writing the summary to a file is pretty 
straightforward.
    
    >>> with open('output.txt','wb') as f:
            f.write(str(aov))
    >>>
    
Working with `Anova` Objects (Advanced)
----------------------------------------

If you wish perform additional operations with the results the data from the main effects and
 interactions can be accessed directly. The `Anova` are dictionaries whose keys coorespond to 
 the main effects and interactions.
    
    >>> for d in aov:
            print(d)
    ('TIMEOFDAY',)
    ('COURSE',)
    ('MODEL',)
    ('TIMEOFDAY', 'COURSE')
    ('TIMEOFDAY', 'MODEL')
    ('COURSE', 'MODEL')
    ('TIMEOFDAY', 'COURSE', 'MODEL')
    
The values are dictionaries of the various values pertaining to the effect.

    >>> from pprint import pprint as pp
    >>> pp(aov[('TIMEOFDAY', 'COURSE', 'MODEL')])
    {'F': 1.9230769230769222,
     'F_gg': 1.923076923076922,
     'F_hf': 1.923076923076922,
     'F_lb': 1.9230769230769222,
     'ci': 0.80005506708787966,
     'ci_gg': 0.80005506708787966,
     'ci_hf': 0.80005506708787966,
     'ci_lb': 0.80005506708787966,
     'critT': 2.3060041350333709,
     'critT_gg': 2.3060041350333709,
     'critT_hf': 2.3060041350333709,
     'critT_lb': 2.3060041350333709,
     'df': 4,
     'df_gg': 1.1590909090909087,
     'df_hf': 1.1590909090909087,
     'df_lb': 2.0,
     'dfe': 8.0,
     'dfe_gg': 2.3181818181818175,
     'dfe_hf': 2.3181818181818175,
     'dfe_lb': 4.0,
     'eps_gg': 0.28977272727272718,
     'eps_hf': 0.28977272727272718,
     'eps_lb': 0.5,
     'eta': 0.067204301075268813,
     'lambda': 2.8846153846153828,
     'lambda_gg': 2.8846153846153828,
     'lambda_hf': 2.8846153846153828,
     'lambda_lb': 2.8846153846153828,
     'mse': 0.36111111111111122,
     'mse_gg': 1.2461873638344234,
     'mse_hf': 1.2461873638344234,
     'mse_lb': 0.72222222222222243,
     'mss': 0.69444444444444431,
     'mss_gg': 2.3965141612200438,
     'mss_hf': 2.3965141612200438,
     'mss_lb': 1.3888888888888886,
     'obs': 3.0,
     'obs_gg': 3.0,
     'obs_hf': 3.0,
     'obs_lb': 3.0,
     'p': 0.19999514760153031,
     'p_gg': 0.2930377602206829,
     'p_hf': 0.2930377602206829,
     'p_lb': 0.2599000384467513,
     'power': 0.15191672432754222,
     'power_gg': 0.087331953378021465,
     'power_hf': 0.087331953378021465,
     'power_lb': 0.10875612151993008,
     'se': 0.40819136075912227,
     'se_gg': 0.40819136075912227,
     'se_hf': 0.40819136075912227,
     'se_lb': 0.40819136075912227,
     'ss': 2.7777777777777772,
     'sse': 2.8888888888888897,
     'y2': array([ 9.        ,  7.66666667,  5.        ,  8.66666667,  5.66666667,
            4.        ,  4.66666667,  5.        ,  2.33333333,  4.33333333,
            2.66666667,  2.66666667,  3.66666667,  2.66666667,  2.33333333,
            1.66666667,  1.66666667,  1.33333333])}

Hopefully that is enough to get you started.