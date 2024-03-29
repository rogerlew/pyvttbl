# Copyright (c) 2012-2024, Roger Lew [see LICENSE.txt]

import os

import pylab
import numpy as np

def histogram_plot(df, val, where=None, bins=10,
              range=None, density=False, cumulative=False,
              fname=None, output_dir='', quality='medium'):
    """
    Makes a histogram plot

       args:
          key: column label of dependent variable

       kwds:
          where: criterion to apply to table before running analysis

          bins: number of bins (default = 10)

          range: list of length 2 defining min and max bin edges
    """

    if where is None:
        where = []

    # check fname
    if not isinstance(fname, str) and fname is not None:
        raise TypeError('fname must be None or string')

    if isinstance(fname, str):
        if not (fname.lower().endswith('.png') or \
                fname.lower().endswith('.svg')):
            raise Exception('fname must end with .png or .svg')                

    # select_col does checking of val and where
    v = df.select_col(val, where=where)
    
    fig=pylab.figure()
    tup = pylab.hist(np.array(v), bins=bins, range=range,
                     density=density, cumulative=cumulative)
    pylab.title(val)

    if fname == None:
        fname = 'hist(%s'%val
        if cumulative:
            fname += ',cumulative=True'
        if density:
            fname += ',density=True'
        fname += ').png'
    
    fname = os.path.join(output_dir, fname)
    
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

    if df.TESTMODE:
        # build and return test dictionary
        return {'bins':tup[0], 'counts':tup[1], 'fname':fname}
