import numpy as np
import scipy.stats
import scipy.optimize

from . import utils as cp_utils
from . import evaluate_dmgs_equation as cp_dmgs
from . import weibull_libs
from . import weibull_derivs


def ppf(x, p=np.arange(0.1, 1.0, 0.1), means=False, waicscores=False, 
                logscores=False, dmgs=True, rust=False, nrust=100000, debug=False):
    """
    Weibull Distribution Predictions Based on a Calibrating Prior
    
    Parameters
    ----------
    x : array_like
        Data values
    p : array_like, optional
        Probabilities for quantiles (default 0.1 to 0.9 by 0.1)
    means : bool, optional
        Whether to calculate means (default False)
    waicscores : bool, optional
        Whether to calculate WAIC scores (default False)
    logscores : bool, optional
        Whether to calculate log scores (default False)
    dmgs : bool, optional
        Whether to use DMGS integration (default True)
    rust : bool, optional
        Whether to use RUST sampling (default False)
    nrust : int, optional
        Number of RUST samples (default 100000)
    debug : bool, optional
        Whether to print debug messages (default False)
        
    Returns
    -------
    dict
        Dictionary containing results
    """
    # 1 intro
    debug = True
    debug = False
    
    # Input validation
    x = cp_utils.to_array(x)
    p = cp_utils.to_array(p)
    
    assert np.all(np.isfinite(x)) and np.all(~np.isnan(x)), "x must be finite and not NaN"
    assert np.all(np.isfinite(p)) and np.all(~np.isnan(p)), "p must be finite and not NaN"
    assert np.all(p > 0) and np.all(p < 1), "p must be between 0 and 1"
    assert np.all(x >= 0), "x must be non-negative"
    
    alpha = 1 - p
    nx = len(x)
    nalpha = len(alpha)
    
    # 2 ml param estimate
    opt = scipy.optimize.minimize(lambda params: -weibull_libs.weibull_loglik(params, x), 
                                 [1, 1], method='BFGS')
    v1hat, v2hat = opt.x
    ml_params = np.array([v1hat, v2hat])
    
    if debug:
        print(f"  v1hat,v2hat={v1hat},{v2hat}")
    
    # 3 aic
    ml_value = -opt.fun
    maic = cp_utils.make_maic(ml_value, nparams=2)
    
    # 4 ml quantiles (vectorized over alpha)
    ml_quantiles = scipy.stats.weibull_min.ppf(1-alpha, c=v1hat, scale=v2hat)
    
    # 5 dmgs
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
        # 6 lddi
        ldd = weibull_derivs.weibull_ldda(x, v1hat, v2hat)
        lddi = np.linalg.inv(ldd)
        standard_errors = cp_utils.make_se(nx, lddi)
        
        # 7 lddd
        if debug:
            print("  calculate lddd")
        lddd = weibull_derivs.weibull_lddda(x, v1hat, v2hat)
        
        # 7 mu1
        if debug:
            print("calculate mu1")
        mu1 = weibull_derivs.weibull_mu1fa(alpha, v1hat, v2hat)
        
        # 8 mu2
        if debug:
            print("calculate mu2")
        mu2 = weibull_derivs.weibull_mu2fa(alpha, v1hat, v2hat)
        
        # 9 q rhp
        if debug:
            print("  rhp")
        lambdad_rhp = np.array([-1/v1hat, -1/v2hat])
        
        # 10 derive the bayesian dq based on v2hat
        if debug:
            print("  fhat, dq and rhp quantiles")
        fhat = scipy.stats.weibull_min.pdf(ml_quantiles, c=v1hat, scale=v2hat)
        dq = cp_dmgs.dmgs(lddi, lddd, mu1, lambdad_rhp, mu2, dim=2)
        rh_quantiles = ml_quantiles + dq / (nx * fhat)
        
        # 11 means
        means_result = weibull_libs.weibull_means(means, ml_params, lddi, lddd, 
                                                  lambdad_rhp, nx, dim=2)
        ml_mean = means_result['ml_mean']
        rh_mean = means_result['rh_mean']
        
        # 12 waicscores
        waic = weibull_libs.weibull_waic(waicscores, x, v1hat, v2hat, lddi, lddd, 
                                        lambdad_rhp)
        waic1 = waic['waic1']
        waic2 = waic['waic2']
        
        # 13 logscores
        logscores_result = weibull_libs.weibull_logscores(logscores, x)
        ml_oos_logscore = logscores_result['ml_oos_logscore']
        rh_oos_logscore = logscores_result['rh_oos_logscore']
        
        # 14 rust
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
        'cp_method': cp_utils.rhp_dmgs_cpmethod()
    }

def rvs(n, x, rust=False, mlcp=True, debug=False):
    """
    Random generation for Weibull CP
    
    Parameters
    ----------
    n : int
        Number of samples
    x : array_like
        Data for parameter estimation
    rust : bool, optional
        Whether to use RUST sampling (default False)
    mlcp : bool, optional
        Whether to use ML/CP approach (default True)
    debug : bool, optional
        Whether to print debug messages (default False)
        
    Returns
    -------
    dict
        Dictionary containing generated samples
    """
    # Input validation
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
        th = tweibull_cp(n, x)['theta_samples']
        ru_deviates = np.zeros(n)
        for i in range(n):
            ru_deviates[i] = scipy.stats.weibull_min.rvs(c=th[i, 0], scale=th[i, 1], size=1)
    
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
    Density function for Weibull CP
    
    Parameters
    ----------
    x : array_like
        Data for parameter estimation
    y : array_like, optional
        Points to evaluate density (default same as x)
    rust : bool, optional
        Whether to use RUST sampling (default False)
    nrust : int, optional
        Number of RUST samples (default 1000)
    debug : bool, optional
        Whether to print debug messages (default False)
        
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
    
    dd = weibull_libs.dweibullsub(x=x, y=y)
    ru_pdf = "rust not selected"
    
    if rust:
        th = tweibull_cp(nrust, x)['theta_samples']
        ru_pdf = np.zeros(len(y))
        for ir in range(nrust):
            ru_pdf += scipy.stats.weibull_min.pdf(y, c=th[ir, 0], scale=th[ir, 1])
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
    Distribution function for Weibull CP
    
    Parameters
    ----------
    x : array_like
        Data for parameter estimation
    y : array_like, optional
        Points to evaluate CDF (default same as x)
    rust : bool, optional
        Whether to use RUST sampling (default False)
    nrust : int, optional
        Number of RUST samples (default 1000)
    debug : bool, optional
        Whether to print debug messages (default False)
        
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
    
    dd = weibull_libs.dweibullsub(x=x, y=y)
    ru_cdf = "rust not selected"
    
    if rust:
        th = tweibull_cp(nrust, x)['theta_samples']
        ru_cdf = np.zeros(len(y))
        for ir in range(nrust):
            ru_cdf += scipy.stats.weibull_min.cdf(y, c=th[ir, 0], scale=th[ir, 1])
        ru_cdf = ru_cdf / nrust
    
    op = {
        'ml_params': dd['ml_params'],
        'ml_cdf': dd['ml_cdf'],
        'cp_cdf': dd['rh_cdf'],
        'ru_cdf': ru_cdf,
        'cp_method': cp_utils.rhp_dmgs_cpmethod()
    }
    return op

def tweibull_cp(n, x, debug=False):
    """
    Not yet implemented: Theta sampling for Weibull CP
    
    Parameters
    ----------
    n : int
        Number of samples
    x : array_like
        Data values
    debug : bool, optional
        Whether to print debug messages (default False)
        
    Returns
    -------
    dict
        Dictionary containing theta samples
    """
    x = cp_utils.to_array(x)

    assert np.all(np.isfinite(x)) and np.all(~np.isnan(x)), "x must be finite and not NaN"
    assert np.all(x >= 0), "x must be non-negative"
    
    t = cp_utils.ru(weibull_derivs.weibull_logf, x=x, n=n, d=2, init=[1, 1])
    
    return {'theta_samples': t['sim_vals']}

