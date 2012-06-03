DataFrame Overview
==================

Description
-----------
:class:`DataFrame` objects are containers for holding tabulated data. They 
inherent :class:`collections.OrderedDict` and hold data in 
:class:`numpy.array` objects. 

Public Methods
--------------
Methods to get data into a :class:`DataFrame`, manipulate and manage data,
and write data. For the most part these remove the user from the fact they 
are using sqlite3 to manipulate data. 

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.__init__

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.__setitem__

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.__delitem__

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.__str__

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.read_tbl  

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.attach

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.insert

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.sort

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.select_col

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.row_iter

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.pivot

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.where

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.where_update

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.summary

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.validate

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.types

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.shape

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.bind_aggregate

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:mod:`pyvttbl.plotting` Wrappers
--------------------------------
Methods to visualize data.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.histogram_plot

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.scatter_plot

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.box_plot

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.interaction_plot

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.scatter_matrix

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:mod:`pyvttbl.stats` Wrappers
-----------------------------
Methods to conduct descriptive and inferential statistical analyses.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.descriptives

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.histogram

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.marginals

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.anova1way

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.anova

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.chisquare1way

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.chisquare2way

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.correlation

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame.ttest

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
             
             
Private Methods
---------------
These methods are for working interfacing :class:`DataFrame`
with sqlite3.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame._get_sqltype

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame._get_nptype

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame._get_mafillvalue

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame._are_col_lengths_equal

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame._determine_sqlite3_type

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame._execute

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame._executemany

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame._get_indices_where

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.DataFrame._build_sqlite3_tbl

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
