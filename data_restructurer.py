from __future__ import print_function

# Copyright (c) 2011, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.

import atexit
import csv
import os
import sys
from copy import copy
from pprint import pprint as pp

from pyvttbl import PyvtTbl, _xuniqueCombinations

def long2wide(in_fname, id, dvs, between=[], within=[],
         covariates=[], out_fname=None, nested=True):

    # load in_fname into a PyvtTbl object
    print('reading "%s"...'%in_fname)
    cls = PyvtTbl()
    cls.readTbl(in_fname)
        
    # loop through DVs and append within columns
    d = [sorted(set(cls[id]))]
    header = [id] + covariates + between

    for col in covariates+between:
        d.extend(cls._pvt(col, cols=[id], aggregate='arbitrary')[0])
        
    # start controls whether nested factors are examined
    if nested : start = 1
    else      : start = len(within)
    
    for i, dv in enumerate(dvs):
        print('\ncollaborating %s'%dv)
        for j in xrange(start, len(within)+1):
            
            for factors in _xuniqueCombinations(within, j):
                print('  pivoting', factors, '...')
                z, clist = cls._pvt(dv, rows=factors, cols=[id],
                                    aggregate='avg')[:2]
                d.extend(z)
                
                # process headers
                for names in clist:
                    h = ','.join(('%s_%s'%(f, str(c)) for (f,c) in names))
                    header.append('%s__%s'%(dv, h))

    # Now we can write the data
    if out_fname == None:
        out_fname = 'wide_data.csv'

    with open(out_fname,'wb') as f:
        wtr = csv.writer(f)
        wtr.writerow([n.upper() for n in header])
        wtr.writerows(zip(*d)) # transpose and write
        
##long2wide(in_fname='long_test_data.csv',
##          id='participant',
##          dvs=['dv1','dv2'],
##          between=['bfactor1'],
##          within=['wfactor1','wfactor2','wfactor3'],
##          covariates=['cov1','cov2'],
##          out_fname='formatted.csv',
##          nested=False)

def goodbye():
    pass

def get(text):
    global top, progress
    os.system('cls')
    print(top)
    print(text, end='')
    default = text[text.find('[')+1:text.find(']')]
    x = sys.stdin.readline()
    if x == '\n':
        x = default
    else:
        x = x[:-1]
    progress += 1
    return x

def getmultcol(text):
    global top, progress, header, assigned
    os.system('cls')
    print(top)
    print('Available column labels:')
    for i,c in enumerate(header):
        if i not in assigned:
            print('  [%i]\t%s'%(i+1,c))
        else:
            print('  [%i]'%(i+1))
    print()
    print(text, end='')  
    x = sys.stdin.readline()
    if x == '\n':
        x = []
    else:
        x = [int(v)-1 for v in x.split(',')]

    assigned.extend(copy(x))
    progress += 1
    return [header[i] for i in x]

if __name__ == '__main__':
    top = """
=============================================================
  Welcome to the guided "long" to "wide" file restructer
    v0.1 press "ctrl + c" to exit

    separate multiple entries with commas
=============================================================
"""
    assigned = []
    progress = 1
    
    ifname = get("input file name [long_test_data.csv]: ")    
    skip = int(get("lines to skip [0]: "))
    delimiter = get("delimiter [,]: ")

    with open(ifname,'rb') as f:
        lines = f.readlines()
        
    header = lines[skip].split(delimiter)
    id = getmultcol('Which column contains the PARTICIPANT IDs: ')[0]
    dvs = getmultcol('Which columns contain DEPENDENT VARIABLE: ')
    between = getmultcol('Which columns contain BETWEEN FACTORS: ')
    within = getmultcol('Which columns contain WITHIN FACTORS: ')
    cov = getmultcol('Which columns contain COVARIATES: ')

    ofname = get("output file name [wide_test_data.csv]: ")
    nested = get("process nested factors [N]: ")
    if 'y' in nested.lower():
        nested = 'True'
    else:
        nested = 'False'

    code="""
long2wide(in_fname='%s',
          id='%s',
          dvs=%s,
          between=%s,
          within=%s,
          covariates=%s,
          out_fname='%s',
          nested=%s)
"""%(ifname,id,str(dvs),str(between),str(within),str(cov),ofname,nested)

    print('Generated code:%s'%code)
    run = get('Run [Y]: ')
    if 'y' in run.lower():
        eval(code)
    print('done.')

