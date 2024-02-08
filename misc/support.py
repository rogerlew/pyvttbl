# Copyright (c) 2011-2024, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.

import math
import hashlib


def _sha1(item):
    # Encode the string representation of 'item' to bytes before hashing
    # Default encoding is utf-8, but you can specify another encoding if necessary
    return '_%s' % hashlib.sha1(str(item).encode('utf-8')).hexdigest()


def _isfloat(string):
    """
    returns true if string can be cast as a float,
    returns zero otherwise
    """
    try:
        float(string)
    except:
        return False
    return True

def _isint(string):
    """
    returns true if string can be cast as an int,
    returns zero otherwise
    """
    try:
        f = float(string)
    except:
        return False
    if round(f) - f == 0:
        return True
    return False

def _flatten(x):
    """_flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).

    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> _flatten([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]"""
    if hasattr(x, 'flatten'):
        return x.flatten()

    result = []
    for el in x:
        #if isinstance(el, (list, tuple)):
        if hasattr(el, "__iter__") and not isinstance(el, str):
            result.extend(_flatten(el))
        else:
            result.append(el)
    return result

def _xunique_combinations(items, n):
    """
    returns the unique combinations of items. the n parameter controls
    the number of elements in items to combine in each combination
    """
    if n == 0:
        yield []
    else:
        for i in range(len(items)):
            for cc in _xunique_combinations(items[i+1:], n-1):
                yield [items[i]]+cc


def _str(x, dtype='a', n=3):
    """Handles string formatting of cell data

        x- is the item being added
        dtype- is so we can index self._dtype 
    """
    
    if x == None : return '--'
    
    try    : f=float(x)
    except : return str(x)

    if   math.isnan(f) : return '--'
    elif math.isinf(f) : return 'inf'
    elif dtype == 'i'  : return str(int(round(f)))
    elif dtype == 'f'  : return '%.*f'%(n, f)
    elif dtype == 'e'  : return '%.*e'%(n, f)
    elif dtype == 't'  : return str(x)
    else:
        if f-round(f) == 0:
            if abs(f) > 1e8:
                return '%.*e'%(n, f)
            else:
                return str(int(round(f)))
        else:
            if abs(f) > 1e8 or abs(f) <= float('1e-%i'%n):
                return '%.*e'%(n, f)
            else:
                return '%.*f'%(n, f)

__all__ = ['_sha1','_isfloat','_isint','_flatten','_xunique_combinations','_str']
