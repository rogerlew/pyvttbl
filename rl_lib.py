from __future__ import print_function

# Copyright (c) 2011, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.

# Python 2 to 3 workarounds
import sys
if sys.version_info[0] == 2:
    _strobj = basestring
    _xrange = xrange
elif sys.version_info[0] == 3:
    _strobj = str
    _xrange = range

def _isfloat(string):
    try:
        float(string)
    except:
        return False
    return True

def _isint(string):
    try:
        f = float(string)
    except:
        return False
    if round(f) - f == 0:
        return True
    return False

def _ifelse(condition, ifTrue, ifFalse):
    if condition:
        return ifTrue
    return ifFalse

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

    result = []
    for el in x:
        #if isinstance(el, (list, tuple)):
        if hasattr(el, "__iter__") and not isinstance(el, _strobj):
            result.extend(_flatten(el))
        else:
            result.append(el)
    return result

def _xunique_combinations(items, n):
    if n == 0:
        yield []
    else:
        for i in _xrange(len(items)):
            for cc in _xunique_combinations(items[i+1:], n-1):
                yield [items[i]]+cc
