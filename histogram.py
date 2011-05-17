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

import csv
import math

from copy import copy
from collections import OrderedDict

from rl_lib import _isfloat
from rl_lib import _isint
from rl_lib import _flatten
from rl_lib import _ifelse
from rl_lib import _xunique_combinations

from texttable import Texttable as TextTable
import pystaggrelite3

class Histogram(OrderedDict):
    def __init__(self, V, cname=None, bins=10,
                 range=None, density=False, cumulative=False):
        V = _flatten(list(V))

        try:
            V = _flatten(list(V))
        except:
            raise TypeError('V must be a list-like object')
            
        super(Histogram, self).__init__()


        if cname == None:
            self.cname = ''
        else:
            self.cname = cname
            
        values, bin_edges = pystaggrelite3.hist(V, bins=bins,
                   range=range, density=density, cumulative=cumulative)

        self['values'] = values
        self['bin_edges'] = bin_edges

        self.V = V
        self.bins = bins
        self.range = range
        self.density = density
        self.cumulative = cumulative
        
    def __str__(self):

        tt = TextTable(48)
        tt.set_cols_dtype(['t', 'f'])
        tt.set_cols_align(['l', 'r'])
        for (k, v) in self.items():
            tt.add_row([' %s'%k, v])
        tt.set_deco(TextTable.HEADER)

        return ''.join(['Descriptive Statistics\n  ',
                         self.cname,
                         '\n==========================\n',
                         tt.draw()])

    def __repr__(self):
        s = 'Histogram(%s'%repr(self.V)

        if self.cname != '':
            s += ', cname=%s'%repr(self.cname)

        if self.bins != 10:
            s += ', bins=%i'%self.bins

        if self.range != None:
            s += ', range=%s'%repr(self.range)

        if density != False:
            s += ', density=True'
            
        if cumulative != False:
            s += ', cumulative=True'

        s+= ')'

        return s
