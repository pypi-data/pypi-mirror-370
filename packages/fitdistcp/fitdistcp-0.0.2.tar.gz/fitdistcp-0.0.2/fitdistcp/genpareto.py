import numpy as np
import scipy.stats as stats
import scipy.optimize as optimize

from . import utils as cp_utils
from . import evaluate_dmgs_equation as cp_dmgs
from . import genpareto_derivs as cp_gpd_c
from . import genpareto_libs as cp_gpd_b


def ppf(x, p=None, kloc=0, ics=None, fdalpha=0.01, customprior=0,
               minxi=-1, maxxi=2.0, means=False, waicscores=False, extramodels=False,
               pdf=False, dmgs=True, rust=False, nrust=100000, debug=False):
    """
    Passed data from the Generalized Pareto Distribution with known location parameter, returns quantiles and other results.
    
    The GP distribution has exceedcance distribution function
    S(x;μ,σ,ξ) = [1+ξ(x-μ)/σ]^(-1/ξ) if ξ ≠ 0
                 exp(-(x-μ)/σ) if ξ = 0
    
    where x is the random variable and μ,σ>0,ξ are the parameters.
    
    The calibrating prior we use is given by
    π(μ,σ,ξ) ∝ 1/σ
    as given in Jewson et al. (2025).
    
    The code will stop with an error if the input data gives a maximum likelihood
    value for the shape parameter that lies outside the range (minxi,maxxi),
    since outside this range there may be numerical problems.
    Such values seldom occur in real observed data for maxima.

    Parameters
    ----------
    x : array_like
        Input data array.
    p : array_like, optional
        Probabilities for quantile calculation (default is np.arange(0.1, 1.0, 0.1)).
    ics : list of float, optional
        Initial parameter estimates for optimization (default is [0, 0]).
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
    if p is None:
        p = np.arange(0.1, 1.0, 0.1)
    if ics is None:
        ics = np.array([0, 0])
    
    x = cp_utils.to_array(x)
    p = cp_utils.to_array(p)
    
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x)), "x must be finite and not NA"
    assert np.all(np.isfinite(p)) and not np.any(np.isnan(p)), "p must be finite and not NA"
    assert np.all(p > 0) and np.all(p < 1), "p must be between 0 and 1"
    assert len(ics) == 2, "ics must have length 2"
    assert not np.any(x < 0), "x must be non-negative"
    
    alpha = 1 - p
    nx = len(x)
    nalpha = len(alpha)
    
    if pdf:
        dalpha = np.minimum(fdalpha * alpha, fdalpha * (1 - alpha))
        alpham = alpha - dalpha
        alphap = alpha + dalpha
    
    # 2 ml param estimate
    ics = cp_gpd_b.gpd_k1_setics(x, ics)
    opt1 = optimize.minimize(lambda params: -cp_gpd_b.gpd_k1_loglik(params, x, kloc), 
                           ics, method='BFGS')
    v1hat = opt1.x[0]   # sigma
    v2hat = opt1.x[1]   # xi
    ml_params = np.array([v1hat, v2hat])
    
    # gpd_k1_checkmle(ml_params,kloc,minxi,maxxi)
    if debug:
        print(f"    v1hat,v2hat={v1hat},{v2hat}")
    
    if (abs(v2hat) >= 1) or (v2hat > 30):
        revert2ml = True
    else:
        revert2ml = False
    
    # 3 aic
    ml_value = opt1.fun
    maic = cp_utils.make_maic(ml_value, nparams=2)
    
    # 4 calc ml quantiles and densities (vectorized over alpha)
    ml_quantiles = stats.genpareto.ppf(1 - alpha, v2hat, loc=kloc, scale=v1hat)
    
    if v2hat < 0:
        ml_max = kloc - v1hat / v2hat
    else:
        ml_max = np.inf
    
    fhat = stats.genpareto.pdf(ml_quantiles, v2hat, loc=kloc, scale=v1hat)
    
    # dmgs
    standard_errors = "dmgs not selected"
    cp_quantiles = "dmgs not selected"
    rh_flat_quantiles = "dmgs not selected"
    lp_quantiles = "dmgs not selected"
    lp2_quantiles = "dmgs not selected"
    dpi_quantiles = "dmgs not selected"
    ru_quantiles = "dmgs not selected"
    ml_pdf = "dmgs not selected"
    cp_pdf = "dmgs not selected"
    rh_flat_pdf = "dmgs not selected"
    waic1 = "dmgs not selected"
    waic2 = "dmgs not selected"
    ml_mean = "dmgs not selected"
    rh_flat_mean = "dmgs not selected"
    cp_mean = "dmgs not selected"
    cp_method = "dmgs not selected"
    
    if dmgs and not revert2ml:
        # 5 alpha pdf stuff
        if pdf:
            xi = v2hat  # xi = c here
            ml_quantilesm = stats.genpareto.ppf(1 - alpham, xi, loc=kloc, scale=v1hat)
            ml_quantilesp = stats.genpareto.ppf(1 - alphap, xi, loc=kloc, scale=v1hat)
            fhatm = stats.genpareto.pdf(ml_quantilesm, xi, loc=kloc, scale=v1hat)
            fhatp = stats.genpareto.pdf(ml_quantilesp, xi, loc=kloc, scale=v1hat)
        
        if debug:
            print(f"ml_quantiles={ml_quantiles}")
        
        # 7 ldd (two versions)
        if debug:
            print("calculate ldd")
        
        ldd = cp_gpd_c.gpd_k1_ldda(x, v1hat, v2hat, kloc)
        lddi = np.linalg.inv(ldd)
        standard_errors = cp_utils.make_se(nx, lddi)
        
        if debug:
            print(f"ldd={ldd}")
        
        # 8 lddd (two versions)
        if debug:
            print("calculate lddd")
        
        lddd = cp_gpd_c.gpd_k1_lddda(x, v1hat, v2hat, kloc)
        
        # 9 mu1 (two versions)
        mu1 = cp_gpd_c.gpd_k1_mu1fa(alpha, v1hat, v2hat, kloc)
        
        if pdf:
            mu1m = cp_gpd_c.gpd_k1_mu1fa(alpham, v1hat, v2hat, kloc)
            mu1p = cp_gpd_c.gpd_k1_mu1fa(alphap, v1hat, v2hat, kloc)
        
        # 10 mu2 (two versions)
        mu2 = cp_gpd_c.gpd_k1_mu2fa(alpha, v1hat, v2hat, kloc)
        
        if pdf:
            mu2m = cp_gpd_c.gpd_k1_mu2fa(alpham, v1hat, v2hat, kloc)
            mu2p = cp_gpd_c.gpd_k1_mu2fa(alphap, v1hat, v2hat, kloc)
        
        # 13 model 4: rh_Flat with flat prior on shape (needs to use 3d version of Bayesian code)
        lambdad_rh_flat = np.array([-1/v1hat, 0])
        dq = cp_dmgs.dmgs(lddi, lddd, mu1, lambdad_rh_flat, mu2, dim=2)
        rh_flat_quantiles = ml_quantiles + dq / (nx * fhat)
        
        if pdf:
            dqm = cp_dmgs.dmgs(lddi, lddd, mu1m, lambdad_rh_flat, mu2m, dim=2)
            dqp = cp_dmgs.dmgs(lddi, lddd, mu1p, lambdad_rh_flat, mu2p, dim=2)
            quantilesm = ml_quantilesm + dqm / (nx * fhatm)
            quantilesp = ml_quantilesp + dqp / (nx * fhatp)
            ml_pdf = fhat
            rh_flat_pdf = -(alphap - alpham) / (quantilesp - quantilesm)
        else:
            ml_pdf = fhat
            rh_flat_pdf = "pdf not selected"
        
        # 15 model 6: Laplace's method
        if extramodels or means:
            lambdad_lp = np.array([0, 0])
            lddd_lp = np.zeros((2, 2, 2))
            dq = cp_dmgs.dmgs(lddi, lddd_lp, mu1, lambdad_lp, mu2, dim=2)
            lp_quantiles = ml_quantiles + dq / (nx * fhat)
        else:
            lp_quantiles = "extramodels not selected"
        
        # 16 model 7: Laplace's method, but with 1/sigma prior
        if extramodels or means:
            lambdad_lp2 = np.array([-1/v1hat, 0])
            lddd_lp2 = np.zeros((2, 2, 2))
            dq = cp_dmgs.dmgs(lddi, lddd_lp2, mu1, lambdad_lp2, mu2, dim=2)
            lp2_quantiles = ml_quantiles + dq / (nx * fhat)
        else:
            lp2_quantiles = "extramodels not selected"
        
        # 17 model 8: user defined xi gradient of log prior
        if extramodels or means:
            lambdad_dpi = np.array([-1/v1hat, customprior])
            dq = cp_dmgs.dmgs(lddi, lddd, mu1, lambdad_dpi, mu2, dim=2)
            dpi_quantiles = ml_quantiles + dq / (nx * fhat)
        else:
            dpi_quantiles = "extramodels not selected"
        
        # 18 means
        means_result = cp_gpd_b.gpd_k1_means(means, ml_params, kloc=kloc)
        
        ml_mean = means_result['ml_mean']
        rh_flat_mean = means_result['rh_flat_mean']
        
        # 19 waicscores
        waic = cp_gpd_b.gpd_k1_waic(waicscores, x, v1hat, v2hat, kloc, lddi, lddd,
                                  lambdad_rh_flat)
        waic1 = waic['waic1']
        waic2 = waic['waic2']
        
        # 21 rust
        ru_quantiles = "rust not selected"
        if rust:
            rustsim = rvs(nrust, x, kloc=kloc, rust=True, mlcp=False)
            ru_quantiles = cp_utils.makeq(rustsim['ru_deviates'], p)
    
    else:
        rh_flat_quantiles = ml_quantiles
        ru_quantiles = ml_quantiles
        lp_quantiles = ml_quantiles
        lp2_quantiles = ml_quantiles
        dpi_quantiles = ml_quantiles
        rh_flat_pdf = ml_pdf
        rh_flat_mean = ml_mean
    # end of if(dmgs)
    
    return {
        'ml_params': ml_params,
        'ml_value': ml_value,
        # 'ldd': ldd,
        # 'lddi': lddi,
        'standard_errors': standard_errors,
        'ml_quantiles': ml_quantiles,
        'ml_max': ml_max,
        'revert2ml': revert2ml,
        'cp_quantiles': rh_flat_quantiles,
        'ru_quantiles': ru_quantiles,
        'lp_quantiles': lp_quantiles,
        'lp2_quantiles': lp2_quantiles,
        'dpi_quantiles': dpi_quantiles,
        'ml_pdf': ml_pdf,
        'cp_pdf': rh_flat_pdf,
        'maic': maic,
        'waic1': waic1,
        'waic2': waic2,
        'ml_mean': ml_mean,
        'cp_mean': rh_flat_mean,
        'cp_method': cp_utils.crhpflat_dmgs_cpmethod()
    }


def rvs(n, x, kloc=0, ics=None, minxi=-1, maxxi=2.0,
               extramodels=False, rust=False, mlcp=True, debug=False):
    """
    Passed data from the Generalized Pareto Distribution, generate random samples from the GPD with calibrating prior.

    Parameters
    ----------
    n : int
        Number of samples to generate.
    x : array_like
        Input data array.
    ics : list of float, optional
        Initial parameter estimates for optimization (default is [0, 0]).
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
    
    if ics is None:
        ics = np.array([0, 0])
    
    x = cp_utils.to_array(x)
    
    # stopifnot(is.finite(n),!is.na(n),is.finite(x),!is.na(x),length(ics)==2,!x<0)
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x)), "x must be finite and not NA"
    assert len(ics) == 2, "ics must have length 2"
    assert not np.any(x < 0), "x must be non-negative"
    
    ml_params = "mlcp not selected"
    ml_deviates = "mlcp not selected"
    ru_deviates = "rust not selected"
    cp_deviates = "rust not selected"
    
    if mlcp:
        q = ppf(x, np.random.uniform(0, 1, n), kloc=kloc, ics=ics, extramodels=extramodels)
        ml_params = q['ml_params']
        ml_deviates = q['ml_quantiles']
        ru_deviates = q['ru_quantiles']
        cp_deviates = q['cp_quantiles']
    
    if rust:
        th = tgpd_k1_cp(n, x)['theta_samples']
        ru_deviates = np.zeros(n)
        for i in range(n):
            c = -th[i, 1]  # Convert xi to scipy parameterization
            ru_deviates[i] = stats.genpareto.rvs(c, loc=kloc, scale=th[i, 0], size=1)[0]
    
    op = {
        'ml_params': ml_params,
        'ml_deviates': ml_deviates,
        'cp_deviates': cp_deviates,
        'ru_deviates': ru_deviates,
        'cp_method': cp_utils.crhpflat_dmgs_cpmethod()
    }
    
    return op


def pdf(x, y=None, kloc=0, ics=np.array([0, 0]),
               minxi=-1, maxxi=2.0,
               rust=False, nrust=1000):
    """
    Passed data from the Generalized Pareto Distribution, compute the density function for the GPD with calibrating prior.

    Parameters
    ----------
    x : array_like
        Input data array.
    y : array_like, optional
        Points at which to evaluate the density (default is x).
    ics : list of float, optional
        Initial parameter estimates for optimization (default is [0, 0]).
    extramodels : bool, optional
        Whether to compute extra models (default is False).
    debug : bool, optional
        If True, print debug information (default is False).

    Returns
    -------
    dict
        Dictionary containing ML parameters, ML PDF, RU PDF, and method info.
    """

    x = cp_utils.to_array(x)
    if y is None:
        y = x
    else:
        y = cp_utils.to_array(y)
    
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x)), "x must be finite and not NA"
    assert np.all(np.isfinite(y)) and not np.any(np.isnan(y)), "y must be finite and not NA"
    assert len(ics) == 2, "ics must have length 2"
    assert not np.any(x < 0), "x must be non-negative"
    assert not np.any(y < 0), "y must be non-negative"
    
    ics = cp_gpd_b.gpd_k1_setics(x, ics)
    opt1 = optimize.minimize(lambda params: -cp_gpd_b.gpd_k1_loglik(params, x, kloc), 
                           ics, method='BFGS')
    v1hat = opt1.x[0]
    v2hat = opt1.x[1]
    
    if v2hat <= (-1):
        revert2ml = True
    else:
        revert2ml = False
    
    ml_params = np.array([v1hat, v2hat])
    # gpd_k1_checkmle(ml_params,kloc,minxi,maxxi)
    
    dd = cp_gpd_b.dgpdsub(x=x, y=y, ics=ics, kloc=kloc,
                        minxi=minxi, maxxi=maxxi)
    ru_pdf = "rust not selected"
    
    if rust and not revert2ml:
        th = tgpd_k1_cp(nrust, x)['theta_samples']
        ru_pdf = np.zeros(len(y))
        for ir in range(nrust):
            c = -th[ir, 1]  # Convert xi to scipy parameterization
            ru_pdf = ru_pdf + stats.genpareto.pdf(y, c, loc=kloc, scale=th[ir, 0])
        ru_pdf = ru_pdf / nrust
    else:
        ru_pdf = dd['ml_pdf']
    
    op = {
        'ml_params': dd['ml_params'],
        'ml_pdf': dd['ml_pdf'],
        'revert2ml': revert2ml,
        'cp_pdf': ru_pdf,
        'cp_method': cp_utils.nopdfcdfmsg()
    }
    
    return op


def cdf(x, y=None, kloc=0, ics = np.array([0, 0]), customprior=0,
               minxi=-1, maxxi=2.0, extramodels=False,
               rust=False, nrust=1000, debug=False):
    """
    Passed data from the Generalized Pareto Distribution, compute the cumulative distribution function for the GPD with calibrating prior.

    Parameters
    ----------
    x : array_like
        Input data array.
    y : array_like, optional
        Points at which to evaluate the CDF (default is x).
    ics : list of float, optional
        Initial parameter estimates for optimization (default is [0, 0]).
    extramodels : bool, optional
        Whether to compute extra models (default is False).
    debug : bool, optional
        If True, print debug information (default is False).

    Returns
    -------
    dict
        Dictionary containing ML parameters, ML CDF, RU CDF, and method info.
    """
    
    if y is None:
        y = x
    
    x = cp_utils.to_array(x)
    y = cp_utils.to_array(y)
    
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x)), "x must be finite and not NA"
    assert np.all(np.isfinite(y)) and not np.any(np.isnan(y)), "y must be finite and not NA"
    assert len(ics) == 2, "ics must have length 2"
    assert not np.any(x < 0), "x must be non-negative"
    assert not np.any(y < 0), "y must be non-negative"
    
    ics = cp_gpd_b.gpd_k1_setics(x, ics)
    opt1 = optimize.minimize(lambda params: -cp_gpd_b.gpd_k1_loglik(params, x, kloc), 
                           ics, method='BFGS')
    v1hat = opt1.x[0]
    v2hat = opt1.x[1]
    
    if v2hat <= (-1):
        revert2ml = True
    else:
        revert2ml = False
    
    ml_params = np.array([v1hat, v2hat])
    # gpd_k1_checkmle(ml_params,kloc,minxi,maxxi)
    
    dd = cp_gpd_b.dgpdsub(x=x, y=y, ics=ics, kloc=kloc,
                        minxi=minxi, maxxi=maxxi)
    ru_cdf = "rust not selected"
    
    if rust and not revert2ml:
        th = tgpd_k1_cp(nrust, x)['theta_samples']
        ru_cdf = np.zeros(len(y))
        for ir in range(nrust):
            c = -th[ir, 1]  # Convert xi to scipy parameterization
            ru_cdf = ru_cdf + stats.genpareto.cdf(y, c, loc=kloc, scale=th[ir, 0])
        ru_cdf = ru_cdf / nrust
    else:
        ru_cdf = dd['ml_cdf']
    
    op = {
        'ml_params': dd['ml_params'],
        'ml_cdf': dd['ml_cdf'],
        'revert2ml': revert2ml,
        'cp_cdf': ru_cdf,
        'cp_method': cp_utils.nopdfcdfmsg()
    }
    
    return op


def tgpd_k1_cp(n, x, kloc=0, ics=None, extramodels=False, debug=False):
    """
    Not implemented: Theta sampling for the GPD with calibrating prior.

    Parameters
    ----------
    n : int
        Number of theta samples to generate.
    x : array_like
        Input data array.
    ics : list of float, optional
        Initial parameter estimates for optimization (default is [0, 0]).
    extramodels : bool, optional
        Whether to compute extra models (default is False).
    debug : bool, optional
        If True, print debug information (default is False).

    Returns
    -------
    dict
        Dictionary containing theta samples.
    """
        
    raise Exception('tgpd_k1_cp (and rust) is not yet implemented in fitdistcp; please use the dmgs method.')
    
    if ics is None:
        ics = np.array([0, 0])
    
    x = cp_utils.to_array(x)
    
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x)), "x must be finite and not NA"
    assert len(ics) == 2, "ics must have length 2"
    assert not np.any(x < 0), "x must be non-negative"
    
    ics = cp_gpd_b.gpd_k1_setics(x, ics)
    t = cp_utils.ru(cp_gpd_b.gpd_k1_logf, x=x, kloc=kloc, n=n, d=2, init=ics)
    
    return {'theta_samples': t['sim_vals']}