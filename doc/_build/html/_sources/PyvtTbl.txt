:class:`pyvttbl.PyvtTbl`
=====================================

Description
-----------
:class:`PyvtTbl` objects are containers for holding pivoted data. 
They are instantiated through DataFrame.pivot. 


Public Methods
--------------

Additional methods inherented from np.ma.MaskedArray that are not 
explicitely listed here may also be available. Keep in mind methods not
listed here may not been have extensively tested. 

.. seealso:: `numpy.ma.MaskedArray <http://docs.scipy.org/doc/numpy/reference/maskedarray.baseclass.html>`_

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.PyvtTbl.__new__

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.PyvtTbl.transpose

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.PyvtTbl.__getitem__

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.PyvtTbl.astype

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.PyvtTbl.flatten

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.PyvtTbl.__iter__

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.PyvtTbl.ndenumerate

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attribute:: pyvttbl.PyvtTbl.flat

    Flat iterator object to iterate over PyvtTbl.
    
|        A `MaskedIterator` iterator is returned by ``x.flat`` for any PyvtTbl
|        `x`. It allows iterating over the array as if it were a 1-D array,
|        either in a for-loop or by calling its `next` method.
|    
|        Iteration is done in C-contiguous style, with the last index varying the
|        fastest. The iterator can also be indexed using basic slicing or
|        advanced indexing.
        
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.PyvtTbl.__repr__

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.PyvtTbl.__str__

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.PyvtTbl.to_dataframe

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.PyvtTbl.__add__

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.PyvtTbl.__radd__

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
             
.. automethod:: pyvttbl.PyvtTbl.__sub__

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.PyvtTbl.__rsub__

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.PyvtTbl.__pow__

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.PyvtTbl.__mul__

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.PyvtTbl.__rmul__

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.PyvtTbl.__div__

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.PyvtTbl.__rdiv__

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.PyvtTbl.__truediv__

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.PyvtTbl.__rtruediv__

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.PyvtTbl.__floordiv__

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.PyvtTbl.__rfloordiv__

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Private Methods
---------------

helper methods for PyvtTbl

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.PyvtTbl._get_rows

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: pyvttbl.PyvtTbl._get_cols

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
