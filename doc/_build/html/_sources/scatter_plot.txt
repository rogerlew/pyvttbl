scatter_plot
============

Produces a scatter_plot with optional trend fitting

Example
--------------------------------

.. sourcecode:: python

    >>> df=DataFrame()
    >>> df.read_tbl('data/iqbrainsize.txt', delimiter='\t')
    >>> df.scatter_plot('TOTVOL', 'FIQ')

produces 'scatter(TOTVOL_X_FIQ).png'

.. image:: _static/scatter(TOTVOL_X_FIQ).png 
    :width: 400px
    :align: center
    :height: 400px
    :alt: scatter(TOTVOL_X_FIQ).png

Example with power trend fit
--------------------------------

.. sourcecode:: python

    >>> df.scatter_plot('TOTVOL', 'FIQ', trend='power')

produces 'scatter(TOTVOL_X_FIQ,trend=power).png'

.. image:: _static/scatter(TOTVOL_X_FIQ,trend=power).png 
    :width: 400px
    :align: center
    :height: 400px
    :alt: scatter(TOTVOL_X_FIQ,trend=power).png