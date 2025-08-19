import numpy as np
import scipy.stats as stats
import scipy.optimize as optimize
import scipy.integrate as integrate
import sys

from . import utils as cp_utils
from . import evaluate_dmgs_equation as cp_dmgs
from . import gamma_derivs


def gamma_waic(waicscores, x, v1hat, fd1, v2hat, fd2, lddi, lddd, lambdad, aderivs):
    """
    Waic
    
    Parameters
    ----------
    waicscores : bool
        Whether to calculate WAIC scores
    x : array-like
        Data values
    v1hat : float
        Shape parameter estimate
    fd1 : float
        Step size for v1 finite differences
    v2hat : float
        Scale parameter estimate  
    fd2 : float
        Step size for v2 finite differences
    lddi : ndarray
        Inverse of second derivative of observed log-likelihood
    lddd : ndarray
        Third derivative of observed log-likelihood
    lambdad : array-like
        Lambda parameter vector
    aderivs : bool
        Whether to use analytical derivatives
        
    Returns
    -------
    dict
        Dictionary with waic1 and waic2 results
    """
    if waicscores:
        if aderivs:
            f1f = gamma_derivs.gamma_f1fa(x, v1hat, v2hat)
        else:
            f1f = gamma_f1f(x, v1hat, fd1, v2hat, fd2)
        
        if aderivs:
            f2f = gamma_derivs.gamma_f2fa(x, v1hat, v2hat)
        else:
            f2f = gamma_f2f(x, v1hat, fd1, v2hat, fd2)
        
        fhatx = stats.gamma.pdf(x, a=v1hat, scale=v2hat)
        waic = cp_utils.make_waic(x, fhatx, lddi, lddd, f1f, lambdad, f2f, dim=2)
        waic1 = waic['waic1']
        waic2 = waic['waic2']
    else:
        waic1 = "waicscores not selected"
        waic2 = "waicscores not selected"
    
    return {'waic1': waic1, 'waic2': waic2}

def gamma_logf(params, x):
    """
    Logf for RUST
    
    Parameters
    ----------
    params : array-like
        Parameters [shape, scale]
    x : array-like
        Data values
        
    Returns
    -------
    float
        Log-likelihood value
    """
    sh = max(params[0], sys.float_info.epsilon)
    sc = max(params[1], sys.float_info.epsilon)
    logf = np.sum(stats.gamma.logpdf(x, a=sh, scale=sc)) - np.log(sh) - np.log(sc)
    return logf

def gamma_loglik(vv, x):
    """
    log-likelihood function
    
    Parameters
    ----------
    vv : array-like
        Parameters [shape, scale]
    x : array-like
        Data values
        
    Returns
    -------
    float
        Log-likelihood value
    """
    n = len(x)
    loglik = np.sum(stats.gamma.logpdf(x, a=max(vv[0], sys.float_info.epsilon), 
                                      scale=max(vv[1], sys.float_info.epsilon)))
    return loglik

def gamma_lmn(x, v1, fd1, v2, fd2, mm, nn):
    """
    One component of the second derivative of the normalized log-likelihood
    
    Parameters
    ----------
    x : array-like
        Data values
    v1 : float
        Shape parameter
    fd1 : float
        Step size for v1 finite differences
    v2 : float
        Scale parameter
    fd2 : float
        Step size for v2 finite differences
    mm : int
        First parameter index (1-based from R, converted to 0-based)
    nn : int
        Second parameter index (1-based from R, converted to 0-based)
        
    Returns
    -------
    float
        Second derivative component
    """
    # Convert from R's 1-based to Python's 0-based indexing
    mm = mm - 1
    nn = nn - 1
    
    d1 = fd1 * v1
    d2 = fd2 * v2
    net3 = np.zeros((3, 2))
    net4 = np.zeros((4, 2))
    lmn = np.zeros(4)
    dd = np.array([d1, d2])
    vv = np.array([v1, v2])
    vvd = np.zeros(2)
    nx = len(x)
    
    # different
    if mm != nn:
        net4[:, mm] = [-1, -1, 1, 1]
        net4[:, nn] = [-1, 1, -1, 1]
        for i in range(4):
            for j in range(2):
                vvd[j] = vv[j] + net4[i, j] * dd[j]
            lmn[i] = np.sum(stats.gamma.logpdf(x, a=vvd[0], scale=vvd[1])) / nx
        dld = (lmn[0] - lmn[1] - lmn[2] + lmn[3]) / (4 * dd[mm] * dd[nn])
    # same
    else:
        net3[:, mm] = [-1, 0, 1]
        for i in range(3):
            for j in range(2):
                vvd[j] = vv[j] + net3[i, j] * dd[j]
            lmn[i] = np.sum(stats.gamma.logpdf(x, a=vvd[0], scale=vvd[1])) / nx
        dld = (lmn[0] - 2 * lmn[1] + lmn[2]) / (dd[mm] * dd[mm])
    
    return dld

def gamma_ldd(x, v1, fd1, v2, fd2):
    """
    Second derivative matrix of the normalized log-likelihood
    
    Parameters
    ----------
    x : array-like
        Data values
    v1 : float
        Shape parameter
    fd1 : float
        Step size for v1 finite differences
    v2 : float
        Scale parameter
    fd2 : float
        Step size for v2 finite differences
        
    Returns
    -------
    ndarray
        2x2 second derivative matrix
    """
    ldd = np.zeros((2, 2))
    for i in range(1, 3):  # R's 1:2
        for j in range(i, 3):  # R's i:2
            ldd[i-1, j-1] = gamma_lmn(x, v1, fd1, v2, fd2, i, j)
    
    for i in range(2, 0, -1):  # R's 2:1
        for j in range(1, i):  # R's 1:(i-1)
            ldd[i-1, j-1] = ldd[j-1, i-1]
    
    return ldd

def gamma_gmn(alpha, v1, fd1, v2, fd2, mm, nn):
    """
    One component of the second derivative of the expected log-likelihood
    
    Parameters
    ----------
    alpha : array-like
        Alpha values
    v1 : float
        Shape parameter
    fd1 : float
        Step size for v1 finite differences
    v2 : float
        Scale parameter
    fd2 : float
        Step size for v2 finite differences
    mm : int
        First parameter index (1-based from R, converted to 0-based)
    nn : int
        Second parameter index (1-based from R, converted to 0-based)
        
    Returns
    -------
    ndarray
        Derivative component values
    """
    # Convert from R's 1-based to Python's 0-based indexing
    mm = mm - 1
    nn = nn - 1
    
    nx = len(alpha)
    d1 = fd1 * v1
    d2 = fd2 * v2
    x = stats.gamma.ppf(1 - alpha, a=v1, scale=v2)
    net3 = np.zeros((3, 2))
    net4 = np.zeros((4, 2))
    lmn = np.zeros((nx, 4))
    dd = np.array([d1, d2])
    vv = np.array([v1, v2])
    vvd = np.zeros(2)
    nx = len(x)
    
    # different
    if mm != nn:
        net4[:, mm] = [-1, -1, 1, 1]
        net4[:, nn] = [-1, 1, -1, 1]
        for i in range(4):
            for j in range(2):
                vvd[j] = vv[j] + net4[i, j] * dd[j]
            lmn[:, i] = stats.gamma.logpdf(x, a=vvd[0], scale=vvd[1])
        dld = (lmn[:, 0] - lmn[:, 1] - lmn[:, 2] + lmn[:, 3]) / (4 * dd[mm] * dd[nn])
    # same
    else:
        net3[:, mm] = [-1, 0, 1]
        for i in range(3):
            for j in range(2):
                vvd[j] = vv[j] + net3[i, j] * dd[j]
            lmn[:, i] = stats.gamma.logpdf(x, a=vvd[0], scale=vvd[1])
        dld = (lmn[:, 0] - 2 * lmn[:, 1] + lmn[:, 2]) / (dd[mm] * dd[mm])
    
    return dld

def gamma_gg(v1, fd1, v2, fd2):
    """
    Second derivative matrix of the expected log-likelihood
    
    Parameters
    ----------
    v1 : float
        Shape parameter
    fd1 : float
        Step size for v1 finite differences
    v2 : float
        Scale parameter
    fd2 : float
        Step size for v2 finite differences
        
    Returns
    -------
    ndarray
        2x2 expected information matrix
    """
    expinfmat = np.zeros((2, 2))
    for i in range(1, 3):  # R's 1:2
        for j in range(i, 3):  # R's i:2
            result, _ = integrate.quad(gamma_gmn, 0, 1, args=(v1, fd1, v2, fd2, i, j))
            expinfmat[i-1, j-1] = -result
    
    for i in range(2, 2+1):  # R's 2:2
        for j in range(1, i):  # R's 1:(i-1)
            expinfmat[i-1, j-1] = expinfmat[j-1, i-1]
    
    return expinfmat

def gamma_lmnp(x, v1, fd1, v2, fd2, mm, nn, rr):
    """
    One component of the third derivative of the normalized log-likelihood
    
    Parameters
    ----------
    x : array-like
        Data values
    v1 : float
        Shape parameter
    fd1 : float
        Step size for v1 finite differences
    v2 : float
        Scale parameter
    fd2 : float
        Step size for v2 finite differences
    mm : int
        First parameter index (1-based from R, converted to 0-based)
    nn : int
        Second parameter index (1-based from R, converted to 0-based)
    rr : int
        Third parameter index (1-based from R, converted to 0-based)
        
    Returns
    -------
    float
        Third derivative component
    """
    # Convert from R's 1-based to Python's 0-based indexing
    mm = mm - 1
    nn = nn - 1
    rr = rr - 1
    
    d1 = fd1 * v1
    d2 = fd2 * v2
    net4 = np.zeros((4, 2))
    net6 = np.zeros((6, 2))
    net8 = np.zeros((8, 2))
    lmn = np.zeros(8)
    dd = np.array([d1, d2])
    vv = np.array([v1, v2])
    vvd = np.zeros(2)
    nx = len(x)
    
    # all diff
    if (mm != nn) and (nn != rr) and (rr != mm):
        net8[:, mm] = [-1, 1, -1, 1, -1, 1, -1, 1]
        net8[:, nn] = [-1, -1, 1, 1, -1, -1, 1, 1]
        net8[:, rr] = [-1, -1, -1, -1, 1, 1, 1, 1]
        for i in range(8):
            for j in range(2):  # Only 2 parameters, not 3
                vvd[j] = vv[j] + net8[i, j] * dd[j]
            lmn[i] = np.sum(stats.gamma.logpdf(x, a=vvd[0], scale=vvd[1])) / nx
        dld1 = (lmn[1] - lmn[0]) / (2 * dd[mm])
        dld2 = (lmn[3] - lmn[2]) / (2 * dd[mm])
        dld21 = (dld2 - dld1) / (2 * dd[nn])
        dld3 = (lmn[5] - lmn[4]) / (2 * dd[mm])
        dld4 = (lmn[7] - lmn[6]) / (2 * dd[mm])
        dld43 = (dld4 - dld3) / (2 * dd[nn])
        dld = (dld43 - dld21) / (2 * dd[rr])
    # all 3 the same
    elif (mm == nn) and (nn == rr):
        net4[:, mm] = [-2, -1, 1, 2]
        for i in range(4):
            for j in range(2):
                vvd[j] = vv[j] + net4[i, j] * dd[j]
            lmn[i] = np.sum(stats.gamma.logpdf(x, a=vvd[0], scale=vvd[1])) / nx
        dld = (-lmn[0] + 2 * lmn[1] - 2 * lmn[2] + lmn[3]) / (2 * dd[mm] * dd[mm] * dd[mm])
    else:
        # 2 the same
        # mm is the repeated one, nn is the other one
        if mm == nn:
            m2 = mm
            n2 = rr
        elif mm == rr:
            m2 = mm
            n2 = nn
        elif nn == rr:
            m2 = nn
            n2 = mm
        net6[:, m2] = [-1, 0, 1, -1, 0, 1]
        net6[:, n2] = [-1, -1, -1, 1, 1, 1]
        for i in range(6):
            for j in range(2):
                vvd[j] = vv[j] + net6[i, j] * dd[j]
            lmn[i] = np.sum(stats.gamma.logpdf(x, a=vvd[0], scale=vvd[1])) / nx
        dld1 = (lmn[2] - 2 * lmn[1] + lmn[0]) / (dd[m2] * dd[m2])
        dld2 = (lmn[5] - 2 * lmn[4] + lmn[3]) / (dd[m2] * dd[m2])
        dld = (dld2 - dld1) / (2 * dd[n2])
    
    return dld

def gamma_lddd(x, v1, fd1, v2, fd2):
    """
    Third derivative tensor of the normalized log-likelihood
    
    Parameters
    ----------
    x : array-like
        Data values
    v1 : float
        Shape parameter
    fd1 : float
        Step size for v1 finite differences
    v2 : float
        Scale parameter
    fd2 : float
        Step size for v2 finite differences
        
    Returns
    -------
    ndarray
        2x2x2 third derivative tensor
    """
    # calculate the unique values
    lddd = np.zeros((2, 2, 2))
    for i in range(1, 3):  # R's 1:2
        for j in range(i, 3):  # R's i:2
            for k in range(j, 3):  # R's j:2
                lddd[i-1, j-1, k-1] = gamma_lmnp(x, v1, fd1, v2, fd2, i, j, k)
    
    # steves dumb algorithm for filling in the non-unique values
    for i in range(2):
        for j in range(2):
            for k in range(2):
                a = [i, j, k]
                b = sorted(a)
                lddd[a[0], a[1], a[2]] = lddd[b[0], b[1], b[2]]
    
    return lddd

def gamma_f1f(y, v1, fd1, v2, fd2):
    """
    DMGS equation 3.3, f1 term
    
    Parameters
    ----------
    y : array-like
        Data values
    v1 : float
        Shape parameter
    fd1 : float
        Step size for v1 finite differences
    v2 : float
        Scale parameter
    fd2 : float
        Step size for v2 finite differences
        
    Returns
    -------
    ndarray
        2 x len(y) matrix of first derivatives
    """
    d1 = fd1 * v1
    d2 = fd2 * v2
    # v1 stuff
    v1m1 = v1 - 1 * d1
    v100 = v1 + 0 * d1
    v1p1 = v1 + 1 * d1
    # v2 stuff
    v2m1 = v2 - 1 * d2
    v200 = v2 + 0 * d2
    v2p1 = v2 + 1 * d2
    # v1 derivatives
    F1m1 = stats.gamma.pdf(y, a=v1m1, scale=v200)
    F1p1 = stats.gamma.pdf(y, a=v1p1, scale=v200)
    # v2 derivatives
    F2m1 = stats.gamma.pdf(y, a=v100, scale=v2m1)
    F2p1 = stats.gamma.pdf(y, a=v100, scale=v2p1)
    f1 = np.zeros((2, len(y)))
    f1[0, :] = (F1p1 - F1m1) / (2 * d1)
    f1[1, :] = (F2p1 - F2m1) / (2 * d2)
    return f1

def gamma_p1f(y, v1, fd1, v2, fd2):
    """
    DMGS equation 3.3, p1 term
    
    Parameters
    ----------
    y : array-like
        Data values
    v1 : float
        Shape parameter
    fd1 : float
        Step size for v1 finite differences
    v2 : float
        Scale parameter
    fd2 : float
        Step size for v2 finite differences
        
    Returns
    -------
    ndarray
        2 x len(y) matrix of first derivatives of CDF
    """
    d1 = fd1 * v1
    d2 = fd2 * v2
    # v1 stuff
    v1m1 = v1 - 1 * d1
    v100 = v1 + 0 * d1
    v1p1 = v1 + 1 * d1
    # v2 stuff
    v2m1 = v2 - 1 * d2
    v200 = v2 + 0 * d2
    v2p1 = v2 + 1 * d2
    # v1 derivatives
    F1m1 = stats.gamma.cdf(y, a=v1m1, scale=v200)
    F1p1 = stats.gamma.cdf(y, a=v1p1, scale=v200)
    # v2 derivatives
    F2m1 = stats.gamma.cdf(y, a=v100, scale=v2m1)
    F2p1 = stats.gamma.cdf(y, a=v100, scale=v2p1)
    p1 = np.zeros((2, len(y)))
    p1[0, :] = (F1p1 - F1m1) / (2 * d1)
    p1[1, :] = (F2p1 - F2m1) / (2 * d2)
    return p1

def gamma_mu1f(alpha, v1, fd1, v2, fd2):
    """
    DMGS equation 3.3, mu1 term
    
    Parameters
    ----------
    alpha : array-like
        Alpha values
    v1 : float
        Shape parameter
    fd1 : float
        Step size for v1 finite differences
    v2 : float
        Scale parameter
    fd2 : float
        Step size for v2 finite differences
        
    Returns
    -------
    ndarray
        2 x len(alpha) matrix of mu1 values
    """
    q00 = stats.gamma.ppf(1 - alpha, a=v1, scale=v2)
    d1 = fd1 * v1
    d2 = fd2 * v2
    # v1 stuff
    v1m1 = v1 - 1 * d1
    v100 = v1 + 0 * d1
    v1p1 = v1 + 1 * d1
    # v2 stuff
    v2m1 = v2 - 1 * d2
    v200 = v2 + 0 * d2
    v2p1 = v2 + 1 * d2
    # v1 derivatives
    F1m1 = stats.gamma.cdf(q00, a=v1m1, scale=v200)
    F1p1 = stats.gamma.cdf(q00, a=v1p1, scale=v200)
    # v2 derivatives
    F2m1 = stats.gamma.cdf(q00, a=v100, scale=v2m1)
    F2p1 = stats.gamma.cdf(q00, a=v100, scale=v2p1)
    mu1 = np.zeros((2, len(alpha)))
    mu1[0, :] = -(F1p1 - F1m1) / (2 * d1)
    mu1[1, :] = -(F2p1 - F2m1) / (2 * d2)
    return mu1

def gamma_f2f(y, v1, fd1, v2, fd2):
    """
    DMGS equation 3.3, f2 term
    
    Parameters
    ----------
    y : array-like
        Data values
    v1 : float
        Shape parameter
    fd1 : float
        Step size for v1 finite differences
    v2 : float
        Scale parameter
    fd2 : float
        Step size for v2 finite differences
        
    Returns
    -------
    ndarray
        2 x 2 x len(y) array of second derivatives
    """
    d1 = fd1 * v1
    d2 = fd2 * v2
    # v1 stuff
    v1m2 = v1 - 2 * d1
    v1m1 = v1 - 1 * d1
    v100 = v1 + 0 * d1
    v1p1 = v1 + 1 * d1
    v1p2 = v1 + 2 * d1
    # v2 stuff
    v2m2 = v2 - 2 * d2
    v2m1 = v2 - 1 * d2
    v200 = v2 + 0 * d2
    v2p1 = v2 + 1 * d2
    v2p2 = v2 + 2 * d2
    F1m2 = stats.gamma.pdf(y, a=v1m2, scale=v200)
    F1m1 = stats.gamma.pdf(y, a=v1m1, scale=v200)
    F100 = stats.gamma.pdf(y, a=v100, scale=v200)
    F1p1 = stats.gamma.pdf(y, a=v1p1, scale=v200)
    F1p2 = stats.gamma.pdf(y, a=v1p2, scale=v200)
    # v2 derivative
    F2m2 = stats.gamma.pdf(y, a=v100, scale=v2m2)
    F2m1 = stats.gamma.pdf(y, a=v100, scale=v2m1)
    F200 = stats.gamma.pdf(y, a=v100, scale=v200)
    F2p1 = stats.gamma.pdf(y, a=v100, scale=v2p1)
    F2p2 = stats.gamma.pdf(y, a=v100, scale=v2p2)
    # cross derivative
    Fcm1m1 = stats.gamma.pdf(y, a=v1m1, scale=v2m1)
    Fcm1p1 = stats.gamma.pdf(y, a=v1m1, scale=v2p1)
    Fcp1m1 = stats.gamma.pdf(y, a=v1p1, scale=v2m1)
    Fcp1p1 = stats.gamma.pdf(y, a=v1p1, scale=v2p1)
    f2 = np.zeros((2, 2, len(y)))
    f2[0, 0, :] = (F1p1 - 2 * F100 + F1m1) / (d1 * d1)
    f2[1, 1, :] = (F2p1 - 2 * F200 + F2m1) / (d2 * d2)
    f2[0, 1, :] = (Fcp1p1 - Fcm1p1 - Fcp1m1 + Fcm1m1) / (4 * d1 * d2)
    # copy
    f2[1, 0, :] = f2[0, 1, :]
    return f2

def gamma_p2f(y, v1, fd1, v2, fd2):
    """
    DMGS equation 3.3, p2 term
    
    Parameters
    ----------
    y : array-like
        Data values
    v1 : float
        Shape parameter
    fd1 : float
        Step size for v1 finite differences
    v2 : float
        Scale parameter
    fd2 : float
        Step size for v2 finite differences
        
    Returns
    -------
    ndarray
        2 x 2 x len(y) array of second derivatives of CDF
    """
    d1 = fd1 * v1
    d2 = fd2 * v2
    # v1 stuff
    v1m2 = v1 - 2 * d1
    v1m1 = v1 - 1 * d1
    v100 = v1 + 0 * d1
    v1p1 = v1 + 1 * d1
    v1p2 = v1 + 2 * d1
    # v2 stuff
    v2m2 = v2 - 2 * d2
    v2m1 = v2 - 1 * d2
    v200 = v2 + 0 * d2
    v2p1 = v2 + 1 * d2
    v2p2 = v2 + 2 * d2
    F1m2 = stats.gamma.cdf(y, a=v1m2, scale=v200)
    F1m1 = stats.gamma.cdf(y, a=v1m1, scale=v200)
    F100 = stats.gamma.cdf(y, a=v100, scale=v200)
    F1p1 = stats.gamma.cdf(y, a=v1p1, scale=v200)
    F1p2 = stats.gamma.cdf(y, a=v1p2, scale=v200)
    # v2 derivative
    F2m2 = stats.gamma.cdf(y, a=v100, scale=v2m2)
    F2m1 = stats.gamma.cdf(y, a=v100, scale=v2m1)
    F200 = stats.gamma.cdf(y, a=v100, scale=v200)
    F2p1 = stats.gamma.cdf(y, a=v100, scale=v2p1)
    F2p2 = stats.gamma.cdf(y, a=v100, scale=v2p2)
    # cross derivative
    Fcm1m1 = stats.gamma.cdf(y, a=v1m1, scale=v2m1)
    Fcm1p1 = stats.gamma.cdf(y, a=v1m1, scale=v2p1)
    Fcp1m1 = stats.gamma.cdf(y, a=v1p1, scale=v2m1)
    Fcp1p1 = stats.gamma.cdf(y, a=v1p1, scale=v2p1)
    p2 = np.zeros((2, 2, len(y)))
    p2[0, 0, :] = (F1p1 - 2 * F100 + F1m1) / (d1 * d1)
    p2[1, 1, :] = (F2p1 - 2 * F200 + F2m1) / (d2 * d2)
    p2[0, 1, :] = (Fcp1p1 - Fcm1p1 - Fcp1m1 + Fcm1m1) / (4 * d1 * d2)
    # copy
    p2[1, 0, :] = p2[0, 1, :]
    return p2

def gamma_mu2f(alpha, v1, fd1, v2, fd2):
    """
    DMGS equation 3.3, mu2 term
    
    Parameters
    ----------
    alpha : array-like
        Alpha values
    v1 : float
        Shape parameter
    fd1 : float
        Step size for v1 finite differences
    v2 : float
        Scale parameter
    fd2 : float
        Step size for v2 finite differences
        
    Returns
    -------
    ndarray
        2 x 2 x len(alpha) array of mu2 values
    """
    q00 = stats.gamma.ppf(1 - alpha, a=v1, scale=v2)
    d1 = fd1 * v1
    d2 = fd2 * v2
    # v1 stuff
    v1m2 = v1 - 2 * d1
    v1m1 = v1 - 1 * d1
    v100 = v1 + 0 * d1
    v1p1 = v1 + 1 * d1
    v1p2 = v1 + 2 * d1
    # v2 stuff
    v2m2 = v2 - 2 * d2
    v2m1 = v2 - 1 * d2
    v200 = v2 + 0 * d2
    v2p1 = v2 + 1 * d2
    v2p2 = v2 + 2 * d2
    mu2 = np.zeros((2, 2, len(alpha)))
    F1m2 = stats.gamma.cdf(q00, a=v1m2, scale=v200)
    F1m1 = stats.gamma.cdf(q00, a=v1m1, scale=v200)
    F100 = stats.gamma.cdf(q00, a=v100, scale=v200)
    F1p1 = stats.gamma.cdf(q00, a=v1p1, scale=v200)
    F1p2 = stats.gamma.cdf(q00, a=v1p2, scale=v200)
    # v2 derivative
    F2m2 = stats.gamma.cdf(q00, a=v100, scale=v2m2)
    F2m1 = stats.gamma.cdf(q00, a=v100, scale=v2m1)
    F200 = stats.gamma.cdf(q00, a=v100, scale=v200)
    F2p1 = stats.gamma.cdf(q00, a=v100, scale=v2p1)
    F2p2 = stats.gamma.cdf(q00, a=v100, scale=v2p2)
    # cross derivative
    Fcm1m1 = stats.gamma.cdf(q00, a=v1m1, scale=v2m1)
    Fcm1p1 = stats.gamma.cdf(q00, a=v1m1, scale=v2p1)
    Fcp1m1 = stats.gamma.cdf(q00, a=v1p1, scale=v2m1)
    Fcp1p1 = stats.gamma.cdf(q00, a=v1p1, scale=v2p1)
    mu2[0, 0, :] = -(F1p1 - 2 * F100 + F1m1) / (d1 * d1)
    mu2[1, 1, :] = -(F2p1 - 2 * F200 + F2m1) / (d2 * d2)
    mu2[0, 1, :] = -(Fcp1p1 - Fcm1p1 - Fcp1m1 + Fcm1m1) / (4 * d1 * d2)
    # copy
    mu2[1, 0, :] = mu2[0, 1, :]
    return mu2

def gamma_means(means, ml_params, lddi, lddd, lambdad_cp, nx, dim=2):
    """
    MLE and RHP predictive means
    
    Parameters
    ----------
    means : bool
        Whether to calculate means
    ml_params : array-like
        Maximum likelihood parameter estimates [shape, scale]
    lddi : ndarray
        Inverse of second derivative matrix
    lddd : ndarray
        Third derivative tensor
    lambdad_cp : array-like
        Lambda parameter vector
    nx : int
        Sample size
    dim : int
        Number of parameters (default 2)
        
    Returns
    -------
    dict
        Dictionary with ml_mean and cp_mean
    """
    # v1 is shape
    # v2 is scale
    if means:
        v1 = ml_params[0]
        v2 = ml_params[1]
        
        # ml mean
        ml_mean = v1 * v2
        
        # cp mean
        meand1 = np.zeros((2, 1))
        meand1[0, 0] = v2
        meand1[1, 0] = v1
        
        meand2 = np.zeros((2, 2, 1))
        meand2[0, 0, 0] = 0
        meand2[0, 1, 0] = 1
        meand2[1, 0, 0] = 1
        meand2[1, 1, 0] = 0
        
        dmean = cp_dmgs.dmgs(lddi, lddd, meand1, lambdad_cp, meand2, dim=2)
        cp_mean = ml_mean + dmean / nx
    else:
        ml_mean = "means not selected"
        cp_mean = "means not selected"
    
    return {'ml_mean': ml_mean, 'cp_mean': cp_mean}

def gamma_logscores(logscores, x, fd1=0.01, fd2=0.01, aderivs=True):
    """
    Log scores for MLE and RHP predictions calculated using leave-one-out
    
    Parameters
    ----------
    logscores : bool
        Whether to calculate log scores
    x : array-like
        Data values
    fd1 : float
        Step size for v1 finite differences (default 0.01)
    fd2 : float
        Step size for v2 finite differences (default 0.01)
    aderivs : bool
        Whether to use analytical derivatives (default True)
        
    Returns
    -------
    dict
        Dictionary with ml_oos_logscore and cp_oos_logscore
    """
    if logscores:
        nx = len(x)
        ml_oos_logscore = 0
        cp_oos_logscore = 0
        for i in range(nx):
            x1 = np.delete(x, i)
            
            dd = dgammasub(x1, x[i], fd1, fd2, aderivs)
            
            ml_params = dd['ml_params']
            
            ml_pdf = dd['ml_pdf']
            ml_oos_logscore = ml_oos_logscore + np.log(ml_pdf)
            
            cp_pdf = dd['cp_pdf']
            cp_oos_logscore = cp_oos_logscore + np.log(max(cp_pdf, sys.float_info.epsilon))
    else:
        ml_oos_logscore = "logscores not selected"
        cp_oos_logscore = "logscores not selected"
    
    return {'ml_oos_logscore': ml_oos_logscore, 'cp_oos_logscore': cp_oos_logscore}


def dgammasub(x, y, fd1=0.01, fd2=0.01, aderivs=True):
    """
    Densities from MLE and RHP
    
    Parameters
    ----------
    x : array-like
        Training data values
    y : float
        Test point
    fd1 : float
        Step size for v1 finite differences (default 0.01)
    fd2 : float
        Step size for v2 finite differences (default 0.01)
    aderivs : bool
        Whether to use analytical derivatives (default True)
        
    Returns
    -------
    dict
        Dictionary with ml_params, ml_pdf, cp_pdf, ml_cdf, cp_cdf
    """
    nx = len(x)
    
    opt = optimize.minimize(lambda params: -gamma_loglik(params, x), 
                          x0=[1, 1], method='BFGS')
    v1hat = opt.x[0]
    v2hat = opt.x[1]
    ml_params = np.array([v1hat, v2hat])
    
    # mle
    ml_pdf = stats.gamma.pdf(y, a=v1hat, scale=v2hat)
    ml_cdf = stats.gamma.cdf(y, a=v1hat, scale=v2hat)
    
    # cp
    if aderivs:
        ldd = gamma_derivs.gamma_ldda(x, v1hat, v2hat)
    else:
        ldd = gamma_ldd(x, v1hat, fd1, v2hat, fd2)
    lddi = np.linalg.inv(ldd)
    
    if aderivs:
        lddd = gamma_derivs.gamma_lddda(x, v1hat, v2hat)
    else:
        lddd = gamma_lddd(x, v1hat, fd1, v2hat, fd2)
    
    if aderivs:
        f1 = gamma_derivs.gamma_f1fa(y, v1hat, v2hat)
    else:
        f1 = gamma_f1f(y, v1hat, fd1, v2hat, fd2)
    
    if aderivs:
        f2 = gamma_derivs.gamma_f2fa(y, v1hat, v2hat)
    else:
        f2 = gamma_f2f(y, v1hat, fd1, v2hat, fd2)
    
    p1 = gamma_p1f(y, v1hat, fd1, v2hat, fd2)
    p2 = gamma_p2f(y, v1hat, fd1, v2hat, fd2)
    lambdad_cp = np.array([-1/v1hat, -1/v2hat])
    df1 = cp_dmgs.dmgs(lddi, lddd, f1, lambdad_cp, f2, dim=2)
    dp1 = cp_dmgs.dmgs(lddi, lddd, p1, lambdad_cp, p2, dim=2)
    cp_pdf = np.maximum(ml_pdf + df1/nx, 0)
    cp_cdf = np.minimum(np.maximum(ml_cdf + dp1/nx, 0), 1)
    
    # return
    return {
        'ml_params': ml_params,
        'ml_pdf': ml_pdf,
        'cp_pdf': cp_pdf,
        'ml_cdf': ml_cdf,
        'cp_cdf': cp_cdf
    }