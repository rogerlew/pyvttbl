from __future__ import print_function

# Copyright (c) 2011, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.

# if it looks like a made an effort to conform to PEP8 then the code
# is fairly mature, if it looks like spaghetti it is because it is
# spaghetti.

# Python 2 to 3 workarounds
import sys
if sys.version_info[0] == 2:
    _strobj = basestring
    _xrange = xrange
elif sys.version_info[0] == 3:
    _strobj = str
    _xrange = range

import csv

from copy import copy

from rl_lib import _isfloat
from rl_lib import _isint
from rl_lib import _flatten
from rl_lib import _ifelse
from rl_lib import _xunique_combinations

from dictset import DictSet
from texttable import Texttable as TextTable

class PyvtTbl(list):
    """
    container holding the pivoted data
    """
    def __init__(self, iterable=None, val='', rnames=[], cnames=[],
                 aggregate='', conditions=DictSet(), where=[],
                 rlabels_attached=False):

        # the key of the value that was aggregated in the pivot
        # table
        self.val = val
        
        # list of lists of paired tuples where the paired tuples
        # hold the (factor, conditions) of the cooresponding row
        self.rnames = rnames 

        # list of lists of paired tuples where the paired tuples
        # hold the (factor, conditions) of the cooresponding column
        self.cnames = cnames

        # string specifing the aggregate function used to summarize
        # data
        self.aggregate = aggregate

        # a DictSet to hold the factor/levels that are not included
        # in the pivot table
        self.conditions = DictSet(conditions)

        # a list of tuples specifying the filtering applied to the
        # the pivot table
        self.where = where

        # a bool stating whether the first columns represent the
        # rlabels
        self.rlabels_attached = rlabels_attached

        if iterable != None:
            super(PyvtTbl, self).__init__(iterable)

    def _get_rows(self):
        if self.rnames == [1]:
            return [1]
        else:
            return [str(k) for (k, v) in self.rnames[0]]

    def _get_cols(self):
        if self.cnames == [1]:
            return [1]
        else:
            return [str(k) for (k, v) in self.cnames[0]]
        
    def __repr__(self):
        return """PyvtTbl(%s,
     val='%s',
     rnames=%s,
     cnames=%s,
     aggregate='%s',
     conditions=%s,
     where=%s,
     rlabels_attached=%s)"""%(super(PyvtTbl, self).__repr__(),
                              self.val,
                              self.rnames.__repr__(),
                              self.cnames.__repr__(),
                              self.aggregate,
                              self.conditions.__repr__(),
                              self.where.__repr__(),
                              self.rlabels_attached.__repr__())
                                    
    def __str__(self):
        """
        pivots, sets, and prints pivot table
        """

        if self == []:
            return '(table is empty)'

        rows = self._get_rows()
        cols = self._get_cols()

        # build first line
        first = '%s(%s)'%(self.aggregate, self.val)
        if self.conditions != []:
            query = []
            for k, op, value in self.where:
                query.append(' %s %s %s'%(k, str(op), str(value)))
            first += ' where' + ' and '.join(query)

        tt = TextTable(max_width=10000000)

        # no rows or cols were specified
        if self.rnames == [1] and self.cnames == [1]:
            # build the header
            header = ['Value']

            # initialize the texttable and add stuff
            tt.set_cols_dtype(['t'])
            tt.set_cols_dtype(['l'])
            tt.add_row(self[0])
            
        elif self.rnames == [1]: # no rows were specified
            # build the header
            header = [',\n'.join('%s=%s'%(f, c) for (f, c) in L) \
                      for L in self.cnames]
            
            # initialize the texttable and add stuff
            tt.set_cols_dtype(['a'] * len(self.cnames))
            tt.set_cols_align(['r'] * len(self.cnames))
            tt.add_row(self[0])
            
        elif self.cnames == [1]: # no cols were specified
            # build the header
            header = rows + ['Value']
            
            # initialize the texttable and add stuff
            tt.set_cols_dtype(['t'] * len(rows) + ['a'])
            tt.set_cols_align(['l'] * len(rows) + ['r'])
            for i, L in enumerate(self.rnames):
                tt.add_row([c for (f, c) in L] + self[i])
            
        else: # table has rows and cols
            # build the header
            header = copy(rows)
            for L in self.cnames:
                header.append(',\n'.join('%s=%s'%(f, c) for (f, c) in L))

            dtypes = ['t'] * len(rows) + ['a'] * len(self.cnames)
            aligns = ['l'] * len(rows) + ['r'] * len(self.cnames)

            # initialize the texttable and add stuff
            tt.set_cols_dtype(dtypes)
            tt.set_cols_align(aligns)
            for i, L in enumerate(self.rnames):
                tt.add_row([c for (f, c) in L] + self[i])

        # add header and decoration
        tt.header(header)
        tt.set_deco(TextTable.HEADER)

        # return the formatted table
        return '%s\n%s'%(first,tt.draw())

    def write(self, fname=None, delimiter=','):
        
        if self == []:
            raise Exception('must call pivot before writing pivot table')

        rows = self._get_rows()
        cols = self._get_cols()
        
        # check or build fname
        if fname != None:
            if not isinstance(fname, _strobj):
                raise TypeError('fname must be a string')
        else:
            # if rows == [1] then lower_rows becomes ['']
            # if cols...
            lower_rows = [str(n).lower().replace('1','') for n in rows]
            lower_cols = [str(n).lower().replace('1','') for n in cols]
            
            fname = '%s~(%s)Z(%s)'%(self.val.lower(),
                                    'X'.join(lower_rows),
                                    'X'.join(lower_cols))
            if delimiter == ',':
                fname += '.csv' 
            elif delimiter == '\t':               
                fname += '.tsv'
            else:
                fname += '.txt'
        
        # build and write first line
        first = '%s(%s)'%(self.aggregate, self.val)
        if self.where != []:
            query = []
            for k, op, value in self.where:
                query.append(' %s %s %s'%(k, str(op), str(value)))
            first += ' where' + ' and '.join(query)
        first = [first]

        data = [] # append the rows to this list and write with
                  # csv writer in one call
        
        # no rows or cols were specified
        if self.rnames == [1] and self.cnames == [1]:
            # build and write the header
            header = ['Value']

            # initialize the texttable and add stuff
            data.append(self[0])
            
        elif self.rnames == [1]: # no rows were specified
            # build the header
            header = ['_'.join('%s=%s'%(f, c) for (f, c) in L) \
                      for L in self.cnames]

            # initialize the texttable and add stuff
            data.append(self[0])
            
        elif self.cnames == [1]: # no cols were specified
            # build the header
            header = rows + ['Value']
            
            # initialize the texttable and add stuff
            for i, L in enumerate(self.rnames):
                data.append([c for (f, c) in L] + self[i])
            
        else: # table has rows and cols
            # build the header
            header = copy(rows)
            for L in self.cnames:
                header.append('_'.join('%s=%s'%(f, c) for (f, c) in L))

            # initialize the texttable and add stuff
            for i, L in enumerate(self.rnames):
                data.append([c for (f, c) in L] + self[i])

        # write file
        with open(fname, 'wb') as fid:
            wtr = csv.writer(fid, delimiter=delimiter)
            wtr.writerow(first)
            wtr.writerow(header)
            wtr.writerows(data)
