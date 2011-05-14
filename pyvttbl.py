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

import anydbm
import csv
import math
import sqlite3
import warnings

from math import isnan, isinf
from pprint import pprint as pp
from copy import copy, deepcopy
from collections import OrderedDict, Counter

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

def _transpose(lists, defval=''):
    """
    http://code.activestate.com/recipes/
    410687-transposing-a-list-of-lists-with-different-lengths/

    >>> a=[[1,2,3],[4,5,6,7]]
    [[1, 4], [2, 5], [3, 6], ['', 7]]

    """
    if not lists:
        return []
    return map(lambda *row: [elem or defval for elem in row], *lists)

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
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(_flatten(el))
        else:
            result.append(el)
    return result

def _xuniqueCombinations(items, n):
    if n == 0:
        yield []
    else:
        for i in _xrange(len(items)):
            for cc in _xuniqueCombinations(items[i+1:], n-1):
                yield [items[i]]+cc


                
# the dataframe class
class PyvtTbl(dict):                            
    def __init__(self):

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
        self.Zexclude = DictSet()

        # prints the sqlite3 queries to standard out before
        # executing them for debuggin purposes
        self.PRINTQUERIES = False 

        # When true the plotting methods return a dict that
        # is validated with unit testing
        self.TESTMODE = False    
        
    def readTbl(self, fname, skip=0, delimiter=',',labels=True):
        """
        Loads tabulated data from a plain text file

        Checks and renames duplicate column labels as well as checking
        for missing cells. readTbl will warn and skip over missing lines.
        """
        self.fname = fname
        
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
        self.typesdict = dict(((n, t) for n, t in zip(self.names, self.types)))
        self.conditions = DictSet(self)
        self.N = len(self.names)
        self.M = len(self.values()[0])

    def __setitem__(self, key, item):
        try:
            item = list(item)
        except:
            raise TypeError("'%s' object is not iterable"%type(item).__name__)

        super(PyvtTbl, self).__setitem__(key, item)

        # set state variables
        self.names.append(key)
        self.types.append(self._checktype(key))
        self.typesdict[key] = self.types[-1]
        self.conditions[key] = self[key]
        self.N = len(self.names)
        self.M = len(self.values()[0])

    def _are_col_lengths_equal(self):

        # if self is not empty
        counts = [len(v) for v in self.values()]
        if all([c-counts[0]+1 == 1 for c in counts]):
            if self == {}:
                self.M = None
            else:
                self.M = len(self.values()[0])
            return True
        else:
            self.M = None
            return False

    def _checktype(self, cname):
        """checks the datatype of self[cname]"""
        if cname not in self:
            raise KeyError(cname)

        if len(self[cname]) == 0:
            return 'null'
        elif all(_isint(v) for v in self[cname]):
            return 'integer'
        elif all(_isfloat(v) for v in self[cname]):
            return 'real'
        else:
            return 'text'

    def _execute(self, query, t=tuple()):
        """private method to execute sqlite3 queries"""
        if self.PRINTQUERIES:
            print(query)
            if len(t)>0:
                print('  ',t)
            print()

        self.cur.execute(query,t)

    def _get_sql_tbl_info(self):
        """
        private method to get a list of tuples containing
        information relevant to the current sqlite3 table
        """
        self.cur.commit()
        self._execute('PRAGMA table_info(TBL)')
        return list(self.cur)
    
    def _pvt(self, val, rows=[], cols=[], aggregate='avg',
              exclude={}, flatten=False):
        """
        private pivot table method

        returns pivot table, rnames, and cnames but doesn't
        set self.Z, self.Zrnames, or self.Zcnames
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
                
        if self=={}:
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

        for k in list(exclude.keys()):
            if k not in self:
                raise KeyError(k)

        # check for duplicate names
        dup = Counter([val]+rows+cols)
        del dup[None]
        if not all([count==1 for count in dup.values()]):
            raise Exception('duplicate labels specified as plot parameters')

        # check aggregate function
        aggregate=aggregate.lower()

        if aggregate not in self.aggregates:
            raise ValueError("supplied aggregate '%s' is not valid"%aggregate)
        
        # check to make sure exclude is mappable
        # todo

        # warn if exclude is not a subset of self.conditions
        if not self.conditions >= exclude:
            warnings.warn("exclude is not a subset of table conditions",
                          RuntimeWarning)
            
        # ignore keys/sets in exclude that aren't in self
        X = self.conditions & exclude
        
        #  2. Create a sqlite table with only the data in columns
        #     specified by val, rows, and cols. Also eliminate
        #     rows that meet the exclude conditions      
        ##############################################################
        nsubset = [val]+rows+cols

        # initialize table
        self.conn.commit()
        self._execute('drop table if exists TBL')

        self.conn.commit()
        query =  'create temp table TBL\n  ('
        query += ', '.join('_%s_ %s'%(n, self.typesdict[n]) for n in nsubset)
        query += ')'
        self._execute(query)

        # build insert query
        query = 'insert into TBL values ('
        query += ','.join('?' for n in nsubset) + ')'

        # for performance it is better to check it once if it is empty
        # values are passed to sqlite as a tuple
        if exclude == {}: 
            for i in _xrange(self.M):
                self._execute(query, tuple(self[n][i] for n in nsubset))
        else:
            for i in _xrange(self.M):
                # X is the intersection of X and self.conditions
                # so we know the keys in X will always be in self
                if X - [(k,[self[k][i]]) for k in X] == X:
                    self._execute(query, tuple((self[n][i] for n in nsubset)))
                    
        # Save (commit) the changes
        self.conn.commit()
        
        #  3. Build rnames and cnames lists
        ##############################################################
        
        # Refresh conditions list so we can build row and col list
        selected_conditions = self.conditions - X
                
        # Build row_list
        if rows==[]:
            row_list=[1]
        else:
            g=selected_conditions.unique_combinations(rows)
            row_list=[zip(rows,v) for v in g]
            
        rsize=len(row_list)
        
        # Build col_list
        if cols==[]:
            col_list=[1]
        else:
            g=selected_conditions.unique_combinations(cols)
            col_list=[zip(cols,v) for v in g]
            
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
        query=['select ']
        if aggregate == 'tolist':
            agg = 'group_concat'
        else:
            agg = aggregate
            
        if row_list==[1] and col_list==[1]:
            query.append('%s( _%s_ ) from TBL'%(agg,val))
        else:
            if row_list==[1]:
                query.append('_%s_'%val)
            else:
                for i,r in enumerate(rows):
                    if i!=0:
                        query.append(', ')
                    query.append('_%s_'%r)

            if col_list==[1]:
                query.append('\n  , %s( _%s_ )'%(agg,val))
            else:
                for cols in col_list:
                    query.append('\n  , %s( case when '%agg)
                    query.append('and '.join(('_%s_="%s"'\
                                              %(k,v) for k,v in cols)))
                    query.append(' then _%s_ end )'%val)

            if row_list==[1]:
                query.append('\nfrom TBL')
            else:                
                query.append('\nfrom TBL group by ')
                
                for i,r in enumerate(rows):
                    if i!=0:
                        query.append(', ')
                    query.append('_%s_'%r)

        #  5. Run Query
        ##############################################################
        self._execute(''.join(query) )

        #  6. Read data to from cursor into a list of lists
        ##############################################################
        d=[]
        val_type = self.typesdict[val]
        if aggregate=='tolist':
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
            d=_flatten(d)

        #  9. return data, rnames, and cnames
        ##############################################################
        return d,row_list,col_list


    def pivot(self, val, rows=[], cols=[], aggregate='avg',
              exclude={}, flatten=False):
        
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
            exclude = dictionary specifying levels to exclude
                keys = colnames
                values = lists of the levels in cooresponding colname to
                         exclude
        """
        d,rnames,cnames = self._pvt(val, rows=rows, cols=cols,
                                    aggregate=aggregate,
                                    exclude=exclude,
                                    flatten=flatten)
        
        # sets results to self attributes
        self.Z = d
        self.Zval = val
        self.Zexclude = self.conditions & exclude
        self.Zaggregate = aggregate
        self.Zrnames = rnames
        self.Zcnames = cnames

        return self.Z, self.Zrnames, self.Zcnames
        
    
    def selectCol(self, val, exclude={}):
        """
        Returns the a copy of the selected value where the conditions
        in exclude are not true. The order of the values in the returned
        list is preserved.
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
        if not self.conditions >= exclude:
            warnings.warn("exclude is not a subset of table conditions",
                          RuntimeWarning)
            
        # ignore keys/sets in exclude that aren't in self
        X = self.conditions & exclude 

        if exclude == {}: # the simple case
            return copy(self[val])

        d=[]
        for i in _xrange(self.M):
            # X is the intersection of X and self.conditions
            # so we know the keys in X will always be in self
            if X - [(k,[self[k][i]]) for k in X] == X:
                d.append(self[val][i])

        return d

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

        if not all([self.typesdict[n] == other.typesdict[n] for n in self.names]):
            raise Exception('types of self and other must match')

        # perform attachment
        for n in self.names:
            self[n].extend(copy(other[n]))

        # update state variables
        self.conditions = DictSet(self)
        self.M = len(self.values()[0])

    def printTable(self, exclude={}):
        if self=={}:
            raise Exception('Table must have data to print data')

        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        if self.M < 1: # self.M gets reset by self._check_tbl_lengths()
            raise Exception('Table must have at least one row to print data')
        
        # ignore keys/sets in exclude that aren't in self
        X = self.conditions & exclude
        
        tt=TextTable(max_width=100000000)
        dtypes=[self.typesdict[n][0] for n in self.names]
        dtypes=list(''.join(dtypes).replace('r','f'))
        tt.set_cols_dtype(dtypes)

        aligns=[_ifelse(dt in 'fi','r','l') for dt in dtypes]
        tt.set_cols_align(aligns)
        
        if exclude=={}: # for performance
                        # better to check it once if it is empty
            for i in _xrange(self.M):
                tt.add_row([self[n][i] for n in self.names])                
        else:
            for i in _xrange(self.M):
                if X - [(k,[self[k][i]]) for k in X] == X:
                    tt.add_row([self[n][i] for n in self.names])

        tt.header(self.names)
        tt.set_deco(TextTable.HEADER)

        # output the table
        print(tt.draw())

    def writeTable(self, exclude={}, fname=None, delimiter=','):
        if self=={}:
            raise Exception('Table must have data to print data')

        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        if self.M < 1: # self.M gets reset by self._check_tbl_lengths()
            raise Exception('Table must have at least one row to print data')
            
        # ignore keys/sets in exclude that aren't in self
        X = self.conditions & exclude
        
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

            if exclude=={}: # for performance
                            # better to check it once if it is empty
                for i in _xrange(self.M):
                    wtr.writerow([_str(self[n][i],n=8) for n in self.names])                
            else:
                for i in _xrange(self.M):
                    if X - [(k,[self[k][i]]) for k in X] == X:
                        wtr.writerow([_str(self[n][i],n=8) for n in self.names])
                                    
    def printPivot(self, val, rows=[], cols=[], aggregate='avg',
                   exclude={}, flatten=False):
        """
        pivots, sets, and prints pivot table
        """
        # _pvt does checking
        self.pivot(val, rows=rows, cols=cols, aggregate=aggregate,
                   exclude=exclude, flatten=flatten)

        # build first line
        first = '%s(%s)'%(self.Zaggregate, self.Zval)
        if self.Zexclude != {}:
            X_list = []
            for (k, v) in sorted(self.Zexclude.items()):
                conditions = ', '.join((str(c) for c in v))
                X_list.append('%s not in {%s}'%(k, conditions))
            first += ' where ' + ' or '.join(X_list)

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
            header = [',\n'.join(['%s=%s'%(f,c) for (f,c) in L]) \
                      for L in self.Zcnames]
            
            # initialize the texttable and add stuff
            tt.set_cols_dtype(['a']*len(self.Zcnames))
            tt.set_cols_align(['r']*len(self.Zcnames))
            tt.add_row(self.Z[0])
            
        elif self.Zcnames == [1]: # no cols were specified
            # build the header
            header = rows + ['Value']
            
            # initialize the texttable and add stuff
            tt.set_cols_dtype(['t']*len(rows)+['a'])
            tt.set_cols_align(['l']*len(rows)+['r'])
            for i,L in enumerate(self.Zrnames):
                tt.add_row([c for (f,c) in L]+self.Z[i])
            
        else: # table has rows and cols
            # build the header
            header = rows + [',\n'.join(['%s=%s'%(f,c) for (f,c) in L]) \
                             for L in self.Zcnames]

            # initialize the texttable and add stuff
            tt.set_cols_dtype(['t']*len(rows)+['a']*len(self.Zcnames))
            tt.set_cols_align(['l']*len(rows)+['r']*len(self.Zcnames))
            for i,L in enumerate(self.Zrnames):
                tt.add_row([c for (f,c) in L]+self.Z[i])

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
        if self.Zexclude != {}:
            X_list=[]
            for (k, v) in sorted(self.Zexclude.items()):
                conditions = '; '.join((str(c) for c in v))
                X_list.append('%s not in {%s}'%(k, conditions))
            first = [self.Zval + ' where ' + ' or '.join(X_list)]
        else:
            first = [self.Zval]

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
            header = ['_'.join(['%s=%s'%(f,c) for (f,c) in L]) \
                      for L in self.Zcnames]

            # initialize the texttable and add stuff
            data.append(self.Z[0])
            
        elif self.Zcnames == [1]: # no cols were specified
            # build the header
            header = rows + ['Value']
            
            # initialize the texttable and add stuff
            for i,L in enumerate(self.Zrnames):
                data.append([c for (f,c) in L]+self.Z[i])
            
        else: # table has rows and cols
            # build the header
            header = rows + ['_'.join(['%s=%s'%(f,c) for (f,c) in L]) \
                             for L in self.Zcnames]

            # initialize the texttable and add stuff
            for i,L in enumerate(self.Zrnames):
                data.append([c for (f,c) in L]+self.Z[i])

        # write file
        with open(fname, 'wb') as fid:
            wtr = csv.writer(fid, delimiter=delimiter)
            wtr.writerow(first)
            wtr.writerow(header)
            wtr.writerows(data)

    def descriptives(self,cname,exclude={}):
        
        """
        Returns a dict of descriptive statistics for column cname
        """
        if self=={}:
            raise Exception('Table must have data to calculate descriptives')

        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        if cname not in self:
            raise KeyError(cname)
        
        V=sorted(self.selectCol(cname,exclude=exclude))
        N=len(V)

        D=OrderedDict()
        D['count']      = N
        D['mean']       = sum(V)/N
        D['var']        = sum([(D['mean']-v)**2 for v in V])/(N-1)
        D['stdev']      = math.sqrt(D['var'])
        D['sem']        = D['stdev']/math.sqrt(N)
        D['rms']        = math.sqrt(sum([v**2 for v in V])/N)
        D['min']        = min(V)
        D['max']        = max(V)
        D['range']      = D['max']-D['min']
        D['median']     = V[int(N/2)]
        if D['count']%2==0:
            D['median']+= V[int(N/2)-1]
            D['median']/= 2.
        D['95ci_lower'] = D['mean']-1.96*D['sem']
        D['95ci_upper'] = D['mean']+1.96*D['sem']

        return D
    
    def printDescriptives(self,cname):
        D=self.descriptives(cname)

        print('Descriptive Statistics for')
        print('',cname                    )
        print('==========================')

        tt=TextTable(48)
        tt.set_cols_dtype(['t','f'])
        tt.set_cols_align(['l','r'])
        for i,(k,v) in enumerate(D.items()):
            tt.add_row([' %s'%k,v])
        tt.set_deco(TextTable.HEADER)
        
        print(tt.draw())


    def marginals(self, val, factors, exclude={}):
        if self=={}:
            raise Exception('Table must have data to calculate marginals')
        
        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        for cname in [val]+factors:
            if cname not in self:
                raise KeyError(cname)

        # check for duplicate names
        dup = Counter([val]+factors)
        del dup[None]
        if not all([count==1 for count in dup.values()]):
            raise Exception('duplicate labels specified as plot parameters')

        if not hasattr(factors, '__iter__'):
            raise TypeError( "'%s' object is not iterable"
                         % type(cols).__name__)

        dmu=self.pivot(val, rows=factors, exclude=exclude,
                       aggregate='avg', flatten=True)[0]

        dN =self.pivot(val, rows=factors, exclude=exclude,
                       aggregate='count', flatten=True)[0]

        dsem,r_list,c_list=self.pivot(val, rows=factors, exclude=exclude,
                                      aggregate='sem', flatten=True)

        # build factors from r_list
        factors=OrderedDict()
        for i,r in enumerate(r_list):
            if i==0:
                for c in r:
                    factors[c[0]]=[]
            
            for j, c in enumerate(r):
                factors[c[0]].append(c[1])

        dlower=[]
        dupper=[]
        for mu,sem in zip(dmu,dsem):
            dlower.append(mu - 1.96*sem)
            dupper.append(mu + 1.96*sem)

        return factors,dmu,dN,dsem,dlower,dupper            
        
    def printMarginals(self, val, factors=None, exclude={}):
        """Plot marginal statisics over factors for val"""

        # marginalMeans handles checking
        x=self.marginalMeans(val,factors=factors,exclude=exclude)
        [f,dmu,dN,dsem,dlower,dupper]=x

        M=[]
        for v in f.values():
            M.append(v)
            
        M.append(dmu)
        M.append(dN)
        M.append(dsem)
        M.append(dlower)
        M.append(dupper)
        M=_transpose(M)

        # figure out the width needed by the condition labels so we can
        # set the width of the table
        flength=sum([max([len(v) for c in v]) for v in f.values()])+len(f)*2

        # build the header
        header=factors+'Mean;Count;Std.\nError;'\
                       '95% CI\nlower;95% CI\nupper'.split(';')

        # initialize the texttable and add stuff
        tt=TextTable(max_width=flength+48)
        tt.set_cols_dtype(['t']*len(factors)+['f','i','f','f','f'])
        tt.set_cols_align(['l']*len(factors)+['r','l','r','r','r'])
        tt.add_rows(M,header=False)
        tt.header(header)
        tt.set_deco(TextTable.HEADER)

        # output the table
        print()
        print(tt.draw())

    def plotBox(self, val, factors=[], exclude={},
            fname=None, quality='medium'):
        if self=={}:
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

        # check for third party packages
        try:
            import pylab
        except:
            raise ImportError('pylab is required for plotting')

        try:
            import numpy as np
        except:
            raise ImportError('numpy is required for plotting')

        # check fname
        if not isinstance(fname, _strobj) and fname != None:
            raise TypeError('fname must be None or string')

        if isinstance(fname, _strobj):
            if not (fname.lower().endswith('.png') or \
                    fname.lower().endswith('.svg')):
                raise Exception('fname must end with .png or .svg')

        if factors == None:
            d = self.selectCol(val, exclude=exclude)            
            fig = pylab.figure()
            pylab.boxplot(np.array(d))
            xticks = pylab.xticks()[0]
            xlabels = [val]
            pylab.xticks(xticks, xlabels)

        else:
            D,cs = self._pvt(val, rows=factors,
                             exclude=exclude,
                             aggregate='tolist')[:2]

            D = [np.array(_flatten(d)) for d in D]

            fig = pylab.figure(figsize=(6*len(factors),6))
            fig.subplots_adjust(left=.05, right=.97, bottom=0.24)
            pylab.boxplot(D)
            xticks = pylab.xticks()[0]
            xlabels = ['\n'.join(['%s = %s'%fc for fc in c]) for c in cs]
            pylab.xticks(xticks, xlabels,
                         rotation='vertical',
                         verticalalignment='top')   


        maintitle = '%s'%val

        if factors != []:
            maintitle += ' by '
            maintitle += ' * '.join(factors)
            
        fig.text(0.5, 0.95, maintitle,
                 horizontalalignment='center',
                 verticalalignment='top')   
            
        if fname == None:
            fname = 'box(%s).png'%val.lower()
        
        # save figure
        if quality=='low' or fname.endswith('.svg'):
            pylab.savefig(fname)
            
        elif quality=='medium':
            pylab.savefig(fname,dpi=200)
            
        elif quality=='high':
            pylab.savefig(fname,dpi=300)
            
        else:
            pylab.savefig(fname)

        pylab.close()

        if self.TESTMODE:
            return True

    def hist(self, val, exclude={}, bins=10,
             range=None, density=False, cumulative=False):          
        V = self.selectCol(val, exclude=exclude)
        return pystaggrelite3.hist(V, bins=bins, range=range,
                                   density=density, cumulative=cumulative)

    def plotHist(self, val, exclude={}, bins=10,
                 range=None, density=False, cumulative=False,
                 fname=None, quality='medium'):    
        
        # check for third party packages
        try:
            import pylab
        except:
            raise ImportError('pylab is required for plotting')

        try:
            import numpy as np
        except:
            raise ImportError('numpy is required for plotting')

        # check fname
        if not isinstance(fname, _strobj) and fname != None:
            raise TypeError('fname must be None or string')

        if isinstance(fname, _strobj):
            if not (fname.lower().endswith('.png') or \
                    fname.lower().endswith('.svg')):
                raise Exception('fname must end with .png or .svg')                

        v = self.selectCol(val, exclude=exclude)
        
        fig=pylab.figure()
        pylab.hist(np.array(v), bins=bins, range=range,
                   normed=density, cumulative=cumulative)

        if fname == None:
            fname = 'hist(%s).png'%val.lower()
        
        # save figure
        if quality=='low' or fname.endswith('.svg'):
            pylab.savefig(fname)
            
        elif quality=='medium':
            pylab.savefig(fname,dpi=200)
            
        elif quality=='high':
            pylab.savefig(fname,dpi=300)
            
        else:
            pylab.savefig(fname)

        pylab.close()

        if self.TESTMODE:
            return True

    def plotMarginals(self, val, xaxis, 
                      seplines=None, sepxplots=None, sepyplots=None,
                      xmin='AUTO', xmax='AUTO', ymin='AUTO', ymax='AUTO',
                      exclude={}, fname=None,
                      quality='low', yerr=None):
        # pylab doesn't like not being closed. To avoid starting
        # a plot without finishing it, we do some extensive checking
        # up front

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

        # check for data
        if self=={}:
            raise Exception('Table must have data to plot marginals')

        # check for third party packages
        try:
            import pylab
        except:
            raise ImportError('pylab is required for plotting')

        try:
            import numpy as np
        except:
            raise ImportError('numpy is required for plotting')

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

        # ignore keys/sets in exclude that aren't in self
        X = self.conditions & exclude

        # check cell counts
        cols=[f for f in [seplines, sepxplots, sepyplots] if f in self]
        counts=self.pivot(val, rows=[xaxis], cols=cols,
                         flatten=True, exclude=X, aggregate='count')[0]

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
            rlevels = copy(self.conditions[sepyplots]) # a set
            numrows = len(rlevels) # a int

            if sepyplots in X:
                rlevels -= set(X[sepyplots])
                numrows -= len(X[sepyplots])

            rlevels = sorted(rlevels) # set -> sorted list
                
        numcols = 1
        clevels = [1]            
        if sepxplots != None:
            clevels = copy(self.conditions[sepxplots])
            numcols = len(clevels)
            
            if sepxplots in X:
                clevels -= set(X[sepyplots])
                numcols -= len(X[sepxplots])

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
                    y, r_list, c_list=self._pvt(val,cols=[xaxis],
                            exclude=X,aggregate='avg',
                            flatten=True)
                    y = np.array(y)

                    if aggregate!=None:
                        yerr=self._pvt(val,cols=[xaxis],
                            exclude=X,aggregate=aggregate,
                            flatten=True)[0]
                        yerr=np.array(yerr)
                        
                    x = [name for [(label,name)] in c_list]
                    
                    if _isfloat(yerr):
                        yerr=np.array([yerr for a in x])

                    if all([_isfloat(a) for a in x]):
                        axs[-1].errorbar(x,y,yerr)
                        if xmin=='AUTO' and xmax=='AUTO':
                            xmin,xmax=axs[-1].get_xlim()
                            xran=xmax-xmin
                            xmin,xmax=xmin-.05*xran,xmax+.05*xran

                        axs[-1].plot([xmin,xmax],[0.,0.],'k:')
                        
                    else : # categorical x axis
                        axs[-1].errorbar(_xrange(len(x)),y.flatten(),yerr)
                        pylab.xticks(_xrange(len(x)),x)
                        xmin,xmax=-.5,len(x)-.5
                        
                        axs[-1].plot([xmin,xmax],[0.,0.],'k:')

                ########## If separate lines are specified ###########
                else:
                    y,r_list,c_list=self._pvt(val,
                            rows=[seplines],cols=[xaxis],exclude=X,
                            aggregate='avg',flatten=False)
                    y=np.array(y)
                    
                    if aggregate!=None:
                        yerrs=self._pvt(val,
                            rows=[seplines],cols=[xaxis],exclude=X,
                            aggregate=aggregate,flatten=False)[0]
                        yerrs=np.array(yerrs)
                        
                    x = [name for [(label,name)] in c_list]

                    if _isfloat(yerr):
                        yerr=np.array([yerr for a in x])

                    plots,labels=[],[]
                    for i,name in enumerate(r_list):
                        if aggregate!=None:
                            yerr=yerrs[i,:]
                        
                        labels.append(name[0][1])

                        if all([_isfloat(a) for a in x]):
                            plots.append(axs[-1].errorbar(x,y[i,:],yerr)[0])
                            if xmin=='AUTO' and xmax=='AUTO':
                                xmin,xmax=axs[-1].get_xlim()
                                xran=xmax-xmin
                                xmin,xmax=xmin-.05*xran,xmax+.05*xran
                                
                            axs[-1].plot([xmin,xmax],[0.,0.],'k:')
                            
                        else : # categorical x axis
                            plots.append(axs[-1].errorbar(
                                _xrange(len(x)),y[i,:],yerr)[0])
                            pylab.xticks(_xrange(len(x)),x)
                            xmin,xmax=-.5,len(x)-.5
                            axs[-1].plot([xmin,xmax],[0.,0.],'k:')

                    pylab.figlegend(plots,labels,loc=1,
                                    labelsep=.005,
                                    handlelen=.01,
                                    handletextsep=.005)

                test['y'].append(y.tolist())
                if yerr==None:
                    test['yerr'].append([])
                else:
                    test['yerr'].append(yerr.tolist())
                test['xmins'].append(xmin)
                test['xmaxs'].append(xmax)

                #  8.2 Add subplot title
                ######################################################
                if rlevels==[1] and clevels==[1]:
                    title = ''
                    
                elif rlevels==[1]:
                    title = _str(clevel)
                    
                elif clevels==[1]:
                    title = _str(rlevel)
                    
                else:
                    title = '%s = %s, %s = %s' % (sepyplots,_str(rlevel),
                                                  sepxplots,_str(rlevel))
                    
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
                    locs,labels=pylab.yticks()
                    pylab.yticks(locs, ['' for l in _xrange(len(locs))])

                # Set the aspect ratio for the subplot
                Dx=abs(axs[-1].get_xlim()[0]-axs[-1].get_xlim()[1])
                Dy=abs(axs[-1].get_ylim()[0]-axs[-1].get_ylim()[1])
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
                             .replace('by','~') \
                             .replace('*','X') \
                             .replace(' ','')
            
        if quality=='low' or fname.endswith('.svg'):
            pylab.savefig(fname)
            
        elif quality=='medium':
            pylab.savefig(fname,dpi=200)
            
        elif quality=='high':
            pylab.savefig(fname,dpi=300)
            
        else:
            pylab.savefig(fname)

        pylab.close()

        test['fname']=fname

        # 11. return the test dictionary
        ##############################################################
        if self.TESTMODE:
            return test
        
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
##df=PyvtTbl()
##df.readTbl('error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
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
df=PyvtTbl()
df.readTbl('suppression~subjectXgroupXageXcycleXphase.csv')
df.plotBox('SUPPRESSION',factors=['GROUP','CYCLE'])
##pp(df.Pivot('ERROR',rows=['SUBJECT','TIMEOFDAY'],exclude={'SUBJECT':['1']}))
##

##    
##df=PyvtTbl()
##df.readTbl('suppression~subjectXgroupXageXcycleXphase.csv')
##df.printPivot('SUPPRESSION',
##         aggregate='count',
##         exclude={'GROUP':['AB'],'CYCLE':[1,2]})
##df.printTable(exclude={'AGE':['old'],'PHASE':['I']})
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
