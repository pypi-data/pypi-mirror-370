import numpy as np
from scipy.stats import genextreme
from scipy.optimize import minimize

from . import utils as cp_utils
from . import genextreme_p1_libs
from . import genextreme_p12_libs
from . import genextreme_p12_derivs
from . import evaluate_dmgs_equation as cp_dmgs


def ppf(x, t1, t2, t01=np.nan, t02=np.nan, n01=np.nan, n02=np.nan, p=np.arange(0.1, 1.0, 0.1),
                ics=np.array([0, 0, 0, 0, 0]), fdalpha=0.01, minxi=-1, maxxi=1, means=False, waicscores=False,
                extramodels=False, pdf=False, dmgs=True, rust=False, nrust=100000, predictordata=True,
                centering=True, debug=False):
    """
    Generalized Extreme Value Distribution with Two Predictors, Predictions based on a Calibrating Prior
    """
    
    # Input validation
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x)), "x must be finite and not NA"
    assert np.all(np.isfinite(p)) and not np.any(np.isnan(p)) and np.all(p > 0) and np.all(p < 1), "p must be finite, not NA, and between 0 and 1"
    assert len(t1) == len(x), "t1 must have same length as x"
    assert len(t2) == len(x), "t2 must have same length as x"
    assert len(ics) == 5, "ics must have length 5"
    
    # 1 intro
    alpha = 1 - p
    nx = len(x)
    nalpha = len(alpha)
    t01 = cp_utils.maket0(t01, n01, t1)
    t02 = cp_utils.maket0(t02, n02, t2)
    if debug:
        print(f" t01={t01}")
        print(f" t02={t02}")
    
    if pdf:
        dalpha = np.minimum(fdalpha * alpha, fdalpha * (1 - alpha))
        alpham = alpha - dalpha
        alphap = alpha + dalpha
    
    # 2 centering
    if centering:
        meant1 = np.mean(t1)
        meant2 = np.mean(t2)
        t1 = t1 - meant1
        t2 = t2 - meant2
        t01 = t01 - meant1
        t02 = t02 - meant2
    
    # 3 ml param estimate
    if debug:
        print(" ml param estimate")
    
    # in a small number of cases, direct maxlik fails. I don't really know why, but it gives nonsense
    # so I'm going to try using gev_p1 maxlik first, to determine initial conditions.
    ics = genextreme_p1_libs.gev_p1_setics(x, t1, ics)
    
    def objective1(params):
        return -genextreme_p1_libs.gev_p1_loglik(params, x, t1)
    
    opt1_result = minimize(objective1, ics, method='L-BFGS-B')
    opt1_par = opt1_result.x
    ics[0] = opt1_par[0]
    ics[1] = opt1_par[1]
    ics[2] = np.log(opt1_par[2])
    ics[3] = 0
    ics[4] = 0  # to avoid an initial error occurring sometimes
    
    def objective2(params):
        return -genextreme_p12_libs.gev_p12_loglik(params, x, t1, t2)
    
    opt1_result2 = minimize(objective2, ics, method='L-BFGS-B')  # this one uses the genextreme routine for dgev
    v1hat = opt1_result2.x[0]
    v2hat = opt1_result2.x[1]
    v3hat = opt1_result2.x[2]
    v4hat = opt1_result2.x[3]
    v5hat = opt1_result2.x[4]
    ml_params = np.array([v1hat, v2hat, v3hat, v4hat, v5hat])
    if debug:
        print(f" ml_params={ml_params}")
    
    if abs(v5hat) >= 1:
        revert2ml = True
    else:
        revert2ml = False
    # I'm having some numerical problems with ldd in reliability testing...only in gev_p12...for nx=10 and xi=0.4
    # maybe limiting v5hat to +1 in this way will help
    # for samples of nx=10, and xi=0.4 this will be triggered very frequently, but so be it
    
    # 4 predictordata
    prd = genextreme_p12_libs.gev_p12_predictordata(predictordata, x, t1, t2, t01, t02, ml_params)
    predictedparameter = prd['predictedparameter']
    adjustedx = prd['adjustedx']
    
    # 5 aic
    if debug:
        print(" aic")
    ml_value = -opt1_result2.fun
    maic = cp_utils.make_maic(ml_value, nparams=5)
    
    # 6 calc ml quantiles and density
    if debug:
        print(" ml_quantiles")
    ml_quantiles = genextreme_p12_libs.qgev_p12(1 - alpha, t01, t02, ymn=v1hat, slope=v2hat, sigma1=v3hat, sigma2=v4hat, xi=v5hat)
    if v5hat < 0:
        ml_max = (v1hat + v2hat * t01) - np.exp((v3hat + v4hat * t02)) / v5hat
    else:
        ml_max = np.inf
    fhat = genextreme_p12_libs.dgev_p12(ml_quantiles, t01, t02, ymn=v1hat, slope=v2hat, sigma1=v3hat, sigma2=v4hat, xi=v5hat, log=False)
    if debug:
        print(f" 1: ml_quantiles={ml_quantiles}")
        print(f" 1: fhat={fhat}")
    
    # dmgs
    standard_errors = "dmgs not selected"
    cp_quantiles = "dmgs not selected"
    ru_quantiles = "dmgs not selected"
    ml_pdf = "dmgs not selected"
    cp_pdf = "dmgs not selected"
    rh_flat_pdf = "dmgs not selected"
    waic1 = "dmgs not selected"
    waic2 = "dmgs not selected"
    ml_mean = "dmgs not selected"
    cp_mean = "dmgs not selected"
    rh_flat_mean = "dmgs not selected"
    
    if dmgs and not revert2ml:
        # 7 alpha pdf stuff
        if pdf:
            ml_quantilesm = genextreme_p12_libs.qgev_p12(1 - alpham, t01, t02, ymn=v1hat, slope=v2hat, sigma1=v3hat, sigma2=v4hat, xi=v5hat)
            ml_quantilesp = genextreme_p12_libs.qgev_p12(1 - alphap, t01, t02, ymn=v1hat, slope=v2hat, sigma1=v3hat, sigma2=v4hat, xi=v5hat)
            fhatm = genextreme_p12_libs.dgev_p12(ml_quantilesm, t01, t02, ymn=v1hat, slope=v2hat, sigma1=v3hat, sigma2=v4hat, xi=v5hat, log=False)
            fhatp = genextreme_p12_libs.dgev_p12(ml_quantilesp, t01, t02, ymn=v1hat, slope=v2hat, sigma1=v3hat, sigma2=v4hat, xi=v5hat, log=False)
        
        # 8 ldd
        if debug:
            print("calc ldd")
        ldd = genextreme_p12_derivs.gev_p12_ldda(x, t1, t2, v1hat, v2hat, v3hat, v4hat, v5hat)
        lddi = np.linalg.solve(ldd, np.eye(5))
        standard_errors = cp_utils.make_se(nx, lddi)
        
        # 10 calculate lddd
        if debug:
            print(" calc lddd")
        lddd = genextreme_p12_derivs.gev_p12_lddda(x, t1, t2, v1hat, v2hat, v3hat, v4hat, v5hat)
        
        # 11 mu1
        if debug:
            print(" calculate mu1")
        mu1 = genextreme_p12_derivs.gev_p12_mu1fa(alpha, t01, t02, v1hat, v2hat, v3hat, v4hat, v5hat)
        if pdf:
            mu1m = genextreme_p12_derivs.gev_p12_mu1fa(alpham, t01, t02, v1hat, v2hat, v3hat, v4hat, v5hat)
            mu1p = genextreme_p12_derivs.gev_p12_mu1fa(alphap, t01, t02, v1hat, v2hat, v3hat, v4hat, v5hat)
        
        # 12 mu2
        if debug:
            print(" calculate mu2")
        mu2 = genextreme_p12_derivs.gev_p12_mu2fa(alpha, t01, t02, v1hat, v2hat, v3hat, v4hat, v5hat)
        if pdf:
            if debug:
                print(" alpha pdf option")
            mu2m = genextreme_p12_derivs.gev_p12_mu2fa(alpham, t01, t02, v1hat, v2hat, v3hat, v4hat, v5hat)
            mu2p = genextreme_p12_derivs.gev_p12_mu2fa(alphap, t01, t02, v1hat, v2hat, v3hat, v4hat, v5hat)
        
        # 13 rh_flat model
        if debug:
            print("call dmgs")
        lambdad_cp = np.zeros(5)
        dq = cp_dmgs.dmgs(lddi, lddd, mu1, lambdad_cp, mu2, dim=5)
        if debug:
            print("make cp quantiles")
        rh_flat_quantiles = ml_quantiles + dq / (nx * fhat)
        
        # 15 alpha pdf
        if debug:
            print("step 15")
        if pdf:
            lambdad_crhp_mle = np.zeros(4)
            dqm = cp_dmgs.dmgs(lddi, lddd, mu1m, lambdad_cp, mu2m, dim=5)
            dqp = cp_dmgs.dmgs(lddi, lddd, mu1p, lambdad_cp, mu2p, dim=5)
            quantilesm = ml_quantilesm + dqm / (nx * fhatm)
            quantilesp = ml_quantilesp + dqp / (nx * fhatp)
            ml_pdf = fhat
            rh_flat_pdf = -(alphap - alpham) / (quantilesp - quantilesm)
        else:
            ml_pdf = fhat
            rh_flat_pdf = "pdf not selected"
        
        # 16 means
        if debug:
            print("step 16")
        means_result = genextreme_p12_libs.gev_p12_means(means, t01, t02, ml_params, nx)
        ml_mean = means_result['ml_mean']
        rh_flat_mean = means_result['crhp_mle_mean']
        
        # 17 waicscores
        if debug:
            print("step 17")
        waic = genextreme_p12_libs.gev_p12_waic(waicscores, x, t1, t2, v1hat, v2hat, v3hat, v4hat, v5hat,
                           lddi, lddd, lambdad_cp)
        waic1 = waic['waic1']
        waic2 = waic['waic2']
        
        # 19 rust
        if debug:
            print("step 19")
        ru_quantiles = "rust not selected"
        if rust:
            rustsim = rvs(nrust, x, t1=t1, t2=t2, t01=t01, t02=t02, rust=True, mlcp=False, debug=debug)
            ru_quantiles = cp_utils.makeq(rustsim['ru_deviates'], p)
    else:
        rh_flat_quantiles = ml_quantiles
        ru_quantiles = ml_quantiles
        rh_flat_pdf = ml_pdf
        rh_flat_mean = ml_mean
    # end of if(dmgs)
    
    # 20 decentering
    if debug:
        print("step 20")
    if centering:
        if debug:
            print(f" qgev:ml_params,meant1={ml_params},{meant1}")
        ml_params[0] = ml_params[0] - ml_params[1] * meant1
        ml_params[2] = ml_params[2] - ml_params[3] * meant2
        if predictordata:
            predictedparameter = predictedparameter - ml_params[1] * meant1
    
    if debug:
        print("step 21")
    
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

def rvs(n, x, t1, t2, t01=np.nan, t02=np.nan, n01=np.nan, n02=np.nan, ics=np.array([0, 0, 0, 0, 0]),
                minxi=-1, maxxi=1, extramodels=False, rust=False, mlcp=True, centering=True, debug=False):
    """Random generation for GEV with two predictors and calibrating prior"""
    
    # Input validation
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x)), "x must be finite and not NA"
    assert len(t1) == len(x), "t1 must have same length as x"
    assert len(t2) == len(x), "t2 must have same length as x"
    assert np.all(np.isfinite(t1)) and np.all(np.isfinite(t2)) and not np.any(np.isnan(t1)) and not np.any(np.isnan(t2)), "t1 and t2 must be finite and not NA"
    assert len(ics) == 5, "ics must have length 5"
    
    t01 = cp_utils.maket0(t01, n01, t1)
    t02 = cp_utils.maket0(t02, n02, t2)
    
    # centering
    if centering:
        meant1 = np.mean(t1)
        meant2 = np.mean(t2)
        t1 = t1 - meant1
        t2 = t2 - meant2
        t01 = t01 - meant1
        t02 = t02 - meant2
    
    ml_params = "mlcp not selected"
    ml_deviates = "mlcp not selected"
    cp_deviates = "mlcp not selected"
    ru_deviates = "rust not selected"
    
    if mlcp:
        q = ppf(x, t1=t1, t2=t2, t01=t01, t02=t02, n01=np.nan, n02=np.nan, p=np.random.uniform(size=n),
                       ics=ics, extramodels=extramodels, centering=centering)
        ml_params = q['ml_params']
        if debug:
            print(f" inside rgev_p12_cp: ml_params={ml_params}")
        ml_deviates = q['ml_quantiles']
        ru_deviates = q['ru_quantiles']
        cp_deviates = q['cp_quantiles']
    
    if rust:
        th = tgev_p12_cp(n, x, t1, t2)['theta_samples']
        ru_deviates = np.zeros(n)
        for i in range(n):
            mu = th[i, 0] + t01 * th[i, 1]
            sigma = np.exp(th[i, 2] + t02 * th[i, 3])
            xi = th[i, 4]
            ru_deviates[i] = genextreme.rvs(c=-xi, loc=mu, scale=sigma, size=1)
    
    # decentering
    if debug:
        print(f" rgev:ml_params,meant1={ml_params},{meant1}")
    if mlcp and centering:
        ml_params[0] = ml_params[0] - ml_params[1] * meant1
        ml_params[2] = ml_params[2] - ml_params[3] * meant2
    
    op = {
        'ml_params': ml_params,
        'ml_deviates': ml_deviates,
        'cp_deviates': cp_deviates,
        'ru_deviates': ru_deviates,
        'cp_method': cp_utils.crhpflat_dmgs_cpmethod()
    }
    
    return op

def pdf(x, t1, t2, t01=np.nan, t02=np.nan, n01=np.nan, n02=np.nan, y=None, ics=np.array([0, 0, 0, 0, 0]),
                minxi=-1, maxxi=1, extramodels=False, rust=False, nrust=10, centering=True, debug=False):
    """Density function for GEV with two predictors and calibrating prior"""
    
    if y is None:
        y = x
    
    # Input validation
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x)), "x must be finite and not NA"
    assert np.all(np.isfinite(y)) and not np.any(np.isnan(y)), "y must be finite and not NA"
    assert len(t1) == len(x), "t1 must have same length as x"
    assert len(t2) == len(x), "t2 must have same length as x"
    assert np.all(np.isfinite(t1)) and np.all(np.isfinite(t2)) and not np.any(np.isnan(t1)) and not np.any(np.isnan(t2)), "t1 and t2 must be finite and not NA"
    assert len(ics) == 5, "ics must have length 5"
    
    if debug:
        print(" maket0")
    t01 = cp_utils.maket0(t01, n01, t1)
    t02 = cp_utils.maket0(t02, n02, t2)
    
    # centering
    if centering:
        if debug:
            print(" centering")
        meant1 = np.mean(t1)
        meant2 = np.mean(t2)
        t1 = t1 - meant1
        t2 = t2 - meant2
        t01 = t01 - meant1
        t02 = t02 - meant2
    
    if debug:
        print(" ics and optim")
    ics = genextreme_p12_libs.gev_p12_setics(x, t1, t2, ics)
    
    def objective(params):
        return -genextreme_p12_libs.gev_p12_loglik(params, x, t1, t2)
    
    opt1_result = minimize(objective, ics, method='L-BFGS-B')
    v1hat = opt1_result.x[0]
    v2hat = opt1_result.x[1]
    v3hat = opt1_result.x[2]
    v4hat = opt1_result.x[3]
    v5hat = opt1_result.x[4]
    
    if v5hat <= -1:
        revert2ml = True
    else:
        revert2ml = False
    
    ml_params = np.array([v1hat, v2hat, v3hat, v4hat, v5hat])
    
    if debug:
        print(" call sub")
    dd = genextreme_p12_libs.dgev_p12sub(x=x, t1=t1, t2=t2, y=y, t01=t01, t02=t02, ics=ics,
                    minxi=minxi, maxxi=maxxi, extramodels=extramodels, debug=debug)
    ru_pdf = "rust not selected"
    ml_params = dd['ml_params']
    
    if rust and not revert2ml:
        if debug:
            print(" rust")
        th = tgev_p12_cp(nrust, x=x, t1=t1, t2=t2, debug=debug)['theta_samples']
        if debug:
            print(" tgev call done")
        ru_pdf = np.zeros(len(y))
        for ir in range(nrust):
            mu = th[ir, 0] + t01 * th[ir, 1]
            sigma = np.exp(th[ir, 2] + t02 * th[ir, 3])
            ru_pdf = ru_pdf + genextreme.pdf(y, c=-th[ir, 4], loc=mu, scale=sigma)

        ru_pdf = ru_pdf / nrust
    else:
        ru_pdf = dd['ml_pdf']
    
    # decentering
    if centering:
        if debug:
            print(" decentering")
            print(f" dgev:ml_params,meant1={ml_params},{meant1}")
        ml_params[0] = ml_params[0] - ml_params[1] * meant1
        ml_params[2] = ml_params[2] - ml_params[3] * meant2
    
    op = {
        'ml_params': ml_params,
        'ml_pdf': dd['ml_pdf'],
        'revert2ml': revert2ml,
        'ru_pdf': ru_pdf,
        'cp_method': cp_utils.nopdfcdfmsg()
    }
    
    return op

def cdf(x, t1, t2, t01=np.nan, t02=np.nan, n01=np.nan, n02=np.nan, y=None, ics=np.array([0, 0, 0, 0, 0]),
                minxi=-1, maxxi=1, extramodels=False, rust=False, nrust=1000, centering=True, debug=False):
    """CDF function for GEV with two predictors and calibrating prior"""
    
    if y is None:
        y = x
    
    # Input validation
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x)), "x must be finite and not NA"
    assert np.all(np.isfinite(y)) and not np.any(np.isnan(y)), "y must be finite and not NA"
    assert len(t1) == len(x), "t1 must have same length as x"
    assert len(t2) == len(x), "t2 must have same length as x"
    assert np.all(np.isfinite(t1)) and np.all(np.isfinite(t2)) and not np.any(np.isnan(t1)) and not np.any(np.isnan(t2)), "t1 and t2 must be finite and not NA"
    assert len(ics) == 5, "ics must have length 5"
    
    t01 = cp_utils.maket0(t01, n01, t1)
    t02 = cp_utils.maket0(t02, n02, t2)
    
    # centering
    if centering:
        meant1 = np.mean(t1)
        meant2 = np.mean(t2)
        t1 = t1 - meant1
        t2 = t2 - meant2
        t01 = t01 - meant1
        t02 = t02 - meant2
    
    ics = genextreme_p12_libs.gev_p12_setics(x, t1, t2, ics)
    
    def objective(params):
        return -genextreme_p12_libs.gev_p12_loglik(params, x, t1, t2)
    
    opt1_result = minimize(objective, ics, method='L-BFGS-B')  # this one uses the genextreme routine for dgev
    v1hat = opt1_result.x[0]
    v2hat = opt1_result.x[1]
    v3hat = opt1_result.x[2]
    v4hat = opt1_result.x[3]
    v5hat = opt1_result.x[4]
    
    if v5hat <= -1:
        revert2ml = True
    else:
        revert2ml = False
    
    ml_params = np.array([v1hat, v2hat, v3hat, v4hat, v5hat])
    
    dd = genextreme_p12_libs.dgev_p12sub(x=x, t1=t1, t2=t2, y=y, t01=t01, t02=t02, ics=ics,
                    minxi=minxi, maxxi=maxxi, extramodels=extramodels, debug=debug)
    ru_cdf = "rust not selected"
    ml_params = dd['ml_params']
    
    if rust and not revert2ml:
        th = tgev_p12_cp(nrust, x, t1, t2)['theta_samples']
        ru_cdf = np.zeros(len(y))
        for ir in range(nrust):
            mu = th[ir, 0] + t01 * th[ir, 1]
            sigma = np.exp(th[ir, 2] + t02 * th[ir, 3])
            xi = th[ir, 4]
            ru_cdf = ru_cdf + genextreme.cdf(y, c=-xi, loc=mu, scale=np.exp(sigma))
            raise Warning(" why is it exp(sigma) here? does it work?")
        ru_cdf = ru_cdf / nrust
    else:
        ru_pdf = dd['ml_pdf']
    
    # decentering
    if centering:
        if debug:
            print(f" pgev:ml_params,meant1={ml_params},{meant1}")
        ml_params[0] = ml_params[0] - ml_params[1] * meant1
        ml_params[2] = ml_params[2] - ml_params[3] * meant2
    
    op = {
        'ml_params': ml_params,
        'ml_cdf': dd['ml_cdf'],
        'revert2ml': revert2ml,
        'ru_cdf': ru_cdf,
        'cp_method': cp_utils.nopdfcdfmsg()
    }
    
    return op

def tgev_p12_cp(n, x, t1, t2, ics=np.array([0, 0, 0, 0, 0]), extramodels=False, debug=False):
    """not implemented: Parameter sampling for GEV with two predictors and calibrating prior"""

    raise Exception('t sampling is not yet implemented.')
    
    # Input validation
    assert np.all(np.isfinite(x)) and not np.any(np.isnan(x)), "x must be finite and not NA"
    assert len(t1) == len(x), "t1 must have same length as x"
    assert len(t2) == len(x), "t2 must have same length as x"
    assert np.all(np.isfinite(t1)) and np.all(np.isfinite(t2)) and not np.any(np.isnan(t1)) and not np.any(np.isnan(t2)), "t1 and t2 must be finite and not NA"
    assert len(ics) == 5, "ics must have length 5"
    
    # centering
    meant1 = np.mean(t1)
    meant2 = np.mean(t2)
    t1 = t1 - meant1
    t2 = t2 - meant2
    
    if debug:
        print(f"sums={np.sum(x)},{np.sum(t1)},{np.sum(t2)},{n}")
    
    th = ru(genextreme_p12_derivs.gev_p12_logf, x=x, t1=t1, t2=t2, n=n, d=5, init=np.array([0, 0, 0, 0, 0]))
    if debug:
        print(" back from rust")
    
    theta_samples = th['sim_vals']
    
    # decentering
    theta_samples[:, 0] = theta_samples[:, 0] - theta_samples[:, 1] * meant1
    theta_samples[:, 2] = theta_samples[:, 2] - theta_samples[:, 3] * meant2
    
    return {'theta_samples': theta_samples}

