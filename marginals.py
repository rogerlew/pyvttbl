from __future__ import print_function

# Copyright (c) 2011, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.

from copy import copy

from collections import OrderedDict, Counter

from rl_lib import _isfloat
from rl_lib import _isint
from rl_lib import _flatten
from rl_lib import _ifelse
from rl_lib import _xunique_combinations

class Marginals(OrderedDict):
    def __init__(self, df, val, factors, where=[]):
        
        if df == {}:
            raise Exception('Table must have data to calculate marginals')
        
        # check to see if data columns have equal lengths
        if not df._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        for cname in [val]+factors:
            if cname not in df.names():
                raise KeyError(cname)

        # check for duplicate names
        dup = Counter([val] + factors)
        del dup[None]
        
        if not all([count == 1 for count in dup.values()]):
            raise Exception('duplicate labels specified as plot parameters')

        if not hasattr(factors, '__iter__'):
            raise TypeError( "'%s' object is not iterable"
                         % type(cols).__name__)
        
        dmu = df.pivot(val, rows=factors, where=where,
                         aggregate='avg', flatten=True)


        dN = df.pivot(val, rows=factors, where=where,
                        aggregate='count', flatten=True)

        dsem = df.pivot(val, rows=factors, where=where,
                              aggregate='sem', flatten=True)
         
        # build factors from r_list
        factors = OrderedDict()
        for i, r in enumerate(dN.rnames):
            if i == 0:
                for c in r:
                    factors[c[0]] = []
            
            for j, c in enumerate(r):
                factors[c[0]].append(c[1])

        dlower = copy(dN)
        dupper = copy(dN)
        for i,(mu, sem) in enumerate(zip(dmu, dsem)):
            dlower[i] = mu - 1.96 * sem
            dupper[i] = mu + 1.96 * sem

        super(Marginals, self).__init__()
        
        self['factors'] = factors
        self['dmu'] = dmu
        self['dN'] = dN
        self['dsem'] = dsem
        self['dlower'] = dlower
        self['dupper'] = dupper           
        
    def __str__(self):
        """Plot marginal statisics over factors for val"""

        # marginals handles checking
        [f, dmu, dN, dsem, dlower, dupper] = self.values()

        M = []
        for v in f.values():
            M.append(v)
            
        M.append(dmu)
        M.append(dN)
        M.append(dsem)
        M.append(dlower)
        M.append(dupper)
        M = zip(*M) # transpose

        # figure out the width needed by the condition labels so we can
        # set the width of the table
        flength = sum([max([len(v) for c in v]) for v in f.values()])
        flength += len(f) * 2

        # build the header
        header = factors + 'Mean;Count;Std.\nError;'\
                           '95% CI\nlower;95% CI\nupper'.split(';')

        dtypes = ['t'] * len(factors) + ['f', 'i', 'f', 'f', 'f']
        aligns = ['l'] * len(factors) + ['r', 'l', 'r', 'r', 'r']
        
        # initialize the texttable and add stuff
        tt = TextTable(max_width=flength+48)
        tt.set_cols_dtype(dtypes)
        tt.set_cols_align(aligns)
        tt.add_rows(M,header=False)
        tt.header(header)
        tt.set_deco(TextTable.HEADER)

        # output the table
        return tt.draw()

