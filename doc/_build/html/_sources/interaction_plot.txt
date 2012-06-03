interaction_plot
================

Produces interaction plots from the specified parameters

2 way interaction plot
--------------------------------

Two argumennts are required. The first specifies the dependent variable
and the second specifies the variable to use on the x-axis.

This example also specifies that the 'CONDITION' factor should be 
seperated.


Example with a single factor
--------------------------------

.. sourcecode:: python

    >>> df=DataFrame()
    >>> df.read_tbl('data/words~ageXcondition.csv')
    >>> df.interaction_plot('WORDS','AGE',
                            seplines='CONDITION')

produces 'interaction_plot(WORDS~AGE_X_CONDITION).png'

.. image:: _static/interaction_plot(WORDS~AGE_X_CONDITION).png 
    :width: 600px
    :align: center
    :height: 500px
    :alt: interaction_plot(WORDS~AGE_X_CONDITION).png

Example with error bars
--------------------------------

The `yerr` keyword controls the errorbars that are placed on 
the plot. It can be None, a float, 'ci', 'stdev', or 'sem'.

'ci' => 95% confidence intervals

.. sourcecode:: python

    >>> df=DataFrame()
    >>> df.read_tbl('data/words~ageXcondition.csv')
    >>> df.interaction_plot('WORDS','AGE',
                            seplines='CONDITION',
                            yerr='ci')

produces 'interaction_plot(WORDS~AGE_X_CONDITION,yerr=ci).png'

.. image:: _static/interaction_plot(WORDS~AGE_X_CONDITION,yerr=ci).png 
    :width: 600px
    :align: center
    :height: 500px
    :alt: interaction_plot(WORDS~AGE_X_CONDITION,yerr=ci).png
    
Error bars for repeated-measures experiments
--------------------------------------------

If the data reflect a repeated measures design the error bars found by
:meth:`interaction_plot` will actually be conservative due to the fact
they do not take into account within-subject variability. [1]_, [2]_ .

In such circumstances the `recommended` method for constructing 
interaction plots is to run an analysis of variance using :class:`Anova`
and use :class:`Anova`. :meth:`plot`. The :class:`Anova` class will calculate
the appropriate error bars based on the specified main effect or interaction. 
By default it uses the highest order main-effect/interaction specified by the 
factors of xaxis, seplines, sepxplots, and sepyplots.

Here is an example of how you would go about doing this.

    >>> df=DataFrame()
    >>> df.read_tbl('data/words~ageXcondition.csv')
    >>> aov = df.anova('WORDS', wfactors=['AGE','CONDITION'])
    >>> aov.plot('WORDS','AGE', seplines='CONDITION',
                 errorbars='ci', output_dir='output')

produces 'interaction_plot(WORDS~AGE_X_CONDITION,yerr=0.319836724826).png'

.. image:: _static/interaction_plot(WORDS~AGE_X_CONDITION,yerr=0.319836724826).png 
    :width: 600px
    :align: center
    :height: 500px
    :alt: interaction_plot(WORDS~AGE_X_CONDITION,yerr=0.319836724826).png

Example with separate horizontal subplots
--------------------------------------------

.. sourcecode:: python

    >>> df=DataFrame()
    >>> df.read_tbl('data\suppression~subjectXgroupXageXcycleXphase.csv')
    >>> df.interaction_plot('SUPPRESSION','CYCLE',
                            seplines='AGE',
                            sepxplots='PHASE',
                            yerr='ci')
    
produces 'interaction_plot(SUPPRESSION~CYCLE_X_AGE_X_PHASE,yerr=ci).png'

.. image:: _static/interaction_plot(SUPPRESSION~CYCLE_X_AGE_X_PHASE,yerr=ci).png 
    :width: 600px
    :align: center
    :height: 250px
    :alt: interaction_plot(SUPPRESSION~CYCLE_X_AGE_X_PHASE,yerr=ci).png
    
    
Example with separate horizontal and vertical subplots
------------------------------------------------------

.. sourcecode:: python

    >>> df=DataFrame()
    >>> df.read_tbl('data\suppression~subjectXgroupXageXcycleXphase.csv')
    >>> df.interaction_plot('SUPPRESSION','CYCLE',
                            seplines='AGE',
                            sepxplots='GROUP',
                            sepyplots='PHASE',
                            yerr='sem')
    
produces 'interaction_plot(SUPPRESSION~CYCLE_X_AGE_X_GROUP_X_PHASE,yerr=sem).png'

.. image:: _static/interaction_plot(SUPPRESSION~CYCLE_X_AGE_X_GROUP_X_PHASE,yerr=sem).png 
    :width: 800px
    :align: center
    :height: 400px
    :alt: interaction_plot(SUPPRESSION~CYCLE_X_AGE_X_GROUP_X_PHASE,yerr=sem).png

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
.. [1] Loftus, G. R., & Masson, M. E.  (1994).  
       Using confidence intervals in within-subject designs.  
       Psychonomic Bulletin & Review, 1(4), 476-490.

.. [2] Masson, M. E. J., & Loftus, G. R.  (2003).  
       Using confidence intervals for graphically based data interpretation.  
       Canadian Journal of Experimental Psychology, 57(3), 203-220.
