import numpy as np
import scipy.stats as stats
import scipy.optimize as optimize
import warnings
import sys

from . import utils as cp_utils
from . import genpareto_derivs as cp_gpd_k1_c


def rgpd_k1_minmax(nx, kloc, sigma, xi, minxi=-0.45, maxxi=0.45):
    """rgpd for gpd_k1 but with maxlik xi within bounds
    
    Returns:
        Vector
    """
    xihat = -9999
    while (xihat < minxi) or (xihat > maxxi):  # 0.46 also works...0.47 doesn't
        xx = stats.genpareto.rvs(c=xi, loc=kloc, scale=sigma, size=nx)
        ics = gpd_k1_setics(xx, np.array([0, 0]))
        opt1 = optimize.minimize(lambda params: -gpd_k1_loglik(params, xx, kloc), 
                               ics, method='BFGS')
        xihat = opt1.x[1]
    return xx

def gpd_k1_waic(waicscores, x, v1hat, v2hat, kloc, lddi, lddd, lambdad):
    """Waic
    
    Returns:
        Dictionary with waic1 and waic2
    """
    if waicscores:
        f1f = cp_gpd_k1_c.gpd_k1_f1fa(x, v1hat, v2hat, kloc)
        f2f = cp_gpd_k1_c.gpd_k1_f2fa(x, v1hat, v2hat, kloc)
        
        fhatx = stats.genpareto.pdf(x, c=v2hat, loc=kloc, scale=v1hat)
        waic = cp_utils.make_waic(x, fhatx, lddi, lddd, f1f, lambdad, f2f, dim=2)
        waic1 = waic['waic1']
        waic2 = waic['waic2']
    else:
        waic1 = "waicscores not selected"
        waic2 = "waicscores not selected"
    
    return {'waic1': waic1, 'waic2': waic2}


def gpd_k1_logf(params, x, kloc):
    """Logf for RUST"""
    sc = max(params[0], sys.float_info.epsilon)
    sh = params[1]
    logf = np.sum(stats.genpareto.logpdf(x, c=sh, loc=kloc, scale=sc)) - np.log(sc)
    return logf


def gpd_k1_setics(x, ics):
    """Set initial conditions"""
    if (ics[0] == 0) and (ics[1] == 0):
        ics_new = [np.std(x, ddof=1), 0]
    else:
        ics_new = ics
    return ics_new


def gpd_k1_loglik(vv, x, kloc):
    """log-likelihood function"""
    n = len(x)
    loglik = np.sum(stats.genpareto.logpdf(
        x, c=vv[1], loc=kloc, scale=max(vv[0], sys.float_info.epsilon)))
    return loglik


def gpd_k1_checkmle(ml_params, kloc, minxi=-1, maxxi=2):
    """Check MLE"""
    # currently not used, because instead I revert2ml
    v1hat = ml_params[0]
    v2hat = ml_params[1]
    if np.isnan(v1hat):
        raise Exception("v1hat is NaN")
    if np.isnan(v2hat):
        raise Exception("v2hat is NaN")
    
    # min xi
    # minxi=0
    if v2hat < minxi:
        warnings.warn(f"\n***v2hat={v2hat}=> execution halted because maxlik shape parameter <{minxi}***\n")
        raise Exception(f"v2hat={v2hat} < minxi={minxi}")
    
    # max xi
    if v2hat > maxxi:
        warnings.warn(f"\n***v2hat={v2hat}=> execution halted because maxlik shape parameter >{maxxi}***\n")
        raise Exception(f"v2hat={v2hat} > maxxi={maxxi}")
    
    # This max value is ad-hoc
    # If it's lowered to 1, then the ppm results for xi=0.6 go wrong, which I understand.
    # If it's increased to 100, then in about 1 in a billion cases, for nx=25,
    # the xi-hat value is very large and the code crashes because lddi can't be calculated.
    # I suspect there is more to understand about that latter part, but for now
    # this is a compromise.


def gpd_k1_means(means, ml_params, kloc=0):
    """Analytical Expressions for Predictive Means
    RHP mean based on the expectation of DMGS equation 2.1"""
    if means:
        # intro
        sigma = ml_params[0]
        xi = ml_params[1]
        
        # set up derivative arrays
        meand1 = np.zeros((2, 1))
        meand2 = np.zeros((2, 2, 1))
        
        # mle
        onemxi = 1 - xi
        onemxisq = onemxi * onemxi
        onemxicu = onemxi * onemxi * onemxi
        ml_mean = kloc + sigma / onemxi
        
        # calculate first derivative array for bayesian xi!=0 cases
        meand1[0, 0] = 1 / onemxi
        meand1[1, 0] = sigma / onemxisq
        
        # calculate second derivative array (only has 1 non-zero term!)
        meand2[0, 0, 0] = 0
        meand2[0, 1, 0] = 1 / onemxisq
        meand2[1, 1, 0] = -2 * sigma / onemxicu
        
        rh_flat_mean = np.inf
        
    else:
        ml_mean = "means not selected"
        rh_flat_mean = "means not selected"
    
    # return
    return {'ml_mean': ml_mean, 'rh_flat_mean': rh_flat_mean}


def dgpdsub(x, y, ics, kloc=0, minxi=None, maxxi=None):
    """Densities for 5 predictions """
    
    ics = gpd_k1_setics(x, ics)
    opt = optimize.minimize(lambda params: -gpd_k1_loglik(params, x, kloc), 
                          ics, method='BFGS')
    v1hat = opt.x[0]
    v2hat = min(maxxi, max(minxi, opt.x[1]))  # just reset in this case
    # v2hat = opt.x[1]
    ml_params = np.array([v1hat, v2hat])
    
    y = cp_utils.fixgpdrange(y, kloc, v1hat, v2hat)
    
    # mle
    ml_pdf = stats.genpareto.pdf(y, c=v2hat, loc=kloc, scale=v1hat)
    ml_cdf = stats.genpareto.cdf(y, c=v2hat, loc=kloc, scale=v1hat)
    
    # return
    return {
        'ml_params': ml_params,
        'ml_pdf': ml_pdf,
        'ml_cdf': ml_cdf
    }