# Copyright (c) 2011-2024, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.

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

    
