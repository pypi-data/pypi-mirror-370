import numpy as np
import sys
import textwrap

from . import evaluate_dmgs_equation as cp_dmgs

 
# Deal with situations in which the user wants d or p outside the GEV range
def fixgevrange(y, v1, v2, v3):
    # I've added minxi now, so that even in the case where I adjust xi slightly
    # in the 'movexiawayfromzero' routine, to avoid being too near zero when
    # calculating analytical gradients, we still adjust the y and we don't
    # get NA errors from the analytical gradient routines, from logp1
    minxi = 10**-7
    y = np.array(y, copy=True)
    
    if v3 < 0:
        # ximax=v1-v2/v3
        ximax = v1 - v2 / (v3 - minxi)
        for i in range(len(y)):
            if y[i] > ximax:
                y[i] = ximax
    
    if v3 > 0:
        # ximin=v1-v2/v3
        ximin = v1 - v2 / (v3 + minxi)
        for i in range(len(y)):
            if y[i] < ximin:
                y[i] = ximin
    
    return y

#  Deal with situations in which the user wants d or p outside the GPD range
def fixgpdrange(y, v1, v2, v3):
    y = np.array(y, copy=True)
    
    if v3 < 0:
        ximin = v1
        ximax = v1 - v2 / v3
        for i in range(len(y)):
            if y[i] < ximin:
                y[i] = ximin
            if y[i] > ximax:
                y[i] = ximax
    else:
        for i in range(len(y)):
            if y[i] < v1:
                y[i] = v1
    
    return y


def movexiawayfromzero(xi):
    #Move xi away from zero a bit
    minxi = 10**-7
    if abs(xi) < minxi:
        if xi >= 0:
            # the problem with this idea could be that increasing xi, when xi is positive,
            # increases the minimum of the gev, and some y values might then lie below the minimum
            # but I've made a change to the 'fixgevrange' routine to deal with that
            # and that seems to fix the problem now
            xi = minxi
        else:
            xi = -minxi
    return xi


def to_array(x):
    # so that certain functions can take either a single number, or an array
    if (isinstance(x, float) or isinstance(x, int)):
        x = [x]
    x = np.asarray(x)
    return x


def ru(arg, **kwargs):
    raise Exception('rust not yet implemented')


def maket0(t0, n0, t):
    # if t0 is specified, does nothing
    # if t0 isn't specified, calculates t0 from n0
    
    if (t0 is None or np.isnan(t0)) and (n0 is None or np.isnan(n0)):
        raise Exception("Either t0 or n0 must be specified")
    if (t0 is not None and not np.isnan(t0)) and (n0 is not None and not np.isnan(n0)):
        raise Exception("Only one of t0 or n0 must be specified")
    if t0 is None or np.isnan(t0):
        t0 = t[n0 - 1]  # Convert to 0-based indexing
    
    return t0

def makemuhat0(t0, n0, t, mle_params):
    t = np.array(t)
    mle_params = np.array(mle_params)
    
    muhat = mle_params[0] + mle_params[1] * t
    
    if t0 is None or np.isnan(t0):
        muhat0 = muhat[n0 - 1]  # Convert to 0-based indexing
    else:
        muhat0 = mle_params[0] + mle_params[1] * t0
    
    return muhat0

def maketa0(t0, n0, t):
    t = np.array(t)
    ta = t - np.mean(t)
    
    if t0 is None or np.isnan(t0):
        ta0 = ta[n0 - 1]  # Convert to 0-based indexing
    else:
        ta0 = t0 - np.mean(t)
    
    return ta0

# make Standard Errors from lddi
def make_se(nx, lddi):
    nd = lddi.shape[0]
    standard_errors = np.zeros(nd, dtype=object)
    
    for i in range(nd):
        if lddi[i, i] > 0:
            standard_errors[i] = "square root not possible"
        else:
            standard_errors[i] = np.sqrt(-lddi[i, i] / nx)
    
    return standard_errors

def make_waic(x, fhatx, lddi, lddd, f1f, lambdad, f2f, dim):
    # waic seems to be a bust because it doesn't make sense for the mle models...it doesn't penalize them at all for parameters
    # the variance version always penalizes twice as much as the difference version...is there a factor of 2 wrong somewhere?
    
    # x is implicit in f1f and f2f
    
    nx = len(x)
    lfhatx = np.log(fhatx)
    fhatxsq = fhatx * fhatx
    lfhatxof = lfhatx / fhatx
    omlfhatx = 1 - lfhatx
    
    outerf1f = np.zeros((dim, dim, nx))
    for i in range(nx):
        for j in range(dim):
            for k in range(dim):
                outerf1f[j, k, i] = np.outer(f1f[j, i], f1f[k, i])
    
    # first term is the llpd
    # which is just the in-sample log-likelihood
    # for mle, should match the log-likelihood at the max
    # calc the probabilities, take the log, add them together
    t1 = np.zeros((dim, nx))
    t2 = np.zeros((dim, dim, nx))
    for i in range(nx):
        t1[:, i] = f1f[:, i]
        t2[:, :, i] = f2f[:, :, i]
    
    dq = cp_dmgs.dmgs(lddi, lddd, t1, lambdad, t2, dim=dim) / nx
    dqq = np.maximum(fhatx + dq, sys.float_info.epsilon)
    logf1_rhp = np.log(dqq)
    sumlogf1_rhp = np.sum(logf1_rhp)
    lppd_rhp = sumlogf1_rhp
    
    # second term is the penalty term
    # this version of it is a difference
    # seems to be the same for maxlik
    t1 = np.zeros((dim, nx))
    t2 = np.zeros((dim, dim, nx))
    for i in range(nx):
        t1[:, i] = f1f[:, i] / fhatx[i]
        t2[:, :, i] = f2f[:, :, i] / fhatx[i] - outerf1f[:, :, i] / fhatxsq[i]
    
    logf2_rhp = lfhatx + cp_dmgs.dmgs(lddi, lddd, t1, lambdad, t2, dim=dim) / nx
    sumlogf2_rhp = np.sum(logf2_rhp)
    pwaic1_rhp = 2 * (sumlogf1_rhp - sumlogf2_rhp)
    
    # alternative version uses the variance thing for the second term
    
    # this version of it is a variance
    # it penalizes more...is there really a factor of 2 needed
    t2inner = np.zeros((dim, dim, nx))
    for i in range(nx):
        t1[:, i] = 2 * lfhatxof[i] * f1f[:, i]
        t2inner[:, :, i] = f2f[:, :, i] * lfhatx[i] + outerf1f[:, :, i] * omlfhatx[i] / fhatx[i]
        t2[:, :, i] = 2 * t2inner[:, :, i] / fhatx[i]
    
    dq = cp_dmgs.dmgs(lddi, lddd, t1, lambdad, t2, dim=dim)
    sumvlogf_rhp = np.sum(lfhatx * lfhatx + dq / nx - logf2_rhp * logf2_rhp)
    pwaic2_rhp = sumvlogf_rhp
    
    waic1 = np.zeros(3)
    waic2 = np.zeros(3)
    waic1[0] = lppd_rhp
    waic1[1] = -pwaic1_rhp
    waic1[2] = waic1[0] + waic1[1]
    waic2[0] = lppd_rhp
    waic2[1] = -pwaic2_rhp
    waic2[2] = waic2[0] + waic2[1]
    
    return {'waic1': waic1, 'waic2': waic2}

def make_cwaic(x, fhatx, lddi, lddd, f1f, lambdad, f2f, dim):
    # waic seems to be a bust because it doesn't make sense for the mle models...it doesn't penalize them at all for parameters
    # the variance version always penalizes twice as much as the difference version...is there a factor of 2 wrong somewhere?
    
    # x is implicit in f1f and f2f
    
    nx = len(x)
    lfhatx = np.log(fhatx)
    fhatxsq = fhatx * fhatx
    lfhatxof = lfhatx / fhatx
    omlfhatx = 1 - lfhatx
    
    outerf1f = np.zeros((dim, dim, nx))
    for i in range(nx):
        for j in range(dim):
            for k in range(dim):
                outerf1f[j, k, i] = np.outer(f1f[j, i], f1f[k, i])
    
    # first term is the llpd
    # which is just the in-sample log-likelihood
    # for mle, should match the log-likelihood at the max
    # calc the probabilities, take the log, add them together
    t1 = np.zeros((dim, nx))
    t2 = np.zeros((dim, dim, nx))
    for i in range(nx):
        t1[:, i] = f1f[:, i]
        t2[:, :, i] = f2f[:, :, i]
    
    dq = cp_dmgs.dmgs(lddi, lddd, t1, lambdad, t2, dim=dim) / nx
    dqq = np.maximum(fhatx + dq, sys.float_info.epsilon)
    logf1_rhp = np.log(dqq)
    sumlogf1_rhp = np.sum(logf1_rhp)
    lppd_rhp = sumlogf1_rhp
    
    # second term is the penalty term
    # this version of it is a difference
    # seems to be the same for maxlik
    t1 = np.zeros((dim, nx))
    t2 = np.zeros((dim, dim, nx))
    for i in range(nx):
        t1[:, i] = f1f[:, i] / fhatx[i]
        t2[:, :, i] = f2f[:, :, i] / fhatx[i] - outerf1f[:, :, i] / fhatxsq[i]
    
    logf2_rhp = lfhatx + cp_dmgs.dmgs(lddi, lddd, t1, lambdad, t2, dim=dim) / nx
    sumlogf2_rhp = np.sum(logf2_rhp)
    pwaic1_rhp = 2 * (sumlogf1_rhp - sumlogf2_rhp)
    
    # alternative version uses the variance thing for the second term
    
    # this version of it is a variance
    # it penalizes more...is there really a factor of 2 needed
    t2inner = np.zeros((dim, dim, nx))
    for i in range(nx):
        t1[:, i] = 2 * lfhatxof[i] * f1f[:, i]
        t2inner[:, :, i] = f2f[:, :, i] * lfhatx[i] + outerf1f[:, :, i] * omlfhatx[i] / fhatx[i]
        t2[:, :, i] = 2 * t2inner[:, :, i] / fhatx[i]
    
    dq = cp_dmgs.dmgs(lddi, lddd, t1, lambdad, t2, dim=dim)
    sumvlogf_rhp = np.sum(lfhatx * lfhatx + dq / nx - logf2_rhp * logf2_rhp)
    pwaic2_rhp = sumvlogf_rhp
    
    waic1 = np.zeros(3)
    waic2 = np.zeros(3)
    waic1[0] = lppd_rhp
    waic1[1] = -pwaic1_rhp
    waic1[2] = waic1[0] + waic1[1]
    waic2[0] = lppd_rhp
    waic2[1] = -pwaic2_rhp
    waic2[2] = waic2[0] + waic2[1]
    
    return {'waic1': waic1, 'waic2': waic2}

def make_maic(ml_value, nparams):
    """
    Calculate MAIC
    Returns Vector of 3 values - the two components of MAIC, and their sum
    """
    maic = np.zeros(3)
    maic[0] = ml_value
    maic[1] = -nparams
    maic[2] = maic[0] + maic[1]
    return maic

def rust_pumethod():
    method = ("The cp results are based posterior simulation using "
              "ratio of uniforms sampling (RUST), "
              "using the predictive matching right Haar prior.")
    method = textwrap.fill(method, width=10000)
    
    return method

def analytic_cpmethod():
    method = ("The cp results are based on an analytic solution of "
              "the Bayesian prediction integral, "
              "using the predictive matching right Haar prior.")
    method = textwrap.fill(method, width=10000)
    
    return method

def rhp_dmgs_cpmethod():
    method = ("The cp results are based on the DMGS approximation of "
              "the Bayesian prediction integral, "
              "using the predictive matching right Haar prior.")
    method = textwrap.fill(method, width=10000)
    
    return method

def crhpflat_dmgs_cpmethod():
    method = ("The cp results are based on the DMGS approximation of "
              "the Bayesian prediction integral, "
              "using the CRHP/flat prior.")
    method = textwrap.fill(method, width=10000)
    
    return method

def adhoc_dmgs_cpmethod():
    method = ("The cp results are based on the DMGS approximation of "
              "the Bayesian prediction integral, "
              "using an ad-hoc prior.")
    method = textwrap.fill(method, width=10000)
    
    return method

def makeq(yy, pp):
    """Calculates quantiles from simulations by inverting the Hazen CDF"""
    yy = np.array(yy)
    pp = np.array(pp)
    nyy = len(yy)
    npp = len(pp)
    syy = np.sort(yy)
    lambda_vals = nyy * pp + 0.5
    qq = np.zeros(npp)
    aa = np.floor(lambda_vals).astype(int)
    eps = lambda_vals - aa
    
    for ii in range(npp):
        if lambda_vals[ii] <= 1:
            qq[ii] = syy[0]
        elif lambda_vals[ii] >= nyy:
            qq[ii] = syy[nyy - 1]
        else:
            qq[ii] = (1 - eps[ii]) * syy[aa[ii] - 1] + eps[ii] * syy[aa[ii]]
    
    return qq

def nopdfcdfmsg():
    """
    Message to explain why GEV and GPD d*** and p*** routines
    don't return DMGS pdfs and cdfs
    """
    msg = "For the pdf and cdf for the " \
    " and GPD, considered as a function of the rv, DMGS doesn't return anything."
    msg = msg + " That's because DMGS can't work outside the range limits."
    msg = msg + " Instead, you could use:"
    msg = msg + " (a) q***, for the inverse CDF, or"
    msg = msg + " (b) q***, with pdf=TRUE, which returns the pdf as a function of probability, or"
    msg = msg + " (c) d*** or p***, with rust=TRUE, which uses rust to generate the pdf and cdf."
    
    return msg