from __future__ import print_function

# Copyright (c) 2011, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.

import csv
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

