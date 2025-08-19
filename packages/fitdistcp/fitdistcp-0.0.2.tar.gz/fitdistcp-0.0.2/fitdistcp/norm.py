import numpy as np
import scipy.stats as stats

from . import norm_libs
from . import utils as cp_utils


def ppf(x, p=np.arange(0.1, 1.0, 0.1), means=False, waicscores=False, 
             logscores=False, rust=False, nrust=100000, unbiasedv=False, debug=False):
    """
    Normal Distribution Predictions Based on a Calibrating Prior
    
    Parameters
    ----------
    x : array-like
        Training data
    p : array-like, default np.arange(0.1, 1.0, 0.1)
        Probability levels for quantiles
    means : bool, default False
        Whether to calculate means
    waicscores : bool, default False
        Whether to calculate WAIC scores
    logscores : bool, default False
        Whether to calculate log scores
    rust : bool, default False
        Whether to use RUST method
    nrust : int, default 100000
        Number of RUST samples
    unbiasedv : bool, default False
        Whether to use unbiased variance
    debug : bool, default False
        Debug flag
        
    Returns
    -------
    dict
        Dictionary containing quantiles and other statistics
    """
    # 1 intro
    x = cp_utils.to_array(x)
    p = cp_utils.to_array(p)
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x))
    assert np.all(np.isfinite(p)) and not np.any(np.isnan(p))
    assert np.all(p > 0) and np.all(p < 1)
    
    alpha = 1 - p
    nx = len(x)
    nalpha = len(alpha)
    
    # 2 ml param estimate
    ml_params = norm_libs.norm_ml_params(x)
    v1hat = ml_params[0]
    v2hat = ml_params[1]
    uv_params = "unbiasedv not selected"
    if unbiasedv:
        uv_params = norm_libs.norm_unbiasedv_params(x)
    
    # 3 aic
    ml_value = np.sum(stats.norm.logpdf(x, loc=v1hat, scale=v2hat))
    maic = cp_utils.make_maic(ml_value, nparams=2)
    
    # 4 ml quantiles (vectorized over alpha)
    ml_quantiles = stats.norm.ppf(1 - alpha, loc=v1hat, scale=v2hat)
    uv_quantiles = "unbiasedv not selected"
    if unbiasedv:
        uv_quantiles = stats.norm.ppf(1 - alpha, loc=uv_params[0], scale=uv_params[1])
    
    # 5 rhp quantiles (vectorized over alpha)
    mu = v1hat
    
    # first, convert sigma from maxlik to unbiased
    sgu = v2hat * np.sqrt(nx / (nx - 1))
    # then, convert sigma to predictive sigma
    sg = sgu * np.sqrt((nx + 1) / nx)
    
    temp = stats.t.ppf(1 - alpha, df=nx - 1)
    rh_quantiles = mu + temp * sg
    
    ldd = "only relevant for DMGS models, not analytic models"
    lddi = "only relevant for DMGS models, not analytic models"
    expinfmat = np.zeros((2, 2))
    expinfmat[0, 0] = nx / (v2hat * v2hat)
    expinfmat[1, 1] = 2 * nx / (v2hat * v2hat)
    expinfmati = np.linalg.inv(expinfmat)
    standard_errors = np.zeros(2)
    standard_errors[0] = np.sqrt(expinfmati[0, 0])
    standard_errors[1] = np.sqrt(expinfmati[1, 1])
    
    # test of gg code (for future implementation of mpd theory, as a test of the mpd code)
    # norm_gg(nx,v1hat,v2hat)
    
    # 6 means (might as well always calculate)
    ml_mean = v1hat
    rh_mean = v1hat
    
    # 7 waicscores
    waic = norm_libs.norm_waic(waicscores, x, v1hat, v2hat)
    waic1 = waic['waic1']
    waic2 = waic['waic2']
    
    # 8 logscores
    logscores_result = norm_libs.norm_logscores(logscores, x)
    ml_oos_logscore = logscores_result['ml_oos_logscore']
    rh_oos_logscore = logscores_result['rh_oos_logscore']
    
    # 9 rust
    ru_quantiles = "rust not selected"
    if rust:
        rustsim = rvs(nrust, x, rust=True, mlcp=False)
        ru_quantiles = cp_utils.makeq(rustsim['ru_deviates'], p)
    
    return {
        'ml_params': ml_params,
        'ml_value': ml_value,
        'uv_params': uv_params,
        # 'ldd': ldd,
        # 'lddi': lddi,
        # 'expinfmat': expinfmat,
        # 'expinfmati': expinfmati,
        'standard_errors': standard_errors,
        'ml_quantiles': ml_quantiles,
        'cp_quantiles': rh_quantiles,
        'ru_quantiles': ru_quantiles,
        'uv_quantiles': uv_quantiles,
        'maic': maic,
        'waic1': waic1,
        'waic2': waic2,
        'ml_oos_logscore': ml_oos_logscore,
        'cp_oos_logscore': rh_oos_logscore,
        'ml_mean': ml_mean,
        'cp_mean': rh_mean,
        'cp_method': cp_utils.analytic_cpmethod()
    }

def rvs(n, x, rust=False, mlcp=True, debug=False):
    """
    Random number generation for normal distribution with calibrating prior
    
    Parameters
    ----------
    n : int
        Number of samples
    x : array-like
        Training data
    rust : bool, default False
        Whether to use RUST method
    mlcp : bool, default True
        Whether to use ML/CP method
    debug : bool, default False
        Debug flag
        
    Returns
    -------
    dict
        Dictionary containing random deviates
    """
    # stopifnot(is.finite(n),!is.na(n),is.finite(x),!is.na(x))
    x = cp_utils.to_array(x)
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x))
    
    ml_params = "mlcp not selected"
    ml_deviates = "mlcp not selected"
    cp_deviates = "mlcp not selected"
    ru_deviates = "rust not selected"
    
    if mlcp:
        q = ppf(x, np.random.uniform(size=n))
        ml_params = q['ml_params']
        ml_deviates = q['ml_quantiles']
        cp_deviates = q['cp_quantiles']
    
    if rust:
        th = tnorm_cp(n, x)['theta_samples']
        ru_deviates = np.zeros(n)
        for i in range(n):
            ru_deviates[i] = np.random.normal(loc=th[i, 0], scale=th[i, 1])
    
    op = {
        'ml_params': ml_params,
        'ml_deviates': ml_deviates,
        'cp_deviates': cp_deviates,
        'ru_deviates': ru_deviates,
        'cp_method': cp_utils.analytic_cpmethod()
    }
    return op

def pdf(x, y=None, rust=False, nrust=1000, debug=False):
    """
    Density function for normal distribution with calibrating prior
    
    Parameters
    ----------
    x : array-like
        Training data
    y : array-like, optional
        Test points (default: same as x)
    rust : bool, default False
        Whether to use RUST method
    nrust : int, default 1000
        Number of RUST samples
    debug : bool, default False
        Debug flag
        
    Returns
    -------
    dict
        Dictionary containing density values
    """
    x = cp_utils.to_array(x)
    if y is None:
        y = x
    y = cp_utils.to_array(y)
    
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x))
    assert np.all(np.isfinite(y)) and not np.any(np.isnan(y))
    
    dd = norm_libs.dnormsub(x=x, y=y)
    ru_pdf = "rust not selected"
    if rust:
        th = tnorm_cp(nrust, x)['theta_samples']
        ru_pdf = np.zeros(len(y))
        for ir in range(nrust):
            ru_pdf = ru_pdf + stats.norm.pdf(y, loc=th[ir, 0], scale=th[ir, 1])
        ru_pdf = ru_pdf / nrust
    
    op = {
        'ml_params': dd['ml_params'],
        'ml_pdf': dd['ml_pdf'],
        'cp_pdf': dd['rh_pdf'],
        'ru_pdf': ru_pdf,
        'cp_method': cp_utils.analytic_cpmethod()
    }
    return op

def cdf(x, y=None, rust=False, nrust=1000, debug=False):
    """
    Cumulative distribution function for normal distribution with calibrating prior
    
    Parameters
    ----------
    x : array-like
        Training data
    y : array-like, optional
        Test points (default: same as x)
    rust : bool, default False
        Whether to use RUST method
    nrust : int, default 1000
        Number of RUST samples
    debug : bool, default False
        Debug flag
        
    Returns
    -------
    dict
        Dictionary containing CDF values
    """
    x = cp_utils.to_array(x)
    if y is None:
        y = x
    y = cp_utils.to_array(y)
    
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x))
    assert np.all(np.isfinite(y)) and not np.any(np.isnan(y))
    
    dd = norm_libs.dnormsub(x=x, y=y)
    ru_cdf = "rust not selected"
    if rust:
        th = tnorm_cp(nrust, x)['theta_samples']
        ru_cdf = np.zeros(len(y))
        for ir in range(nrust):
            ru_cdf = ru_cdf + stats.norm.cdf(y, loc=th[ir, 0], scale=th[ir, 1])
        ru_cdf = ru_cdf / nrust
    
    op = {
        'ml_params': dd['ml_params'],
        'ml_cdf': dd['ml_cdf'],
        'cp_cdf': dd['rh_cdf'],
        'ru_cdf': ru_cdf,
        'cp_method': cp_utils.analytic_cpmethod()
    }
    return op

def tnorm_cp(n, x, debug=False):
    """
    Not yet implemented: Theta sampling for normal distribution with calibrating prior
    
    Parameters
    ----------
    n : int
        Number of samples
    x : array-like
        Training data
    debug : bool, default False
        Debug flag
        
    Returns
    -------
    dict
        Dictionary containing theta samples
    """
    # stopifnot(is.finite(n),!is.na(n),is.finite(x),!is.na(x))
    x = cp_utils.to_array(x)
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x))
    
    t = cp_utils.ru(norm_libs.norm_logf, x=x, n=n, d=2, init=[np.mean(x), np.std(x)])
    
    return {'theta_samples': t['sim_vals']}
