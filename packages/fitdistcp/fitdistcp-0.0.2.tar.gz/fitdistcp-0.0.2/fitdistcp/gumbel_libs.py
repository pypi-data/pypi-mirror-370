import numpy as np
import sys
import scipy.stats
import scipy.optimize

from . import gumbel_derivs
from . import utils as cp_utils
from . import evaluate_dmgs_equation as cp_dmgs


def gumbel_waic(waicscores, x, v1hat, v2hat, lddi, lddd, lambdad):
    if waicscores:
        f1f = gumbel_derivs.gumbel_f1fa(x, v1hat, v2hat)
        f2f = gumbel_derivs.gumbel_f2fa(x, v1hat, v2hat)
        
        fhatx = scipy.stats.gumbel_r.pdf(x, loc=v1hat, scale=v2hat)
        waic = cp_utils.make_waic(x, fhatx, lddi, lddd, f1f, lambdad, f2f, dim=2)
        waic1 = waic['waic1']
        waic2 = waic['waic2']
    else:
        waic1 = "waicscores not selected"
        waic2 = "waicscores not selected"
    
    return {'waic1': waic1, 'waic2': waic2}

def gumbel_logf(params, x):
    m = params[0]
    s = np.maximum(params[1], sys.float_info.epsilon)
    logf = np.sum(scipy.stats.gumbel_r.logpdf(x, loc=m, scale=s)) - np.log(s)
    return logf

def gumbel_loglik(vv, x):
    loglik = np.sum(scipy.stats.gumbel_r.logpdf(x, loc=vv[0], scale=max(vv[1], sys.float_info.epsilon)))
    return loglik

def gumbel_means(means, ml_params, lddi, lddd, lambdad_rhp, nx, dim=2):
    """MLE and RHP predictive means """
    if means:
        # intro
        eulerconstant = 0.57721566490153286060651209008240243104215933593992
        
        # ml mean
        ml_mean = ml_params[0] + ml_params[1] * eulerconstant
        
        # rhp mean
        meand1 = np.zeros((2, 1))
        meand1[0, 0] = 1
        meand1[1, 0] = eulerconstant
        meand2 = np.zeros((2, 2, 1))  # but all zero for gumbel
        dmean = cp_dmgs.dmgs(lddi, lddd, meand1, lambdad_rhp, meand2, dim=2)
        rh_mean = ml_mean + dmean / nx
    else:
        ml_mean = "means not selected"
        rh_mean = "means not selected"
    
    return {'ml_mean': ml_mean, 'rh_mean': rh_mean}

def gumbel_logscores(logscores, x):
    """Log scores for MLE and RHP predictions calculated using leave-one-out """
    if logscores:
        nx = len(x)
        ml_oos_logscore = 0
        rh_oos_logscore = 0
        for i in range(nx):
            x1 = np.concatenate([x[:i], x[i+1:]])
            
            dd = dgumbelsub(x1, x[i])
            
            ml_params = dd['ml_params']
            
            ml_pdf = dd['ml_pdf']
            ml_oos_logscore = ml_oos_logscore + np.log(ml_pdf)
            
            rh_pdf = dd['rh_pdf']
            rh_oos_logscore = rh_oos_logscore + np.log(max(rh_pdf, sys.float_info.epsilon))
    else:
        ml_oos_logscore = "logscores not selected"
        rh_oos_logscore = "logscores not selected"
    
    return {'ml_oos_logscore': ml_oos_logscore, 'rh_oos_logscore': rh_oos_logscore}

def dgumbelsub(x, y):
    """Densities from MLE and RHP"""
    nx = len(x)
    
    v1start = np.mean(x)
    v2start = np.std(x)
    
    # Use minimize with negative log-likelihood since optim with fnscale=-1 maximizes
    def neg_loglik(params):
        return -gumbel_loglik(params, x)
    
    opt = scipy.optimize.minimize(neg_loglik, [v1start, v2start])
    v1hat = opt.x[0]
    v2hat = opt.x[1]
    ml_params = np.array([v1hat, v2hat])
    
    # mle
    ml_pdf = scipy.stats.gumbel_r.pdf(y, loc=v1hat, scale=v2hat)
    ml_cdf = scipy.stats.gumbel_r.cdf(y, loc=v1hat, scale=v2hat)
    
    # rhp
    ldd = gumbel_derivs.gumbel_ldda(x, v1hat, v2hat)
    lddi = np.linalg.inv(ldd)
    lddd = gumbel_derivs.gumbel_lddda(x, v1hat, v2hat)
    
    f1 = gumbel_derivs.gumbel_f1fa(y, v1hat, v2hat)
    f2 = gumbel_derivs.gumbel_f2fa(y, v1hat, v2hat)
    
    p1 = gumbel_derivs.gumbel_p1fa(y, v1hat, v2hat)
    p2 = gumbel_derivs.gumbel_p2fa(y, v1hat, v2hat)
    
    lambdad_rhp = np.array([0, -1/v2hat])
    df1 = cp_dmgs.dmgs(lddi, lddd, f1, lambdad_rhp, f2, dim=2)
    dp1 = cp_dmgs.dmgs(lddi, lddd, p1, lambdad_rhp, p2, dim=2)
    rh_pdf = np.maximum(ml_pdf + df1/nx, 0)
    rh_cdf = np.minimum(np.maximum(ml_cdf + dp1/nx, 0), 1)
    
    # return
    return {
        'ml_params': ml_params,
        'ml_pdf': ml_pdf,
        'rh_pdf': rh_pdf,
        'ml_cdf': ml_cdf,
        'rh_cdf': rh_cdf
    }
