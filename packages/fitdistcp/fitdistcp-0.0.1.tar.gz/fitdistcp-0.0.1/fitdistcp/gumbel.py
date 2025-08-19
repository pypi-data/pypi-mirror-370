import numpy as np
import scipy.stats
import scipy.optimize

from . import utils as cp_utils
from . import evaluate_dmgs_equation as cp_dmgs
from . import gumbel_derivs
from . import gumbel_libs


def ppf(x, p=np.arange(0.1, 1.0, 0.1), means=False, waicscores=False, logscores=False, 
               dmgs=True, rust=False, nrust=100000, debug=False):
    """
    Gumbel Distribution Predictions Based on a Calibrating Prior.

    Parameters
    ----------
    x : array_like
        Observed data, must be finite and not NaN.
    p : array_like, optional
        Probabilities at which to compute quantiles (default: np.arange(0.1, 1.0, 0.1)).
    means : bool, optional
        Whether to compute means (default: False).
    waicscores : bool, optional
        Whether to compute WAIC scores (default: False).
    logscores : bool, optional
        Whether to compute log scores (default: False).
    dmgs : bool, optional
        Whether to use DMGS analytic corrections (default: True).
    rust : bool, optional
        Whether to use the "rust" simulation method (default: False).
    nrust : int, optional
        Number of simulations for "rust" (default: 100000).
    debug : bool, optional
        If True, print debug information (default: False).

    Returns
    -------
    dict
        Dictionary containing ML and calibrating prior quantiles, means, scores, and method information.
    """

    x = cp_utils.to_array(x)
    p = cp_utils.to_array(p)
    
    # Input validation
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x)), "x must be finite and not NA"
    assert np.all(np.isfinite(p)) and not np.any(np.isnan(p)), "p must be finite and not NA"
    assert np.all(p > 0) and np.all(p < 1), "p must be between 0 and 1"
    
    alpha = 1 - p
    nx = len(x)
    nalpha = len(alpha)
    
    # 2 ml param estimate
    if debug:
        print("2 calc ml param estimate")
    
    v1start = np.mean(x)
    v2start = np.std(x)
    
    def neg_loglik(params):
        return -gumbel_libs.gumbel_loglik(params, x)
    
    opt = scipy.optimize.minimize(neg_loglik, [v1start, v2start])
    v1hat = opt.x[0]
    v2hat = opt.x[1]
    ml_params = np.array([v1hat, v2hat])
    
    if debug:
        print(f"  v1hat,v2hat={v1hat},{v2hat}//")
    
    # 3 aic
    ml_value = -opt.fun
    maic = cp_utils.make_maic(ml_value, nparams=2)
    
    # 4 ml quantiles (vectorized over alpha)
    ml_quantiles = scipy.stats.gumbel_r.ppf(1-alpha, loc=v1hat, scale=v2hat)
    
    # dmgs
    standard_errors = "dmgs not selected"
    rh_quantiles = "dmgs not selected"
    ru_quantiles = "dmgs not selected"
    waic1 = "dmgs not selected"
    waic2 = "dmgs not selected"
    ml_oos_logscore = "dmgs not selected"
    rh_oos_logscore = "dmgs not selected"
    cp_oos_logscore = "dmgs not selected"
    ml_mean = "dmgs not selected"
    rh_mean = "dmgs not selected"
    cp_mean = "dmgs not selected"
    cp_method = "dmgs not selected"
    
    if dmgs:
        # 5 lddi
        if debug:
            print("  calculate ldd,lddi")
        ldd = gumbel_derivs.gumbel_ldda(x, v1hat, v2hat)
        lddi = np.linalg.inv(ldd)
        standard_errors = cp_utils.make_se(nx, lddi)
        
        # 6 lddd
        if debug:
            print("  calculate lddd")
        lddd = gumbel_derivs.gumbel_lddda(x, v1hat, v2hat)
        
        # 7 mu1
        if debug:
            print("  calculate mu1")
        mu1 = gumbel_derivs.gumbel_mu1fa(alpha, v1hat, v2hat)
        
        # 8 mu2
        if debug:
            print("  calculate mu2")
        mu2 = gumbel_derivs.gumbel_mu2fa(alpha, v1hat, v2hat)
        
        # 9 rhp
        lambdad_rhp = np.array([0, -1/v2hat])
        
        # 10 fhat, dq and quantiles
        if debug:
            print("  fhat, dq and quantiles")
        fhat = scipy.stats.gumbel_r.pdf(ml_quantiles, loc=v1hat, scale=v2hat)
        dq = cp_dmgs.dmgs(lddi, lddd, mu1, lambdad_rhp, mu2, dim=2)
        rh_quantiles = ml_quantiles + dq / (nx * fhat)
        
        # 11 means
        means_result = gumbel_libs.gumbel_means(means, ml_params, lddi, lddd, lambdad_rhp, nx, dim=2)
        ml_mean = means_result['ml_mean']
        rh_mean = means_result['rh_mean']
        
        # 12 waicscores
        waic = gumbel_libs.gumbel_waic(waicscores, x, v1hat, v2hat, lddi, lddd, lambdad_rhp)
        waic1 = waic['waic1']
        waic2 = waic['waic2']
        
        # 13 logscores
        logscores_result = gumbel_libs.gumbel_logscores(logscores, x)
        ml_oos_logscore = logscores_result['ml_oos_logscore']
        rh_oos_logscore = logscores_result['rh_oos_logscore']
        
        # 14 rust
        ru_quantiles = "rust not selected"
        if rust:
            rustsim = rvs(nrust, x, rust=True, mlcp=False)
            ru_quantiles = gumbel_libs.makeq(rustsim['ru_deviates'], p)
    
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
        'cp_method': cp_utils.rhp_dmgs_cpmethod()
    }

def rvs(n, x, rust=False, mlcp=True, debug=False):
    """
    Random number generation for Gumbel calibrating prior.

    Parameters
    ----------
    n : int
        Number of random variates to generate.
    x : array_like
        Observed data, must be finite and not NaN.
    rust : bool, optional
        Whether to use the "rust" simulation method (default: False).
    mlcp : bool, optional
        Whether to use ML and calibrating prior (default: True).
    debug : bool, optional
        If True, print debug information (default: False).

    Returns
    -------
    dict
        Dictionary containing ML, calibrating prior, and rust deviates, parameters, and method information.
    """
    x = cp_utils.to_array(x)
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x)), "x must be finite and not NA"
    
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
        th = tgumbel_cp(n, x)['theta_samples']
        ru_deviates = np.zeros(n)
        for i in range(n):
            ru_deviates[i] = scipy.stats.gumbel_r.rvs(loc=th[i, 0], scale=th[i, 1])
    
    op = {
        'ml_params': ml_params,
        'ml_deviates': ml_deviates,
        'cp_deviates': cp_deviates,
        'ru_deviates': ru_deviates,
        'cp_method': cp_utils.rhp_dmgs_cpmethod()
    }
    
    return op

def pdf(x, y=None, rust=False, nrust=1000, debug=False):
    """
    Density function for Gumbel calibrating prior.

    Parameters
    ----------
    x : array_like
        Observed data, must be finite and not NaN.
    y : array_like, optional
        Points at which to evaluate the density (default: x).
    rust : bool, optional
        Whether to use the "rust" simulation method (default: False).
    nrust : int, optional
        Number of simulations for "rust" (default: 1000).
    debug : bool, optional
        If True, print debug information (default: False).

    Returns
    -------
    dict
        Dictionary containing ML, calibrating prior, and rust densities, parameters, and method information.
    """
    x = cp_utils.to_array(x)
    if y is None:
        y = x
    else:
        y = cp_utils.to_array(y)
    
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x)), "x must be finite and not NA"
    assert np.all(np.isfinite(y)) and not np.any(np.isnan(y)), "y must be finite and not NA"
    
    dd = gumbel_libs.dgumbelsub(x=x, y=y)
    ru_pdf = "rust not selected"
    
    if rust:
        th = tgumbel_cp(nrust, x)['theta_samples']
        ru_pdf = np.zeros(len(y))
        for ir in range(nrust):
            ru_pdf += scipy.stats.gumbel_r.pdf(y, loc=th[ir, 0], scale=th[ir, 1])
        ru_pdf = ru_pdf / nrust
    
    op = {
        'ml_params': dd['ml_params'],
        'ml_pdf': dd['ml_pdf'],
        'cp_pdf': dd['rh_pdf'],
        'ru_pdf': ru_pdf,
        'cp_method': cp_utils.rhp_dmgs_cpmethod()
    }
    
    return op

def cdf(x, y=None, rust=False, nrust=1000, debug=False):
    """
    Cumulative distribution function for Gumbel calibrating prior.

    Parameters
    ----------
    x : array_like
        Observed data, must be finite and not NaN.
    y : array_like, optional
        Points at which to evaluate the CDF (default: x).
    rust : bool, optional
        Whether to use the "rust" simulation method (default: False).
    nrust : int, optional
        Number of simulations for "rust" (default: 1000).
    debug : bool, optional
        If True, print debug information (default: False).

    Returns
    -------
    dict
        Dictionary containing ML, calibrating prior, and rust CDFs, parameters, and method information.
    """
    x = cp_utils.to_array(x)
    if y is None:
        y = x
    else:
        y = cp_utils.to_array(y)
    
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x)), "x must be finite and not NA"
    assert np.all(np.isfinite(y)) and not np.any(np.isnan(y)), "y must be finite and not NA"
    
    dd = gumbel_libs.dgumbelsub(x=x, y=y)
    ru_cdf = "rust not selected"
    
    if rust:
        th = tgumbel_cp(nrust, x)['theta_samples']
        ru_cdf = np.zeros(len(y))
        for ir in range(nrust):
            ru_cdf += scipy.stats.gumbel_r.cdf(y, loc=th[ir, 0], scale=th[ir, 1])
        ru_cdf = ru_cdf / nrust
    
    op = {
        'ml_params': dd['ml_params'],
        'ml_cdf': dd['ml_cdf'],
        'cp_cdf': dd['rh_cdf'],
        'ru_cdf': ru_cdf,
        'cp_method': cp_utils.rhp_dmgs_cpmethod()
    }
    
    return op

def tgumbel_cp(n, x, debug=False):
    """
    Not implemented: Theta sampling function for Gumbel calibrating prior.

    Parameters
    ----------
    n : int
        Number of samples to generate.
    x : array_like
        Observed data, must be finite and not NaN.
    debug : bool, optional
        If True, print debug information (default: False).

    Returns
    -------
    dict
        Dictionary containing theta samples.
        
    """
    raise Exception('Not yet implemented.')
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x)), "x must be finite and not NA"
    
    t = ru(gumbel_libs.gumbel_logf, x=x, n=n, d=2, init=[np.mean(x), np.std(x)])
    
    return {'theta_samples': t['sim_vals']}

