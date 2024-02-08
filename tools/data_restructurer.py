# Copyright (c) 2011-2024, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.

import csv
from pyvttbl import DataFrame


def _xunique_combinations(items, n):
    """
    returns the unique combinations of items. the n parameter controls
    the number of elements in items to combine in each combination
    """
    if n == 0:
        yield []
    else:
        for i in range(len(items)):
            for cc in _xunique_combinations(items[i+1:], n-1):
                yield [items[i]]+cc


def long2wide(in_fname, id, dvs, between=[], within=[],
         covariates=[], out_fname=None, nested=True):

    # load in_fname into a PyvtTbl object
    print('reading "%s"...'%in_fname)
    cls = DataFrame()
    cls.read_tbl(in_fname)
        
    # loop through DVs and append within columns
    d = [sorted(set(cls[id]))]
    header = [id] + covariates + between

    for col in covariates+between:
        z = cls.pivot(col, cols=[id], aggregate='arbitrary')
        d.extend(list(z))
        
    # start controls whether nested factors are examined
    if nested : start = 1
    else      : start = len(within)
    
    for i, dv in enumerate(dvs):
        print('\ncollaborating %s'%dv)
        for j in range(start, len(within)+1):
            
            for factors in _xunique_combinations(within, j):
                print('  pivoting', factors, '...')
                z = cls.pivot(dv, rows=factors, cols=[id],
                                    aggregate='avg')
                d.extend(list(z))
                
                # process headers
                for names in z.rnames:
                    h = '_'.join(('%s.%s'%(f, str(c)) for (f,c) in names))
                    header.append('%s__%s'%(dv, h))

    # Now we can write the data
    if out_fname == None:
        out_fname = 'wide_data.csv'

    with open(out_fname,'w') as f:
        wtr = csv.writer(f)
        wtr.writerow([n.upper() for n in header])
        wtr.writerows(zip(*d)) # transpose and write
        

if __name__ == "__main__":
    import time

    t0=time.time()
    print('need to format data for spss... (this may take a few minutes)')

    fname='collaborated.csv'

    covariates='age,gender,dicho_correct,dicho_misses,dicho_FA,SAAT_noncomp_correct,'\
               'SAAT_noncomp_incorrect,SAAT_comp_correct,SAAT_comp_incorrect'.split(',')

    within='speed,target_dir,agreement'.split(',')

    dvs='correct_decision_raw,decision_at_safe_distance_raw,decision_distance_raw,'\
        'decision_latency_raw,decision_proportion_raw,decision_ttc_proportion_raw,'\
        'decision_ttc_raw,detection_distance_raw,detection_latency_raw,'\
        'detection_proportion_raw,detection_ttc_proportion_raw,detection_ttc_raw,'\
        'position_distance_raw,position_latency_raw,risk_level_raw,trial_raw'.split(',')
     
    ##long2wide(fname, 'participant',dvs=dvs,within=within,covariates=covariates,nested=False)

    long2wide(in_fname=fname,
              id='participant',
              dvs=dvs,
              between=[],
              within=within,
              covariates=covariates,
              out_fname='formatted.csv',
              nested=True)

    print('\ndone.')
    print(time.time()-t0)
