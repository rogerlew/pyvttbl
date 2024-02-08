# Copyright (c) 2011-2024, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.

# std lib
from collections import Counter,OrderedDict
from copy import copy

# third party modules
from pyvttbl.misc import pystaggrelite3

# included modules
from pyvttbl.misc.texttable import Texttable as TextTable
from pyvttbl.misc.support import *


class Histogram(OrderedDict):
    def __init__(self, *args, **kwds):
        if len(args) > 1:
            raise Exception('expecting only 1 argument')

        self.cname = kwds.get('cname', None)
        self.bins = kwds.get('bins', 10)
        self.range = kwds.get('range', None)
        self.density = kwds.get('density', False)
        self.cumulative = kwds.get('cumulative', False)

        if len(args) == 1:
            super(Histogram, self).__init__(args[0])
        else:
            super(Histogram, self).__init__()
            
    def run(self, V, cname=None, bins=10,
                 range=None, density=False, cumulative=False):   
        """
        generates and stores histogram data for numerical data in V
        """
        
        super(Histogram, self).__init__()

        try:
            V = sorted(_flatten(list(V)))
        except:
            raise TypeError('V must be a list-like object')

        if len(V) == 0:
            raise Exception('V has zero length')
            
        if cname == None:
            self.cname = ''
        else:
            self.cname = cname

        values, bin_edges = pystaggrelite3.hist(V, bins=bins,
                   range=range, density=density, cumulative=cumulative)

        self['values'] = values
        self['bin_edges'] = bin_edges
        
        if cname == None:
            self.cname = ''
        else:
            self.cname = cname
            
        self.bins = bins
        self.range = range
        self.density = density
        self.cumulative = cumulative
        
    def __str__(self):

        tt = TextTable(48)
        tt.set_cols_dtype(['f', 'f'])
        tt.set_cols_align(['r', 'r'])
        for (b, v) in zip(self['bin_edges'],self['values']+['']):
            tt.add_row([b, v])
        tt.set_deco(TextTable.HEADER)
        tt.header(['Bins','Values'])

        return ''.join([('','Cumulative ')[self.cumulative],
                        ('','Density ')[self.density],
                        'Histogram for ', self.cname, '\n',
                        tt.draw()])

    def __repr__(self):
        if self == {}:
            return 'Histogram()'
        
        s = []
        for k, v in self.items():
            s.append("('%s', %s)"%(k, repr(v)))
        args = '[' + ', '.join(s) + ']'
        
        kwds = []            
        if self.cname is not None:
            kwds.append(f", cname='{self.cname}'")

        if self.bins != 10:
            kwds.append(f', bins={self.bins}')

        if self.range is not None:
            kwds.append(f', range={self.range}')

        if self.density != False:
            kwds.append(f', density={self.density}')
            
        if self.cumulative != False:
            kwds.append(f', cumulative={self.cumulative}')
            
        kwds= ''.join(kwds)

        return 'Histogram(%s%s)'%(args, kwds)
