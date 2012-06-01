.. pyvttbl documentation master file, created by
   sphinx-quickstart on Thu May 31 00:22:55 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pyvttbl's documentation!
===================================

Pivot tables (also called contingency tables and cross tabulation tables) 
are a powerful means of data visualization and data summarization. When 
dealing with large data sets with multiple variables, or multiple 
datasets manually manipulating the pivot tables in WYSIWYG (what you see 
is what you get) spreadsheets can quickly become troublesome and error 
prone. In these instances it becomes preferred or even necessary to use 
a YAFIYGI (you ask for it you got it) model to automate all or part of 
the data summarization process.

There are already existing Python pivot table modules available. The ones 
I have found don't support multidimensional data, require Windows and 
Excel, or are incomplete and abandoned. They also are usually tailored 
towards an information technology audience as opposed to a scientific/
research audience. On the other extreme are projects like PyTables. 
PyTables is an impressive undertaking but many datasets just aren't 
complex enough to justify the effort required to get data into PyTables. 
The :mod:`pyvttbl` module presented here offers a solution for datasets of 
"Goldilocks" complexity; too much for spreadsheets, but too little for 
coding custom solutions or configuring PyTables.

Behind the scenes :mod:`pyvttbl` uses sqlite3 to handle much of the data 
manipulation. sqlite3 is fast and part of the Python standard library.

The project described was supported by NIH Grant Number P20 RR016454 from 
the INBRE Program of the National Center for Research Resources.

.. note::

    Version 0.5.0.0 introduced changes that are not backwards compatible with
    previous versions. 
    
    :class:`DataFrame` items are now numpy.arrays or numpy.ma.masked_arrays.
    :class:`PyvtTbl` objects are now subclasses of numpy.ma.masked_arrays. These changes make
    handling missing data easier and better incorporate the power and succinctness of
    NumPy. 
    
    :class:`DataFrame` indexing (__getitem__) no longer accepts "where" queries. This allows for 
    any hashable object to be used as a :class:`DataFrame` key (string, tuple, etc.).  keys can 
    have spaces and special characters or just be distinguished by capitalization. 
    Sqlite3 is keeped happy by hashing all the keys. 

Contents:
==========

.. toctree::
   :maxdepth: 2
   :numbered:
   
   install.rst
   quick-start.rst
   DataFrame.rst
   PyvtTbl.rst
   plotting.rst
   stats.rst
   
Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

