import numpy as np
import scipy.stats
import scipy.special
import scipy.optimize
import sys

from . import utils as cp_utils
from . import evaluate_dmgs_equation as cp_dmgs
from . import weibull_derivs


def weibull_waic(waicscores, x, v1hat, v2hat, lddi, lddd, lambdad):
    """
    Waic for RUST
    
    Parameters
    ----------
    waicscores : bool
        Whether to calculate WAIC scores
    x : array_like
        Data values
    v1hat : float
        Shape parameter estimate
    v2hat : float
        Scale parameter estimate
    lddi : array_like
        Inverse of negative Hessian matrix
    lddd : array_like
        Third derivative array
    lambdad : array_like
        Lambda parameter for RHP
        
    Returns
    -------
    dict
        Dictionary containing waic1 and waic2 results
    """
    if waicscores:
        f1f = weibull_derivs.weibull_f1fa(x, v1hat, v2hat)
        f2f = weibull_derivs.weibull_f2fa(x, v1hat, v2hat)
        
        fhatx = scipy.stats.weibull_min.pdf(x, c=v1hat, scale=v2hat)
        waic = cp_utils.make_waic(x, fhatx, lddi, lddd, f1f, lambdad, f2f, dim=2)
        waic1 = waic['waic1']
        waic2 = waic['waic2']
    else:
        waic1 = "waicscores not selected"
        waic2 = "waicscores not selected"
    
    return {'waic1': waic1, 'waic2': waic2}

def weibull_logf(params, x):
    """
    Logf for RUST
    
    Parameters
    ----------
    params : array_like
        Parameters [shape, scale]
    x : array_like
        Data values
        
    Returns
    -------
    float
        Log-likelihood value with priors
    """
    sh = np.maximum(np.minimum(20, params[0]), np.sqrt(sys.float_info.epsilon))
    sc = np.maximum(params[1], np.sqrt(sys.float_info.epsilon))
    logf = np.sum(scipy.stats.weibull_min.logpdf(x, c=sh, scale=sc)) - np.log(sh) - np.log(sc)
    return logf

def weibull_loglik(vv, x):
    """
    log-likelihood function
    
    Parameters
    ----------
    vv : array_like
        Parameters [shape, scale]
    x : array_like
        Data values
        
    Returns
    -------
    float
        Log-likelihood value
    """
    n = len(x)
    shape_param = np.maximum(np.minimum(20, vv[0]), np.sqrt(sys.float_info.epsilon))
    scale_param = np.maximum(vv[1], np.sqrt(sys.float_info.epsilon))
    loglik = np.sum(scipy.stats.weibull_min.logpdf(x, c=shape_param, scale=scale_param))
    return loglik

def weibull_means(means, ml_params, lddi, lddd, lambdad_rhp, nx, dim=2):
    """
    MLE and RHP predictive means
    
    Parameters
    ----------
    means : bool
        Whether to calculate means
    ml_params : array_like
        ML parameter estimates [v1, v2]
    lddi : array_like
        Inverse of negative Hessian matrix
    lddd : array_like
        Third derivative array
    lambdad_rhp : array_like
        Lambda parameter for RHP
    nx : int
        Sample size
    dim : int, optional
        Dimension (default 2)
        
    Returns
    -------
    dict
        Dictionary containing ml_mean and rh_mean
    """
    # v1 is shape
    # v2 is scale
    if means:
        v1 = ml_params[0]
        v2 = ml_params[1]
        f1 = 1 + (1 / v1)
        iv12 = 1 / (v1 * v1)
        iv13 = 1 / (v1 * v1 * v1)
        
        # ml mean
        ml_mean = v2 * scipy.special.gamma(f1)
        
        # rhp mean
        meand1 = np.zeros((2, 1))
        meand1[0, 0] = -v2 * scipy.special.gamma(f1) * scipy.special.digamma(f1) * iv12
        meand1[1, 0] = scipy.special.gamma(f1)
        
        meand2 = np.zeros((2, 2, 1))
        meand2[0, 0, 0] = v2 * (scipy.special.gamma(f1) * scipy.special.polygamma(1, f1) * iv12 + 2 * scipy.special.gamma(f1) * scipy.special.digamma(f1) * iv13)
        meand2[0, 1, 0] = -scipy.special.gamma(f1) * scipy.special.digamma(f1) * iv12
        meand2[1, 0, 0] = meand2[0, 1, 0]
        meand2[1, 1, 0] = 0
        
        dmean = cp_dmgs.dmgs(lddi, lddd, meand1, lambdad_rhp, meand2, dim=2)
        rh_mean = ml_mean + dmean / nx
    else:
        ml_mean = "means not selected"
        rh_mean = "means not selected"
    
    return {'ml_mean': ml_mean, 'rh_mean': rh_mean}

def weibull_logscores(logscores, x):
    """
    Log scores for MLE and RHP predictions calculated using leave-one-out
    
    Parameters
    ----------
    logscores : bool
        Whether to calculate log scores
    x : array_like
        Data values
        
    Returns
    -------
    dict
        Dictionary containing ml_oos_logscore and rh_oos_logscore
    """
    if logscores:
        nx = len(x)
        ml_oos_logscore = 0
        rh_oos_logscore = 0
        
        for i in range(nx):
            # Create x1 by removing element at index i
            x1 = np.concatenate([x[:i], x[i+1:]])
            
            dd = dweibullsub(x1, x[i])
            
            ml_params = dd['ml_params']
            
            ml_pdf = dd['ml_pdf']
            ml_oos_logscore = ml_oos_logscore + np.log(ml_pdf)
            
            rh_pdf = dd['rh_pdf']
            rh_oos_logscore = rh_oos_logscore + np.log(np.maximum(rh_pdf, sys.float_info.epsilon))
    else:
        ml_oos_logscore = "logscores not selected"
        rh_oos_logscore = "logscores not selected"
    
    return {'ml_oos_logscore': ml_oos_logscore, 'rh_oos_logscore': rh_oos_logscore}

def dweibullsub(x, y):
    """
    Densities from MLE and RHP
    
    Parameters
    ----------
    x : array_like
        Training data
    y : float
        Prediction point
        
    Returns
    -------
    dict
        Dictionary containing ml_params, ml_pdf, rh_pdf, ml_cdf, rh_cdf
    """
    nx = len(x)
    
    # Optimization for MLE
    def neg_loglik(params):
        return -weibull_loglik(params, x)
    
    opt = scipy.optimize.minimize(neg_loglik, x0=np.array([1.0, 1.0]), method='BFGS')
    v1hat = opt.x[0]
    v2hat = opt.x[1]
    ml_params = np.array([v1hat, v2hat])
    
    # mle
    ml_pdf = scipy.stats.weibull_min.pdf(y, c=v1hat, scale=v2hat)
    ml_cdf = scipy.stats.weibull_min.cdf(y, c=v1hat, scale=v2hat)
    
    # rhp
    ldd = weibull_derivs.weibull_ldda(x, v1hat, v2hat)
    lddi = np.linalg.inv(ldd)
    lddd = weibull_derivs.weibull_lddda(x, v1hat, v2hat)
    
    f1 = weibull_derivs.weibull_f1fa(y, v1hat, v2hat)
    f2 = weibull_derivs.weibull_f2fa(y, v1hat, v2hat)
    
    p1 = weibull_derivs.weibull_p1fa(y, v1hat, v2hat)
    p2 = weibull_derivs.weibull_p2fa(y, v1hat, v2hat)
    
    lambdad_rhp = np.array([-1 / v1hat, -1 / v2hat])
    df1 = cp_dmgs.dmgs(lddi, lddd, f1, lambdad_rhp, f2, dim=2)
    dp1 = cp_dmgs.dmgs(lddi, lddd, p1, lambdad_rhp, p2, dim=2)
    rh_pdf = np.maximum(ml_pdf + df1 / nx, 0)
    rh_cdf = np.minimum(np.maximum(ml_cdf + dp1 / nx, 0), 1)
    
    # return
    return {
        'ml_params': ml_params,
        'ml_pdf': ml_pdf,
        'rh_pdf': rh_pdf,
        'ml_cdf': ml_cdf,
        'rh_cdf': rh_cdf
    }
