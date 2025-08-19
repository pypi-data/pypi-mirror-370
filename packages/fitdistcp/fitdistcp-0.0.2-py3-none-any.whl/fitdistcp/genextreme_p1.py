import numpy as np
from scipy.optimize import minimize
from scipy import stats
import warnings

from . import utils as cp_utils
from . import evaluate_dmgs_equation as cp_dmgs
from . import genextreme_p1_libs as cp_gev_p1_b
from . import genextreme_p1_derivs as cp_gev_p1_c


def ppf(x, t, t0=None, n0=None, p=np.arange(0.1, 1.0, 0.1), ics=np.array([0,0,0,0]),
               fdalpha=0.01, minxi=-1, maxxi=1, means=False, waicscores=False, extramodels=False,
               pdf=False, dmgs=True, rust=False, nrust=100000, predictordata=True,
               centering=True, debug=False):
    """Generalized Extreme Value Distribution with a Predictor, Predictions Based on a Calibrating Prior.

    Parameters
    ----------
    x : array_like
        Input data array.
    t : array_like
        Predictor variable array.
    t0 : array_like or None, optional
        Predictor values for prediction (default is None).
    n0 : int or None, optional
        Number of prediction points (default is None).
    p : array_like, optional
        Probabilities for quantile calculation (default is np.arange(0.1, 1.0, 0.1)).
    ics : array_like, optional
        Initial parameter estimates for optimization (default is [0, 0, 0, 0]).
    fdalpha : float, optional
        Finite difference step for PDF estimation (default is 0.01).
    minxi : float, optional
        Minimum value for the shape parameter xi (default is -1).
    maxxi : float, optional
        Maximum value for the shape parameter xi (default is 1).
    means : bool, optional
        Whether to compute means for extra models (default is False).
    waicscores : bool, optional
        Whether to compute WAIC scores (default is False).
    extramodels : bool, optional
        Whether to compute extra models (default is False).
    pdf : bool, optional
        Whether to compute PDFs (default is False).
    dmgs : bool, optional
        Whether to use the DMGS method (default is True).
    rust : bool, optional
        Whether to use the rust method (default is False).
    nrust : int, optional
        Number of rust simulations (default is 100000).
    predictordata : bool, optional
        Whether to return predictor data (default is True).
    centering : bool, optional
        Whether to center the predictor variable (default is True).
    debug : bool, optional
        If True, print debug information (default is False).

    Returns
    -------
    dict
        Dictionary containing ML parameters, quantiles, PDFs, means, WAIC scores, and other results.
    """

    x = cp_utils.to_array(x)
    t = cp_utils.to_array(t)
    
    # Input validation
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x))
    assert np.all(np.isfinite(p)) and not np.any(np.isnan(p)) and np.all(p > 0) and np.all(p < 1)
    assert len(ics) == 4

    # 1 intro
    alpha = 1 - p
    nx = len(x)
    nalpha = len(alpha)
    t0 = cp_utils.maket0(t0, n0, t)
    
    if debug:
        print(f" t0={t0}")
    
    if pdf:
        dalpha = np.minimum(fdalpha * alpha, fdalpha * (1 - alpha))
        alpham = alpha - dalpha
        alphap = alpha + dalpha

    # 2 centering
    if centering:
        meant = np.mean(t)
        t = t - meant
        t0 = t0 - meant

    # 3 ml param estimate
    if debug:
        print(" ml param estimate")
    
    ics = cp_gev_p1_b.gev_p1_setics(x, t, ics)
    
    # Define objective function for optimization
    def neg_loglik(params):
        return -cp_gev_p1_b.gev_p1_loglik(params, x, t)
    
    opt1 = minimize(neg_loglik, ics, method='BFGS')
    if not opt1.success:
        warnings.warn('scipy.optimize.minimize fails due to precision loss.')
    v1hat = opt1.x[0]
    v2hat = opt1.x[1] 
    v3hat = opt1.x[2]
    v4hat = opt1.x[3]
    ml_params = np.array([v1hat, v2hat, v3hat, v4hat])
    
    if debug:
        print(f" ml_params={ml_params}")
    
    if abs(v4hat) >= 1:
        revert2ml = True
    else:
        revert2ml = False

    # 4 predictordata
    prd = cp_gev_p1_b.gev_p1_predictordata(predictordata, x, t, t0, ml_params)
    predictedparameter = prd['predictedparameter']
    adjustedx = prd['adjustedx']

    # 5 aic
    if debug:
        print(" aic")
    
    ml_value = -opt1.fun
    maic = cp_utils.make_maic(ml_value, nparams=4)

    # 6 calc ml quantiles and density
    if debug:
        print(" ml_quantiles")
    
    ml_quantiles = cp_gev_p1_b.qgev_p1((1-alpha), t0, ymn=v1hat, slope=v2hat, sigma=v3hat, xi=v4hat)
    
    if v4hat < 0:
        ml_max = (v1hat + v2hat * t0) - v3hat / v4hat
    else:
        ml_max = np.inf
    
    fhat = cp_gev_p1_b.dgev_p1(ml_quantiles, t0, ymn=v1hat, slope=v2hat, sigma=v3hat, xi=v4hat, log=False)
    
    if debug:
        print(f" ml_quantiles={ml_quantiles}")
        print(f" fhat={fhat}")

    # dmgs initialization
    standard_errors = "dmgs not selected"
    rh_flat_quantiles = "dmgs not selected"
    cp_quantiles = "dmgs not selected"
    ru_quantiles = "dmgs not selected"
    rh_flat_pdf = "dmgs not selected"
    ml_pdf = "dmgs not selected"
    cp_pdf = "dmgs not selected"
    waic1 = "dmgs not selected"
    waic2 = "dmgs not selected"
    ml_mean = "dmgs not selected"
    cp_mean = "dmgs not selected"
    rh_flat_mean = "dmgs not selected"
    cp_method = "dmgs not selected"
    
    if dmgs and not revert2ml:
        # 7 alpha pdf stuff
        # -for now, I only make the pdf. I could add cdf too I suppose. Somehow.
        if pdf:
            ml_quantilesm = cp_gev_p1_b.qgev_p1((1-alpham), t0, ymn=v1hat, slope=v2hat, sigma=v3hat, xi=v4hat)
            ml_quantilesp = cp_gev_p1_b.qgev_p1((1-alphap), t0, ymn=v1hat, slope=v2hat, sigma=v3hat, xi=v4hat)
            fhatm = cp_gev_p1_b.dgev_p1(ml_quantilesm, t0, ymn=v1hat, slope=v2hat, sigma=v3hat, xi=v4hat, log=False)
            fhatp = cp_gev_p1_b.dgev_p1(ml_quantilesp, t0, ymn=v1hat, slope=v2hat, sigma=v3hat, xi=v4hat, log=False)

        # 8 ldd
        ldd = cp_gev_p1_c.gev_p1_ldda(x, t, v1hat, v2hat, v3hat, v4hat)
        
        if debug:
            print(f" ldd={ldd}")
            print(f" det(ldd)={np.linalg.det(ldd)}")
        
        lddi = np.linalg.solve(ldd, np.eye(ldd.shape[0]))
        standard_errors = cp_utils.make_se(nx, lddi)

        # 10 calculate lddd
        if debug:
            print(" lddd")
        
        lddd = cp_gev_p1_c.gev_p1_lddda(x, t, v1hat, v2hat, v3hat, v4hat)

        # 11 mu1
        if debug:
            print(" calculate mu1")
        
        mu1 = cp_gev_p1_c.gev_p1_mu1fa(alpha, t0, v1hat, v2hat, v3hat, v4hat)

        if pdf:
            mu1m = cp_gev_p1_c.gev_p1_mu1fa(alpham, t0, v1hat, v2hat, v3hat, v4hat)
            mu1p = cp_gev_p1_c.gev_p1_mu1fa(alphap, t0, v1hat, v2hat, v3hat, v4hat)

        # 12 mu2
        if debug:
            print(" calculate mu2")
        
        mu2 = cp_gev_p1_c.gev_p1_mu2fa(alpha, t0, v1hat, v2hat, v3hat, v4hat)

        if pdf:
            mu2m = cp_gev_p1_c.gev_p1_mu2fa(alpham, t0, v1hat, v2hat, v3hat, v4hat)
            mu2p = cp_gev_p1_c.gev_p1_mu2fa(alphap, t0, v1hat, v2hat, v3hat, v4hat)

        # 15 model 4: rh_Flat with flat prior on shape (needs to use 4d version of Bayesian code)
        lambdad_rh_flat = np.array([0, 0, -1/v3hat, 0])
        dq = cp_dmgs.dmgs(lddi, lddd, mu1, lambdad_rh_flat, mu2, dim=4)
        rh_flat_quantiles = ml_quantiles + dq / (nx * fhat)
        
        if pdf:
            dqm = cp_dmgs.dmgs(lddi, lddd, mu1m, lambdad_rh_flat, mu2m, dim=4)
            dqp = cp_dmgs.dmgs(lddi, lddd, mu1p, lambdad_rh_flat, mu2p, dim=4)
            quantilesm = ml_quantilesm + dqm / (nx * fhatm)
            quantilesp = ml_quantilesp + dqp / (nx * fhatp)
            ml_pdf = fhat
            rh_flat_pdf = -(alphap - alpham) / (quantilesp - quantilesm)
        else:
            ml_pdf = fhat
            rh_flat_pdf = "pdf not selected"

        # 17 means
        means_result = cp_gev_p1_b.gev_p1_means(means, t0, ml_params, lddi, lddd,
                                               lambdad_rh_flat, nx, dim=4)
        ml_mean = means_result['ml_mean']
        rh_flat_mean = means_result['rh_flat_mean']

        # 18 waicscores
        waic = cp_gev_p1_b.gev_p1_waic(waicscores, x, t, v1hat, v2hat, v3hat, v4hat,
                                      lddi, lddd, lambdad_rh_flat)
        waic1 = waic['waic1']
        waic2 = waic['waic2']

        # 20 rust
        ru_quantiles = "rust not selected"
        if rust:
            rustsim = rvs(nrust, x, t=t, t0=t0, rust=True, mlcp=False)
            ru_quantiles = cp_utils.makeq(rustsim['ru_deviates'], p)
    else:
        rh_flat_quantiles = ml_quantiles
        ru_quantiles = ml_quantiles
        rh_flat_pdf = ml_pdf
        rh_flat_mean = ml_mean

    # 21 decentering
    if centering:
        ml_params[0] = ml_params[0] - ml_params[1] * meant
        if predictordata:
            predictedparameter = predictedparameter - ml_params[1] * meant

    return {
        'ml_params': ml_params,
        'ml_value': ml_value,
        'predictedparameter': predictedparameter,
        'adjustedx': adjustedx,
        'standard_errors': standard_errors,
        'revert2ml': revert2ml,
        'ml_quantiles': ml_quantiles,
        'ml_max': ml_max,
        'cp_quantiles': rh_flat_quantiles,
        'ru_quantiles': ru_quantiles,
        'ml_pdf': ml_pdf,
        'cp_pdf': rh_flat_pdf,
        'maic': maic,
        'waic1': waic1,
        'waic2': waic2,
        'ml_mean': ml_mean,
        'cp_mean': rh_flat_mean,
        'cp_method': cp_utils.crhpflat_dmgs_cpmethod()
    }

def rvs(n, x, t, t0=None, n0=None, ics=np.array([0,0,0,0]),
               minxi=-1, maxxi=1, extramodels=False, rust=False, mlcp=True, debug=False):
    """
    Random generation for GEV distribution with predictor and calibrating prior.

    Parameters
    ----------
    n : int
        Number of samples to generate.
    x : array_like
        Input data array.
    t : array_like
        Predictor variable array.
    t0 : array_like or None, optional
        Predictor values for prediction (default is None).
    n0 : int or None, optional
        Number of prediction points (default is None).
    ics : array_like, optional
        Initial parameter estimates for optimization (default is [0, 0, 0, 0]).
    minxi : float, optional
        Minimum value for the shape parameter xi (default is -1).
    maxxi : float, optional
        Maximum value for the shape parameter xi (default is 1).
    extramodels : bool, optional
        Whether to compute extra models (default is False).
    rust : bool, optional
        Whether to use the rust method (default is False).
    mlcp : bool, optional
        Whether to use ML and CP deviates (default is True).
    debug : bool, optional
        If True, print debug information (default is False).

    Returns
    -------
    dict
        Dictionary containing ML parameters, ML deviates, CP deviates, RU deviates, and method info.
    """
    
    x = cp_utils.to_array(x)
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x))
    assert np.all(np.isfinite(t)) and not np.any(np.isnan(t))
    assert len(ics) == 4

    t0 = cp_utils.maket0(t0=t0, n0=n0, t=t)

    # centering
    meant = np.mean(t)
    t = t - meant
    t0 = t0 - meant

    ml_params = "mlcp not selected"
    ml_deviates = "mlcp not selected"
    ru_deviates = "rust not selected"
    cp_deviates = "rust not selected"

    if mlcp:
        q = ppf(x, t=t, t0=t0, n0=None, p=np.random.uniform(0, 1, n), ics=ics, extramodels=extramodels)
        ml_params = q['ml_params']
        ml_deviates = q['ml_quantiles']
        ru_deviates = q['ru_quantiles']
        cp_deviates = q['cp_quantiles']

    if rust:
        th = tgev_p1_cp(n, x, t)['theta_samples']
        ru_deviates = np.zeros(n)
        for i in range(n):
            mu = th[i,0] + t0 * th[i,1]
            ru_deviates[i] = stats.genextreme.rvs(c=-th[i,3], loc=mu, scale=th[i,2], size=1)

    # decentering
    if mlcp:
        ml_params[0] = ml_params[0] - ml_params[1] * meant

    op = {
        'ml_params': ml_params,
        'ml_deviates': ml_deviates,
        'cp_deviates': cp_deviates,
        'ru_deviates': ru_deviates,
        'cp_method': cp_utils.crhpflat_dmgs_cpmethod()
    }

    return op

def pdf(x, t, t0=None, n0=None, y=None, ics=np.array([0,0,0,0]),
               minxi=-1, maxxi=1, extramodels=False,
               rust=False, nrust=1000, centering=True, debug=False):
    """
    Density function for GEV distribution with predictor and calibrating prior
    Parameters
    ----------
    x : array_like
        Input data array.
    t : array_like
        Predictor variable array.
    t0 : array_like or None, optional
        Predictor values for prediction (default is None).
    n0 : int or None, optional
        Number of prediction points (default is None).
    y : array_like or None, optional
        Points at which to evaluate the density (default is x).
    ics : array_like, optional
        Initial parameter estimates for optimization (default is [0, 0, 0, 0]).
    minxi : float, optional
        Minimum value for the shape parameter xi (default is -1).
    maxxi : float, optional
        Maximum value for the shape parameter xi (default is 1).
    extramodels : bool, optional
        Whether to compute extra models (default is False).
    rust : bool, optional
        Whether to use the rust method (default is False).
    nrust : int, optional
        Number of rust simulations (default is 1000).
    centering : bool, optional
        Whether to center the predictor variable (default is True).
    debug : bool, optional
        If True, print debug information (default is False).

    Returns
    -------
    dict
        Dictionary containing ML parameters, ML PDF, RU PDF, and method info.
    """
    
    if y is None:
        y = x
        
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x))
    assert np.all(np.isfinite(y)) and not np.any(np.isnan(y))
    assert np.all(np.isfinite(t)) and not np.any(np.isnan(t))
    assert len(ics) == 4

    t0 = cp_utils.maket0(t0, n0, t)

    # centering
    if centering:
        meant = np.mean(t)
        t = t - meant
        t0 = t0 - meant

    ics = cp_gev_p1_b.gev_p1_setics(x, t, ics)
    
    # Define objective function for optimization
    def neg_loglik(params):
        return -cp_gev_p1_b.gev_p1_loglik(params, x, t)
    
    opt1 = minimize(neg_loglik, ics, method='BFGS')
    v1hat = opt1.x[0]
    v2hat = opt1.x[1] 
    v3hat = opt1.x[2]
    v4hat = opt1.x[3]
    
    if v4hat <= (-1):
        revert2ml = True
    else:
        revert2ml = False
        
    ml_params = np.array([v1hat, v2hat, v3hat, v4hat])
    
    dd = cp_gev_p1_b.dgev_p1sub(x=x, t=t, y=y, t0=t0, ics=ics, minxi=minxi, maxxi=maxxi, extramodels=extramodels)
    ru_pdf = "rust not selected"
    ml_params = dd['ml_params']

    if rust and not revert2ml:
        th = tgev_p1_cp(nrust, x, t)['theta_samples']
        ru_pdf = np.zeros(len(y))
        for ir in range(nrust):
            mu = th[ir,0] + t0 * th[ir,1]
            ru_pdf = ru_pdf + stats.genextreme.pdf(y, c=-th[ir,3], loc=mu, scale=th[ir,2])
        ru_pdf = ru_pdf / nrust
    else:
        ru_pdf = dd['ml_pdf']

    # decentering
    if centering:
        ml_params[0] = ml_params[0] - ml_params[1] * meant

    op = {
        'ml_params': ml_params,
        'ml_pdf': dd['ml_pdf'],
        'revert2ml': revert2ml,
        'ru_pdf': ru_pdf,
        'cp_method': cp_utils.nopdfcdfmsg()
    }

    return op

def cdf(x, t, t0=None, n0=None, y=None, ics=np.array([0,0,0,0]),
               minxi=-1, maxxi=1, extramodels=False,
               rust=False, nrust=1000, centering=True, debug=False):
    """
    Distribution function for GEV distribution with predictor and calibrating prior.

    Parameters
    ----------
    x : array_like
        Input data array.
    t : array_like
        Predictor variable array.
    t0 : array_like or None, optional
        Predictor values for prediction (default is None).
    n0 : int or None, optional
        Number of prediction points (default is None).
    y : array_like or None, optional
        Points at which to evaluate the CDF (default is x).
    ics : array_like, optional
        Initial parameter estimates for optimization (default is [0, 0, 0, 0]).
    minxi : float, optional
        Minimum value for the shape parameter xi (default is -1).
    maxxi : float, optional
        Maximum value for the shape parameter xi (default is 1).
    extramodels : bool, optional
        Whether to compute extra models (default is False).
    rust : bool, optional
        Whether to use the rust method (default is False).
    nrust : int, optional
        Number of rust simulations (default is 1000).
    centering : bool, optional
        Whether to center the predictor variable (default is True).
    debug : bool, optional
        If True, print debug information (default is False).

    Returns
    -------
    dict
        Dictionary containing ML parameters, ML CDF, RU CDF, and method info.
    """
    
    if y is None:
        y = x
        
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x))
    assert np.all(np.isfinite(y)) and not np.any(np.isnan(y))
    assert np.all(np.isfinite(t)) and not np.any(np.isnan(t))
    assert len(ics) == 4

    t0 = cp_utils.maket0(t0, n0, t)
    
    # centering
    if centering:
        meant = np.mean(t)
        t = t - meant
        t0 = t0 - meant

    ics = cp_gev_p1_b.gev_p1_setics(x, t, ics)
    
    # Define objective function for optimization
    def neg_loglik(params):
        return -cp_gev_p1_b.gev_p1_loglik(params, x, t)
    
    opt1 = minimize(neg_loglik, ics, method='BFGS')
    v1hat = opt1.x[0]
    v2hat = opt1.x[1] 
    v3hat = opt1.x[2]
    v4hat = opt1.x[3]
    
    if v4hat <= (-1):
        revert2ml = True
    else:
        revert2ml = False
        
    ml_params = np.array([v1hat, v2hat, v3hat, v4hat])
    
    dd = cp_gev_p1_b.dgev_p1sub(x=x, t=t, y=y, t0=t0, ics=ics, minxi=minxi, maxxi=maxxi, extramodels=extramodels)
    ru_cdf = "rust not selected"
    ml_params = dd['ml_params']

    if rust and not revert2ml:
        th = tgev_p1_cp(nrust, x, t)['theta_samples']
        ru_cdf = np.zeros(len(y))
        for ir in range(nrust):
            mu = th[ir,0] + t0 * th[ir,1]
            ru_cdf = ru_cdf + stats.genextreme.cdf(y, c=-th[ir,3], loc=mu, scale=th[ir,2])
        ru_cdf = ru_cdf / nrust
    else:
        ru_pdf = dd['ml_pdf']

    # decentering
    if centering:
        ml_params[0] = ml_params[0] - ml_params[1] * meant

    op = {
        'ml_params': ml_params,
        'ml_cdf': dd['ml_cdf'],
        'revert2ml': revert2ml,
        'ru_cdf': ru_cdf,
        'cp_method': cp_utils.nopdfcdfmsg()
    }
    
    return op

def tgev_p1_cp(n, x, t, ics=np.array([0,0,0,0]),
               extramodels=False, debug=False):
    """Not implemented: Theta sampling for GEV distribution with predictor and calibrating prior

    Parameters
    ----------
    n : int
        Number of theta samples to generate.
    x : array_like
        Input data array.
    t : array_like
        Predictor variable array.
    ics : array_like, optional
        Initial parameter estimates for optimization (default is [0, 0, 0, 0]).
    extramodels : bool, optional
        Whether to compute extra models (default is False).
    debug : bool, optional
        If True, print debug information (default is False).

    Returns
    -------
    dict
        Dictionary containing theta samples.
    """

    raise Exception('tgev_p1_cp (and rust) is not yet implemented in fitdistcp; please use the dmgs method.')
    
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x))
    assert np.all(np.isfinite(t)) and not np.any(np.isnan(t))
    assert len(ics) == 4

    # centering
    meant = np.mean(t)
    t = t - meant

    ics = cp_gev_p1_b.gev_p1_setics(x, t, ics)
    th = cp_utils.ru(cp_gev_p1_b.gev_p1_logf, x=x, t=t, n=n, d=4, init=ics)
    theta_samples = th['sim_vals']
    
    # decentering
    theta_samples[:,0] = theta_samples[:,0] - theta_samples[:,1] * meant

    return {'theta_samples': theta_samples}

