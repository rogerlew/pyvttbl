# Copyright (c) 2011-2024, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.

from collections import Counter,OrderedDict

from pyvttbl.misc.texttable import Texttable as TextTable


class Marginals(OrderedDict):
    """
       Calculates means, counts, standard errors, and confidence intervals
       for the marginal conditions of the factorial combinations specified in
       the factors list.

       args:
          key: column label (of the dependent variable)

       kwds:
          factors: list of column labels to segregate data

          where: criterion to apply to table before running analysis

       returns:
          a :mod:`pyvttbl.stats`. :class:`Marginals` object
    """

    def __init__(self, *args, **kwds):
        if len(args) > 1:
            raise Exception('expecting only 1 argument')

        self.val = kwds.get('val')
        self.factors = kwds.get('factors')
        self.where = kwds.get('where', [])

        if len(args) == 1:
            super(Marginals, self).__init__(args[0])
        else:
            super(Marginals, self).__init__()
            
    def run(self, df, val, factors, where=None):   
        """
        generates and stores marginal data from the DataFrame df
        and column labels in factors.
        """

        if where is None:
            where = []
        
        if df == {}:
            raise Exception('Table must have data to calculate marginals')
        
        # check to see if data columns have equal lengths
        if not df._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        for cname in [val]+factors:
            if cname not in df.keys():
                raise KeyError(cname)

        # check for duplicate keys
        dup = Counter([val] + factors)
        del dup[None]
        
        if not all([count == 1 for count in dup.values()]):
            raise Exception('duplicate labels specified as plot parameters')

        if not hasattr(factors, '__iter__'):
            raise TypeError( "'%s' object is not iterable"
                         % type(factors).__name__)
        
        dmu = df.pivot(val, rows=factors, where=where,
                         aggregate='avg')


        dN = df.pivot(val, rows=factors, where=where,
                        aggregate='count')

        dsem = df.pivot(val, rows=factors, where=where,
                              aggregate='sem')
        
        # build factors from r_list
        factorials = OrderedDict()
        for i, r in enumerate(dN.rnames):
            if i == 0:
                for c in r:
                    factorials[c[0]] = []
            
            for j, c in enumerate(r):
                factorials[c[0]].append(c[1])

        dlower = dmu - 1.96 * dsem
        dupper = dmu + 1.96 * dsem
        
        super(Marginals, self).__init__()

        self['factorials'] = factorials
        self['dmu'] = [float(v) for v in dmu]
        self['dN'] = [float(v) for v in dN]
        self['dsem'] = [float(v) for v in dsem]
        self['dlower'] = [float(v) for v in dlower]
        self['dupper'] = [float(v) for v in dupper]

        self.val = val
        self.factors = factors
        self.where = where
        
    def __str__(self):
        """Returns human readable string representaition of Marginals"""

        M = []
        for v in self['factorials'].values():
            M.append(v)
            
        M.append(self['dmu'])
        M.append(self['dN'])
        M.append(self['dsem'])
        M.append(self['dlower'])
        M.append(self['dupper'])
        M = zip(*M) # transpose

        # figure out the width needed by the condition labels so we can
        # set the width of the table
        flength = sum([max([len(v) for c in v])
                       for v in self['factorials'].values()])
        flength += len(self['factorials']) * 2

        # build the header
        header = self.factors + 'Mean;Count;Std.\nError;'\
                           '95% CI\nlower;95% CI\nupper'.split(';')

        dtypes = ['t'] * len(self.factors) + ['f', 'i', 'f', 'f', 'f']
        aligns = ['l'] * len(self.factors) + ['r', 'l', 'r', 'r', 'r']
        
        # initialize the texttable and add stuff
        tt = TextTable(max_width=10000000)
        tt.set_cols_dtype(dtypes)
        tt.set_cols_align(aligns)
        tt.add_rows(M, header=False)
        tt.header(header)
        tt.set_deco(TextTable.HEADER)

        # output the table
        return tt.draw()

    def __repr__(self):
        if self == {}:
            return 'Marginals()'
        
        s = []
        for k, v in self.items():
            s.append("('%s', %s)"%(k, repr(v)))
        args = '[' + ', '.join(s) + ']'
        
        kwds = []            
        if self.val is not None:
            kwds.append(", val='%s'"%self.val)
            
        if self.factors is not None:
            kwds.append(", factors=%s"%self.factors)
            
        if self.where != []:
            if isinstance(self.where, str):
                kwds.append(", where='%s'"%self.where)
            else:
                kwds.append(", where=%s"%self.where)
        kwds= ''.join(kwds)

        return 'Marginals(%s%s)'%(args, kwds)
