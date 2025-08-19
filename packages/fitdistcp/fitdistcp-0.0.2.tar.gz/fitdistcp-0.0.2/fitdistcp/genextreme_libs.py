import numpy as np
import scipy.optimize as optimize
import scipy.special as special
from scipy.stats import genextreme

from . import utils as cp_utils
from . import genextreme_derivs as cp_gev_c


def rgev_minmax(nx, mu, sigma, xi, minxi=-1, maxxi=1):
    """rgev but with maxlik xi guaranteed within bounds"""
    xihat = -9999
    while (xihat < minxi) or (xihat > maxxi):
        xx = genextreme.rvs(c=-xi, loc=mu, scale=sigma, size=nx)
        ics = gev_setics(xx, np.array([0, 0, 0]))
        opt1 = optimize.minimize(lambda params: -gev_loglik(params, xx), 
                               ics, method='BFGS')
        xihat = opt1.x[2]
    return xx


def gev_waic(waicscores, x, v1hat, v2hat, v3hat, lddi, lddd, lambdad):
    #Returns Dictionary containing waic1 and waic2
    if waicscores:
        f1f = cp_gev_c.gev_f1fa(x, v1hat, v2hat, v3hat)
        f2f = cp_gev_c.gev_f2fa(x, v1hat, v2hat, v3hat)
        
        fhatx = genextreme.pdf(x, c=-v3hat, loc=v1hat, scale=v2hat)
        waic = cp_utils.make_waic(x, fhatx, lddi, lddd, f1f, lambdad, f2f, dim=3)
        waic1 = waic['waic1']
        waic2 = waic['waic2']
    else:
        waic1 = "waicscores not selected"
        waic2 = "waicscores not selected"
    return {'waic1': waic1, 'waic2': waic2}


def gev_logf(params, x):
    #Returns   (float) Log likelihood value
    mu = params[0]
    sc = np.maximum(params[1], np.finfo(float).eps)
    sh = params[2]
    
    logf = np.sum(genextreme.logpdf(x, c=-sh, loc=mu, scale=sc)) - np.log(sc)
    return logf


def gev_setics(x, ics):
    # set initial conditions
    if (ics[0] == 0) and (ics[1] == 0) and (ics[2] == 0):
        ics[0] = np.mean(x)
        ics[1] = np.std(x, ddof=1)
        ics[2] = 0
    return ics


def gev_pwm_params(x):
    """
    Parameters
        x : numpy.ndarray
    Returns 
        array: PWM parameter estimates
    """
    raise Exception('The PWM method is not yet implemented in fitdistcp; please use Maximum Likelihood.')
    # Note: fExtremes::gevFit with PWM method is not directly available in Python
    # This would need a custom PWM implementation or alternative library
    # Simple method of moments approximation as placeholder
    pw_params = np.zeros(3)
    pw_params[0] = np.mean(x)           # mu
    pw_params[1] = np.std(x, ddof=1)    # sigma
    pw_params[2] = 0                    # xi
    
    return pw_params


def gev_loglik(vv, x):
    # return log-likelihood gev
    loglik = np.sum(genextreme.logpdf(x, c=-vv[2], loc=vv[0], 
                                     scale=np.maximum(vv[1], np.finfo(float).eps)))
    return loglik


def gev_means(means, ml_params, lddi, lddd, lambdad_rh_flat, lambdad_custom, nx, dim=3):
    """
    Analytical Expressions for Predictive Means
    RHP mean based on the expectation of DMGS equation 2.1
    Returns Dictionary containing ml_mean, rh_flat_mean, custom_mean
    """
    if means:
        # intro
        eulerconstant = 0.57721566490153286060651209008240243104215933593992
        mu = ml_params[0]
        sigma = ml_params[1]
        xi = ml_params[2]
        
        # set up derivative arrays
        meand1 = np.zeros((3, 1))
        meand2 = np.zeros((3, 3, 1))  # but all zero for gumbel
        
        if ml_params[2] == 0:
            # xi=0 case
            
            # mle
            ml_mean = mu + sigma * eulerconstant
            # calculate first derivative array for bayesian xi=0 cases
            meand1[0, 0] = 1
            meand1[1, 0] = eulerconstant
            # meand2 is all zero as initialized
        else:
            # non-gumbel case
            g0 = special.gamma(1 - xi)
            g1 = g0 * special.digamma(1 - xi)
            g2 = (special.polygamma(1, 1 - xi) * g0 * g0 + g1 * g1) / g0
            
            # mle
            ml_mean = mu + sigma * (g0 - 1) / xi
            # calculate first derivative array for bayesian xi!=0 cases
            meand1[0, 0] = 1
            meand1[1, 0] = (g0 - 1) / xi
            meand1[2, 0] = (1 - g0 - xi * g1) * sigma / (xi * xi)
            # calculate second derivative array (only has 1 non-zero term!)
            meand2[1, 2, 0] = (1 - g0 - xi * g1) / (xi * xi)
            meand2[2, 1, 0] = meand2[1, 2, 0]
            meand2[2, 2, 0] = sigma * (-2 + 2 * g0 + 2 * xi * g1 + xi * xi * g2) / (xi * xi * xi)
        
        # I've realized now that when we integrate over xi, the mean is Inf
        rh_flat_mean = np.inf
        custom_mean = np.inf
    else:
        ml_mean = "means not selected"
        rh_flat_mean = "means not selected"
        custom_mean = "means not selected"
    
    # return
    return {
        'ml_mean': ml_mean,
        'rh_flat_mean': rh_flat_mean,
        'custom_mean': custom_mean
    }


def dgevsub(x, y, ics):
    """
    Densities for 5 predictions
    Returns Dictionary containing ml_params, ml_pdf, ml_cdf
    """
    
    ics = gev_setics(x, ics)
    opt = optimize.minimize(lambda params: -gev_loglik(params, x), 
                           ics, method='BFGS')
    v1hat = opt.x[0]
    v2hat = opt.x[1]
    v3hat = opt.x[2]
    ml_params = np.array([v1hat, v2hat, v3hat])
    
    # mle
    ml_pdf = genextreme.pdf(y, c=-v3hat, loc=v1hat, scale=v2hat)
    ml_cdf = genextreme.cdf(y, c=-v3hat, loc=v1hat, scale=v2hat)
    
    # return
    return {
        'ml_params': ml_params,
        'ml_pdf': ml_pdf,
        'ml_cdf': ml_cdf
    }