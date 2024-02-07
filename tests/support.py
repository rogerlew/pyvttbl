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

from collections import Counter
from pyvttbl.misc.support import *

import difflib

def fcmp(d,r):
    """
    Compares two files, d and r, cell by cell. Float comparisons 
    are made to 4 decimal places. Extending this function could
    be a project in and of itself.
    """
    # we need to compare the files
    dh=open(d,'r')
    rh=open(r,'r')

    

    diff = difflib.ndiff(dh.read().splitlines(keepends=True),
                         rh.read().splitlines(keepends=True))
    print(''.join(diff))

    
