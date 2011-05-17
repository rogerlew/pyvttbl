from __future__ import print_function

# Copyright (c) 2011, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.

# Python 2 to 3 workarounds
import sys
if sys.version_info[0] == 2:
    _strobj = basestring
##    _xrange = xrange
elif sys.version_info[0] == 3:
    _strobj = str
##    _xrange = range

import collections
import csv
##import inspect
##import math
import sqlite3
import warnings

##from pprint import pprint as pp
from copy import copy, deepcopy
from collections import OrderedDict, Counter

# check for third party packages
try:
    import pylab
    HAS_PYLAB = True
except:
    HAS_PYLAB = False
    
try:
    import numpy as np
    HAS_NUMPY = True
except:
    HAS_NUMPY = False

# locals
# I have modifed the texttable module original
# published by Gerome Fournier <jefke(at)free.fr>.
# I have modified it to provide more readable float
# printing and I am redistributing it under GPL.
from texttable import Texttable as TextTable
from texttable import _str

from dictset import DictSet
import pystaggrelite3

from pyvttbl import PyvtTbl
from descriptives import Descriptives
from marginals import Marginals
from histogram import Histogram

from rl_lib import _isfloat
from rl_lib import _isint
from rl_lib import _flatten
from rl_lib import _ifelse
##from rl_lib import _xunique_combinations

if HAS_NUMPY and HAS_PYLAB:
    from plot import *
    
# the dataframe class
class DataFrame(OrderedDict):                            
    def __init__(self, *args, **kwds):
        """
        initialize a PyvtTbl object

          keep in mind that because this class uses sqlite3
          behind the scenes the keys are case-insensitive
        """
        super(DataFrame, self).__init__()
        
        # Initialize sqlite3
        self.conn = sqlite3.connect(':memory:')
        self.cur = self.conn.cursor()
        self.aggregates = 'avg count count group_concat '  \
                          'group_concat max min sum total tolist' \
                          .split()

        # Bind pystaggrelite3 aggregators to sqlite3
        for n, a, f in pystaggrelite3.getaggregators():
            self.conn.create_aggregate(n, a, f)
            self.aggregates.append(n)

        self.aggregates = tuple(self.aggregates)

        # holds the factors conditions (and all the data values)
        # maybe this should be built on the fly for necessary
        # columns only?
        self.conditions = DictSet(self) 

        # prints the sqlite3 queries to stdout before
        # executing them for debugging purposes
        self.PRINTQUERIES = False

        super(DataFrame, self).update(*args, **kwds)

    def readTbl(self, fname, skip=0, delimiter=',',labels=True):
        """
        loads tabulated data from a plain text file

          Checks and renames duplicate column labels as well as checking
          for missing cells. readTbl will warn and skip over missing lines.
        """
        
        # open and read dummy coded data results file to data dictionary
        fid = open(fname, 'r')
        csv_reader = csv.reader(fid, delimiter=delimiter)
        d = OrderedDict()
        colnames = []
        
        for i, row in enumerate(csv_reader):
            # skip requested rows
            if i < skip:
                pass
            
            # read column labels from ith+1 line
            elif i == skip and labels:
                colnameCounter = Counter()
                for k, colname in enumerate(row):
                    colnameCounter[colname] += 1
                    if colnameCounter[colname] > 1:
                        warnings.warn("Duplicate label '%s' found"
                                      %colname,
                                      RuntimeWarning)
                        colname = '%s_%i'%(colname, colnameCounter[colname])                    
                    colnames.append(colname)
                    d[colname] = []

            # if labels is false we need to make labels
            elif i == skip and not labels:
                colnames = ['COL_%s'%(k+1) for k in range(len(row))]
                for j,colname in enumerate(colnames):
                    if _isfloat(row[j]):
                        d[colname] = [float(row[j])]
                    else:
                        d[colname] = [row[i]]

            # for remaining lines where i>skip...
            else:
                if len(row) != len(colnames):
                    warnings.warn('Skipping line %i of file. '
                                  'Expected %i cells found %i'\
                                  %(i+1, len(colnames), len(row)),
                                  RuntimeWarning)
                else:                    
                    for j, colname in enumerate(colnames):
                        if _isfloat(row[j]):
                            d[colname].append(float(row[j]))
                        else:
                            d[colname].append(row[j])
            
        # close data file
        fid.close()
        self.clear()
        for k, v in d.items():
            name_type = (k, self._check_sqlite3_type(v))
            super(DataFrame, self).__setitem__(name_type, v)
            
        del d
        self.conditions = DictSet(self)

    def __setitem__(self, key, item):
        """
        assign a column in the table

          The assigned item must be iterable. To add a single row use
          the insert method. To attach another table to this one use
          the attach method.
        """
        if not isinstance(key, collections.Hashable):
            raise TypeError("'%s' object is not hashable"%type(key).__name__)
        
        try:
            item = list(item)
        except:
            raise TypeError("'%s' object is not iterable"%type(item).__name__)

        old = None
        if isinstance(key, tuple):
            name_type = key
        else:
            # check to see if we need to do type checking after
            # the item is set
            if key in self.names():
                old = (key, self.typesdict()[key])
                
            name_type = (key, self._check_sqlite3_type(item))

        n = name_type[0]
        if isinstance(n, _strobj) and (n not in self.names()) and \
          (n.lower() in map(str.lower, self.names())):
            raise Exception('sqlite3 keys are case-insensitive')
            
        super(DataFrame, self).__setitem__(name_type, item)

        if old != None and old != name_type:
            del self[old]
        
        self.conditions[name_type] = self[key]

    def __delitem__(self, key):
        """
        delete a column from the table
        """
        if isinstance(key, tuple):
            name_type = key
        else:
            name_type = (key, self.typesdict()[key])
            
        del self.conditions[name_type]
        super(DataFrame, self).__delitem__(name_type)

    def __getitem__(self, key):
        if isinstance(key, tuple):
            name_type = key
        else:
            name_type = (key, self.typesdict()[key])
            
        return super(DataFrame, self).__getitem__(name_type)

    def __str__(self):
        if self == {}:
            return '(table is empty)'
        
        tt = TextTable(max_width=100000000)
        dtypes = [t[0] for t in self.types()]
        dtypes = list(''.join(dtypes).replace('r', 'f'))
        tt.set_cols_dtype(dtypes)

        aligns = [_ifelse(dt in 'fi','r','l') for dt in dtypes]
        tt.set_cols_align(aligns)

        if self.shape()[1] > 0:
            tt.add_rows(zip(*list(self.values())))
            
        tt.header(self.names())
        tt.set_deco(TextTable.HEADER)

        # output the table
        return tt.draw()
        
    def names(self):
        if len(self) == 0:
            return tuple()
        
        return list(zip(*list(self.keys())))[0]

    def types(self):
        if len(self) == 0:
            return tuple()
        
        return list(zip(*list(self.keys())))[1]

    def typesdict(self):
        return OrderedDict(self.keys())

    def shape(self):
        if len(self) == 0:
            return (0, 0)
        
        return (len(self), len(self.values()[0]))
    
    def _are_col_lengths_equal(self):
        """
        private method to check if the items in self have equal lengths

          returns True if all the items are equal
          returns False otherwise
        """
        # if self is not empty
        counts = map(len, self.values())
        if all(c - counts[0] + 1 == 1 for c in counts):
            return True
        else:
            return False

    def _check_sqlite3_type(self, iterable):
        """
        checks the sqlite3 datatype of iterable

          returns either 'null', 'integer', 'real', or 'text'
        """
        if len(iterable) == 0:
            return 'null'
        elif all(map(_isint, iterable)):
            return 'integer'
        elif all(map(_isfloat, iterable)):
            return 'real'
        else:
            return 'text'

    def _execute(self, query, t=tuple()):
        """
        private method to execute sqlite3 query

          When the PRINTQUERIES bool is true it prints the queries
          before executing them
        """
        if self.PRINTQUERIES:
            print(query)
            if len(t) > 0:
                print('  ', t)
            print()

        self.cur.execute(query, t)

    def _executemany(self, query, tlist):
        """
        private method to execute sqlite3 queries

          When the PRINTQUERIES bool is true it prints the queries
          before executing them. The execute many method is about twice
          as fast for building tables as the execute method.
        """
        if self.PRINTQUERIES:
            print(query)
            print('  ', tlist[0])
            print('   ...\n')

        self.cur.executemany(query, tlist)

    def _build_sqlite3_tbl(self, nsubset, where=[]):
        """
        build or rebuild sqlite table with columns in nsubset based on
        the where list

          where should be a list of tuples. Each tuple should have three
          elements. The first should be a column key (label). The second
          should be an operator: in, =, !=, <, >. The third element
          should contain value for the operator.
        """
        #  1. Perform some checkings
        ##############################################################
        if not hasattr(where, '__iter__'):
            raise TypeError( "'%s' object is not iterable"
                             % type(where).__name__)

        try:
            W = [tup for tup in where if tup[0] in self.names()]
        except:
            raise Exception('cannot unpack tuples from where')
        
        #  2. Get the neccesary data into a temparary table          
        ##############################################################           
        nsubset2 = list(set(nsubset) | set(tup[0] for tup in W))
        
        # initialize table
        self.conn.commit()
        self._execute('drop table if exists TBL2')

        self.conn.commit()
        query =  'create temp table TBL2\n  ('
        query += ', '.join('_%s_ %s'%(n, self.typesdict()[n]) for n in nsubset2)
        query += ')'
        self._execute(query)

        # build insert query
        query = 'insert into TBL2 values ('
        query += ','.join('?' for n in nsubset2) + ')'
        self._executemany(query, zip(*[self[n] for n in nsubset2]))
        self.conn.commit()

        #  3. Use sqlite3 to eliminate rows that should be excluded  
        ##############################################################
        if W == []:
            self._execute('drop table if exists TBL')
            self.conn.commit()
            
            self._execute('alter table TBL2 rename to TBL')
            self.conn.commit()
        else:
            self._execute('drop table if exists TBL')
            self.conn.commit()
            
            query = []
            for n in nsubset:
                query.append('_%s_ %s'%(n, self.typesdict()[n]))
            query = ', '.join(query)
            query =  'create temp table TBL\n  (' + query + ')'
            
            self._execute(query)

            # build insert query
            query = []
            for k,op,value in W:
                if _isfloat(value):
                    query.append(' _%s_ %s %s'%(k, op, value))
                elif isinstance(value,list):
                    if _isfloat(value[0]):
                        args = ', '.join(str(v) for v in value)
                    else:
                        args = ', '.join('"%s"'%v for v in value)
                    query.append(' _%s_ %s (%s)'%(k, op, args))
                else:
                    query.append(' _%s_ %s "%s"'%(k, op, value))
                    

            query = ' and '.join(query)
            nstr = ', '.join('_%s_'%n for n in nsubset)
            query = 'insert into TBL select %s from TBL2\n where '%nstr + query
            
            # run query
            self._execute(query)
            self.conn.commit()

            # delete TBL2
            self._execute('drop table if exists TBL2')
            self.conn.commit()

    def _get_sql_tbl_info(self):
        """
        private method to get a list of tuples containing information
        relevant to the current sqlite3 table

          Returns a list of tuples. Each tuple cooresponds to a column.
          Tuples include the column name, data type, whether or not the
          column can be NULL, and the default value for the column.
        """
        self.conn.commit()
        self._execute('PRAGMA table_info(TBL)')
        return list(self.cur)
    
    def pivot(self, val, rows=[], cols=[], aggregate='avg',
              where=[], flatten=False, attach_rlabels=False):
        
        # public method, saves table to self variables after pivoting
        """
        Returns a PyvtTbl object.

        Behavior is modeled after the PivotTables in Excel 2007.

            val = the colname to place as the data in the table
            rows = list of colnames whos combinations will become rows
                   in the table if left blank their will be one row
            cols = list of colnames whos combinations will become cols
                   in the table if left blank their will be one col
            aggregate = function applied across data going into each cell
                      of the table
                      http://www.sqlite.org/lang_aggfunc.html
            where = list of tuples
        """
        ##############################################################
        # pivot programmatic flow                                     #
        ##############################################################
        #  1. Check to make sure the table can be pivoted with the   #
        #     specified parameters                                   #
        #  2. Create a sqlite table with only the data in columns    #
        #     specified by val, rows, and cols. Also eliminate       #
        #     rows that meet the exclude conditions                  #
        #  3. Build rnames and cnames lists                          #
        #  4. Build query based on val, rows, and cols               #
        #  5. Run query                                              #
        #  6. Read data to from cursor into a list of lists          #
        #  7. Clean up                                               #
        #  8. flatten if specified                                   #
        #  9. return data, rnames, and cnames                        #
        ##############################################################


        #  1. Check to make sure the table can be pivoted with the
        #     specified parameters
        ##############################################################
        #  This may seem excessive but it provides better feedback
        #  to the user if the errors can be parsed out before had
        #  instead of crashing on confusing looking code segments
                
        if self == {}:
            raise Exception('Table must have data to print data')
        
        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        # check the supplied arguments
        if val not in self.names():
            raise KeyError(val)

        if not hasattr(rows, '__iter__'):
            raise TypeError( "'%s' object is not iterable"
                             % type(cols).__name__)

        if not hasattr(cols, '__iter__'):
            raise TypeError( "'%s' object is not iterable"
                             % type(cols).__name__)
        
        for k in rows:
            if k not in self.names():
                raise KeyError(k)
            
        for k in cols:
            if k not in self.names():
                raise KeyError(k)

        for k in [tup[0] for tup in where]:
            if k not in self.names():
                raise KeyError(k)

        # check for duplicate names
        dup = Counter([val] + rows + cols)
        del dup[None]
        if not all(count == 1 for count in dup.values()):
            raise Exception('duplicate labels specified')

        # check aggregate function
        aggregate = aggregate.lower()

        if aggregate not in self.aggregates:
            raise ValueError("supplied aggregate '%s' is not valid"%aggregate)
        
        # check to make sure where is properly formatted
        # todo
        
        #  2. Create a sqlite table with only the data in columns
        #     specified by val, rows, and cols. Also eliminate
        #     rows that meet the exclude conditions      
        ##############################################################
        self._build_sqlite3_tbl([val] + rows + cols, where)
        
        #  3. Build rnames and cnames lists
        ##############################################################
        
        # Refresh conditions list so we can build row and col list
        self._execute('select %s from TBL'
                      %', '.join('_%s_'%n for n in [val] + rows + cols))
        Zconditions = DictSet(zip([val]+rows+cols, zip(*list(self.cur))))
                
        # Build rnames
        if rows == []:
            rnames = [1]
        else:
            g = Zconditions.unique_combinations(rows)
            rnames = [zip(rows, v) for v in g]
            
        rsize = len(rnames)
        
        # Build cnames
        if cols == []:
            cnames = [1]
        else:
            g = Zconditions.unique_combinations(cols)
            cnames = [zip(cols, v) for v in g]
            
        csize=len(cnames)

        #  4. Build query based on val, rows, and cols
        ##############################################################
        #  Here we are using string formatting to build the query.
        #  This method is generally discouraged for security, but
        #  in this circumstance I think it should be okay. The column
        #  labels are protected with leading and trailing underscores.
        #  The rest of the query is set by the logic.
        #
        #  When we pass the data in we use the (?) tuple format
        if aggregate == 'tolist':
            agg = 'group_concat'
        else:
            agg = aggregate
            
        query = ['select ']            
        if rnames == [1] and cnames == [1]:
            query.append('%s( _%s_ ) from TBL'%(agg, val))
        else:
            if rnames == [1]:
                query.append('_%s_'%val)
            else:
                for i, r in enumerate(rows):
                    if i != 0:
                        query.append(', ')
                    query.append('_%s_'%r)

            if cnames == [1]:
                query.append('\n  , %s( _%s_ )'%(agg, val))
            else:
                for cols in cnames:
                    query.append('\n  , %s( case when '%agg)
                    if all(map(_isfloat, zip(*cols)[1])):
                        query.append(' and '\
                             .join(('_%s_=%s'%(k, v) for k, v in cols)))
                    else:
                        query.append(' and '\
                             .join(('_%s_="%s"'%(k ,v) for k, v in cols)))
                    query.append(' then _%s_ end )'%val)

            if rnames == [1]:
                query.append('\nfrom TBL')
            else:                
                query.append('\nfrom TBL group by ')
                
                for i, r in enumerate(rows):
                    if i != 0:
                        query.append(', ')
                    query.append('_%s_'%r)

        #  5. Run Query
        ##############################################################
        self._execute(''.join(query))

        #  6. Read data to from cursor into a list of lists
        ##############################################################

        d = []
        val_type = self.typesdict()[val]

        # keep the columns with the row labels
        if attach_rlabels:
            if aggregate == 'tolist':
                for row in self.cur:
                    d.append([])
                    for cell in list(row):
                        if val_type == 'real' or val_type == 'integer':
                            d[-1].append(eval('[%s]'%cell))
                        else:
                            d[-1].append(cell.split(','))
            else:
                for row in self.cur:
                    d.append(list(row))

            cnames = [(r, '') for r in rows].extend(cnames)
                    
        # eliminate the columns with row labels
        else:
            if aggregate == 'tolist':
                for row in self.cur:
                    d.append([])
                    for cell in list(row)[-len(cnames):]:
                        if val_type == 'real' or val_type == 'integer':
                            d[-1].append(eval('[%s]'%cell))
                        else:
                            d[-1].append(cell.split(','))
            else:
                for row in self.cur:
                    d.append(list(row)[-len(cnames):])

        #  7. Clean up
        ##############################################################
        self.conn.commit()

        #  8. flatten if specified
        ##############################################################
        if flatten:
            d = _flatten(d)

        #  9. return data, rnames, and cnames
        ##############################################################

        return PyvtTbl(d, val, rnames, cnames,
                       aggregate, Zconditions, where,
                       attach_rlabels)        
    
    def select_col(self, val, where=[]):
        """
        Returns the a copy of the selected values based on the where parameter
        """
        # 1.
        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        # 2.
        # check the supplied arguments
        if val not in self.names():
            raise KeyError(val)

        # check to make sure exclude is mappable
        # todo

        # warn if exclude is not a subset of self.conditions
        if not set(self.names()) >= set(tup[0] for tup in where):
            warnings.warn("where is not a subset of table conditions",
                          RuntimeWarning)
            
        if where == []: 
            return copy(self[val])             
        else:
            self._build_sqlite3_tbl([val], where)
            self._execute('select * from TBL')
            return [r[0] for r in self.cur]

    def sort(self, order=[]):
        """
        sort the table in-place

          order is a list of factors to sort by
          to reverse order append " desc" to the factor
        """

        # Check arguments        
        if self == {}:
            raise Exception('Table must have data to sort data')
        
        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')
        
        if not hasattr(order, '__iter__'):
            raise TypeError( "'%s' object is not iterable"
                             % type(order).__name__)

        # check or build order
        if order == []:
            order = self.names()

        # there are probably faster ways to do this, we definitely need
        # to treat the words as tokens to avoid problems were column
        # names are substrings of other column names
        for i, k in enumerate(order):
            ks = k.split()
            if ks[0] not in self.names():
                raise KeyError(k)
            
            if len(ks) == 1:
                order[i] = '_%s_'%ks[0]

            elif len(ks) == 2:
                if ks[1].lower() not in ['desc', 'asc']:
                    raise Exception("'order arg must be 'DESC' or 'ASC'")
                order[i] = '_%s_ %s'%(ks[0], ks[1])

            elif len(ks) > 2:
                raise Exception('too many parameters specified')

        # build table
        self._build_sqlite3_tbl(self.names())

        # build and excute query
        query = 'select * from TBL order by ' + ', '.join(order)
        self._execute(query)

        # read sorted order from cursor
        d = []
        for row in self.cur:
            d.append(list(row))

        d = zip(*d) # transpose
        for i, n in enumerate(self.names()):
            self[n] = list(d[i])

    def where(self, where):
        """
        Applies the where filter to a copy of the DataFrame, and
        returns the new DataFrame. The associated DataFrame is not copied.
        """
        new = DataFrame()
        
        self._build_sqlite3_tbl(self.names(), where)
        self._execute('select * from TBL')
        for n, values in zip(self.names(), zip(*list(self.cur))):
            new[n] = list(values)        

        return new
    
    def where_update(self, where):
        """
        Applies the where filter in-place. The associated DataFrame is
        not updated.
        """
        self._build_sqlite3_tbl(self.names(), where)
        self._execute('select * from TBL')
        for n, values in zip(self.names(), zip(*list(self.cur))):
            self[n] = list(values)
    
    def validate(self, criteria, verbose=False, report=False):
        """
        validate the data in the table.
        
          The criteria argument should be a dict. The keys should
          coorespond to columns in the table. The values should be
          functions which take a single parameter and return a boolean.

          Validation fails if the keys in the criteria dict is not a
          subset of the table keys.
        """
        # do some checking
        if self == {}:
            raise Exception('table must have data to validate data')
        
        try:        
            c = set(criteria.keys())
            s = set(self.names())
        except:
            raise TypeError('criteria must be mappable type')

        # check if the criteria dict has keys that aren't in self
        all_keys_found = bool((c ^ (c & s)) == set())

        # if the user doesn't want a detailed report we don't have
        # to do as much book keeping and can greatly simplify the
        # logic
        if not verbose and not report:
            if all_keys_found:
                return all(all(map(criteria[k], self[k])) for k in criteria)
            else:
                return False

        # loop through specified columns and apply the
        # validation function to each value in the column
        valCounter = Counter()
        reportDict = {}
        for k in (c & s):
            reportDict[k] = []
            if verbose:
                print('\nValidating %s:'%k)
                
            for i,v in enumerate(self[k]):
                try:
                    func = criteria[k]
                    result = func(v)
                except:
                    result = False
                    valCounter['code_failures'] +=1
                
                valCounter[result] += 1
                valCounter['n'] += 1

                if result:
                    if verbose:
                        print('.', end='')
                else:
                    reportDict[k].append(
                        "Error: on index %i value "
                        "'%s' failed validation"%(i, str(v)))
                    if verbose:
                        print('X', end='')
            if verbose:
                print()

        # do some book keeping
        pass_or_fail = (valCounter['n'] == valCounter[True]) & all_keys_found

        # print a report if the user has requested one
        if report:
            print('\nReport:')
            for k in (c&s):
                if len(reportDict[k]) > 0:
                    print('While validating %s:'%k)
                for line in reportDict[k]:
                    print('   ',line)

            print(  '  Values tested:', valCounter['n'],
                  '\n  Values passed:', valCounter[True],
                  '\n  Values failed:', valCounter[False])

            if valCounter['code_failures'] != 0:
                print('\n  (%i values failed because '
                      'func(x) did not properly execute)'
                      %valCounter['code_failures'])

            if not all_keys_found:
                print('\n  Error: criteria dict contained '
                      'keys not found in table:'
                      '\n   ', ', '.join(c ^ (c & s)))

            if pass_or_fail:
                print('\n***Validation PASSED***')
            else:
                print('\n***Validation FAILED***')

        # return the test result
        return pass_or_fail

    def attach(self, other):
        """
        attaches a second pivot table to this pivot table
        if the second table has a superset of columns
        """

        # do some checking
        if not isinstance(other, DataFrame):
            raise TypeError('second argument must be a DataFrame')
        
        if not self._are_col_lengths_equal():
            raise Exception('columns in self have unequal lengths')
        
        if not other._are_col_lengths_equal():
            raise Exception('columns in other have unequal lengths')

        if not set(self.names()) == set(other.names()):
            raise Exception('self and other must have the same columns')

        if not all(self.typesdict()[n] == other.typesdict()[n]
                                                   for n in self.names()):
            raise Exception('types of self and other must match')

        # perform attachment
        for n in self.names():
            self[n].extend(copy(other[n]))

        # update state variables
        self.conditions = DictSet(self)

    def insert(self, row):
        """
        insert a row into the table

        The row should be mappable. e.g. a dict or a list with key/value
        pairs. 
        """
        try:
            c = set(dict(row).keys())
            s = set(self.names())
        except:
            raise TypeError('row must be mappable type')
        
        # the easy case
        if self == {}:
            # if the table is empty try and unpack the table as
            # a row so it preserves the order of the column names
            if isinstance(row, list):
                for (k, v) in row:
                    self[k] = [v]
                    self.conditions[k] = [v]
            else:
                for (k, v) in dict(row).items():
                    self[k] = [v]
                    self.conditions[k] = [v]
        elif c - s == set():
            for (k, v) in dict(row).items():
                self[k].append(v)
                self.conditions[k].add(v)
        else:
            raise Exception('row must have the same keys as the table')

    def write(self, where=[], fname=None, delimiter=','):
        if self == {}:
            raise Exception('Table must have data to print data')

        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        if self.shape()[1] < 1:
            raise Exception('Table must have at least one row to print data')
        
        # check or build fname
        if fname != None:
            if not isinstance(fname, _strobj):
                raise TypeError('fname must be a string')
        else:
            lower_names = [str(n).lower().replace('1','') for n in self.names()]
            fname = 'X'.join(lower_names)

            if delimiter == ',':
                fname += '.csv' 
            elif delimiter == '\t':               
                fname += '.tsv'
            else:
                fname += '.txt'

        with open(fname,'wb') as fid:
            wtr = csv.writer(fid, delimiter=delimiter)
            wtr.writerow(self.names())

            if where == []: 
                wtr.writerows(zip(*list(self[n] for n in self.names())))
            else:
                self._build_sqlite3_tbl(self.names(), where)
                self._execute('select * from TBL')
                wtr.writerows(list(self.cur))

    def descriptives(self, cname, where=[]):
        """
        Returns a dict of descriptive statistics for column cname
        """
        if self == {}:
            raise Exception('Table must have data to calculate descriptives')

        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        if cname not in self.names():
            raise KeyError(cname)
        
        V = sorted(self.select_col(cname, where=where))
        return Descriptives(V, cname)

    def marginals(self, val, factors, where=[]):
        if self == {}:
            raise Exception('Table must have data to find marginals')

        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')
        
        return Marginals(self, val, factors, where)
        
    def histogram(self, cname, where=[], bins=10,
                  range=None, density=False, cumulative=False):
        """
        Returns Histogram object
        """
        if self == {}:
            raise Exception('Table must have data to calculate histogram')

        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        if cname not in self.names():
            raise KeyError(cname)
        
        V = sorted(self.select_col(cname, where=where))
        return Histogram(V, cname=cname, bins=bins, range=range,
                         density=density, cumulative=cumulative)

##df=DataFrame()
##df.readTbl('suppression~subjectXgroupXageXcycleXphase.csv')
##
##print(df)
