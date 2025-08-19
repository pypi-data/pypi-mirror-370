import numpy as np
import sys
import scipy.stats

from . import expon_derivs as exp_derivs
from . import utils as cp_utils


def exp_waic(waicscores, x, v1hat):
    """
    Waicscores
    @inherit manwaic return
    @inheritParams manf
    """
    if waicscores:
        f1f = exp_derivs.exp_f1fa(x, v1hat)
        f2f = exp_derivs.exp_f2fa(x, v1hat)
        
        ldd = exp_derivs.exp_ldda(x, v1hat)
        lddi = np.linalg.inv(ldd)
        lddd = exp_derivs.exp_lddda(x, v1hat)
        fhatx = scipy.stats.expon.pdf(x, scale=1/v1hat)
        lambdad_rhp = -1/v1hat
        waic = cp_utils.make_waic(x, fhatx, lddi, lddd, f1f, lambdad_rhp, f2f, dim=1)
        waic1 = waic['waic1']
        waic2 = waic['waic2']
    else:
        waic1 = "waicscores not selected"
        waic2 = "waicscores not selected"
    
    return {'waic1': waic1, 'waic2': waic2}

def exp_logf(params, x):
    """
    Logf for RUST
    @inherit manlogf return
    @inheritParams manf
    """
    l = np.maximum(params[0], sys.float_info.epsilon)
    logf = np.sum(scipy.stats.expon.logpdf(x, scale=1/l)) - np.log(l)
    return logf

def exp_logscores(logscores, x):
    """
    Log scores for MLE and RHP predictions calculated using leave-one-out
    @inherit manlogscores return
    @inheritParams manf
    """
    if logscores:
        # I could put the logs inside dexpsub, but I'd have to actually calculate the log for the rhp case
        
        nx = len(x)
        ml_oos_logscore = 0
        rh_oos_logscore = 0
        for i in range(nx):
            x1 = np.concatenate([x[:i], x[i+1:]])
            dd = dexpsub(x1, x[i])
            ml_params1 = (nx-1) / np.sum(x1)
            # ml
            ml_pdf = dd['ml_pdf']
            ml_oos_logscore = ml_oos_logscore + np.log(ml_pdf)
            # rhp
            rh_pdf = dd['rh_pdf']
            rh_oos_logscore = rh_oos_logscore + np.log(rh_pdf)
    else:
        ml_oos_logscore = "logscores not selected"
        rh_oos_logscore = "logscores not selected"
    
    return {'ml_oos_logscore': ml_oos_logscore, 'rh_oos_logscore': rh_oos_logscore}

def dexpsub(x, y):
    """
    Densities from MLE and RHP
    @inherit mandsub return
    @inheritParams manf
    """
    nx = len(x)
    
    # ml
    ml_params = nx / np.sum(x)
    ml_pdf = scipy.stats.expon.pdf(y, scale=1/ml_params)
    ml_cdf = scipy.stats.expon.cdf(y, scale=1/ml_params)
    
    # rhp pdf
    sx = np.sum(x)
    top = sx**nx
    bot1 = (sx + y)**(nx + 1)
    rh_pdf = nx * top / bot1
    rh_pdf = np.maximum(rh_pdf, 0)
    
    # rhp cdf
    bot2 = (sx + y)**nx
    rh_cdf = 1 - top / bot2
    rh_cdf = np.minimum(np.maximum(rh_cdf, 0), 1)
    
    # return
    return {
        'ml_params': ml_params,
        'ml_pdf': ml_pdf,
        'rh_pdf': rh_pdf,
        'ml_cdf': ml_cdf,
        'rh_cdf': rh_cdf
    }

