import numpy as np
import scipy.stats
import sys

from . import utils as cp_utils
from . import lnorm_derivs


def norm_ml_params(x):
    """Maximum likelihood parameters for normal distribution"""
    n = len(x)
    mean_est = np.mean(x)
    var_est = np.sum((x - mean_est)**2) / n
    sd_est = np.sqrt(var_est)
    return np.array([mean_est, sd_est])


def lnorm_waic(waicscores, x, v1hat, v2hat):
    """
    Waic for RUST
    
    Parameters
    ----------
    waicscores : bool
        Whether to calculate WAIC scores
    x : array-like
        Data values
    v1hat : float
        Estimated meanlog parameter
    v2hat : float
        Estimated sdlog parameter
    
    Returns
    -------
    dict
        Dictionary containing waic1 and waic2 scores
    """
    if waicscores:
        f1f = lnorm_derivs.lnorm_f1fa(x, v1hat, v2hat)
        f2f = lnorm_derivs.lnorm_f2fa(x, v1hat, v2hat)
        
        ldd = lnorm_derivs.lnorm_ldda(x, v1hat, v2hat)
        lddi = np.linalg.inv(ldd)
        lddd = lnorm_derivs.lnorm_lddda(x, v1hat, v2hat)
        fhatx = scipy.stats.lognorm.pdf(x, s=v2hat, scale=np.exp(v1hat))
        lambdad_rhp = np.array([0, -1/v2hat])
        waic = cp_utils.make_waic(x, fhatx, lddi, lddd, f1f, lambdad_rhp, f2f, dim=2)
        waic1 = waic['waic1']
        waic2 = waic['waic2']
    else:
        waic1 = "waicscores not selected"
        waic2 = "waicscores not selected"
    
    return {'waic1': waic1, 'waic2': waic2}


def lnorm_logf(params, x):
    """
    Logf for RUST
    
    Parameters
    ----------
    params : array-like
        Parameters [meanlog, sdlog]
    x : array-like
        Data values
    
    Returns
    -------
    float
        Log-likelihood value
    """
    m = params[0]
    s = np.maximum(params[1], sys.float_info.epsilon)
    logf = np.sum(scipy.stats.lognorm.logpdf(x, s=s, scale=np.exp(m))) - np.log(s)
    return logf


def lnorm_logscores(logscores, x):
    """
    Log scores for MLE and RHP predictions calculated using leave-one-out
    
    Parameters
    ----------
    logscores : bool
        Whether to calculate log scores
    x : array-like
        Data values
    
    Returns
    -------
    dict
        Dictionary containing ml_oos_logscore and rh_oos_logscore
    """
    if logscores:
        y = np.log(x)
        nx = len(x)
        ml_oos_logscore = 0
        rh_oos_logscore = 0
        
        for i in range(nx):
            # Create leave-one-out dataset
            x1 = np.concatenate([x[:i], x[i+1:]])
            
            dd = dlnormsub(x1, x[i])
            
            ml_params = dd['ml_params']
            
            ml_pdf = dd['ml_pdf']
            ml_oos_logscore = ml_oos_logscore + np.log(ml_pdf)
            
            rh_pdf = dd['rh_pdf']
            rh_oos_logscore = rh_oos_logscore + np.log(rh_pdf)
    else:
        ml_oos_logscore = "logscores not selected"
        rh_oos_logscore = "logscores not selected"
    
    return {'ml_oos_logscore': ml_oos_logscore, 'rh_oos_logscore': rh_oos_logscore}


def dlnormsub(x, y):
    """
    Densities from MLE and RHP
    
    Parameters
    ----------
    x : array-like
        Training data values
    y : float
        Test data value
    
    Returns
    -------
    dict
        Dictionary containing ml_params, ml_pdf, rh_pdf, ml_cdf, rh_cdf
    """
    # great potential for confusion here
    # x and y are both lognormal
    # logx and logy are both normal
    
    nx = len(x)
    logx = np.log(x)
    logy = np.log(y)
    
    # ml
    ml_params = norm_ml_params(logx)  # this really should be norm not lnorm
    ml_pdf = scipy.stats.lognorm.pdf(y, s=ml_params[1], scale=np.exp(ml_params[0]))
    ml_cdf = scipy.stats.lognorm.cdf(y, s=ml_params[1], scale=np.exp(ml_params[0]))
    
    # rhp pdf
    # -first, convert sigma from maxlik to unbiased
    sgu = ml_params[1] * np.sqrt(nx/(nx-1))
    # then, convert sigma to predictive sigma
    sg1 = sgu * np.sqrt((nx+1)/nx)
    
    logyd = (logy - ml_params[0]) / sg1
    rh_pdf = (scipy.stats.t.pdf(logyd, df=nx-1)) / (y * sg1)  # note the extra exp term here, to convert to loglnormal predictive density
    rh_pdf = np.maximum(rh_pdf, 0)
    
    # rhp cdf
    rh_cdf = scipy.stats.t.cdf(logyd, df=nx-1)
    rh_cdf = np.minimum(np.maximum(rh_cdf, 0), 1)
    
    # return
    return {
        'ml_params': ml_params,
        'ml_pdf': ml_pdf,
        'rh_pdf': rh_pdf,
        'ml_cdf': ml_cdf,
        'rh_cdf': rh_cdf
    }

