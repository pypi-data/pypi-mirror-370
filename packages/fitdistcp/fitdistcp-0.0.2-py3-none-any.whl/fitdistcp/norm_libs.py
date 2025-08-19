import numpy as np
import sys
from scipy import stats

from . import utils as cp_utils
from . import norm_derivs


def norm_waic(waicscores, x, v1hat, v2hat):
    """
    Waic
    
    Parameters
    ----------
    waicscores : bool
        Whether to calculate WAIC scores
    x : array_like
        Data values
    v1hat : float
        Estimated parameter 1 (mean)
    v2hat : float
        Estimated parameter 2 (standard deviation)
        
    Returns
    -------
    dict
        Dictionary containing waic1 and waic2 results
    """
    if waicscores:
        f1f = norm_derivs.norm_f1fa(x, v1hat, v2hat)
        f2f = norm_derivs.norm_f2fa(x, v1hat, v2hat)
        ldd = norm_derivs.norm_ldda(x, v1hat, v2hat)
        lddi = np.linalg.inv(ldd)
        lddd = norm_derivs.norm_lddda(x, v1hat, v2hat)
        fhatx = stats.norm.pdf(x, loc=v1hat, scale=v2hat)
        lambdad_rhp = np.array([0, -1/v2hat])
        waic = cp_utils.make_waic(x, fhatx, lddi, lddd, f1f, lambdad_rhp, f2f, dim=2)
        waic1 = waic['waic1']
        waic2 = waic['waic2']
    else:
        waic1 = "waicscores not selected"
        waic2 = "waicscores not selected"
    
    return {'waic1': waic1, 'waic2': waic2}


def norm_logf(params, x):
    """
    Logf for RUST
    
    Parameters
    ----------
    params : array_like
        Parameter vector [mean, std_dev]
    x : array_like
        Data values
        
    Returns
    -------
    float
        Log-likelihood value
    """
    m = params[0]
    s = np.maximum(params[1], sys.float_info.epsilon)
    logf = np.sum(stats.norm.logpdf(x, loc=m, scale=s)) - np.log(s)
    return logf


def norm_ml_params(x):
    """
    Maximum likelihood estimator
    
    Parameters
    ----------
    x : array_like
        Data values
        
    Returns
    -------
    ndarray
        Vector of ML parameter estimates
    """
    mlparams = np.zeros(2)
    nx = len(x)
    mlparams[0] = np.mean(x)
    mlparams[1] = np.sqrt((nx-1)/nx) * np.std(x, ddof=1)
    return mlparams


def norm_unbiasedv_params(x):
    """
    Method of moments estimator
    
    Parameters
    ----------
    x : array_like
        Data values
        
    Returns
    -------
    ndarray
        Vector of parameter estimates
    """
    params = np.zeros(2)
    nx = len(x)
    params[0] = np.mean(x)
    params[1] = np.std(x, ddof=1)
    return params


def norm_logscores(logscores, x):
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
        
        for i in range(nx):  # 1:nx becomes 0:nx in Python
            x1 = np.concatenate([x[:i], x[i+1:]])  # x[-i] in R becomes this in Python
            
            dd = dnormsub(x1, x[i])
            ml_params = dd['ml_params']
            
            ml_pdf = dd['ml_pdf']
            ml_oos_logscore = ml_oos_logscore + np.log(ml_pdf)
            
            rh_pdf = dd['rh_pdf']
            rh_oos_logscore = rh_oos_logscore + np.log(rh_pdf)
    else:
        ml_oos_logscore = "logscores not selected"
        rh_oos_logscore = "logscores not selected"
    
    return {'ml_oos_logscore': ml_oos_logscore, 'rh_oos_logscore': rh_oos_logscore}


def dnormsub(x, y):
    """
    Densities from MLE and RHP
    
    Parameters
    ----------
    x : array_like
        Training data
    y : float
        Test point
        
    Returns
    -------
    dict
        Dictionary containing ml_params, ml_pdf, rh_pdf, ml_cdf, rh_cdf
    """
    nx = len(x)
    
    # ml
    ml_params = norm_ml_params(x)
    ml_pdf = stats.norm.pdf(y, loc=ml_params[0], scale=ml_params[1])
    ml_cdf = stats.norm.cdf(y, loc=ml_params[0], scale=ml_params[1])
    
    # rhp pdf
    # -first, convert sigma from maxlik to unbiased
    sgu = ml_params[1] * np.sqrt(nx/(nx-1))
    # then, convert sigma to predictive sigma
    sg1 = sgu * np.sqrt((nx+1)/nx)
    
    yd = (y - ml_params[0]) / sg1
    rh_pdf = stats.t.pdf(yd, df=nx-1) / sg1
    rh_pdf = np.maximum(rh_pdf, 0)
    
    # rhp cdf
    rh_cdf = stats.t.cdf(yd, df=nx-1)
    rh_cdf = np.minimum(np.maximum(rh_cdf, 0), 1)
    
    # return
    return {
        'ml_params': ml_params,
        'ml_pdf': ml_pdf,
        'rh_pdf': rh_pdf,
        'ml_cdf': ml_cdf,
        'rh_cdf': rh_cdf
    }
