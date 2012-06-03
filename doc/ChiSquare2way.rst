ChiSquare2way
==============================================

:class:`ChiSquare2way` conducts a two-sample chi-squared test on a list of frequencies.

A 2 x 2 example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:class:`ChiSquare2way` needs the data in a :class:`DataFrame` with one 
observation per row. Once it is in a :class:`DataFrame` the user just has to 
specify the row factor and the column factor. 

In this example we use a  :mod:`collections`. :class:`Counter` object
to build the DataFrame from frequency counts.

::

    >>> from pyvttbl import DataFrame
    >>> from collection import Counter
    >>> df=DataFrame()
    >>> df['FAULTS'] = list(Counter(Low=177,High=181).elements())
    >>> df['FAULTS'] = df['FAULTS'][::-1] # reverse 'FAULT' data
    >>> df['VERDICT'] = list(Counter(Guilty=153, NotGuilty=24).elements()) + \
                        list(Counter(Guilty=105, NotGuilty=76).elements())

    >>> x2= df.chisquare2way('FAULTS','VERDICT')
    >>> print(x2)
    Chi-Square: two Factor

    SUMMARY
             Guilty     NotGuilty   Total 
    =====================================
    High          105          76     181 
            (130.441)    (50.559)         
    Low           153          24     177 
            (127.559)    (49.441)         
    =====================================
    Total         258         100     358 

    SYMMETRIC MEASURES
                              Value    Approx.  
                                        Sig.    
    ===========================================
    Cramer's V                0.317   8.686e-10 
    Contingency Coefficient   0.302   5.510e-09 
    N of Valid Cases            358             

    CHI-SQUARE TESTS
                            Value    df       P     
    ===============================================
    Pearson Chi-Square      35.930    1   2.053e-09 
    Continuity Correction   34.532    1   4.201e-09 
    Likelihood Ratio        37.351    1           0 
    N of Valid Cases           358                  

    CHI-SQUARE POST-HOC POWER
           Measure                 
    ==============================
    Effect size w            0.317 
    Non-centrality lambda   35.930 
    Critical Chi-Square      3.841 
    Power                    1.000 
    

A 2 x 3 example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Here a different approach is taken to get the data into the :class:`DataFrame`

::

    >>> df=DataFrame()
    >>> rfactors= ['Countrol']*903 + ['Message']*869
    >>> cfactors= ['Trash Can']*41 + ['Litter']*385 + ['Removed']*477
    >>> cfactors+=['Trash Can']*80 + ['Litter']*290 + ['Removed']*499
    >>> x2= ChiSquare2way()
    >>> x2.run(rfactors, cfactors)
    >>> print(x2)
    
    Chi-Square: two Factor

    SUMMARY
                Litter      Removed    Trash Can   Total 
    ====================================================
    Countrol         385         477          41     903 
               (343.976)   (497.363)    (61.661)         
    Message          290         499          80     869 
               (331.024)   (478.637)    (59.339)         
    ====================================================
    Total            675         976         121    1772 

    SYMMETRIC MEASURES
                              Value    Approx.  
                                        Sig.    
    ===========================================
    Cramer's V                0.121   3.510e-07 
    Contingency Coefficient   0.120   4.263e-07 
    N of Valid Cases           1772             

    CHI-SQUARE TESTS
                         Value    df       P     
    ============================================
    Pearson Chi-Square   25.794    2   2.506e-06 
    Likelihood Ratio     26.056    2   2.198e-06 
    N of Valid Cases       1772                  

    CHI-SQUARE POST-HOC POWER
           Measure                 
    ==============================
    Effect size w            0.121 
    Non-centrality lambda   25.794 
    Critical Chi-Square      5.991 
    Power                    0.997 