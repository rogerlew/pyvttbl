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

class Descriptives(OrderedDict):
    def __init__(self, V, cname=None):
        V = _flatten(list(V))

##        try:
##            V = _flatten(list(V))
##        except:
##            raise TypeError('V must be a list-like object')
            
        super(Descriptives, self).__init__()

        if cname == None:
            self.cname = ''
        else:
            self.cname = cname
            
        self.V = V
        N = len(V)

        self['count'] = N
        self['mean'] = sum(V) / N
        self['var'] = sum([(self['mean']-v)**2 for v in V]) / (N - 1)
        self['stdev']= math.sqrt(self['var'])
        self['sem'] = self['stdev'] / math.sqrt(N)
        self['rms'] = math.sqrt(sum([v**2 for v in V]) / N)
        self['min'] = min(V)
        self['max'] = max(V)
        self['range'] = self['max'] - self['min']
        self['median'] = V[int(N/2)]
        if self['count'] % 2 == 0:
            self['median'] += V[int(N/2)-1]
            self['median'] /= 2.
        self['95ci_lower'] = self['mean'] - 1.96*self['sem']
        self['95ci_upper'] = self['mean'] + 1.96*self['sem']
    
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
        if self.cname == '':
            return 'Descriptives(%s)'%repr(self.V)
        else:
            return 'Descriptives(%s, %s)'%(repr(self.V),self.cname)
