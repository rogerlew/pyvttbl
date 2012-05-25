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
from collections import OrderedDict, Counter, namedtuple

import pylab
import scipy
import numpy as np

import pystaggrelite3
from dictset import DictSet

import stats
from stats.qsturng import qsturng, psturng
from misc.texttable import Texttable as TextTable
from misc.support import *
import plotting

# base.py holds DataFrame and Pyvttbl
# this file is a bit long but they can't be split without
# running into circular import complications

# the dataframe class
class DataFrame(OrderedDict):
    """holds the data in a dummy-coded group format"""
    def __init__(self, *args, **kwds):
        """
        initialize a DataFrame object

          keep in mind that because this class uses sqlite3
          behind the scenes the keys are case-insensitive
        """
        super(DataFrame, self).__init__()
        
        # Initialize sqlite3
        self.conn = sqlite3.connect(':memory:')
        self.cur = self.conn.cursor()
        self.aggregates = tuple('avg count count group_concat '  \
                                'group_concat max min sum total tolist' \
                                .split())

        # Bind pystaggrelite3 aggregators to sqlite3
        for n, a, f in pystaggrelite3.getaggregators():
            self.bind_aggregate(n, a, f)

        # holds the factors conditions (and all the data values)
        # maybe this should be built on the fly for necessary
        # columns only?
        self.conditions = DictSet([(n, self[n]) for n in self.names()]) 

        # prints the sqlite3 queries to stdout before
        # executing them for debugging purposes
        self.PRINTQUERIES = False

        # controls whether plot functions return the test dictionaries
        self.TESTMODE = False

        super(DataFrame, self).update(*args, **kwds)

    def bind_aggregate(self, name, arity, func):
        self.conn.create_aggregate(name, arity, func)
        
        self.aggregates = list(self.aggregates)
        self.aggregates.append(name)
        self.aggregates = tuple(self.aggregates)

    def read_tbl(self, fname, skip=0, delimiter=',',labels=True):
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
                    colname = colname.strip().replace(' ','_')
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
                        colname = colname.strip().replace(' ','_')
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
        self.conditions = DictSet([(n,self[n]) for n in self.names()])

    def __contains__(self, key):
        return key in self.names()
        
    def __setitem__(self, key, item):
        """
        assign a column in the table

          the key should be a string (it will be converted to a string)
          if it is not supplied as one. The key must also not have white
          space and must not be a case variant of an existing key. These
          constraints are to avoid problems when placing data into
          sqlite3.

          The assigned item must be iterable. To add a single row use
          the insert method. To  another table to this one use
          the attach method.
        """
        # check item
        if not hasattr(item, '__iter__'):
            raise TypeError("'%s' object is not iterable"%type(item).__name__)

        # tuple, no where conditions to handle
        if isinstance(key, tuple):
            name, dtype = key
            if name.lower() in map(str.lower, self.names()) and \
               name not in self.names():
                raise Exception("a case variant of '%s' already exists"%name)
            if name in self.names() and dtype != self.typesdict()[name]:
                del self[name]
            super(DataFrame, self).__setitem__((name, dtype), item)
            self.conditions[name] = self[key]
            return

        # string, no where conditions to handle
        split_key = str(key).split()
        name = split_key[0]
        if len(split_key) == 1:
            dtype = self._check_sqlite3_type(item)
            if name.lower() in map(str.lower, self.names()) and \
               name not in self.names():
                raise Exception("a case variant of '%s' already exists"%name)
            if name in self.names():
                del self[name]
            super(DataFrame, self).__setitem__((name, dtype), item)
            self.conditions[name] = self[key]
            return

        # string, with where conditions to handle    
        if name not in self.names():
            raise KeyError(name)
        self._get_indices_where(split_key[1:])

        indices = [tup[0] for tup in list(self.cur)]

        if len(indices) != len(item):
            raise Exception('Length of items must length '
                            'of conditions in selection')
        for i,v in zip(indices, item):
            self[name][i] = v
        self.conditions[name] = self[key]

    def __getitem__(self, key):
        """
        returns an item
        """
        if isinstance(key, tuple):
            name_type = key
            return super(DataFrame, self).__getitem__(name_type)
        
        split_key = str(key).split()
        if len(split_key) == 1:
            name_type = (split_key[0], self.typesdict()[split_key[0]])
            return super(DataFrame, self).__getitem__(name_type)

        if split_key[0] not in self.names():
            raise KeyError(split_key[0])

        self._get_indices_where(split_key[1:])

        return [self[split_key[0]][tup[0]] for tup in self.cur]

    def __delitem__(self, key):
        """
        delete a column from the table
        """
        if isinstance(key, tuple):
            name_type = key
        else:
            key = str(key)
            name_type = (key, self.typesdict()[key])
            
        del self.conditions[key]
        super(DataFrame, self).__delitem__(name_type)
        
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
        
        tt.header(self.names())
        if self.shape()[1] > 0:
            tt.add_rows(zip(*list(self.values())), header=False)
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

    def _get_indices_where(self, where):
        # where should be a split string. No sense splitting it twice
        
        # preprocess where
        tokens = []
        nsubset2 = set()
        names = self.names()
        for w in where:
            if w in names:
                tokens.append('_%s_'%w)
                nsubset2.add(w)
            else:
                tokens.append(w)
        where = ' '.join(tokens)

        super(DataFrame, self).__setitem__(('INDICES','integer'),
                                         range(self.shape()[1]))
                                         
        nsubset2.add('INDICES')

        # build the table
        self.conn.commit()
        self._execute('drop table if exists GTBL')

        self.conn.commit()
        query =  'create temp table GTBL\n  ('
        query += ', '.join('_%s_ %s'%(n, self.typesdict()[n]) for n in nsubset2)
        query += ')'
        self._execute(query)

        # build insert query
        query = 'insert into GTBL values ('
        query += ','.join('?' for n in nsubset2) + ')'
        self._executemany(query, zip(*[self[n] for n in nsubset2]))
        self.conn.commit()

        super(DataFrame, self).__delitem__(('INDICES','integer'))

        # get the indices
        query = 'select _INDICES_ from GTBL %s'%where
        self._execute(query)
        

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
            # Initialize another temporary table
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
        returns a PyvtTbl object
        """

        if rows == None:
            rows = []
            
        if cols == None:
            cols = []
            
        if where == None:
            where = []

        p = PyvtTbl()
        p.run(self, val, rows, cols, aggregate,
                       where, flatten, attach_rlabels)
        return p
        
    
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
        Applies the where filter in-place.
        """
        self._build_sqlite3_tbl(self.names(), where)
        self._execute('select * from TBL')
        for n, values in zip(self.names(), zip(*list(self.cur))):
            del self[n]
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
        self.conditions = DictSet([(n, self[n]) for n in self.names()])

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
        d = stats.Descriptives()
        d.run(V, cname)
        return d

    def summary(self, where=None):
        """
        prints a the (cname) for each column in the DataFrame
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
        
        m = stats.Marginals()
        m.run(self, val, factors, where)
        return m

    def anova1way(self, val, factor, posthoc='tukey', where=None):
        """
        returns an ANOVA1way object containing the results of a
        one-way analysis of variance on val over the conditions
        in factor. The conditions do not necessarily need to have
        equal numbers of samples.
        """
        if where == None:
            where = []

        if self == {}:
            raise Exception('Table must have data to find marginals')

        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        # build list of lists for ANOVA1way object
        list_of_lists = []
        pt = self.pivot(val,rows=[factor],
                        aggregate='tolist',
                        where=where)
        for L in pt:
            list_of_lists.append(L[0])

        # build list of condiitons
        conditions_list = [tup[1] for [tup] in pt.rnames]

        a = stats.Anova1way()
        a.run(list_of_lists, val, factor, conditions_list, posthoc=posthoc)
        return a
    
    def chisquare1way(self, observed, expected_dict=None,
                      alpha=0.05, where=None):
        """
        Returns a ChiSquare1way object containing the results of a
        chi-square goodness-of-fit test on the data in observed. The data
        in the observed column are treated a categorical. Expected counts
        can be given with the expected_dict. It should be a dictionary
        object with keys matching the categories in observed and values
        with the expected counts. The categories in the observed column
        must be a subset of the keys in the expected_dict. If
        expected_dict is None,the total N is assumed to be equally
        distributed across all groups.
        """
        # ched the expected_dict
        if expected_dict != None:
            try:
                expected_dict2 = dict(copy(expected_dict))
            except:
                raise TypeError("'%s' is not a mappable type"
                                %type(expected_dict).__name__())

            if not self.conditions[observed] <= set(expected_dict2.keys()):
                raise Exception('expected_dict must contain a superset of  '
                                'of the observed categories')
        else:
            expected_dict2 = Counter()

        # find the counts
        observed_dict=Counter(self.select_col(observed, where))

        # build arguments for ChiSquare1way
        observed_list = []
        expected_list = []
        conditions_list = sorted(set(observed_dict.keys()) |
                                 set(expected_dict2.keys()))
        for key in conditions_list:
            observed_list.append(observed_dict[key])
            expected_list.append(expected_dict2[key])

        if expected_dict == None:
            expected_list = None

        # run analysis
        x = stats.ChiSquare1way()
        x.run(observed_list, expected_list, conditions_list=conditions_list,
              measure=observed, alpha=alpha)

        return x

    def chisquare2way(self, rfactor, cfactor, alpha=0.05, where=None):
        row_factor = self.select_col(rfactor, where)
        col_factor = self.select_col(cfactor, where)

        x2= stats.ChiSquare2way()
        x2.run(row_factor, col_factor, alpha=alpha)
        return x2


    def correlation(self, variables, coefficient='pearson',
                    alpha=0.05, where=None):
        """
        calculates a correlation matrix between the measures
        in the the variables parameter. The correlation
        coefficient can be set to pearson, spearman,
        kendalltau, or pointbiserial.
        """
        list_of_lists = []
        for var in sorted(variables):
            list_of_lists.append(self.select_col(var, where))

        cor= stats.Correlation()
        cor.run(list_of_lists, sorted(variables),
                coefficient=coefficient, alpha=alpha)
        return cor
                
    def ttest(self, aname, bname=None, pop_mean=0., paired=False,
              equal_variance=True, where=None):
        """
        If bname is not specified a one-way t-test is performed on
        comparing the values in column aname with a hypothesized
        population mean of 0. The hypothesized population mean can
        be specified through the pop_mean parameter.

        If bname is provided the values in aname and bname are
        compared. When paired is True. A matched pairs t-test is
        performed and the equal_variance parameter is ignored.

        When paired is false the samples in aname and bname are
        treated as independent.
        """
        if where == None:
            where = []

        if self == {}:
            raise Exception('Table must have data to find marginals')

        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')
        
        adata = self.select_col(aname, where=where)
        if bname != None:
            bdata = self.select_col(bname, where=where)
        else:
            bdata = None
        
        t = stats.Ttest()
        t.run(adata, bdata, pop_mean=pop_mean,
              paired=paired, equal_variance=equal_variance,
              aname=aname, bname=bname)
        return t
        
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
        h = stats.Histogram()
        h.run(V, cname=cname, bins=bins, range=range,
              density=density, cumulative=cumulative)
        return h

    def anova(self, dv, sub='SUBJECT', wfactors=None, bfactors=None,
              measure='', transform='', alpha=0.05):
        aov=stats.Anova()
        aov.run(self, dv, sub=sub, wfactors=wfactors, bfactors=bfactors,
                measure=measure, transform=transform, alpha=alpha)
        return aov
        
    def histogram_plot(self, val, **kwargs):
        return plotting.histogram_plot(self, val, **kwargs)

    histogram_plot.__doc__ = plotting.histogram_plot.__doc__
    
    def scatter_plot(self, aname, bname, **kwargs):
        return plotting.scatter_plot(self, aname, bname, **kwargs)

    scatter_plot.__doc__ = plotting.scatter_plot.__doc__

    def box_plot(self, val, factors=None, **kwargs):
        return plotting.box_plot(self, val, factors=factors, **kwargs)

    box_plot.__doc__ = plotting.box_plot.__doc__

    def interaction_plot(self, val, xaxis, **kwargs):
        return plotting.interaction_plot(self, val, xaxis, **kwargs)

    interaction_plot.__doc__ = plotting.interaction_plot.__doc__
    
    def scatter_matrix(self, variables, **kwargs):
        return plotting.scatter_matrix(self, variables, **kwargs)

    scatter_matrix.__doc__ = plotting.scatter_matrix.__doc__
        
class PyvtTbl(list):
    """
    list of lists container holding the pivoted data
    """
    def __init__(self, *args, **kwds):
        if len(args) > 1:
            raise Exception('expecting only 1 argument')

        if kwds.has_key('val'):
            self.val = kwds['val']
        else:
            self.val = None

        if kwds.has_key('show_tots'):
            self.show_tots = kwds['show_tots']
        else:
            self.show_tots = True

        if kwds.has_key('calc_tots'):
            self.calc_tots = kwds['calc_tots']
        else:
            self.calc_tots = True
            
        if kwds.has_key('row_tots'):
            self.row_tots = kwds['row_tots']
        else:
            self.row_tots = None
                
        if kwds.has_key('col_tots'):
            self.col_tots = kwds['col_tots']
        else:
            self.col_tots = None
            
        if kwds.has_key('grand_tot'):
            self.grand_tot = kwds['grand_tot']
        else:
            self.grand_tot = None
            
        if kwds.has_key('rnames'):
            self.rnames = kwds['rnames']
        else:
            self.rnames = None

        if kwds.has_key('cnames'):
            self.cnames = kwds['cnames']
        else:
            self.cnames = None

        if kwds.has_key('aggregate'):
            self.aggregate = kwds['aggregate']
        else:
            self.aggregate = 'avg'
            
        if kwds.has_key('flatten'):
            self.flatten = kwds['flatten']
        else:
            self.flatten = False
            
        if kwds.has_key('where'):
            self.where = kwds['where']
        else:
            self.where = []

        if kwds.has_key('attach_rlabels'):
            self.attach_rlabels = kwds['attach_rlabels']
        else:
            self.attach_rlabels = False

        if len(args) == 1:
            super(PyvtTbl, self).__init__(args[0])
        else:
            super(PyvtTbl, self).__init__()
            
    def run(self, df, val, rows=None, cols=None,
                 aggregate='avg', where=None, flatten=False,
                 attach_rlabels=False, calc_tots=True):
        
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
            
        if rows == None:
            rows = []
            
        if cols == None:
            cols = []
            
        if where == None:
            where = []
            
        ##############################################################
        # pivot programmatic flow                                    #
        ##############################################################
        #  1.  Check to make sure the table can be pivoted with the  #
        #      specified parameters                                  #
        #  2.  Create a sqlite table with only the data in columns   #
        #      specified by val, rows, and cols. Also eliminate      #
        #      rows that meet the exclude conditions                 #
        #  3.  Build rnames and cnames lists                         #
        #  4.  Build query based on val, rows, and cols              #
        #  5.  Run query                                             #
        #  6.  Read data to from cursor into a list of lists         #
        #  7.  Query grand, row, and column totals                   #
        #  8.  Clean up                                              #
        #  9.  flatten if specified                                  #
        #  10. return data, rnames, and cnames                       #
        ##############################################################

        #  1. Check to make sure the table can be pivoted with the
        #     specified parameters
        ##############################################################
        #  This may seem excessive but it provides better feedback
        #  to the user if the errors can be parsed out before had
        #  instead of crashing on confusing looking code segments
            
                
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
            rnames = []

            conditions_set = set(zip(*[df[n] for n in rows]))
            for vals in Zconditions.unique_combinations(rows):
                if tuple(vals) in conditions_set:
                    rnames.append(zip(rows,vals))
        
        # Build cnames
        if cols == []:
            cnames = [1]
        else:
            cnames = []

            conditions_set = set(zip(*[df[n] for n in cols]))
            for vals in Zconditions.unique_combinations(cols):
                if tuple(vals) in conditions_set:
                    cnames.append(zip(cols,vals))
        
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
                query.append(', '.join('_%s_'%r for r in rows))

            if cnames == [1]:
                query.append('\n  , %s( _%s_ )'%(agg, val))
            else:
                for cs in cnames:
                    query.append('\n  , %s( case when '%agg)
                    if all(map(_isfloat, zip(*cols)[1])):
                        query.append(
                        ' and '.join(('_%s_=%s'%(k, v) for k, v in cs)))
                    else:
                        query.append(
                        ' and '.join(('_%s_="%s"'%(k ,v) for k, v in cs)))
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

        #  6. Read data from cursor into a list of lists
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

        #  7. Get totals
        ##############################################################
        if calc_tots:
            if aggregate in ['tolist', 'group_concat', 'arbitrary']:
                self.calc_tots = False
            else:
                query = 'select %s( _%s_ ) from TBL'%(agg, val)
                df._execute(query)
                self.grand_tot = list(df.cur)[0][0]

                if cnames != [1] and rnames != [1]:
                    query = ['select %s( _%s_ ) from TBL group by'%(agg, val)]
                    query.append(', '.join('_%s_'%r for r in rows))
                    df._execute(' '.join(query))
                    self.row_tots = [tup[0] for tup in df.cur]
                    
                    query = ['select %s( _%s_ ) from TBL group by'%(agg, val)]
                    query.append(', '.join('_%s_'%r for r in cols))
                    df._execute(' '.join(query))
                    self.col_tots = [tup[0] for tup in df.cur]                
        
        #  8. Clean up
        ##############################################################
        df.conn.commit()

        #  9. flatten if specified
        ##############################################################
        if flatten:
            d = _flatten(d)

        #  10. set data, rnames, and cnames
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

    def transpose(self):
        """
        tranpose the pivot table in place
        """
        super(PyvtTbl,self).__init__([list(r) for r in zip(*self)])
        self.rnames,self.cnames = self.cnames,self.rnames
        self.row_tots,self.col_tots = self.col_tots,self.row_tots

    def _are_row_lengths_equal(self):
        """
        private method to check if the lists in self have equal lengths

          returns True if all the items are equal
          returns False otherwise
        """
        # if self is not empty
        counts = map(len, self.__iter__())
        if all(c - counts[0] + 1 == 1 for c in counts):
            return True
        else:
            return False
        
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

    def shape(self):
        """
        returns the size of the pivot table as a tuple. Does not
        include row label columns.

          The first element is the number of columns.
          The second element is the number of rows
        """
        if len(self) == 0:
            return (0, 0)
        
        return (len(self.rnames), len(self[0]))

    def write(self, fname=None, delimiter=','):
        """
        writes the pivot table to a plaintext file

          as currently implemented does not write grandtotals
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
        first = ['%s(%s)'%(self.aggregate, self.val)]

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

    def to_dataframe(self):
        """
        returns a DataFrame excluding row and column totals
        """
        # import goes here to avoid circular imports
        if self == []:
            return DataFrame()

        if self.flatten:
            raise NotImplementedError(
                'Pyvttbl.to_dataframe() cannot handle flatten tables.')

        rows = self._get_rows()
        cols = self._get_cols()

        # initialize DataFrame
        df = DataFrame()
        
        # no rows or cols were specified
        if self.rnames == [1] and self.cnames == [1]:
            # build the header
            header = ['Value']
            
        elif self.rnames == [1]: # no rows were specified
            # build the header
            header = ['__'.join('%s=%s'%(f, c) for (f, c) in L) \
                      for L in self.cnames]
            
            df.insert(zip(header, self[0]))
            
        elif self.cnames == [1]: # no cols were specified
            # build the header
            header = rows + ['Value']
            
            for i, L in enumerate(self.rnames):
                df.insert(zip(header, [c for (f, c) in L] + self[i]))
            
        else: # table has rows and cols
            # build the header
            header = copy(rows)
            for L in self.cnames:
                header.append('__'.join('%s=%s'%(f, c) for (f, c) in L))
            
            for i, L in enumerate(self.rnames):
                df.insert(zip(header, [c for (f, c) in L] + self[i]))

        return df
    
    def __str__(self):
        """
        returns a human friendly string representation of the table
        """        
        if self == []:
            return '(table is empty)'

        if self.flatten:
            return super(PyvtTbl, self).__str__()

        showtots = self.show_tots and self.calc_tots

        rows = self._get_rows()
        cols = self._get_cols()

        # initialize table
        tt = TextTable(max_width=0)

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
            if showtots:
                header.append('Total')
            
            # initialize the texttable and add stuff
            # False and True evaluate as 0 and 1 for integer addition
            # and list indexing
            tt.set_cols_dtype(['a'] * (len(self.cnames)+showtots))
            tt.set_cols_align(['r'] * (len(self.cnames)+showtots))
            tt.add_row(self[0]+([],[self.grand_tot])[showtots])
            
        elif self.cnames == [1]: # no cols were specified
            # build the header
            header = rows + ['Value']
            
            # initialize the texttable and add stuff
            tt.set_cols_dtype(['t'] * len(rows) + ['a'])
            tt.set_cols_align(['l'] * len(rows) + ['r'])
            for i, L in enumerate(self.rnames):
                tt.add_row([c for (f, c) in L] + self[i])

            if showtots:
                tt.footer(['Total'] + 
                          ['']*(len(rows)-1) +
                          [self.grand_tot])
            
        else: # table has rows and cols
            # build the header
            header = copy(rows)
            for L in self.cnames:
                header.append(',\n'.join('%s=%s'%(f, c) for (f, c) in L))
            if showtots:
                header.append('Total')

            dtypes = ['t'] * len(rows) + ['a'] * (len(self.cnames)+showtots)
            aligns = ['l'] * len(rows) + ['r'] * (len(self.cnames)+showtots)

            # initialize the texttable and add stuff
            tt.set_cols_dtype(dtypes)
            tt.set_cols_align(aligns)
            for i, L in enumerate(self.rnames):
                tt.add_row([c for (f, c) in L] +
                           self[i] +
                           ([],[self.row_tots[i]])[showtots])

            if showtots:
                tt.footer(['Total'] + 
                          ['']*(len(rows)-1) +
                          self.col_tots +
                          [self.grand_tot])

        # add header and decoration
        tt.header(header)
        tt.set_deco(TextTable.HEADER | TextTable.FOOTER)

        # return the formatted table
        return '%s(%s)\n%s'%(self.aggregate, self.val, tt.draw())

    def __repr__(self):
        """
        returns a machine friendly string representation of the object
        """
        if self == []:
            return 'PyvtTbl()'

        args = super(PyvtTbl, self).__repr__()
        kwds = []
        if self.val != None:
            kwds.append(", val='%s'"%self.val)

        if self.show_tots != True:
            kwds.append(", show_tots=False")

        if self.calc_tots != True:
            kwds.append(", calc_tots=False")

        if self.row_tots != None:
            kwds.append(', row_tots=%s'%repr(self.row_tots))
                
        if self.col_tots != None:
            kwds.append(', col_tots=%s'%repr(self.col_tots))
            
        if self.grand_tot != None:
            kwds.append(', grand_tot=%s'%repr(self.grand_tot))
            
        if self.rnames != None:
            kwds.append(', rnames=%s'%repr(self.rnames))

        if self.cnames != None:
            kwds.append(', cnames=%s'%repr(self.cnames))

        if self.aggregate != 'avg':
            kwds.append(", aggregate='%s'"%self.aggregate)
            
        if self.flatten != False:
            kwds.append(', flatten=%s'%self.flatten)
            
        if self.where != []:
            if isinstance(self.where, _strobj):
                kwds.append(", where='%s'"%self.where)
            else:
                kwds.append(", where=%s"%self.where)

        if self.attach_rlabels != False:
            kwds.append(', attach_rlabels=%s'%self.attach_rlabels)

        if len(kwds)>1:
            kwds = ''.join(kwds)
            
        return 'PyvtTbl(%s%s)'%(args,kwds)
