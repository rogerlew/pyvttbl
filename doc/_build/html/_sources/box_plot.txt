:meth:`pyvttbl.plotting.box_plot` Overview
=================================================

Produces a box plot over a factor or factors

Example
--------------------------------

.. sourcecode:: python

    >>> df=DataFrame()
    >>> df.read_tbl('data/words~ageXcondition.csv')
    >>> df.box_plot('WORDS')

produces 'box(words).png'

.. image:: _static/box(words).png 
    :width: 400px
    :align: center
    :height: 300px
    :alt: box(words).png

Example with a single factor
--------------------------------

.. sourcecode:: python

    >>> df.box_plot('WORDS', ['AGE'])

produces 'box(WORDS~AGE).png'

.. image:: _static/box(WORDS~AGE).png 
    :width: 400px
    :align: center
    :height: 400px
    :alt: box(WORDS~AGE).png

Example with two factors
--------------------------------

.. sourcecode:: python

    >>> df.box_plot('WORDS', ['AGE','CONDITIONS'])
             
produces 'box(WORDS~AGE_X_CONDITION).png'

.. image:: _static/box(WORDS~AGE_X_CONDITION).png
    :width: 600px
    :align: center
    :height: 300px
    :alt: box(WORDS~AGE_X_CONDITION).png