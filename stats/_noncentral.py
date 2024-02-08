from __future__ import print_function

# Copyright (c) 2011-2024, Roger Lew [see LICENSE.txt]

import scipy

def nctcdf(x,df,nc):
    """
    Noncentral t cumulative distribution function (cdf)
    
    P = nctcdf(x,df,nc) computes the noncentral
    F cdf at each of the values in {x} using the
    corresponding degrees of freedom in {df} and positive
    noncentrality parameters in {nc}. 
    """
    return scipy.stats.nct(df,nc).cdf(x)

def ncfcdf(x,df1,df2,nc):
    """
    Noncentral F cumulative distribution function (cdf)
    
    P = ncfcdf(x,df1,df2,ncA) computes the noncentral
    F cdf at each of the values in {x} using the
    corresponding numerator degrees of freedom in {df1},
    denominator degrees of freedom in {df2}, and positive
    noncentrality parameters in {nc}. 
    """
    return scipy.stats.ncf(df1,df2,nc).cdf(x)

def ncx2cdf(x,df,nc):
    """
    Noncentral t cumulative distribution function (cdf)
    
    P = nctcdf(x,df,nc) computes the noncentral
    F cdf at each of the values in {x} using the
    corresponding degrees of freedom in {df} and positive
    noncentrality parameters in {nc}. 
    """
    return scipy.stats.ncx2(df,nc).cdf(x)
