Anova1way
==========================================

`Anova1way` performs a single factor between analysis of variance.
The analysis automatically calculates descriptive, performs the O'Brien test 
for heterosphericity (H0 is that the variances are equal), performs post-hoc 
power analyses, and post-hoc pairwise comparisons. 

This ANOVA method is robust to non-equivalent sample sizes. The observed power 
estimates have been validated against `G*Power <http://www.psycho.uni-duesseldorf.de/aap/projects/gpower/>`_. 

Post-hoc comparisons can be made using the Tukey Test or the Newman-Keuls Test. 
If you are unfamiliar with these post-hoc multiple comparisons the idea is that the 
ANOVA will tell you if the data suggests that something is going on between the groups 
(not from the same population), but it doesn't tell you which groups are different 
from one another. The post-hoc comparisons compare the groups to one another and try 
and identify which pairs are different. 

Using the Anova1way object directly
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Example data from .. _Abdi, H. & Williams, L. J. (2010):http://www.utdallas.edu/~herve/abdi-NewmanKeuls2010-pretty.pdf. 
By default Anova1way will use the Tukey test for pairwise comparisons.

.. sourcecode:: python

    from pyvttbl import Anova1way
    d = [[21.0, 20.0, 26.0, 46.0, 35.0, 13.0, 41.0, 30.0, 42.0, 26.0],
         [23.0, 30.0, 34.0, 51.0, 20.0, 38.0, 34.0, 44.0, 41.0, 35.0],
         [35.0, 35.0, 52.0, 29.0, 54.0, 32.0, 30.0, 42.0, 50.0, 21.0],
         [44.0, 40.0, 33.0, 45.0, 45.0, 30.0, 46.0, 34.0, 49.0, 44.0],
         [39.0, 44.0, 51.0, 47.0, 50.0, 45.0, 39.0, 51.0, 39.0, 55.0]]
    conditions_list = 'Contact Hit Bump Collide Smash'.split()
    D=Anova1way()
    D.run(d, conditions_list=conditions_list)
    print(D)

::

    Anova: Single Factor on Measure

    SUMMARY
    Groups    Count   Sum   Average   Variance 
    ==========================================
    Contact      10   300        30    116.444 
    Hit          10   350        35     86.444 
    Bump         10   380        38    122.222 
    Collide      10   410        41     41.556 
    Smash        10   460        46     33.333 

    O'BRIEN TEST FOR HOMOGENEITY OF VARIANCE
    Source of Variation       SS       df      MS         F     P-value   eta^2   Obs. power 
    ========================================================================================
    Treatments             68081.975    4   17020.494   1.859     0.134   0.142        0.498 
    Error                 412050.224   45    9156.672                                        
    ========================================================================================
    Total                 480132.199   49                                                    

    ANOVA
    Source of Variation    SS    df   MS      F     P-value   eta^2   Obs. power 
    ============================================================================
    Treatments            1460    4   365   4.562     0.004   0.289        0.837 
    Error                 3600   45    80                                        
    ============================================================================
    Total                 5060   49                                              

    POSTHOC MULTIPLE COMPARISONS

    Tukey HSD: Table of q-statistics
              Bump   Collide    Contact      Hit       Smash   
    ==========================================================
    Bump      0      1.061 ns   2.828 ns   1.061 ns   2.828 ns 
    Collide          0          3.889 +    2.121 ns   1.768 ns 
    Contact                     0          1.768 ns   5.657 ** 
    Hit                                    0          3.889 +  
    Smash                                             0        
    ==========================================================
      + p < .10 (q-critical[5, 45] = 3.59038343675)
      * p < .05 (q-critical[5, 45] = 4.01861178004)
     ** p < .01 (q-critical[5, 45] = 4.89280842987)


Using the Newman-Keuls Test
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. sourcecode:: python

    from pyvttbl import Anova1way
    d = [[21.0, 20.0, 26.0, 46.0, 35.0, 13.0, 41.0, 30.0, 42.0, 26.0],
         [23.0, 30.0, 34.0, 51.0, 20.0, 38.0, 34.0, 44.0, 41.0, 35.0],
         [35.0, 35.0, 52.0, 29.0, 54.0, 32.0, 30.0, 42.0, 50.0, 21.0],
         [44.0, 40.0, 33.0, 45.0, 45.0, 30.0, 46.0, 34.0, 49.0, 44.0],
         [39.0, 44.0, 51.0, 47.0, 50.0, 45.0, 39.0, 51.0, 39.0, 55.0]]
    conditions_list = 'Contact Hit Bump Collide Smash'.split()
    D=Anova1way()
    D.run(d, conditions_list=conditions_list, posthoc='SNK')
    print(D)

::

    Anova: Single Factor on Measure

    SUMMARY
    Groups    Count   Sum   Average   Variance 
    ==========================================
    Contact      10   300        30    116.444 
    Hit          10   350        35     86.444 
    Bump         10   380        38    122.222 
    Collide      10   410        41     41.556 
    Smash        10   460        46     33.333 

    O'BRIEN TEST FOR HOMOGENEITY OF VARIANCE
    Source of Variation       SS       df      MS         F     P-value   eta^2   Obs. power 
    ========================================================================================
    Treatments             68081.975    4   17020.494   1.859     0.134   0.142        0.498 
    Error                 412050.224   45    9156.672                                        
    ========================================================================================
    Total                 480132.199   49                                                    

    ANOVA
    Source of Variation    SS    df   MS      F     P-value   eta^2   Obs. power 
    ============================================================================
    Treatments            1460    4   365   4.562     0.004   0.289        0.837 
    Error                 3600   45    80                                        
    ============================================================================
    Total                 5060   49                                              

    POSTHOC MULTIPLE COMPARISONS

    SNK: Step-down table of q-statistics
           Pair           i    |diff|     q     range   df     p     Sig. 
    =====================================================================
    Contact vs. Smash      1   16.000   5.657       5   45   0.002   **   
    Collide vs. Contact    2   11.000   3.889       4   45   0.041   *    
    Hit vs. Smash          3   11.000   3.889       4   45   0.041   *    
    Bump vs. Smash         4    8.000   2.828       3   45   0.124   ns   
    Bump vs. Contact       5    8.000   2.828       3   45   0.124   ns   
    Collide vs. Hit        6    6.000   2.121       2   45   0.141   ns   
    Collide vs. Smash      7    5.000       -       -    -       -   ns   
    Contact vs. Hit        8    5.000       -       -    -       -   ns   
    Bump vs. Collide       9    3.000       -       -    -       -   ns   
    Bump vs. Hit          10    3.000       -       -    -       -   ns   
      + p < .10,   * p < .05,   ** p < .01,   *** p < .001

Running Single Factor ANOVA with :class:`DataFrame`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The examples above pass a list of lists to :class:`Anova1Way`. The :class:`DataFrame` object 
also has a wrapper method for running a single factor ANOVA. It assumes data is in the 
stacked format with one observation per row.

Let's begin by making up some data. 

    >>> from pyvttbl import DataFrame
    >>> from random import random
    >>> sample = lambda mult, N : [random()*mult for i in xrange(N)]
    >>> df = DataFrame(zip(['IV','DV'], [['A']*10, sample(1, 10)]))
    >>> df.attach(DataFrame(zip(['IV','DV'], [['B']*10, sample(2, 10)])))
    >>> df.attach(DataFrame(zip(['IV','DV'], [['C']*10, sample(3, 10)])))
    >>> print(df)
    IV    DV   
    ==========
    A    0.779 
    A    0.706 
    A    0.418 
    A    0.388 
    A    0.542 
    A    0.014 
    A    0.941 
    A    0.058 
    A    0.830 
    A    0.110 
    B    1.263 
    B    1.559 
    B    1.069 
    B    1.524 
    B    1.700 
    B    1.187 
    B    1.980 
    B    1.657 
    B    1.145 
    B    0.103 
    C    2.264 
    C    1.863 
    C    2.374 
    C    0.972 
    C    2.257 
    C    0.467 
    C    1.077 
    C    1.001 
    C    2.984 
    C    2.422 
    

Now we can run the analysis
    
    >>> aov = df.anova1way('DV', 'IV')
    >>> print(aov)

::

    Anova: Single Factor on DV

    SUMMARY
    Groups   Count    Sum     Average   Variance 
    ============================================
    A           10    4.785     0.478      0.114 
    B           10   13.185     1.319      0.265 
    C           10   17.681     1.768      0.685 

    O'BRIEN TEST FOR HOMOGENEITY OF VARIANCE
    Source of Variation    SS     df    MS       F     P-value   eta^2   Obs. power 
    ===============================================================================
    Treatments            1.749    2   0.875   3.697     0.038   0.215        0.566 
    Error                 6.388   27   0.237                                        
    ===============================================================================
    Total                 8.137   29                                                

    ANOVA
    Source of Variation     SS     df    MS       F       P-value    eta^2   Obs. power 
    ===================================================================================
    Treatments             8.569    2   4.285   12.083   1.787e-04   0.472        0.900 
    Error                  9.574   27   0.355                                           
    ===================================================================================
    Total                 18.143   29                                                   

    POSTHOC MULTIPLE COMPARISONS

    Tukey HSD: Table of q-statistics
        A      B          C     
    ===========================
    A   0   2.443 ns   3.751 *  
    B       0          1.308 ns 
    C                  0        
    ===========================
      + p < .10 (q-critical[3, 27] = 3.0301664694)
      * p < .05 (q-critical[3, 27] = 3.50576984879)
     ** p < .01 (q-critical[3, 27] = 4.49413305084)
