from __future__ import print_function

# Copyright (c) 2012, Roger Lew [see LICENSE.txt]

# Python 2 to 3 workarounds
import sys
if sys.version_info[0] == 2:
    _strobj = basestring
    _xrange = xrange
elif sys.version_info[0] == 3:
    _strobj = str
    _xrange = range

import pylab
import numpy as np

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
