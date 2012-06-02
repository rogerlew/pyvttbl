Installing pyvttbl
================

The requirements for using pyvttbl are:

1.  **Python 2.7.x** (This package uses the *OrderedDict* and *Counter* objects 
    introduced in the collections module of 2.7. )
2.  **SciPy** : (tested with 0.9.0)
3.  **NumPy** : (tested with 1.5.1)
4.  **Matplotlib** : (tested with 1.0.1)

Options to install pyvttbl

1.  Acquire pyvttbl from PyPi

    1. get `setuptools <http://pypi.python.org/pypi/setuptools/>`_
    2. run easy_install pyvttbl
	
    .. note::
        the module should install un-zipped
		
2.  Install from source

    1. You will also need to acquire `dictset 
       <http://code.google.com/p/dictset/>`_ and `pystaggrelite3 
       <http://code.google.com/p/py-st-a-ggre-lite3/>`_
	   
    .. note::
	
        If you use easy_install it should automatically acquire dictset 
        and pystaggrelite3.
		
    2. `Obtain source from PyPi <http://pypi.python.org/pypi/pyvttbl/>`_
	3. Unzip
	4. Run "setup.py install" 
	
To develop pyvttbl you should also have:

1.  **nose** (using 0.11.3)
2.  **Sphinx** : (tested with 1.1.3)

