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

# std lib
import math
from collections import Counter,OrderedDict
from copy import copy

from pyvttbl.misc.texttable import Texttable as TextTable
from pyvttbl.misc.support import *

class Descriptives(OrderedDict):
    def __init__(self, *args, **kwds):
        if len(args) > 1:
            raise Exception('expecting only 1 argument')

        if kwds.has_key('cname'):
            self.cname = kwds['cname']
        else:
            self.cname = None
            
        if len(args) == 1:
            super(Descriptives, self).__init__(args[0])
        else:
            super(Descriptives, self).__init__()
            
    def run(self, V, cname=None):
        """
        generates and stores descriptive statistics for the
        numerical data in V
        """        
        try:
            V = sorted(_flatten(list(copy(V))))
        except:
            raise TypeError('V must be a list-like object')
            
        if cname == None:
            self.cname = ''
        else:
            self.cname = cname
            
        N = float(len(V))

        self['count'] = N
        self['mean'] = sum(V) / N
        self['mode'] = Counter(V).most_common()[0][0]
        self['var'] = sum([(self['mean']-v)**2 for v in V]) / (N - 1)
        self['stdev']= math.sqrt(self['var'])
        self['sem'] = self['stdev'] / math.sqrt(N)
        self['rms'] = math.sqrt(sum([v**2 for v in V]) / N)
        self['min'] = min(V)
        self['Q1'] = V[int(N/4.)]
        if int(N) % 2 == 0:
            self['Q1'] += V[int(N/4.)-1]
            self['Q1'] /= 2
        self['median'] = V[int(N/2.)]
        if int(N/2.) % 2 == 0:
            self['median'] += V[int(N/2.)-1]
            self['median'] /= 2.
        self['Q3'] = V[int(3*N/4.)]
        if int(N/2.) % 2 == 0:
            self['Q3'] += V[int(N/4.)*3-1]
            self['Q3'] /= 2
        self['max'] = max(V)
        self['range'] = self['max'] - self['min']
        self['95ci_lower'] = self['mean'] - 1.96*self['sem']
        self['95ci_upper'] = self['mean'] + 1.96*self['sem']
    
    def __str__(self):

        if self == {}:
            return '(no data in object)'

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
        if self == {}:
            return 'Descriptives()'
        
        s = []
        for k, v in self.items():
            s.append("('%s', %s)"%(k, repr(v)))
        args = '[' + ', '.join(s) + ']'
        
        kwds = ''     
        if self.cname != None:
            kwds = ", cname='%s'"%self.cname


        return 'Descriptives(%s%s)'%(args, kwds)
        
