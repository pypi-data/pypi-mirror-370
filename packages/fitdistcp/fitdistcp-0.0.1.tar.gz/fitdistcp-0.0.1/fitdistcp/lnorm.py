import numpy as np
import scipy.stats

from . import utils as cp_utils
from . import lnorm_libs


def ppf(x, p=np.arange(0.1, 1.0, 0.1), means=False, waicscores=False, logscores=False, rust=False, nrust=100000, debug=False):
    """
    Log-normal Distribution Predictions Based on a Calibrating Prior
    
    Parameters
    ----------
    x : array-like
        Training data values
    p : array-like, optional
        Probabilities for quantiles (default: np.arange(0.1, 1.0, 0.1))
    means : bool
        Whether to calculate means (default False)
    waicscores : bool
        Whether to calculate WAIC scores (default False)
    logscores : bool
        Whether to calculate log scores (default False)
    rust : bool
        Whether to use RUST method (default False)
    nrust : int
        Number of RUST samples (default 100000)
    debug : bool
        Debug flag (default False)
        
    Returns
    -------
    dict
        Dictionary containing quantiles and related statistics
    """
    
    # Input validation
    x = cp_utils.to_array(x)
    p = cp_utils.to_array(p)
    assert np.all(np.isfinite(x)) and np.all(~np.isnan(x)), "x must be finite and not NaN"
    assert np.all(np.isfinite(p)) and np.all(~np.isnan(p)), "p must be finite and not NaN"
    assert np.all(p > 0) and np.all(p < 1), "p must be between 0 and 1"
    assert np.all(x >= 0), "x must be non-negative"
    
    alpha = 1 - p
    y = np.log(x)
    nx = len(x)
    nalpha = len(alpha)
    
    # 2 ml param estimate
    ml_params = lnorm_libs.norm_ml_params(y)  # note that it uses y, and the normal routine
    v1hat = ml_params[0]
    v2hat = ml_params[1]
    
    # 3 aic
    ml_value = np.sum(scipy.stats.lognorm.logpdf(x, s=v2hat, scale=np.exp(v1hat)))
    maic = cp_utils.make_maic(ml_value, nparams=2)
    
    # 4 ml quantiles (vectorized over alpha)
    ml_quantiles = scipy.stats.lognorm.ppf(1-alpha, s=v2hat, scale=np.exp(v1hat))
    
    ldd = "only relevant for DMGS models, not analytic models"
    lddi = "only relevant for DMGS models, not analytic models"
    expinfmat = np.zeros((2, 2))
    expinfmat[0, 0] = nx / (v2hat * v2hat)
    expinfmat[1, 1] = 2 * nx / (v2hat * v2hat)
    expinfmati = np.linalg.inv(expinfmat)
    standard_errors = np.zeros(2)
    standard_errors[0] = np.sqrt(expinfmati[0, 0])
    standard_errors[1] = np.sqrt(expinfmati[1, 1])
    
    # 5 rhp quantiles
    mu = np.mean(y)
    # calculate the unbiased variance
    s1 = np.sqrt(np.var(y, ddof=1))  # ddof=1 for unbiased variance like R's var()
    temp = scipy.stats.t.ppf(1-alpha, df=nx-1)
    # convert the unbiased to predictive
    rh_quantiles = np.exp(mu + temp * s1 * np.sqrt(1 + 1/nx))
    
    # 6 means (might as well always calculate)
    ml_mean = np.exp(v1hat + 0.5 * v2hat * v2hat)
    rh_mean = "no analytic expression"
    
    # 7 waicscores
    waic = lnorm_libs.lnorm_waic(waicscores, x, v1hat, v2hat)
    waic1 = waic['waic1']
    waic2 = waic['waic2']
    
    # 8 logscores
    logscores_result = lnorm_libs.lnorm_logscores(logscores, x)
    ml_oos_logscore = logscores_result['ml_oos_logscore']
    rh_oos_logscore = logscores_result['rh_oos_logscore']
    
    # 9 rust
    ru_quantiles = "rust not selected"
    if rust:
        rustsim = rvs(nrust, x, rust=True, mlcp=False)
        ru_quantiles = cp_utils.makeq(rustsim['ru_deviates'], p)
    
    # return
    return {
        'ml_params': ml_params,
        'ml_value': ml_value,
        'standard_errors': standard_errors,
        'ml_quantiles': ml_quantiles,
        'cp_quantiles': rh_quantiles,
        'ru_quantiles': ru_quantiles,
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
    Random generation for log-normal with calibrating prior
    
    Parameters
    ----------
    n : int
        Number of samples to generate
    x : array-like
        Training data values
    rust : bool
        Whether to use RUST method (default False)
    mlcp : bool
        Whether to use ML/CP method (default True)
    debug : bool
        Debug flag (default False)
        
    Returns
    -------
    dict
        Dictionary containing random deviates and parameters
    """
    x = cp_utils.to_array(x)
    assert np.all(np.isfinite(x)) and np.all(~np.isnan(x)), "x must be finite and not NaN"
    assert np.all(x >= 0), "x must be non-negative"
    
    ml_params = "mlcp not selected"
    ml_deviates = "mlcp not selected"
    cp_deviates = "mlcp not selected"
    ru_deviates = "rust not selected"
    
    if mlcp:
        q = ppf(x, np.random.uniform(0, 1, n))
        ml_params = q['ml_params']
        ml_deviates = q['ml_quantiles']
        cp_deviates = q['cp_quantiles']
    
    if rust:
        th = tlnorm_cp(n, x)['theta_samples']
        ru_deviates = np.zeros(n)
        for i in range(n):
            ru_deviates[i] = scipy.stats.lognorm.rvs(s=th[i, 1], scale=np.exp(th[i, 0]), size=1)[0]
    
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
    Density function for log-normal with calibrating prior
    
    Parameters
    ----------
    x : array-like
        Training data values
    y : array-like, optional
        Test data values (default: same as x)
    rust : bool
        Whether to use RUST method (default False)
    nrust : int
        Number of RUST samples (default 1000)
    debug : bool
        Debug flag (default False)
        
    Returns
    -------
    dict
        Dictionary containing density values
    """
    x = cp_utils.to_array(x)
    if y is None:
        y = x
    else:
        y = cp_utils.to_array(y)
    
    assert np.all(np.isfinite(x)) and np.all(~np.isnan(x)), "x must be finite and not NaN"
    assert np.all(np.isfinite(y)) and np.all(~np.isnan(y)), "y must be finite and not NaN"
    assert np.all(x >= 0), "x must be non-negative"
    assert np.all(y >= 0), "y must be non-negative"
    
    dd = lnorm_libs.dlnormsub(x=x, y=y)  # dlnormsub expects scalar y
    ru_pdf = "rust not selected"
    
    if rust:
        th = tlnorm_cp(nrust, x)['theta_samples']
        ru_pdf = np.zeros(len(y))
        for ir in range(nrust):
            ru_pdf = ru_pdf + scipy.stats.lognorm.pdf(y, s=th[ir, 1], scale=np.exp(th[ir, 0]))
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
    Cumulative distribution function for log-normal with calibrating prior
    
    Parameters
    ----------
    x : array-like
        Training data values
    y : array-like, optional
        Test data values (default: same as x)
    rust : bool
        Whether to use RUST method (default False)
    nrust : int
        Number of RUST samples (default 1000)
    debug : bool
        Debug flag (default False)
        
    Returns
    -------
    dict
        Dictionary containing CDF values
    """
    x = cp_utils.to_array(x)
    if y is None:
        y = x
    else:
        y = cp_utils.to_array(y)
    
    assert np.all(np.isfinite(x)) and np.all(~np.isnan(x)), "x must be finite and not NaN"
    assert np.all(np.isfinite(y)) and np.all(~np.isnan(y)), "y must be finite and not NaN"
    assert np.all(x >= 0), "x must be non-negative"
    assert np.all(y >= 0), "y must be non-negative"
    
    dd = lnorm_libs.dlnormsub(x=x, y=y[0] if len(y) == 1 else y)  # dlnormsub expects scalar y
    ru_cdf = "rust not selected"
    
    if rust:
        th = tlnorm_cp(nrust, x)['theta_samples']
        ru_cdf = np.zeros(len(y))
        for ir in range(nrust):
            ru_cdf = ru_cdf + scipy.stats.lognorm.cdf(y, s=th[ir, 1], scale=np.exp(th[ir, 0]))
        ru_cdf = ru_cdf / nrust
    
    op = {
        'ml_params': dd['ml_params'],
        'ml_cdf': dd['ml_cdf'],
        'cp_cdf': dd['rh_cdf'],
        'ru_cdf': ru_cdf,
        'cp_method': cp_utils.analytic_cpmethod()
    }
    
    return op


def tlnorm_cp(n, x, debug=False):
    """
    Not yet implemented: Theta sampling for log-normal with calibrating prior
    
    Parameters
    ----------
    n : int
        Number of samples to generate
    x : array-like
        Training data values
    debug : bool
        Debug flag (default False)
        
    Returns
    -------
    dict
        Dictionary containing theta samples
    """
    x = cp_utils.to_array(x)
    assert np.all(np.isfinite(x)) and np.all(~np.isnan(x)), "x must be finite and not NaN"
    assert np.all(x >= 0), "x must be non-negative"
    
    # Initialize with method of moments estimates
    log_x = np.log(x)
    init_meanlog = np.mean(log_x)
    init_sdlog = np.std(log_x, ddof=1)
    
    t = cp_utils.ru(lnorm_libs.lnorm_logf, x=x, n=n, d=2, init=[init_meanlog, init_sdlog])
    
    return {'theta_samples': t['sim_vals']}
