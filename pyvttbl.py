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

import collections
import csv
import inspect
import math
import sqlite3
import warnings

from math import isnan, isinf
from pprint import pprint as pp
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

# I have modifed the texttable module original
# published by Gerome Fournier <jefke(at)free.fr>.
# I have modified it to provide more readable float
# printing and I am redistributing it under GPL.
from texttable import Texttable as TextTable

# I wrote and tested this private static method.
# I am re-distributing text table so I know it won't change
from texttable import _str  

# I am the author of these non-standard packages. I have
# extensively tested both of them and they do not rely on
# non-standard code.
from dictset import DictSet
import pystaggrelite3


# private functions begin with an underscore. Feel free to use them
# but they may not remain backwards compatible or remain at all.

def _isfloat(string):
    try:
        float(string)
    except:
        return False
    return True

def _isint(string):
    try:
        f = float(string)
    except:
        return False
    if round(f) - f == 0:
        return True
    return False

def _ifelse(condition, ifTrue, ifFalse):
    if condition:
        return ifTrue
    return ifFalse

def _flatten(x):
    """_flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).

    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> _flatten([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]"""

    result = []
    for el in x:
        #if isinstance(el, (list, tuple)):
        if hasattr(el, "__iter__") and not isinstance(el, _strobj):
            result.extend(_flatten(el))
        else:
            result.append(el)
    return result

def _xunique_combinations(items, n):
    if n == 0:
        yield []
    else:
        for i in _xrange(len(items)):
            for cc in _xunique_combinations(items[i+1:], n-1):
                yield [items[i]]+cc
                
# the dataframe class
class PyvtTbl(dict):                            
    def __init__(self):
        """
        initialize a PyvtTbl object

          keep in mind that because this class uses sqlite3
          behind the scenes the keys are case-insensitive
        """

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
        
        # Initialize state variables
        ####################################################
        # we really don't need to initialize them here, but
        # it is a good excuse to explain what they are
        
        # same as self.keys() it is a hackish way to have an
        # ordereddict, plus it gives a consistent convention
        # to the column row names
        self.names = [] 

        # list to hold the sqlite3 data types of the table data
        self.types = [] 

        # holds the factors conditions (and all the data values)
        # maybe this should be built on the fly for necessary
        # columns only?
        self.conditions = DictSet() 

        # a dict with keys cooresponding to column names and
        # values cooresponding to the datatype of the column
        self.typesdict = {} 
        
        self.N = 0    # num cols in table
        self.M = None # num rows in table

        # list of lists to hold pivot data
        self.Z = [[]]

        # the key of the value that was aggregated in the pivot
        # table
        self.Zval = ''
        
        # list of lists of paired tuples where the paired tuples
        # hold the (factor, conditions) of the cooresponding row
        self.Zrnames = [] 

        # list of lists of paired tuples where the paired tuples
        # hold the (factor, conditions) of the cooresponding column
        self.Zcnames = [] 

        # string specifing the aggregate function used to summarize
        # data
        self.Zaggregate = '' 

        # a DictSet to hold the factor/levels that are not included
        # in the pivot table
        self.Zconditions = DictSet()

        # a list of tuples specifying the filtering applied to the
        # the pivot table
        self.Zwhere = []

        # prints the sqlite3 queries to standard out before
        # executing them for debugging purposes
        self.PRINTQUERIES = False

        # When true the plotting methods return a dict that
        # is validated with unit testing
        self.TESTMODE = False
        
    def readTbl(self, fname, skip=0, delimiter=',',labels=True):
        """
        loads tabulated data from a plain text file

          Checks and renames duplicate column labels as well as checking
          for missing cells. readTbl will warn and skip over missing lines.
        """
        
        # open and read dummy coded data results file to data dictionary
        fid = open(fname, 'r')
        csv_reader = csv.reader(fid, delimiter=delimiter)
        self.clear()
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
                    self[colname] = []

            # if labels is false we need to make labels
            elif i == skip and not labels:
                colnames = ['COL_%s'%(k+1) for k in range(len(row))]
                for j,colname in enumerate(colnames):
                    if _isfloat(row[j]):
                        self[colname] = [float(row[j])]
                    else:
                        self[colname] = [row[i]]

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
                            self[colname].append(float(row[j]))
                        else:
                            self[colname].append(row[j])
            
        # close data file
        fid.close()

        # set state variables
        self.names = colnames
        self.types = [self._checktype(n) for n in colnames]
        self.typesdict = dict(zip(self.names, self.types))
        self.conditions = DictSet(self)
        self.N = len(self.names)
        self.M = len(self.values()[0])

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

        super(PyvtTbl, self).__setitem__(key, list(item))

        # update state variables
        if key not in self.names:
            self.names.append(key)
            self.types.append(self._checktype(key))
            
        self.typesdict[key] = self._checktype(key)
        self.conditions[key] = self[key]
        self.N = len(self.names)
        self.M = len(self.values()[0])

    def __delitem__(self, key):
        """
        delete a column from the table
        """
        super(PyvtTbl, self).__delitem__(key)

        # update state variables
        index = self.names.index(key)
        self.names.pop(index)
        self.types.pop(index)
            
        del self.typesdict[key]
        del self.conditions[key]
        self.N = len(self.names)    

    def _are_col_lengths_equal(self):
        """
        private method to check if the items in self have equal lengths

          returns True if all the items are equal
          returns False otherwise
        """
        
        # if self is not empty
        counts = [len(v) for v in self.values()]
        if all([c - counts[0] + 1 == 1 for c in counts]):
            if self == {}:
                self.M = None
            else:
                self.M = len(self.values()[0])
            return True
        else:
            self.M = None
            return False

    def _duplicate_names_exist(self):
        """
        private method to check if the items in self have equal lengths

          returns True if all the items are equal
          returns False otherwise
        """
        
        # if self is not empty
        return (len(self.names) - set(n.lower() for n in self.names)) != 0
        
    def _checktype(self, cname):
        """
        checks the sqlite3 datatype of self[cname]

          returns either 'null', 'integer', 'real', or 'text'
        """
        if cname not in self:
            raise KeyError(cname)

        if len(self[cname]) == 0:
            return 'null'
        elif all(map(_isint, self[cname])):
            return 'integer'
        elif all(map(_isfloat, self[cname])):
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

##    def _build_sqlite3_tbl_old(self, nsubset, where=[]):
##        """
##        build or rebuild sqlite table with columns in nsubset and where
##        the key-conditions in exclude are not True.
##        """
##        X = self.conditions & exclude
##        
##        # initialize table
##        self.conn.commit()
##        self._execute('drop table if exists TBL')
##
##        self.conn.commit()
##        query =  'create temp table TBL\n  ('
##        query += ', '.join('_%s_ %s'%(n, self.typesdict[n]) for n in nsubset)
##        query += ')'
##        self._execute(query)
##
##        # build insert query
##        query = 'insert into TBL values ('
##        query += ','.join('?' for n in nsubset) + ')'
##
##        # for performance it is better to check it once if it is empty
##        # values are passed to sqlite as a tuple
##        if exclude == {}: 
##            for i in _xrange(self.M):
##                self._execute(query, tuple(self[n][i] for n in nsubset))
##        else:
##            for i in _xrange(self.M):
##                # X is the intersection of X and self.conditions
##                # so we know the keys in X will always be in self
##                if X - [(k,[self[k][i]]) for k in X] == X:
##                    self._execute(query, tuple((self[n][i] for n in nsubset)))
##
##        # Save (commit) the changes
##        self.conn.commit()

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
            W = [tup for tup in where if tup[0] in self]
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
        query += ', '.join('_%s_ %s'%(n, self.typesdict[n]) for n in nsubset2)
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
                query.append('_%s_ %s'%(n, self.typesdict[n]))
            query = ', '.join(query)
            query =  'create temp table TBL\n  (' + query + ')'
            
            self._execute(query)

            # build insert query
            query = []
            for k,op,value in W:
                if _isfloat(value):
                    query.append(' _%s_ %s %s'%(k,op,value))
                elif isinstance(value,list):
                    if _isfloat(value[0]):
                        args = ', '.join(str(v) for v in value)
                    else:
                        args = ', '.join('"%s"'%v for v in value)
                    query.append(' _%s_ %s (%s)'%(k,op,args))
                else:
                    query.append(' _%s_ %s "%s"'%(k,op,value))
                    

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
    
    def _pvt(self, val, rows=[], cols=[], aggregate='avg',
              where=[], flatten=False, attach_rlabels=False):
        """
        private pivot table method

          returns pivot table, rnames, and cnames but doesn't
          set self.Z, self.Zrnames, self.Zcnames, and self.Zconditions
        """
        ##############################################################
        # _pvt programmatic flow                                     #
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
        if val not in self:
            raise KeyError(val)

        if not hasattr(rows, '__iter__'):
            raise TypeError( "'%s' object is not iterable"
                             % type(cols).__name__)

        if not hasattr(cols, '__iter__'):
            raise TypeError( "'%s' object is not iterable"
                             % type(cols).__name__)
        
        for k in rows:
            if k not in self:
                raise KeyError(k)
            
        for k in cols:
            if k not in self:
                raise KeyError(k)

        for k in [tup[0] for tup in where]:
            if k not in self:
                raise KeyError(k)

        # check for duplicate names
        dup = Counter([val] + rows + cols)
        del dup[None]
        if not all([count == 1 for count in dup.values()]):
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
                
        # Build row_list
        if rows == []:
            row_list = [1]
        else:
            g = Zconditions.unique_combinations(rows)
            row_list = [zip(rows, v) for v in g]
            
        rsize = len(row_list)
        
        # Build col_list
        if cols == []:
            col_list = [1]
        else:
            g = Zconditions.unique_combinations(cols)
            col_list = [zip(cols, v) for v in g]
            
        csize=len(col_list)

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
        if row_list == [1] and col_list == [1]:
            query.append('%s( _%s_ ) from TBL'%(agg, val))
        else:
            if row_list == [1]:
                query.append('_%s_'%val)
            else:
                for i, r in enumerate(rows):
                    if i != 0:
                        query.append(', ')
                    query.append('_%s_'%r)

            if col_list == [1]:
                query.append('\n  , %s( _%s_ )'%(agg, val))
            else:
                for cols in col_list:
                    query.append('\n  , %s( case when '%agg)
                    if all(map(_isfloat, zip(*cols)[1])):
                        query.append(' and '\
                             .join(('_%s_=%s'%(k, v) for k, v in cols)))
                    else:
                        query.append(' and '\
                             .join(('_%s_="%s"'%(k ,v) for k, v in cols)))
                    query.append(' then _%s_ end )'%val)

            if row_list == [1]:
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
        val_type = self.typesdict[val]

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

            col_list = [(r, '') for r in rows].extend(col_list)
                    
        # eliminate the columns with row labels
        else:
            if aggregate == 'tolist':
                for row in self.cur:
                    d.append([])
                    for cell in list(row)[-len(col_list):]:
                        if val_type == 'real' or val_type == 'integer':
                            d[-1].append(eval('[%s]'%cell))
                        else:
                            d[-1].append(cell.split(','))
            else:
                for row in self.cur:
                    d.append(list(row)[-len(col_list):])

        #  7. Clean up
        ##############################################################
        self.conn.commit()

        #  8. flatten if specified
        ##############################################################
        if flatten:
            d = _flatten(d)

        #  9. return data, rnames, and cnames
        ##############################################################
        
        return d, row_list, col_list, Zconditions

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
            order = deepcopy(self.names)

        # there are probably faster ways to do this, we definitely need
        # to treat the words as tokens to avoid problems were column
        # names are substrings of other column names
        for i, k in enumerate(order):
            ks = k.split()
            if ks[0] not in self:
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
        self._build_sqlite3_tbl(self.names)

        # build and excute query
        query = 'select * from TBL order by ' + ', '.join(order)
        self._execute(query)

        # read sorted order from cursor
        d = []
        for row in self.cur:
            d.append(list(row))

        d = zip(*d) # transpose
        for i,n in enumerate(self.names):
            self[n] = list(d[i])

    def where_update(self, where):
        """
        Applies the filtering provided in where to the table
        """
        pass
        
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
            s = set(self.keys())
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
        for k in (c&s):
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

    def pivot(self, val, rows=[], cols=[], aggregate='avg',
              where=[], flatten=False, attach_rlabels=False):
        
        # public method, saves table to self variables after pivoting
        """
        Returns a pivot table as a 2d numpy array.

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
        d, rnames, cnames, conds = self._pvt(val, rows=rows, cols=cols,
                                             aggregate=aggregate,
                                             where=where,
                                             flatten=flatten,
                                             attach_rlabels=attach_rlabels)
         
        # sets results to self attributes
        self.Z = d
        self.Zval = val
        self.Zconditions = conds
        self.Zwhere = where
        self.Zaggregate = aggregate
        self.Zrnames = rnames
        self.Zcnames = cnames

        return self.Z, self.Zrnames, self.Zcnames        
    
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
        if val not in self:
            raise KeyError(val)

        # check to make sure exclude is mappable
        # todo

        # warn if exclude is not a subset of self.conditions
        if not set(self.names) >= set(tup[0] for tup in where):
            warnings.warn("where is not a subset of table conditions",
                          RuntimeWarning)
            
        if where == []: 
            return copy(self[val])             
        else:
            self._build_sqlite3_tbl([val], where)
            self._execute('select * from TBL')
            return [r[0] for r in self.cur]

    def attach(self, other):
        """
        attaches a second pivot table to this pivot table
        if the second table has a superset of columns
        """

        # do some checking
        if not isinstance(other, PyvtTbl):
            raise TypeError('second argument must be a PyvtTbl')
        
        if not self._are_col_lengths_equal():
            raise Exception('columns in self have unequal lengths')
        
        if not other._are_col_lengths_equal():
            raise Exception('columns in other have unequal lengths')

        if not set(self.names) == set(other.names):
            raise Exception('self and other must have the same columns')

        if not all([self.typesdict[n] == other.typesdict[n]
                                                   for n in self.names]):
            raise Exception('types of self and other must match')

        # perform attachment
        for n in self.names:
            self[n].extend(copy(other[n]))

        # update state variables
        self.conditions = DictSet(self)
        self.M = len(self.values()[0])

    def insert(self, row):
        """
        insert a row into the table

        The row should be mappable. e.g. a dict or a list with key/value
        pairs. 
        """
        try:
            c, s = set(dict(row).keys()), set(self.keys())
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
        
    def printTable(self, where=[]):
        if self == {}:
            raise Exception('Table must have data to print data')

        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        if self.M < 1: # self.M gets reset by self._check_tbl_lengths()
            raise Exception('Table must have at least one row to print data')
        
        # ignore tuples in where that aren't in self
        W = [tup for tup in where if tup[0] in self]
        
        tt = TextTable(max_width=100000000)
        dtypes = [self.typesdict[n][0] for n in self.names]
        dtypes = list(''.join(dtypes).replace('r', 'f'))
        tt.set_cols_dtype(dtypes)

        aligns = [_ifelse(dt in 'fi','r','l') for dt in dtypes]
        tt.set_cols_align(aligns)
        
        if where == []: 
                tt.add_rows(zip(*list(self[n] for n in self.names)))              
        else:
            self._build_sqlite3_tbl(self.names, where)
            self._execute('select * from TBL')
            tt.add_rows(list(self.cur))
        
        tt.header(self.names)
        tt.set_deco(TextTable.HEADER)

        # output the table
        print(tt.draw())

    def writeTable(self, where=[], fname=None, delimiter=','):
        if self == {}:
            raise Exception('Table must have data to print data')

        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        if self.M < 1: # self.M gets reset by self._check_tbl_lengths()
            raise Exception('Table must have at least one row to print data')
        
        # check or build fname
        if fname != None:
            if not isinstance(fname, _strobj):
                raise TypeError('fname must be a string')
        else:
            lower_names = [str(n).lower().replace('1','') for n in self.names]
            
            fname = 'X'.join(lower_names)

            if delimiter == ',':
                fname += '.csv' 
            elif delimiter == '\t':               
                fname += '.tsv'
            else:
                fname += '.txt'

        with open(fname,'wb') as fid:
            wtr = csv.writer(fid, delimiter=delimiter)
            wtr.writerow(self.names)

            if where == []: 
                wtr.writerows(zip(*list(self[n] for n in self.names)))
            else:
                self._build_sqlite3_tbl(self.names, where)
                self._execute('select * from TBL')
                wtr.writerows(list(self.cur))
                                    
    def printPivot(self, val, rows=[], cols=[], aggregate='avg',
                   where=[], flatten=False):
        """
        pivots, sets, and prints pivot table
        """
        # _pvt does checking
        self.pivot(val, rows=rows, cols=cols, aggregate=aggregate,
                   where=where, flatten=flatten)

        # build first line
        first = '%s(%s)'%(self.Zaggregate, self.Zval)
        if self.Zconditions != []:
            query = []
            for k, op, value in where:
                query.append(' %s %s %s'%(k, str(op), str(value)))
            first += ' where' + ' and '.join(query)

        tt = TextTable(max_width=10000000)

        # no rows or cols were specified
        if self.Zrnames == [1] and self.Zcnames == [1]:
            # build the header
            header = ['Value']

            # initialize the texttable and add stuff
            tt.set_cols_dtype(['t'])
            tt.set_cols_dtype(['l'])
            tt.add_row(self.Z[0])
            
        elif self.Zrnames == [1]: # no rows were specified
            # build the header
            header = [',\n'.join('%s=%s'%(f, c) for (f, c) in L) \
                      for L in self.Zcnames]
            
            # initialize the texttable and add stuff
            tt.set_cols_dtype(['a'] * len(self.Zcnames))
            tt.set_cols_align(['r'] * len(self.Zcnames))
            tt.add_row(self.Z[0])
            
        elif self.Zcnames == [1]: # no cols were specified
            # build the header
            header = rows + ['Value']
            
            # initialize the texttable and add stuff
            tt.set_cols_dtype(['t'] * len(rows) + ['a'])
            tt.set_cols_align(['l'] * len(rows) + ['r'])
            for i, L in enumerate(self.Zrnames):
                tt.add_row([c for (f, c) in L] + self.Z[i])
            
        else: # table has rows and cols
            # build the header
            header = copy(rows)
            for L in self.Zcnames:
                header.append(',\n'.join('%s=%s'%(f, c) for (f, c) in L))

            dtypes = ['t'] * len(rows) + ['a'] * len(self.Zcnames)
            aligns = ['l'] * len(rows) + ['r'] * len(self.Zcnames)

            # initialize the texttable and add stuff
            tt.set_cols_dtype(dtypes)
            tt.set_cols_align(aligns)
            for i, L in enumerate(self.Zrnames):
                tt.add_row([c for (f, c) in L] + self.Z[i])

        # add header and decoration
        tt.header(header)
        tt.set_deco(TextTable.HEADER)

        # output the table
        print(first)
        print(tt.draw())

    def writePivot(self, fname=None, delimiter=','):
        
        if len(_flatten(self.Z)) == 0:
            raise Exception('must call pivot before writing pivot table')
        
        if self.Zrnames == [1]:
            rows = [1]
        else:
            rows = [str(k) for (k, v) in self.Zrnames[0]]

        if self.Zcnames == [1]:
            cols = [1]
        else:
            cols = [str(k) for (k, v) in self.Zcnames[0]]
        
        # check or build fname
        if fname != None:
            if not isinstance(fname, _strobj):
                raise TypeError('fname must be a string')
        else:
            # if rows == [1] then lower_rows becomes ['']
            # if cols...
            lower_rows = [str(n).lower().replace('1','') for n in rows]
            lower_cols = [str(n).lower().replace('1','') for n in cols]
            
            fname = '%s~(%s)Z(%s)'%(self.Zval.lower(),
                                    'X'.join(lower_rows),
                                    'X'.join(lower_cols))
            if delimiter == ',':
                fname += '.csv' 
            elif delimiter == '\t':               
                fname += '.tsv'
            else:
                fname += '.txt'
        
        # build and write first line
        first = '%s(%s)'%(self.Zaggregate, self.Zval)
        if self.Zwhere != []:
            query = []
            for k, op, value in self.Zwhere:
                query.append(' %s %s %s'%(k, str(op), str(value)))
            first += ' where' + ' and '.join(query)
        first = [first]

        data = [] # append the rows to this list and write with
                  # csv writer in one call
        
        # no rows or cols were specified
        if self.Zrnames == [1] and self.Zcnames == [1]:
            # build and write the header
            header = ['Value']

            # initialize the texttable and add stuff
            data.append(self.Z[0])
            
        elif self.Zrnames == [1]: # no rows were specified
            # build the header
            header = ['_'.join('%s=%s'%(f, c) for (f, c) in L) \
                      for L in self.Zcnames]

            # initialize the texttable and add stuff
            data.append(self.Z[0])
            
        elif self.Zcnames == [1]: # no cols were specified
            # build the header
            header = rows + ['Value']
            
            # initialize the texttable and add stuff
            for i, L in enumerate(self.Zrnames):
                data.append([c for (f, c) in L] + self.Z[i])
            
        else: # table has rows and cols
            # build the header
            header = copy(rows)
            for L in self.Zcnames:
                header.append('_'.join('%s=%s'%(f, c) for (f, c) in L))

            # initialize the texttable and add stuff
            for i, L in enumerate(self.Zrnames):
                data.append([c for (f, c) in L] + self.Z[i])

        # write file
        with open(fname, 'wb') as fid:
            wtr = csv.writer(fid, delimiter=delimiter)
            wtr.writerow(first)
            wtr.writerow(header)
            wtr.writerows(data)

    def descriptives(self, cname, where=[]):
        
        """
        Returns a dict of descriptive statistics for column cname
        """
        if self == {}:
            raise Exception('Table must have data to calculate descriptives')

        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        if cname not in self:
            raise KeyError(cname)
        
        V = sorted(self.select_col(cname, where=where))
        N = len(V)

        D = OrderedDict()
        D['count']      = N
        D['mean']       = sum(V) / N
        D['var']        = sum([(D['mean']-v)**2 for v in V]) / (N - 1)
        D['stdev']      = math.sqrt(D['var'])
        D['sem']        = D['stdev'] / math.sqrt(N)
        D['rms']        = math.sqrt(sum([v**2 for v in V]) / N)
        D['min']        = min(V)
        D['max']        = max(V)
        D['range']      = D['max'] - D['min']
        D['median']     = V[int(N/2)]
        if D['count']%2 == 0:
            D['median'] += V[int(N/2)-1]
            D['median'] /= 2.
        D['95ci_lower'] = D['mean'] - 1.96*D['sem']
        D['95ci_upper'] = D['mean'] + 1.96*D['sem']

        return D
    
    def printDescriptives(self, cname):
        D = self.descriptives(cname)

        print('Descriptive Statistics for')
        print('', cname                   )
        print('==========================')

        tt = TextTable(48)
        tt.set_cols_dtype(['t', 'f'])
        tt.set_cols_align(['l', 'r'])
        for (k, v) in D.items():
            tt.add_row([' %s'%k, v])
        tt.set_deco(TextTable.HEADER)
        
        print(tt.draw())

    def marginals(self, val, factors, where=[]):
        if self == {}:
            raise Exception('Table must have data to calculate marginals')
        
        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        for cname in [val]+factors:
            if cname not in self:
                raise KeyError(cname)

        # check for duplicate names
        dup = Counter([val] + factors)
        del dup[None]
        
        if not all([count == 1 for count in dup.values()]):
            raise Exception('duplicate labels specified as plot parameters')

        if not hasattr(factors, '__iter__'):
            raise TypeError( "'%s' object is not iterable"
                         % type(cols).__name__)

        dmu = self.pivot(val, rows=factors, where=where,
                         aggregate='avg', flatten=True)[0]

        dN = self.pivot(val, rows=factors, where=where,
                        aggregate='count', flatten=True)[0]

        dsem, r_list, c_list = self.pivot(val, rows=factors, where=where,
                                          aggregate='sem', flatten=True)
 
        # build factors from r_list
        factors = OrderedDict()
        for i, r in enumerate(r_list):
            if i == 0:
                for c in r:
                    factors[c[0]] = []
            
            for j, c in enumerate(r):
                factors[c[0]].append(c[1])

        dlower = []
        dupper = []
        for mu, sem in zip(dmu, dsem):
            dlower.append(mu - 1.96*sem)
            dupper.append(mu + 1.96*sem)

        return factors, dmu, dN, dsem, dlower, dupper            
        
    def printMarginals(self, val, factors, where=[]):
        """Plot marginal statisics over factors for val"""

        # marginals handles checking
        x = self.marginals(val, factors=factors, where=where)
        [f, dmu, dN, dsem, dlower, dupper] = x

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
        print()
        print(tt.draw())

    def plotBox(self, val, factors=[], where=[],
            fname=None, quality='medium'):

        if not (HAS_NUMPY and HAS_PYLAB):
            raise ImportError('numpy and pylab are required for plotting')
        
        # check to see if there is any data in the table
        if self == {}:
            raise Exception('Table must have data to print data')
        
        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        # check the supplied arguments
        if val not in self:
            raise KeyError(val)

        if not hasattr(factors, '__iter__'):
            raise TypeError( "'%s' object is not iterable"
                             % type(factors).__name__)
        
        for k in factors:
            if k not in self:
                raise KeyError(k)
            
        # check for duplicate names
        dup = Counter([val]+factors)
        del dup[None]
        if not all([count==1 for count in dup.values()]):
            raise Exception('duplicate labels specified as plot parameters')

        # check fname
        if not isinstance(fname, _strobj) and fname != None:
            raise TypeError('fname must be None or string')

        if isinstance(fname, _strobj):
            if not (fname.lower().endswith('.png') or \
                    fname.lower().endswith('.svg')):
                raise Exception('fname must end with .png or .svg')

        test = {}

        if factors == []:
            d = self.select_col(val, where=where)            
            fig = pylab.figure()
            pylab.boxplot(np.array(d))
            xticks = pylab.xticks()[0]
            xlabels = [val]
            pylab.xticks(xticks, xlabels)

            test['d'] = d
            test['val'] = val

        else:
            D, cs = self._pvt(val, rows=factors,
                              where=where,
                              aggregate='tolist')[:2]

            D = [np.array(_flatten(d)) for d in D]

            fig = pylab.figure(figsize=(6*len(factors),6))
            fig.subplots_adjust(left=.05, right=.97, bottom=0.24)
            pylab.boxplot(D)
            xticks = pylab.xticks()[0]
            xlabels = ['\n'.join('%s = %s'%fc for fc in c) for c in cs]
            pylab.xticks(xticks, xlabels,
                         rotation='vertical',
                         verticalalignment='top')

            test['d'] = D
            test['xlabels'] = xlabels

        maintitle = '%s'%val

        if factors != []:
            maintitle += ' by '
            maintitle += ' * '.join(factors)
            
        fig.text(0.5, 0.95, maintitle,
                 horizontalalignment='center',
                 verticalalignment='top')
        
        test['maintitle'] = maintitle
            
        if fname == None:
            fname = 'box(%s).png'%val.lower()

        test['fname'] = fname
        
        # save figure
        if quality == 'low' or fname.endswith('.svg'):
            pylab.savefig(fname)
            
        elif quality == 'medium':
            pylab.savefig(fname, dpi=200)
            
        elif quality == 'high':
            pylab.savefig(fname, dpi=300)
            
        else:
            pylab.savefig(fname)

        pylab.close()

        if self.TESTMODE:
            return test

    def hist(self, val, where=[], bins=10,
             range=None, density=False, cumulative=False):
        
        V = self.select_col(val, where=where)
        return pystaggrelite3.hist(V,
                                   bins=bins,
                                   range=range,
                                   density=density,
                                   cumulative=cumulative)

    def plotHist(self, val, where=[], bins=10,
                 range=None, density=False, cumulative=False,
                 fname=None, quality='medium'):    
        
        # check for third party packages
        if not (HAS_NUMPY and HAS_PYLAB):
            raise ImportError('numpy and pylab are required for plotting')

        # check fname
        if not isinstance(fname, _strobj) and fname != None:
            raise TypeError('fname must be None or string')

        if isinstance(fname, _strobj):
            if not (fname.lower().endswith('.png') or \
                    fname.lower().endswith('.svg')):
                raise Exception('fname must end with .png or .svg')                

        # select_col does checking of val and where
        v = self.select_col(val, where=where)
        
        fig=pylab.figure()
        tup = pylab.hist(np.array(v), bins=bins, range=range,
                         normed=density, cumulative=cumulative)
        pylab.title(val)

        if fname == None:
            fname = 'hist(%s).png'%val.lower()
        
        # save figure
        if quality == 'low' or fname.endswith('.svg'):
            pylab.savefig(fname)
            
        elif quality == 'medium':
            pylab.savefig(fname, dpi=200)
            
        elif quality == 'high':
            pylab.savefig(fname, dpi=300)
            
        else:
            pylab.savefig(fname)

        pylab.close()

        if self.TESTMODE:
            # build and return test dictionary
            return {'bins':tup[0], 'counts':tup[1], 'fname':fname}

    def plotMarginals(self, val, xaxis, 
                      seplines=None, sepxplots=None, sepyplots=None,
                      xmin='AUTO', xmax='AUTO', ymin='AUTO', ymax='AUTO',
                      where=[], fname=None, quality='low', yerr=None):

        ##############################################################
        # plotMarginals programmatic flow                            #
        ##############################################################
        #  1. Check to make sure a plot can be generated with the    # 
        #     specified arguments and parameter                      #
        #  2. Set yerr aggregate                                     #
        #  3. Figure out ymin and ymax if 'AUTO' is specified        #
        #  4. Figure out how many subplots we need to make and the   #
        #     levels of those subplots                               #
        #  5. Initialize pylab.figure and set plot parameters        #
        #  6. Build and set main title                               #
        #  7. loop through the the rlevels and clevels and make      #
        #     subplots                                               #
        #      7.1 Create new axes for the subplot                   #
        #      7.2 Add subplot title                                 #
        #      7.3 Format the subplot                                #
        #      7.4 Iterate plotnum counter                           #
        #  8. Place yerr text in bottom right corner                 #
        #  9. Save the figure                                        #
        # 10. return the test dictionary                             #
        ##############################################################

        #  1. Check to make sure a plot can be generated with the    
        #     specified arguments and parameter
        ##############################################################
        # pylab doesn't like not being closed. To avoid starting
        # a plot without finishing it, we do some extensive checking
        # up front

        # check for data
        if self == {}:
            raise Exception('Table must have data to plot marginals')

        # check for third party packages
        if not (HAS_NUMPY and HAS_PYLAB):
            raise ImportError('numpy and pylab are required for plotting')

        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        # check to make sure arguments are column labels
        if val not in self:
            raise KeyError(val)

        if xaxis not in self:
            raise KeyError(xaxis)
        
        if seplines not in self and seplines != None:
            raise KeyError(seplines)

        if sepxplots not in self and sepxplots != None:
            raise KeyError(sepxplots)
        
        if sepyplots not in self and sepyplots != None:
            raise KeyError(sepyplots)

        # check for duplicate names
        dup = Counter([val, xaxis, seplines, sepxplots, sepyplots])
        del dup[None]
        if not all([count == 1 for count in dup.values()]):
            raise Exception('duplicate labels specified as plot parameters')

        # check fname
        if not isinstance(fname, _strobj) and fname != None:
            raise TypeError('fname must be None or string')

        if isinstance(fname, _strobj):
            if not (fname.lower().endswith('.png') or \
                    fname.lower().endswith('.svg')):
                raise Exception('fname must end with .png or .svg')                

        # check cell counts
        cols = [f for f in [seplines, sepxplots, sepyplots] if f in self]
        counts = self.pivot(val, rows=[xaxis], cols=cols,
                            flatten=True, where=where, aggregate='count')[0]

        for count in counts:
            if count < 1:
                raise Exception('cell count too low to calculate mean')

        #  2. Initialize test dictionary
        ##############################################################
        # To test the plotting a dict with various plot parameters
        # is build and returned to the testing module. In this
        # scenario our primary concern is that the values represent
        # what we think they represent. Whether they match the plot
        # should be fairly obvious to the user. 
        test = {}
        
        #  3. Set yerr aggregate so sqlite knows how to calculate yerr
        ##############################################################
        
        # check yerr
        aggregate = None
        if yerr == 'sem':
            aggregate = 'sem'
            
        elif yerr == 'stdev':
            aggregate = 'stdev'
            
        elif yerr == 'ci':
            aggregate = 'ci'

        for count in counts:
            if aggregate != None and count < 2:
                raise Exception('cell count too low to calculate %s'%yerr)

        test['yerr'] = yerr
        test['aggregate'] = aggregate

        #  4. Figure out ymin and ymax if 'AUTO' is specified
        ##############################################################            
        desc = self.descriptives(val)
        
        if ymin == 'AUTO':
            # when plotting postive data always have the y-axis go to 0
            if desc['min'] >= 0.:
                ymin = 0. 
            else:
                ymin = desc['mean'] - 3.*desc['stdev']
        if ymax == 'AUTO':
            ymax = desc['mean'] + 3.*desc['stdev']

        if any([isnan(ymin), isinf(ymin), isnan(ymax), isinf(ymax)]):
            raise Exception('calculated plot bounds nonsensical')

        test['ymin'] = ymin
        test['ymax'] = ymax

        #  5. Figure out how many subplots we need to make and the
        #     levels of those subplots
        ##############################################################      
        numrows = 1
        rlevels = [1]
        if sepyplots != None:
            rlevels = copy(self.Zconditions[sepyplots]) # a set
            numrows = len(rlevels) # a int
            rlevels = sorted(rlevels) # set -> sorted list
                
        numcols = 1
        clevels = [1]            
        if sepxplots != None:
            clevels = copy(self.Zconditions[sepxplots])
            numcols = len(clevels)
            clevels = sorted(clevels) # set -> sorted list

        test['numrows']  = numrows
        test['rlevels']  = rlevels
        test['numcols']  = numcols
        test['clevels']  = clevels
        
        #  6. Initialize pylab.figure and set plot parameters
        ##############################################################  
        fig = pylab.figure(figsize=(6*numcols, 4*numrows+1))
        fig.subplots_adjust(wspace=.05, hspace=0.2)
        
        #  7. Build and set main title
        ##############################################################  
        maintitle = '%s by %s'%(val,xaxis)
        
        if seplines:
            maintitle += ' * %s'%seplines
        if sepxplots:
            maintitle += ' * %s'%sepxplots
        if sepyplots:
            maintitle += ' * %s'%sepyplots
            
        fig.text(0.5, 0.95, maintitle,
                 horizontalalignment='center',
                 verticalalignment='top')

        test['maintitle']  = maintitle
        
        #  8. loop through the the rlevels and clevels and make
        #     subplots
        ##############################################################
        test['y'] = []
        test['yerr'] = []
        test['subplot_titles'] = []
        test['xmins'] = []
        test['xmaxs'] = []
        
        plotnum = 1 # subplot counter
        axs = []

        for r, rlevel in enumerate(rlevels):
            for c, clevel in enumerate(clevels):
                
                #  8.1 Create new axes for the subplot
                ######################################################
                axs.append(pylab.subplot(numrows, numcols, plotnum))

                ######## If separate lines are not specified #########
                if seplines == None:
                    y, r_list, c_list = self._pvt(val, cols=[xaxis],
                                                  where=where,
                                                  aggregate='avg',
                                                  flatten=True)[:3]
                    y = np.array(y)

                    if aggregate != None:
                        yerr = self._pvt(val, cols=[xaxis],
                                         where=where,
                                         aggregate=aggregate,
                                         flatten=True)[0]
                        yerr = np.array(yerr)
                        
                    x = [name for [(label, name)] in c_list]
                    
                    if _isfloat(yerr):
                        yerr = np.array([yerr for a in x])

                    if all([_isfloat(a) for a in x]):
                        axs[-1].errorbar(x, y, yerr)
                        if xmin == 'AUTO' and xmax == 'AUTO':
                            xmin, xmax = axs[-1].get_xlim()
                            xran = xmax - xmin
                            xmin = xmin - 0.05*xran
                            xmax = xmax + 0.05*xran

                        axs[-1].plot([xmin, xmax], [0., 0.], 'k:')
                        
                    else : # categorical x axis
                        axs[-1].errorbar(_xrange(len(x)), y.flatten(), yerr)
                        pylab.xticks(_xrange(len(x)), x)
                        xmin = - 0.5
                        xmax = len(x) - 0.5
                        
                        axs[-1].plot([xmin, xmax], [0., 0.], 'k:')

                ########## If separate lines are specified ###########
                else:
                    y, r_list, c_list = self._pvt(val,
                                                  rows=[seplines],
                                                  cols=[xaxis],
                                                  where=where,
                                                  aggregate='avg',
                                                  flatten=False)[:3]
                    y = np.array(y)
                    
                    if aggregate != None:
                        yerrs = self._pvt(val,
                                          rows=[seplines],
                                          cols=[xaxis],
                                          where=where,
                                          aggregate=aggregate,
                                          flatten=False)[0]
                        yerrs = np.array(yerrs)
                        
                    x = [name for [(label, name)] in c_list]

                    if _isfloat(yerr):
                        yerr = np.array([yerr for a in x])

                    plots = []
                    labels = []
                    for i, name in enumerate(r_list):
                        if aggregate != None:
                            yerr = yerrs[i,:]
                        
                        labels.append(name[0][1])

                        if all([_isfloat(a) for a in x]):
                            plots.append(axs[-1].errorbar(x, y[i,:], yerr)[0])
                            if xmin=='AUTO' and xmax=='AUTO':
                                xmin , xmax = axs[-1].get_xlim()
                                xran = xmax - xmin
                                xmin = xmin - .05*xran
                                xmax = xmax + .05*xran
                                
                            axs[-1].plot([xmin, xmax], [0.,0.], 'k:')
                            
                        else : # categorical x axis
                            plots.append(axs[-1].errorbar(_xrange(len(x)),
                                                          y[i,:],
                                                          yerr)[0])
                            pylab.xticks(_xrange(len(x)), x)
                            xmin = - 0.5
                            xmax = len(x) - 0.5
                            
                            axs[-1].plot([xmin, xmax], [0., 0.], 'k:')

                    pylab.figlegend(plots, labels, loc=1,
                                    labelsep=.005,
                                    handlelen=.01,
                                    handletextsep=.005)

                test['y'].append(y.tolist())
                if yerr == None:
                    test['yerr'].append([])
                else:
                    test['yerr'].append(yerr.tolist())
                test['xmins'].append(xmin)
                test['xmaxs'].append(xmax)

                #  8.2 Add subplot title
                ######################################################
                if rlevels == [1] and clevels == [1]:
                    title = ''
                    
                elif rlevels == [1]:
                    title = _str(clevel)
                    
                elif clevels == [1]:
                    title = _str(rlevel)
                    
                else:
                    title = '%s = %s, %s = %s' \
                            % (sepyplots, _str(rlevel), sepxplots, _str(rlevel))
                    
                pylab.title(title, fontsize='medium')
                test['subplot_titles'].append(title)

                #  8.3 Format the subplot
                ######################################################
                pylab.xlim(xmin, xmax)
                pylab.ylim(ymin, ymax)

                # supress tick labels unless subplot is on the bottom
                # row or the far left column
                if r != (len(rlevels) - 1):
                    locs, labels = pylab.xticks()
                    pylab.xticks(locs, ['' for l in _xrange(len(locs))])
                    
                if c != 0:
                    locs, labels = pylab.yticks()
                    pylab.yticks(locs, ['' for l in _xrange(len(locs))])

                # Set the aspect ratio for the subplot
                Dx = abs(axs[-1].get_xlim()[0] - axs[-1].get_xlim()[1])
                Dy = abs(axs[-1].get_ylim()[0] - axs[-1].get_ylim()[1])
                axs[-1].set_aspect(.75*Dx/Dy)
                
                #  8.4 Iterate plotnum counter
                ######################################################
                plotnum += 1

        #  9. Place yerr text in bottom right corner
        ##############################################################
        if aggregate != None:
            if aggregate == 'ci':
                aggregate = '95% ci' 
                
            pylab.xlabel('\n\n                '
                         '*Error bars reflect %s'\
                         %aggregate.upper())

        # 10. Save the figure
        ##############################################################
        if fname == None:
            fname = maintitle.lower() \
                             .replace('by', '~') \
                             .replace('*', 'X') \
                             .replace(' ', '')
            
        if quality == 'low' or fname.endswith('.svg'):
            pylab.savefig(fname)
            
        elif quality == 'medium':
            pylab.savefig(fname, dpi=200)
            
        elif quality == 'high':
            pylab.savefig(fname, dpi=300)
            
        else:
            pylab.savefig(fname)

        pylab.close()

        test['fname'] = fname

        # 11. return the test dictionary
        ##############################################################
        if self.TESTMODE:
            return test





##df=PyvtTbl()
##df.readTbl('error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
##df.printDescriptives('ERROR')
##df.printTable(where=[('ERROR','==',10.)])
##print(df.Z)

##from random import shuffle
##a=[0.0,1.,2.,3.,4.]
##b=range(1,11)*10
##
##print(a)
##
##df=PyvtTbl()
##for A,B in zip(a,b):
##    df.insert({'A':A, 'B':B})
##
##print(df['A'])
##
##df.sort(['A',])
##print(df['A'])

##from random import random
##df=PyvtTbl()
##conditionsDict=DictSet({'A':[10,20,40,80],
##                        'B':[100,800],
##                      'rep':range(100)})
##
##df.insert([('A',10),('B',100),('sum',1),('rep',1)])
##for A,B,rep in conditionsDict.unique_combinations():
##    s = A*random() + B*random()
##
##    df.insert([('A',A),('B',B),('sum',s),('rep',rep)])
##
##print(df.types)
##    
##df.printTable()
##df._xunique_combinationsot('sum',rows=['A'],cols=['B'])
####W[-1]=10000.
##
##
##_hist(x, bins=13, weights=W, cumulative=False, density=False)
##
##import pylab
##pylab.figure()
##(N, B, patches)=pylab.hist(x, bins=-13, weights=W, cumulative=False, normed=False)
##print(patches)
##for n,b in zip(N, B):
##    print(_str(b,'f',3),n)
##
##pylab.close()


##df.sort(['MODEL DESC', 'COURSE'])
##df.printTable()
##df['DUM']=range(48)
##df['DUM'].pop()
##
##df._execute('PRAGMA table_info(TBL)')
##for c in df.cur: print(c)

##self.df['DUM'].pop()
        
##'''
##select SUBJECT 
##  , COURSE
##  ,avg(case when TIMEOFDAY='T1' then ERROR end) 
##  ,avg(case when TIMEOFDAY='T2' then ERROR end) 
##from PVTTBL group by SUBJECT,COURSE
##'''
##



##pp(df.Pivot('ERROR',rows=['SUBJECT','TIMEOFDAY'],exclude={'SUBJECT':['1']}))
##

##    
##df=PyvtTbl()
##df.readTbl('suppression~subjectXgroupXageXcycleXphase.csv')
##
##
##df.printPivot('SUPPRESSION',['GROUP','AGE'],['CYCLE','PHASE'],
##              aggregate='count',
##              where=[('AGE','not in',['old']),
##                     ('PHASE','not in',['I'])])
##
##df.printTable(where=[('AGE','not in',['old']),
##                     ('PHASE','not in',['I'])])
##
##df.printDescriptives('SUPPRESSION')
##df.writePivot()

##
##pp(m)
##df.Plot('SUPPRESSION', xaxis='PHASE',
##        seplines='CYCLE',sepxplots='GROUP',yerr='sem')
##
##df['RECIP_SUPPRESSION']=.log10(df['SUPPRESSION']+.00001)
##
##print df.keys()
##df.PrintDescriptives('RECIP_SUPPRESSION')
##
##df.PrintMarginalMeans('RECIP_SUPPRESSION',factors=['GROUP','PHASE','CYCLE'])
##

##df._execute("select _SUPPRESSION_ from TBL where not _CYCLE_='1.' and not _CYCLE_='2.'")
##for row in df.cur:
##    print row
    
##
##for l in d:
##    print l
    
#,exclude={'SUBJECT':['1','2','3','4']}))
##df.Plot('SUPPRESSION', 'CYCLE')

##         exclude={'SUBJECT':['1']})
##
##import time
##
##t0=time.time()
##print('need to format data for spss... (this may take a few minutes)')
##
##fname='collaborated.csv'
##
##covariates='age,gender,dicho_correct,dicho_misses,dicho_FA,SAAT_noncomp_correct,'\
##           'SAAT_noncomp_incorrect,SAAT_comp_correct,SAAT_comp_incorrect'.split(',')
##
##within='speed,target_dir,agreement'.split(',')
##
##dvs='correct_decision_raw,decision_at_safe_distance_raw,decision_distance_raw,'\
##    'decision_latency_raw,decision_proportion_raw,decision_ttc_proportion_raw,'\
##    'decision_ttc_raw,detection_distance_raw,detection_latency_raw,'\
##    'detection_proportion_raw,detection_ttc_proportion_raw,detection_ttc_raw,'\
##    'position_distance_raw,position_latency_raw,risk_level_raw,trial_raw'.split(',')
##    
##df=DataFrame()
##df.ReadTbl(fname)
##df.Export4SPSS('participant',dvs=dvs,within=within,covariates=covariates,nested=False)
##
##print('\ndone.')
##print(time.time()-t0)
