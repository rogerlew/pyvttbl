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

import collections
import csv
import itertools
import inspect
import math
import sqlite3
import warnings

from pprint import pprint as pp
from copy import copy, deepcopy
from collections import OrderedDict, Counter

import pystaggrelite3
from dictset import DictSet
from texttable import Texttable as TextTable

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

def _isfloat(string):
    """
    returns true if string can be cast as a float,
    returns zero otherwise
    """
    try:
        float(string)
    except:
        return False
    return True

def _isint(string):
    """
    returns true if string can be cast as an int,
    returns zero otherwise
    """
    try:
        f = float(string)
    except:
        return False
    if round(f) - f == 0:
        return True
    return False

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
    """
    returns the unique combinations of items. the n parameter controls
    the number of elements in items to combine in each combination
    """
    if n == 0:
        yield []
    else:
        for i in _xrange(len(items)):
            for cc in _xunique_combinations(items[i+1:], n-1):
                yield [items[i]]+cc

def _str(x, dtype='a', n=3):
    """
    makes string formatting more human readable
    """
    try    : f=float(x)
    except : return str(x)
    
    if   dtype == 'i' : return str(int(round(f)))
    elif dtype == 'f' : return '%.*f'%(n, f)
    elif dtype == 'e' : return '%.*e'%(n, f)
    elif dtype == 't' : return str(x)
    else:
        if f-round(f) == 0:
            if abs(f) > 1e8:
                return '%.*e'%(n, f)
            else:
                return str(int(round(f)))
        else:
            if abs(f) > 1e8 or abs(f) < 1e-8:
                return '%.*e'%(n, f)
            else:
                return '%.*f'%(n, f)
            
# the dataframe class
class DataFrame(OrderedDict):
    """holds the data in a dummy-coded group format"""
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

        # controls whether plot functions return the test dictionaries
        self.TESTMODE = True

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

          the key should be a string (it will be converted to a string)
          if it is not supplied as one. The key must also not have white
          space and must not be a case variant of an existing key. These
          constraints are to avoid problems when placing data into
          sqlite3.

          The assigned item must be iterable. To add a single row use
          the insert method. To attach another table to this one use
          the attach method.
        """
        if not isinstance(key, collections.Hashable):
            raise TypeError("'%s' object is not hashable"%type(key).__name__)
        
        if not hasattr(item, '__iter__'):
            raise TypeError("'%s' object is not iterable"%type(item).__name__)

        old = None
        if isinstance(key, tuple):
            name_type = (str(key[0]),str(key[1]))
        else:
            # check to see if we need to do type checking after
            # the item is set
            key = str(key)

            if ''.join(key.split()) != key:
                raise Exception('keys cannot contain whitespace')
            
            if key in self.names():
                old = (key, self.typesdict()[key])
                
            name_type = (key, self._check_sqlite3_type(item))

        n = name_type[0]
        if isinstance(n, _strobj) and (n not in self.names()) and \
          (n.lower() in map(str.lower, self.names())):
            raise Exception("a case variant of '%s' already exists"%n)
            
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
            key = str(key)
            name_type = (key, self.typesdict()[key])
            
        del self.conditions[name_type]
        super(DataFrame, self).__delitem__(name_type)

    def __getitem__(self, key):
        """
        returns an item
        """
        if isinstance(key, tuple):
            name_type = key
        else:
            key = str(key)
            name_type = (key, self.typesdict()[key])
            
        return super(DataFrame, self).__getitem__(name_type)

    def __str__(self):
        """
        returns human friendly string representation of object
        """
        if self == {}:
            return '(table is empty)'
        
        tt = TextTable(max_width=100000000)
        dtypes = [t[0] for t in self.types()]
        dtypes = list(''.join(dtypes).replace('r', 'f'))
        tt.set_cols_dtype(dtypes)

        aligns = [('l','r')[dt in 'fi'] for dt in dtypes]
        tt.set_cols_align(aligns)

        if self.shape()[1] > 0:
            tt.add_rows(zip(*list(self.values())))
            
        tt.header(self.names())
        tt.set_deco(TextTable.HEADER)

        # output the table
        return tt.draw()
        
    def names(self):
        """
        returns a list of the column labels
        """
        if len(self) == 0:
            return tuple()
        
        return list(zip(*list(self.keys())))[0]

    def types(self):
        """
        returns a list of the sqlite3 datatypes of the columns 
        """
        if len(self) == 0:
            return tuple()
        
        return list(zip(*list(self.keys())))[1]

    def typesdict(self):
        """
        returns a lookup dictionary of names and datatypes
        """
        return OrderedDict(self.keys())

    def shape(self):
        """
        returns the size of the table as a tuple

          The first element is the number of columns.
          The second element is the number of rows
        """
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

    def _build_sqlite3_tbl(self, nsubset, where=None):
        """
        build or rebuild sqlite table with columns in nsubset based on
        the where list

          where can be a list of tuples. Each tuple should have three
          elements. The first should be a column key (label). The second
          should be an operator: in, =, !=, <, >. The third element
          should contain value for the operator.

          where can also be a list of strings. or a single string.
        """
        if where == None:
            where = []

        if isinstance(where, _strobj):
            where = [where]
            
        #  1. Perform some checkings
        ##############################################################
        if not hasattr(where, '__iter__'):
            raise TypeError( "'%s' object is not iterable"
                             % type(where).__name__)

        nsubset = map(str, nsubset)

        #  2. Figure out which columns need to go into the table
        #     to be able to filter the data
        ##############################################################           
        nsubset2 = set(nsubset)
        for item in where:
            if isinstance(item, _strobj):
                nsubset2.update(w for w in item.split() if w in self.names())
            else:
                if str(item[0]) in self.names():
                    nsubset2.add(str(item[0]))

        # orders nsubset2 to match the order in self.names()
        nsubset2 = [n for n in self.names() if n in nsubset2]

        print(nsubset2)
        
        #  3. Build a table
        ##############################################################
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

        #  4. If where == None then we are done. Otherwise we need
        #     to build query to filter the rows
        ##############################################################
        if where == []:
            self._execute('drop table if exists TBL')
            self.conn.commit()
            
            self._execute('alter table TBL2 rename to TBL')
            self.conn.commit()
        else:
            # Initialize another temparary table
            self._execute('drop table if exists TBL')
            self.conn.commit()
            
            query = []
            for n in nsubset:
                query.append('_%s_ %s'%(n, self.typesdict()[n]))
            query = ', '.join(query)
            query =  'create temp table TBL\n  (' + query + ')'
            self._execute(query)

            # build filter query
            query = []
            for item in where:
                # process item as a string
                if isinstance(item, _strobj):
                    tokens = []
                    for word in item.split():
                        if word in self.names():
                            tokens.append('_%s_'%word)
                        else:
                            tokens.append(word)
                    query.append(' '.join(tokens))

                # process item as a tuple
                else:
                    try:
                        (k,op,value) = item
                    except:
                        raise Exception('could not upack tuple from where')
                    
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

    def _get_sqlite3_tbl_info(self):
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
    
    def pivot(self, val, rows=None, cols=None, aggregate='avg',
              where=None, flatten=False, attach_rlabels=False):
        """
        instance method of DataFrame which returns a PyvtTbl object
        """

        if rows == None:
            rows = []
            
        if cols == None:
            cols = []
            
        if where == None:
            where = []

        return PyvtTbl(self, val, rows, cols, aggregate,
                       where, flatten, attach_rlabels)
    
    def select_col(self, val, where=None):
        """
        returns the a copy of the selected values based on the
        where parameter
        """
        if where == None:
            where = []

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

    def sort(self, order=None):
        """
        sort the table in-place

          order is a list of factors to sort by
          to reverse order append " desc" to the factor
        """
        if order == None:
            order = []

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
        attaches a second DataFrame to this DataFrame

          both DataFrames must have the same columns
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

          The row should be mappable. e.g. a dict or a list with
          key/value pairs. 
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

    def write(self, where=None, fname=None, delimiter=','):
        """
        write the contents of the DataFrame to a plaintext file
        """
        if where == None:
            where = []

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
            lnames = [str(n).lower().replace('1','') for n in self.names()]
            fname = 'X'.join(lnames)

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

    def descriptives(self, cname, where=None):
        """
        returns a dict of descriptive statistics for column cname
        """

        if where == None:
            where = []

        if self == {}:
            raise Exception('Table must have data to calculate descriptives')

        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        if cname not in self.names():
            raise KeyError(cname)
        
        V = self.select_col(cname, where=where)
        return Descriptives(V, cname)

    def summary(self, where=None):
        """
        prints a the Descriptives(cname) for each column in the DataFrame
        """
        for (cname,dtype) in self.keys():
            if dtype in ['real', 'integer']:
                print(self.descriptives(cname, where))
                print()

            else:
                print('%s contains non-numerical data\n'%cname)

    def marginals(self, val, factors, where=None):
        """
        returns a marginals object containg means, counts,
        standard errors, and confidence intervals for the
        marginal conditions of the factorial combinations
        sepcified in the factors list.
        """
        if where == None:
            where = []

        if self == {}:
            raise Exception('Table must have data to find marginals')

        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')
        
        return Marginals(self, val, factors, where)
        
    def histogram(self, cname, where=None, bins=10,
                  range=None, density=False, cumulative=False):
        """
        Returns Histogram object
        """
        if where == None:
            where = []
            
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



    # conditionally load plot methods
    if HAS_NUMPY and HAS_PYLAB:
        def histogram_plot(self, val, where=None, bins=10,
                      range=None, density=False, cumulative=False,
                      fname=None, quality='medium'):
            """
            Creates a histogram plot with the specified parameters
            """
            
            if where == None:
                where = []

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

        def box_plot(self, val, factors=None, where=None,
                fname=None, quality='medium'):
            """
            Creates a box plot with the specified parameters
            """

            if factors == None:
                factors = []

            if where == None:
                where = []

            # check to see if there is any data in the table
            if self == {}:
                raise Exception('Table must have data to print data')
            
            # check to see if data columns have equal lengths
            if not self._are_col_lengths_equal():
                raise Exception('columns have unequal lengths')

            # check the supplied arguments
            if val not in self.names():
                raise KeyError(val)

            if not hasattr(factors, '__iter__'):
                raise TypeError( "'%s' object is not iterable"
                                 % type(factors).__name__)
            
            for k in factors:
                if k not in self.names():
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
                D = self.pivot(val, rows=factors,
                               where=where,
                               aggregate='tolist')

                fig = pylab.figure(figsize=(6*len(factors),6))
                fig.subplots_adjust(left=.05, right=.97, bottom=0.24)
                pylab.boxplot([np.array(_flatten(d)) for d in D])
                xticks = pylab.xticks()[0]
                xlabels = ['\n'.join('%s = %s'%fc for fc in c) for c in D.rnames]
                pylab.xticks(xticks, xlabels,
                             rotation='vertical',
                             verticalalignment='top')

                test['d'] = [np.array(_flatten(d)) for d in D]
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

        def interaction_plot(self, val, xaxis, 
                        seplines=None, sepxplots=None, sepyplots=None,
                        xmin='AUTO', xmax='AUTO', ymin='AUTO', ymax='AUTO',
                        where=None, fname=None, quality='low', yerr=None):
            """
            Creates an interaction plot with the specified parameters
            """

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

            if where == None:
                where = []

            # check for data
            if self == {}:
                raise Exception('Table must have data to plot marginals')

            # check to see if data columns have equal lengths
            if not self._are_col_lengths_equal():
                raise Exception('columns have unequal lengths')

            # check to make sure arguments are column labels
            if val not in self.names():
                raise KeyError(val)

            if xaxis not in self.names():
                raise KeyError(xaxis)
            
            if seplines not in self.names() and seplines != None:
                raise KeyError(seplines)

            if sepxplots not in self.names() and sepxplots != None:
                raise KeyError(sepxplots)
            
            if sepyplots not in self.names() and sepyplots != None:
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
            cols = [f for f in [seplines, sepxplots, sepyplots] if f in self.names()]
            counts = self.pivot(val, rows=[xaxis], cols=cols,
                                flatten=True, where=where, aggregate='count')

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

            if any([math.isnan(ymin), math.isinf(ymin), math.isnan(ymax), math.isinf(ymax)]):
                raise Exception('calculated plot bounds nonsensical')

            test['ymin'] = ymin
            test['ymax'] = ymax

            #  5. Figure out how many subplots we need to make and the
            #     levels of those subplots
            ##############################################################      
            numrows = 1
            rlevels = [1]
            if sepyplots != None:
                rlevels = copy(counts.conditions[sepyplots]) # a set
                numrows = len(rlevels) # a int
                rlevels = sorted(rlevels) # set -> sorted list
                    
            numcols = 1
            clevels = [1]            
            if sepxplots != None:
                clevels = copy(counts.conditions[sepxplots])
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
                        y = self.pivot(val, cols=[xaxis], where=where,
                                       aggregate='avg', flatten=True)

                        if aggregate != None:
                            yerr = self.pivot(val, cols=[xaxis],
                                              where=where,
                                              aggregate=aggregate,
                                              flatten=True)
                        
                        x = [name for [(label, name)] in y.cnames]
                        
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
                            axs[-1].errorbar(_xrange(len(x)), y, yerr)
                            pylab.xticks(_xrange(len(x)), x)
                            xmin = - 0.5
                            xmax = len(x) - 0.5
                            
                            axs[-1].plot([xmin, xmax], [0., 0.], 'k:')

                    ########## If separate lines are specified ###########
                    else:
                        y = self.pivot(val, rows=[seplines], cols=[xaxis],
                                       where=where, aggregate='avg',
                                       flatten=False)
                        
                        if aggregate != None:
                            yerrs = self.pivot(val,
                                               rows=[seplines],
                                               cols=[xaxis],
                                               where=where,
                                               aggregate=aggregate,
                                               flatten=False)
                            
                        x = [name for [(label, name)] in y.cnames]

                        if _isfloat(yerr):
                            yerr = np.array([yerr for a in x])

                        plots = []
                        labels = []
                        for i, name in enumerate(y.rnames):
                            if aggregate != None:
                                yerr = yerrs[i]
                            
                            labels.append(name[0][1])

                            if all([_isfloat(a) for a in x]):
                                plots.append(
                                    axs[-1].errorbar(x, y[i], yerr)[0])
                                
                                if xmin == 'AUTO' and xmax == 'AUTO':
                                    xmin , xmax = axs[-1].get_xlim()
                                    xran = xmax - xmin
                                    xmin = xmin - .05*xran
                                    xmax = xmax + .05*xran
                                    
                                axs[-1].plot([xmin, xmax], [0.,0.], 'k:')
                                
                            else : # categorical x axis
                                plots.append(
                                    axs[-1].errorbar(
                                        _xrange(len(x)), y[i],yerr)[0])
                                
                                pylab.xticks(_xrange(len(x)), x)
                                xmin = - 0.5
                                xmax = len(x) - 0.5
                                
                                axs[-1].plot([xmin, xmax], [0., 0.], 'k:')

                        pylab.figlegend(plots, labels, loc=1,
                                        labelsep=.005,
                                        handlelen=.01,
                                        handletextsep=.005)

                    test['y'].append(y)
                    if yerr == None:
                        test['yerr'].append([])
                    else:
                        test['yerr'].append(yerr)
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


class PyvtTbl(list):
    """
    list of lists container holding the pivoted data
    """
    def __init__(self, df=None, val=None, rows=None, cols=None,
                 aggregate='avg', where=None, flatten=False,
                 attach_rlabels=False):
        
        # public method, saves table to df variables after pivoting
        """
        val = the colname to place as the data in the table
        rows = list of colnames whos combinations will become rows
               in the table if left blank their will be one row
        cols = list of colnames whos combinations will become cols
               in the table if left blank their will be one col
        aggregate = function applied across data going into each cell
                  of the table
                  http://www.sqlite.org/lang_aggfunc.html
        where = list of tuples or list of strings for filtering data
        """
        if df == None or df == {}:
            self.df=None
            self.val=None
            self.rows=None
            self.cols=None
            self.aggregate='avg'
            self.where=None
            self.flatten=False
            self.attach_rlabels=False

            self.rnames = [1]
            self.cnames = [1]
            self.Conditions = DictSet()
            
            super(PyvtTbl, self).__init__()

            return
            
        if rows == None:
            rows = []
            
        if cols == None:
            cols = []
            
        if where == None:
            where = []
            

        ##############################################################
        # pivot programmatic flow                                    #
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

        if df == None:
            df = DataFrame()
            
        if rows == None:
            rows = []
            
        if cols == None:
            cols = []
            
        if where == None:
            where = []
                
        # check to see if data columns have equal lengths
        if not df._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        # check the supplied arguments
        if val not in df.names():
            raise KeyError(val)

        if not hasattr(rows, '__iter__'):
            raise TypeError( "'%s' object is not iterable"
                             % type(cols).__name__)

        if not hasattr(cols, '__iter__'):
            raise TypeError( "'%s' object is not iterable"
                             % type(cols).__name__)
        
        for k in rows:
            if k not in df.names():
                raise KeyError(k)
            
        for k in cols:
            if k not in df.names():
                raise KeyError(k)

        # check for duplicate names
        dup = Counter([val] + rows + cols)
        del dup[None]
        if not all(count == 1 for count in dup.values()):
            raise Exception('duplicate labels specified')

        # check aggregate function
        aggregate = aggregate.lower()

        if aggregate not in df.aggregates:
            raise ValueError("supplied aggregate '%s' is not valid"%aggregate)
        
        # check to make sure where is properly formatted
        # todo
        
        #  2. Create a sqlite table with only the data in columns
        #     specified by val, rows, and cols. Also eliminate
        #     rows that meet the exclude conditions      
        ##############################################################
        df._build_sqlite3_tbl([val] + rows + cols, where)
        
        #  3. Build rnames and cnames lists
        ##############################################################
        
        # Refresh conditions list so we can build row and col list
        df._execute('select %s from TBL'
                      %', '.join('_%s_'%n for n in [val] + rows + cols))
        Zconditions = DictSet(zip([val]+rows+cols, zip(*list(df.cur))))
                
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
        df._execute(''.join(query))

        #  6. Read data to from cursor into a list of lists
        ##############################################################

        d = []
        val_type = df.typesdict()[val]

        # keep the columns with the row labels
        if attach_rlabels:
            if aggregate == 'tolist':
                for row in df.cur:
                    d.append([])
                    for cell in list(row):
                        if val_type == 'real' or val_type == 'integer':
                            d[-1].append(eval('[%s]'%cell))
                        else:
                            d[-1].append(cell.split(','))
            else:
                for row in df.cur:
                    d.append(list(row))

            cnames = [(r, '') for r in rows].extend(cnames)
                    
        # eliminate the columns with row labels
        else:
            if aggregate == 'tolist':
                for row in df.cur:
                    d.append([])
                    for cell in list(row)[-len(cnames):]:
                        if val_type == 'real' or val_type == 'integer':
                            d[-1].append(eval('[%s]'%cell))
                        else:
                            d[-1].append(cell.split(','))
            else:
                for row in df.cur:
                    d.append(list(row)[-len(cnames):])

        #  7. Clean up
        ##############################################################
        df.conn.commit()

        #  8. flatten if specified
        ##############################################################
        if flatten:
            d = _flatten(d)

        #  9. return data, rnames, and cnames
        ##############################################################
        self.df = df
        self.val = val
        self.rows = rows
        self.cols = cols
        self.aggregate = aggregate
        self.where = where
        self.flatten = flatten
        self.attach_rlabels = attach_rlabels

        self.rnames = rnames 
        self.cnames = cnames
        self.aggregate = aggregate
        self.conditions = Zconditions

        super(PyvtTbl, self).__init__(d)

    def _get_rows(self):
        """
        returns a list of tuples containing row labels and conditions
        """
        if self.rnames == [1]:
            return [1]
        else:
            return [str(k) for (k, v) in self.rnames[0]]

    def _get_cols(self):
        """
        returns a list of tuples containing column labels and conditions
        """
        if self.cnames == [1]:
            return [1]
        else:
            return [str(k) for (k, v) in self.cnames[0]]
        
    def __repr__(self):
        """
        returns a machine friendly string representation of the object
        """ 
        rows = self._get_rows()
        cols = self._get_cols()
        
        rlabel = self.attach_rlabels
        return 'PyvtTbl(' + ''.join([
            ('df=%s'%repr(self.df), '')[self.df == None],
            (',val=%s'%repr(self.val), '')[self.val == None],
            (',rows=%s'%repr(rows), '')[rows == [1]],
            (',cols=%s'%repr(cols), '')[cols == [1]],
            (',aggregate=%s'%self.aggregate, '')[self.aggregate == 'avg'],
            (',where=%s'%repr(self.where), '')[self.where == None],
            (',flatten=%s'%self.flatten, '')[self.flatten == False],
            (',attach_rlabels=%s'%rlabel, '')[rlabel == False] ]) + ')'   
            
    def __str__(self):
        """
        returns a human friendly string representaiton of the table
        """

        if self == []:
            return '(table is empty)'

        rows = self._get_rows()
        cols = self._get_cols()

        # build first line
        first = '%s(%s)'%(self.aggregate, self.val)
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
        """
        writes the pivot table to a plaintext file
        """
        
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

			
class Descriptives(OrderedDict):
    def __init__(self, V=None, cname=None):
        """
        generates and stores descriptive statistics for the
        numerical data in V
        """
        
        try:
            V = sorted(_flatten(list(V)))
        except:
            raise TypeError('V must be a list-like object')
            
        super(Descriptives, self).__init__()

        if cname == None:
            self.cname = ''
        else:
            self.cname = cname
            
        self.V = V

        N = float(len(V))

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
        self['mode'] = Counter(V).most_common()[0][0]
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

			
class Histogram(OrderedDict):
    def __init__(self, V=None, cname=None, bins=10,
                 range=None, density=False, cumulative=False):   
        """
        generates and stores histogram data for numerical data in V
        """
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
        return 'Histogram(' + ''.join([
            (',V=%s'%%repr(self.V), '')[self.V == None],
            (',cname=%s'%repr(self.cname), '')[self.cname == None],
            (',bins=%i'%self.bins, '')[self.bins == 10],
            (',range=%s'%repr(self.range), '')[self.range == None],
            (',density=%s'%self.density, '')[self.density == False],
            (',cumulative=%s'%self.cumulative, '')[self.cumulative == False]
                                       ]) + ')'

class Marginals(OrderedDict):
    def __init__(self, df=None, val=None, factors=None, where=None):   
        """
        generates and stores marginal data from the DataFrame df
        and column labels in factors.
        """

        if where == None:
            where = []
        
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

        self.df = df
        self.val = val
        self.factors = factors
        self.where = where
        
    def __str__(self):
        """Returns human readable string representaition of Marginals"""

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

    def __repr__(self):
        return 'Marginals(' + ''.join([
            ('df=%s'%repr(self.df), '')[self.df == None],
            (',val=%5'%self.val, '')[self.val == None],
            (',factors=%s'%repr(self.factors), '')[self.factors == None],
            (',where=%s'%repr(self.where), '')[self.where == False] ]) + ')'
