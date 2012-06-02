:class:`pyvttbl.stats.Ttest` Overview
==============================================
This class is capable of performing 1 sample, paired 
2 sample, and equal and unequal independent sample t-tests.

The observed power estimates have been validated against G*Power.

Example 1 sample t-test
-----------------------------

The `pop_mean` keyword specifies the population mean against which the data is tested.

::

    >>> df = DataFrame()
    >>> df.read_tbl('data/suppression~subjectXgroupXageXcycleXphase.csv')
    >>> D=df.ttest('SUPPRESSION', pop_mean=17.)
    >>> print(D)
    t-Test: One Sample for means
     
                              SUPPRESSION 
    =====================================
    Sample Mean                    19.541 
    Hypothesized Pop. Mean             17 
    Variance                      228.326 
    Observations                      384 
    df                                383 
    t Stat                          3.295 
    alpha                           0.050 
    P(T<=t) one-tail            5.384e-04 
    t Critical one-tail             1.966 
    P(T<=t) two-tail                0.001 
    t Critical two-tail             1.649 
    P(T<=t) two-tail                0.001 
    Effect size d                   0.168 
    delta                           3.295 
    Observed power one-tail         0.950 
    Observed power two-tail         0.908 
            

Example paired t-test
-----------------------------

Here the :class:`Ttest` object is passed lists of data.

::

    >>> from pyvttbl.stats import Ttest
    >>> A = [3,4, 5,8,9, 1,2,4, 5]
    >>> B = [6,19,3,2,14,4,5,17,1]
    >>> D=Ttest()
    >>> D.run(A, B, paired=True)
    >>> print(D)
    t-Test: Paired Two Sample for means
                        A        B    
    =========================================
    Mean                       4.556    7.889 
    Variance                   6.778   47.111 
    Observations                   9        9 
    Pearson Correlation        0.102          
    df                             8          
    t Stat                    -1.411          
    alpha                      0.050          
    P(T<=t) one-tail           0.098          
    t Critical one-tail        2.306          
    P(T<=t) two-tail           0.196          
    t Critical two-tail        1.860          
    P(T<=t) two-tail           0.196          
    Effect size dz             0.470          
    delta                      1.411          
    Observed power one-tail    0.362          
    Observed power two-tail    0.237          
    >>>
    
Example Independent sample t-test assuming unequal variances
-------------------------------------------------------------

Can handle non-equivalent sample sizes.


Example data from http://alamos.math.arizona.edu/~rychlik/math263/class_notes/Chapter7/R/

::

    >>> from pyvttbl.stats import Ttest
    >>> A = [24,61,59,46,43,44,52,43,58,67,62,57,71,49,54,43,53,57,49,56,33]
    >>> B = [42,33,46,37,43,41,10,42,55,19,17,55,26,54,60,28,62,20,53,48,37,85,42]
    >>> D=Ttest()
    >>> D.run(A, B, paired=True)
    >>> print(D)
    t-Test: Two-Sample Assuming Unequal Variances
                             A         B    
    ===========================================
    Mean                       51.476    41.522 
    Variance                  121.162   294.079 
    Observations                   21        23 
    df                         37.855           
    t Stat                      2.311           
    alpha                       0.050           
    P(T<=t) one-tail            0.013           
    t Critical one-tail         2.025           
    P(T<=t) two-tail            0.026           
    t Critical two-tail         1.686           
    P(T<=t) two-tail            0.026           
    Effect size d               0.691           
    delta                       2.185           
    Observed power one-tail     0.692           
    Observed power two-tail     0.567           
    
    
Example Independent sample t-test assuming equal variances
-------------------------------------------------------------

And last but not least...

::

    >>> from pyvttbl.stats import Ttest
    >>> A = [3,4, 5,8,9, 1,2,4, 5]
    >>> B = [6,19,3,2,14,4,5,17,1]
    >>> D=Ttest()
    >>> D.run(A, B, equal_variance=True)
    >>> print(D)
    t-Test: Two-Sample Assuming Equal Variances
                                A        B    
    =========================================
    Mean                       4.556        9 
    Variance                   6.778   54.222 
    Observations                   9       10 
    Pooled Variance           31.895          
    df                            17          
    t Stat                    -1.713          
    alpha                      0.050          
    P(T<=t) one-tail           0.052          
    t Critical one-tail        2.110          
    P(T<=t) two-tail           0.105          
    t Critical two-tail        1.740          
    P(T<=t) two-tail           0.105          
    Effect size d              0.805          
    delta                      1.610          
    Observed power one-tail    0.460          
    Observed power two-tail    0.330          

