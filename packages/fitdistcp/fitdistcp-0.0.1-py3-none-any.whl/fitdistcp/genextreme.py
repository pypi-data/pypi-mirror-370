import numpy as np
from scipy import stats
from scipy.optimize import minimize

from . import evaluate_dmgs_equation as cp_dmgs
from . import utils as cp_utils
from . import genextreme_libs as cp_gev_b
from . import genextreme_derivs as cp_gev_c


def ppf(x, p = np.arange(0.1, 1.0, 0.1),
           ics =  [0, 0, 0],
           fdalpha = 0.01,
           means = False,
           waicscores = False,
           extramodels = False,
           pdf = False,
           customprior: float = 0,
           dmgs = True,
           debug = False):
    """
    Passed data from the Generalized Extreme Value Distribution, returns quantiles and other results based on a Calibrating Prior.
    The calibrating prior we use is given by π(μ,σ,ξ) ∝ 1/σ as given in Jewson et al. (2025).

    Parameters
    ----------
    x : array_like
        Input data array.
    p : array_like, optional
        Probabilities for quantile calculation (default is np.arange(0.1, 1.0, 0.1)).
    ics : list of float, optional
        Initial parameter estimates for optimization (default is [0, 0, 0]).
    fdalpha : float, optional
        Finite difference step for PDF estimation (default is 0.01).
    means : bool, optional
        Whether to compute means for extra models (default is False).
    waicscores : bool, optional
        Whether to compute WAIC scores (default is False).
    extramodels : bool, optional
        Whether to compute extra models (default is False).
    pdf : bool, optional
        Whether to compute PDFs (default is False).
    customprior : float, optional
        Custom prior value for shape parameter (default is 0).
    dmgs : bool, optional
        Whether to use the DMGS method (default is True).
    debug : bool, optional
        If True, print debug information (default is False).

    Returns
    -------
    dict
        Dictionary containing ML parameters, quantiles, PDFs, means, WAIC scores, and other results.
    """
    
    # 1 intro
    # optional parameters removed until rust, pwm are implemented
    nrust = 1000
    pwm = False
    rust = False

    x = cp_utils.to_array(x)
    p = cp_utils.to_array(p)
    
    # Input validation
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x)), "x must be finite and not NaN"
    assert np.all(np.isfinite(p)) and not np.any(np.isnan(p)), "p must be finite and not NaN"
    assert np.all(p > 0) and np.all(p < 1), "p must be between 0 and 1"
    assert len(ics) == 3, "ics must have length 3"
    assert fdalpha < 1, "fdalpha must be less than 1"
    
    alpha = 1-p
    nx = len(x)
    
    if pdf:
        dalpha = np.minimum(fdalpha * alpha, fdalpha * (1 - alpha))
        alpham = alpha - dalpha
        alphap = alpha + dalpha
    

    # 2 ml param estimate
    ics = cp_gev_b.gev_setics(x, ics)
    
    # Use minimize instead of optim (with negative log-likelihood)
    opt1 = minimize(lambda params: -cp_gev_b.gev_loglik(params, x), ics, method='BFGS')
    v1hat = opt1.x[0]
    v2hat = opt1.x[1]  
    v3hat = opt1.x[2]
    ml_params = [v1hat, v2hat, v3hat]
    
    if debug:
        print(f"    v1hat,v2hat,v3hat={v1hat},{v2hat},{v3hat}")
    
    pw_params = "pwm not selected"
    if pwm:
        pw_params = cp_gev_b.gev_pwm_params(x)
    
    if abs(v3hat) >= 1:
        revert2ml = True
    else:
        revert2ml = False
    
    # 3 aic
    ml_value = -opt1.fun
    maic = cp_utils.make_maic(ml_value, nparams=3)
    
    # 4 calc ml quantiles and densities (vectorized over alpha)
    ml_quantiles = stats.genextreme.ppf(1 - alpha,-v3hat, loc=v1hat, scale=v2hat)
    
    if v3hat < 0:
        ml_max = v1hat - v2hat / v3hat
    else:
        ml_max = np.inf
    
    fhat = stats.genextreme.pdf(ml_quantiles, -v3hat, loc=v1hat, scale=v2hat)
    
    pw_quantiles = "pwm not selected"
    if pwm:
        pw_quantiles = stats.genextreme.ppf(1 - alpha,-pw_params[2],loc=pw_params[0], scale=pw_params[1])
    
    # dmgs
    standard_errors = "dmgs not selected"
    rh_flat_quantiles = "dmgs not selected"
    cp_quantiles = "dmgs not selected"
    ru_quantiles = "dmgs not selected"
    custom_quantiles = "dmgs not selected"
    ml_pdf = "dmgs not selected"
    rh_flat_pdf = "dmgs not selected"
    cp_pdf = "dmgs not selected"
    waic1 = "dmgs not selected"
    waic2 = "dmgs not selected"
    ml_mean = "dmgs not selected"
    rh_mean = "dmgs not selected"
    rh_flat_mean = "dmgs not selected"
    cp_mean = "dmgs not selected"
    cp_method = "dmgs not selected"
    custom_mean = "dmgs not selected"
    
    # 5 alpha pdf stuff
    if dmgs and not revert2ml:
        if debug:
            print(f"  ml_quantiles={ml_quantiles}")
        
        if pdf:
            ml_quantilesm = stats.genextreme.ppf(1 - alpham, -v3hat, loc=v1hat, scale=v2hat)
            ml_quantilesp = stats.genextreme.ppf(1 - alphap, -v3hat, loc=v1hat, scale=v2hat)
            fhatm = stats.genextreme.pdf(ml_quantilesm, -v3hat,loc=v1hat, scale=v2hat)
            fhatp = stats.genextreme.pdf(ml_quantilesp, -v3hat,loc=v1hat, scale=v2hat)
        
        # 7 ldd
        if debug:
            print("  calculate ldd")
        ldd = cp_gev_c.gev_ldda(x, v1hat, v2hat, v3hat)
        lddi = np.linalg.inv(ldd)
        standard_errors = cp_utils.make_se(nx, lddi)
        
        # 8 lddd
        if debug:
            print("  calculate lddd")
        lddd = cp_gev_c.gev_lddda(x, v1hat, v2hat, v3hat)
        
        # 9 mu1
        mu1 = cp_gev_c.gev_mu1fa(alpha, v1hat, v2hat, v3hat)
        if pdf:
            mu1m = cp_gev_c.gev_mu1fa(alpham, v1hat, v2hat, v3hat)
            mu1p = cp_gev_c.gev_mu1fa(alphap, v1hat, v2hat, v3hat)
        
        # 10 mu2
        mu2 = cp_gev_c.gev_mu2fa(alpha, v1hat, v2hat, v3hat)
        if pdf:
            mu2m = cp_gev_c.gev_mu2fa(alpham, v1hat, v2hat, v3hat)
            mu2p = cp_gev_c.gev_mu2fa(alphap, v1hat, v2hat, v3hat)
        
        # 13 model 4: rh_flat with flat prior on shape
        lambdad_rh_flat = np.asarray([0, -1/v2hat, 0])
        dq = cp_dmgs.dmgs(lddi, lddd, mu1, lambdad_rh_flat, mu2, dim=3)
        rh_flat_quantiles = ml_quantiles + dq / (nx * fhat)
        
        if pdf:
            dqm = cp_dmgs.dmgs(lddi, lddd, mu1m, lambdad_rh_flat, mu2m, dim=3)
            dqp = cp_dmgs.dmgs(lddi, lddd, mu1p, lambdad_rh_flat, mu2p, dim=3)
            quantilesm = ml_quantilesm + dqm / (nx * fhatm)
            quantilesp = ml_quantilesp + dqp / (nx * fhatp)
            ml_pdf = fhat
            rh_flat_pdf = -(alphap - alpham) / (quantilesp - quantilesm)
        else:
            ml_pdf = fhat
            rh_flat_pdf = "pdf not selected"
        
        # 15 model 6: custom prior on shape parameter
        if extramodels or means:
            lambdad_custom = np.asarray([0, -1/v2hat, customprior])
            dq = cp_dmgs.dmgs(lddi, lddd, mu1, lambdad_custom, mu2, dim=3)
            custom_quantiles = ml_quantiles + dq / (nx * fhat)
        else:
            custom_quantiles = "extramodels not selected"
            lambdad_custom = 0
        
        # 16 means
        # check that lambdad_custom=0 is the correct result if neither extramodels nor means holds
        means_result = cp_gev_b.gev_means(means, ml_params, lddi, lddd,
                                lambdad_rh_flat, lambdad_custom, nx, dim=3)
        ml_mean = means_result['ml_mean']
        rh_flat_mean = means_result['rh_flat_mean']
        custom_mean = means_result['custom_mean']
        
        # 17 waicscores
        waic = cp_gev_b.gev_waic(waicscores, x, v1hat, v2hat, v3hat, lddi, lddd, lambdad_rh_flat)
        waic1 = waic['waic1']
        waic2 = waic['waic2']
        
        # 19 rust
        ru_quantiles = "rust not selected"
        if rust:
            rustsim = rvs(nrust, x, rust=True, mlcp=False)
            ru_quantiles = cp_gev_b.makeq(rustsim['ru_deviates'], p)
        
        # end of if(dmgs)
    else:
        rh_flat_quantiles = ml_quantiles
        ru_quantiles = ml_quantiles
        pw_quantiles = ml_quantiles
        custom_quantiles = ml_quantiles
        rh_flat_pdf = ml_pdf
        rh_flat_mean = ml_mean
        custom_mean = ml_mean
    
    return {
        'ml_params': ml_params,
        'pw_params': pw_params,
        'ml_value': ml_value,
        'standard_errors': standard_errors,
        'ml_quantiles': ml_quantiles,
        'ml_max': ml_max,
        'revert2ml': revert2ml,
        'cp_quantiles': rh_flat_quantiles,
        'ru_quantiles': ru_quantiles,
        'pw_quantiles': pw_quantiles,
        'custom_quantiles': custom_quantiles,
        'ml_pdf': ml_pdf,
        'cp_pdf': rh_flat_pdf,
        'maic': maic,
        'waic1': waic1,
        'waic2': waic2,
        'ml_mean': ml_mean,
        'cp_mean': rh_flat_mean,
        'custom_mean': custom_mean,
        'cp_method': cp_utils.crhpflat_dmgs_cpmethod()
    }


def rvs(n, x, ics  = [0, 0, 0], extramodels = False, mlcp = True):
    """
    Passed data from the Generalized Extreme Value Distribution, generate random samples from the same distribution with calibrating prior.

    Parameters
    ----------
    n : int
        Number of samples to generate.
    x : array_like
        Input data array.
    ics : list of float, optional
        Initial parameter estimates for optimization (default is [0, 0, 0]).
    extramodels : bool, optional
        Whether to compute extra models (default is False).
    mlcp : bool, optional
        Whether to use ML and CP deviates (default is True).
    debug : bool, optional
        If True, print debug information (default is False).

    Returns
    -------
    dict
        Dictionary containing ML parameters, ML deviates, CP deviates, RU deviates, and method info.
    """
    
    # optional parameter removed until rust is implemented
    rust = False

    x = cp_utils.to_array(x)
    
    assert np.isfinite(n) and not np.isnan(n), "n must be finite and not NaN"
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x)), "x must be finite and not NaN"
    assert len(ics) == 3, "ics must have length 3"
    
    ml_params = "mlcp not selected"
    ml_deviates = "mlcp not selected"
    cp_deviates = "mlcp not selected"
    ru_deviates = "rust not selected"
    
    if mlcp:
        q = ppf(x, np.random.uniform(0, 1, n), ics=ics, extramodels=extramodels)
        ml_params = q['ml_params']
        ml_deviates = q['ml_quantiles']
        ru_deviates = q['ru_quantiles']
        cp_deviates = q['cp_quantiles']
    
    if rust:
        th = tgev_cp(n, x)['theta_samples']
        ru_deviates = np.zeros(n)
        for i in range(n):
            ru_deviates[i] = stats.genextreme.rvs(-th[i, 2], loc=th[i, 0], scale=th[i, 1])
    
    return {
        'ml_params': ml_params,
        'ml_deviates': ml_deviates,
        'cp_deviates': cp_deviates,
        'ru_deviates': ru_deviates,
        'cp_method': cp_utils.crhpflat_dmgs_cpmethod()
    }


def pdf(x, y = None, ics = [0, 0, 0]):
    """
    Passed data from the Generalized Extreme Value Distribution, compute the density function for the GEV distribution with calibrating prior.

    Parameters
    ----------
    x : array_like
        Input data array.
    y : array_like, optional
        Points at which to evaluate the density (default is x).
    ics : list of float, optional
        Initial parameter estimates for optimization (default is [0, 0, 0]).
    extramodels : bool, optional
        Whether to compute extra models (default is False).
    debug : bool, optional
        If True, print debug information (default is False).

    Returns
    -------
    dict
        Dictionary containing ML parameters, ML PDF, RU PDF, and method info.
    """

    # optional parameters removed until rust is implemented
    rust = False
    nrust = 1000
    
    x = cp_utils.to_array(x)
    if y is None:
        y = x
    else:
        y = cp_utils.to_array(y)
    
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x)), "x must be finite and not NaN"
    assert np.all(np.isfinite(y)) and not np.any(np.isnan(y)), "y must be finite and not NaN"
    assert len(ics) == 3, "ics must have length 3"
    
    ics = cp_gev_b.gev_setics(x, ics)
    opt1 = minimize(lambda params: -cp_gev_b.gev_loglik(params, x), ics, method='BFGS')
    v1hat = opt1.x[0]
    v2hat = opt1.x[1]
    v3hat = opt1.x[2]
    
    if v3hat <= -1:
        revert2ml = True
    else:
        revert2ml = False
    
    dd = cp_gev_b.dgevsub(x=x, y=y, ics=ics)
    ru_pdf = "rust not selected"
    
    if rust and not revert2ml:
        th = tgev_cp(nrust, x)['theta_samples']
        ru_pdf = np.zeros(len(y))
        for ir in range(nrust):
            ru_pdf = ru_pdf + stats.genextreme.pdf(y, -th[ir, 2],loc=th[ir, 0], scale=th[ir, 1])
        ru_pdf = ru_pdf / nrust
    else:
        ru_pdf = dd['ml_pdf']
    
    return {
        'ml_params': dd['ml_params'],
        'ml_pdf': dd['ml_pdf'],
        'revert2ml': revert2ml,
        'cp_pdf': ru_pdf,
        'cp_method': cp_utils.nopdfcdfmsg()
    }


def cdf(x, y = None,
           ics = [0, 0, 0],
           extramodels = False,
           debug = False):
    """
    Passed data from the Generalized Extreme Value Distribution, compute the cumulative distribution function for the GEV distribution with calibrating prior.

    Parameters
    ----------
    x : array_like
        Input data array.
    y : array_like, optional
        Points at which to evaluate the CDF (default is x).
    ics : list of float, optional
        Initial parameter estimates for optimization (default is [0, 0, 0]).
    extramodels : bool, optional
        Whether to compute extra models (default is False).
    debug : bool, optional
        If True, print debug information (default is False).

    Returns
    -------
    dict
        Dictionary containing ML parameters, ML CDF, RU CDF, and method info.
    """

    # optional parameters removed until rust is implemented
    rust = False
    nrust = 1000
    
    x = cp_utils.to_array(x)
    if y is None:
        y = x
    y = cp_utils.to_array(y)
    
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x)), "x must be finite and not NaN"
    assert np.all(np.isfinite(y)) and not np.any(np.isnan(y)), "y must be finite and not NaN"
    assert len(ics) == 3, "ics must have length 3"
    
    ics = cp_gev_b.gev_setics(x, ics)
    opt1 = minimize(lambda params: -cp_gev_b.gev_loglik(params, x), ics, method='BFGS')
    v1hat = opt1.x[0]
    v2hat = opt1.x[1]
    v3hat = opt1.x[2]
    
    if v3hat <= -1:
        revert2ml = True
    else:
        revert2ml = False
    
    ml_params = [v1hat, v2hat, v3hat]
    dd = cp_gev_b.dgevsub(x=x, y=y, ics=ics)
    ru_cdf = "rust not selected"
    
    if rust and not revert2ml:
        th = tgev_cp(nrust, x)['theta_samples']
        ru_cdf = np.zeros(len(y))
        for ir in range(nrust):
            ru_cdf = ru_cdf + stats.genextreme.cdf(y, -th[ir, 2], loc=th[ir, 0], scale=th[ir, 1])
        ru_cdf = ru_cdf / nrust
    else:
        ru_cdf = dd['ml_cdf']
    
    return {
        'ml_params': dd['ml_params'],
        'ml_cdf': dd['ml_cdf'],
        'revert2ml': revert2ml,
        'cp_cdf': ru_cdf,
        'cp_method': cp_utils.nopdfcdfmsg()
    }


# not yet implemented
def tgev_cp(n, x, ics = [0, 0, 0]):
    """
    Not yet implemented: Theta sampling for the GEV distribution with calibrating prior.

    Parameters
    ----------
    n : int
        Number of theta samples to generate.
    x : array_like
        Input data array.
    ics : list of float, optional
        Initial parameter estimates for optimization (default is [0, 0, 0]).
    extramodels : bool, optional
        Whether to compute extra models (default is False).
    debug : bool, optional
        If True, print debug information (default is False).

    Returns
    -------
    dict
        Dictionary containing theta samples.
    """
        
    raise Exception('tgev_cp (and rust) is not yet implemented in fitdistcp; please use the dmgs method.')
    
    x = cp_utils.to_array(x)
    
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x)), "x must be finite and not NaN"
    assert len(ics) == 3, "ics must have length 3"
    
    ics = cp_gev_b.gev_setics(x, ics)
    t = ru(cp_gev_b.gev_logf, x=x, n=n, d=3, init=ics)
    
    return {'theta_samples': t['sim_vals']}