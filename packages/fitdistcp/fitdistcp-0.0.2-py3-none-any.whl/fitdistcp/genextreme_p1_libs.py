import numpy as np
import scipy.stats as stats
from scipy.optimize import minimize
from scipy.special import gamma, digamma, polygamma
import sys

from . import utils as cp_utils
from . import genextreme_p1_derivs as cp_gev_p1_c


def rgev_p1_minmax(nx, mu, sigma, xi, tt, minxi=-0.45, maxxi=0.45, centering=True):
    """rgev for gev_p1 but with maxlik xi within bounds"""
    xihat = -9999
    if centering:
        tt = tt - np.mean(tt)
    
    while (xihat < minxi) or (xihat > maxxi):  # 0.46 also works...0.47 doesn't
        xx = stats.genextreme.rvs(c=-xi, loc=mu, scale=sigma, size=nx)
        ics = gev_p1_setics(xx, tt, np.array([0, 0, 0, 0]))
        
        # Define objective function for minimization (negative log-likelihood)
        def neg_loglik(params):
            return -gev_p1_loglik(params, xx, tt)
        
        opt1 = minimize(neg_loglik, ics, method='BFGS')
        xihat = opt1.x[3]
    
    return xx


def gev_p1_waic(waicscores, x, t0, v1hat, v2hat, v3hat, v4hat, lddi, lddd, lambdad):
    """WAIC calculation """
    if waicscores:
        f1f = cp_gev_p1_c.gev_p1_f1fw(x, t0, v1hat, v2hat, v3hat, v4hat)
        f2f = cp_gev_p1_c.gev_p1_f2fw(x, t0, v1hat, v2hat, v3hat, v4hat)
        fhatx = dgev_p1(x, t0, ymn=v1hat, slope=v2hat, sigma=v3hat, xi=v4hat, log=False)
        waic = cp_utils.make_waic(x, fhatx, lddi, lddd, f1f, lambdad, f2f, dim=4)
        waic1 = waic['waic1']
        waic2 = waic['waic2']
    else:
        waic1 = "waicscores not selected"
        waic2 = "waicscores not selected"
    
    return {'waic1': waic1, 'waic2': waic2}


def gev_p1_predictordata(predictordata, x, t, t0, params):
    """Predicted Parameter and Generalized Residuals"""
    if predictordata:
        # calculate the probabilities of the data using the fitted model
        a = params[0]
        b = params[1]
        sc = params[2]
        sh = params[3]
        mu = a + b * t
        px = stats.genextreme.cdf(x, c=-sh, loc=mu, scale=sc)
        
        # calculate the quantiles for those probabilities at t0
        mu0 = a + b * t0
        qx = stats.genextreme.ppf(px, c=-sh, loc=mu0, scale=sc)
        predictedparameter = mu
        adjustedx = qx
    else:
        predictedparameter = "predictordata not selected"
        adjustedx = "predictordata not selected"
    
    return {'predictedparameter': predictedparameter, 'adjustedx': adjustedx}


def gev_p1_logf(params, x, t):
    """Logf for RUST    """
    a = params[0]
    b = params[1]
    sc = np.maximum(params[2], np.sqrt(sys.float_info.epsilon))
    sh = params[3]
    mu = a + b * t
    logf = np.sum(stats.genextreme.logpdf(x, c=-sh, loc=mu, scale=sc)) - np.log(sc)
    return logf


def gev_p1_setics(x, t, ics):
    """Set initial conditions"""
    nx = len(x)
    if (ics[0] == 0) and (ics[1] == 0) and (ics[2] == 0) and (ics[3] == 0):
        # Linear regression equivalent to R's lm(x~t)
        A = np.vstack([np.ones(len(t)), t]).T
        coeffs = np.linalg.lstsq(A, x, rcond=None)[0]
        ics[0] = coeffs[0]  # intercept
        ics[1] = coeffs[1]  # slope
        xhat = ics[0] + ics[1] * t
        ics[2] = np.sqrt(np.sum((x - xhat)**2) / nx)
        ics[3] = 0
    
    return ics


def gev_p1_loglik(vv, x, t):
    """Observed log-likelihood function  """
    n = len(x)
    mu = vv[0] + vv[1] * t  # so mean is a vector, just like x
    loglik = np.sum(stats.genextreme.logpdf(x, c=-vv[3], loc=mu, 
                                          scale=max(vv[2], sys.float_info.epsilon)))
    return loglik


def gev_p1_checkmle(ml_params, minxi=-1, maxxi=1):
    """Check MLE"""
    # currently not used, because instead I revert2ml
    v1hat = ml_params[0]
    v2hat = ml_params[1]
    v3hat = ml_params[2]
    v4hat = ml_params[3]
    
    if np.isnan(v1hat):
        raise ValueError("v1hat is NaN")
    if np.isnan(v2hat):
        raise ValueError("v2hat is NaN")
    if np.isnan(v3hat):
        raise ValueError("v3hat is NaN")
    if np.isnan(v4hat):
        raise ValueError("v4hat is NaN")
    
    if v4hat < minxi:
        raise ValueError(f"\n***v4hat={v4hat}=> execution halted because maxlik shape parameter <{minxi}***\n")
    if v4hat > maxxi:
        raise ValueError(f"\n***v4hat={v4hat}=> execution halted because maxlik shape parameter >{maxxi}***\n")


def qgev_p1(p, t0, ymn, slope, sigma, xi):
    """GEVD-with-p1: Quantile function """
    return stats.genextreme.ppf(p, c=-xi, loc=(ymn + slope * t0), scale=sigma)

def dgev_p1(x, t0, ymn, slope, sigma, xi, log=False):
    """GEVD-with-p1: Density function
    
    Args:
        x: data vector
        t0: time value
        ymn: mean parameter
        slope: slope parameter
        sigma: scale parameter
        xi: shape parameter
        log: whether to return log density (default False)
    
    Returns:
        Density values
    """
    mu = ymn + slope * t0
    if log:
        return stats.genextreme.logpdf(x, c=-xi, loc=mu, scale=sigma)
    else:
        return stats.genextreme.pdf(x, c=-xi, loc=mu, scale=sigma)


def pgev_p1(y, t0, ymn, slope, sigma, xi):
    """GEVD-with-p1: Distribution function """
    return stats.genextreme.cdf(y, c=-xi, loc=(ymn + slope * t0), scale=sigma)


def gev_p1_means(means, t0, ml_params, lddi, lddd, lambdad_rh_flat, nx, dim=4):
    """Analytical expressions for Predictive Means
    RHP mean based on the expectation of DMGS equation 2.1
    """

    if means:
        # intro
        eulerconstant = 0.57721566490153286060651209008240243104215933593992
        ymn = ml_params[0]
        slope = ml_params[1]
        sigma = ml_params[2]
        xi = ml_params[3]
        
        # set up derivative arrays
        meand1 = np.zeros((4, 1))
        meand2 = np.zeros((4, 4, 1))  # but all zero for gumbel
        
        if ml_params[3] == 0:
            # xi=0 case
            
            # mle
            ml_mean = ymn + slope * t0 + sigma * eulerconstant
            # calculate first derivative array for bayesian xi=0 cases
            meand1[0, 0] = 1
            meand1[1, 0] = t0
            meand1[2, 0] = eulerconstant
            meand1[3, 0] = 0
            # meand2 is all zero as initialized
            
        else:
            # non-gumbel case
            
            g0 = gamma(1 - xi)
            g1 = g0 * digamma(1 - xi)
            g2 = (polygamma(1, 1 - xi) * g0 * g0 + g1 * g1) / g0  # trigamma is polygamma(1, x)
            # mle
            ml_mean = ymn + slope * t0 + sigma * (g0 - 1) / xi
            # calculate first derivative array for bayesian xi!=0 cases
            meand1[0, 0] = 1
            meand1[1, 0] = t0
            meand1[2, 0] = (g0 - 1) / xi
            meand1[3, 0] = (1 - g0 - xi * g1) * sigma / (xi * xi)
            # calculate second derivative array (only has 1 non-zero term!)
            meand2[2, 3, 0] = (1 - g0 - xi * g1) / (xi * xi)
            meand2[3, 2, 0] = meand2[2, 3, 0]
            meand2[3, 3, 0] = sigma * (-2 + 2 * g0 + 2 * xi * g1 + xi * xi * g2) / (xi * xi * xi)
        
        # I've realized now that when I integrate over xi, the mean in Inf
        rh_flat_mean = np.inf
        
    else:
        ml_mean = "means not selected"
        rh_flat_mean = "means not selected"
    
    # return
    return {'ml_mean': ml_mean, 'rh_flat_mean': rh_flat_mean}


def dgev_p1sub(x, t, y, t0, ics, minxi, maxxi, extramodels=False):
    """Densities for 5 predictions """
    nx = len(x)
    
    ics = gev_p1_setics(x, t, ics)
    
    # Define objective function for minimization (negative log-likelihood)
    def neg_loglik(params):
        return -gev_p1_loglik(params, x, t)
    
    opt = minimize(neg_loglik, ics, method='BFGS')
    v1hat = opt.x[0]
    v2hat = opt.x[1]
    v3hat = opt.x[2]
    v4hat = min(maxxi, max(minxi, opt.x[3]))
    ml_params = np.array([v1hat, v2hat, v3hat, v4hat])
    
    # now that I've dropped dmgs, not sure I need this anymore
    # muhat0 = v1hat + v2hat * t0
    # y = fixgevrange(y, muhat0, v3hat, v4hat)
    
    # mle
    ml_pdf = dgev_p1(y, t0, ymn=v1hat, slope=v2hat, sigma=v3hat, xi=v4hat)
    ml_cdf = pgev_p1(y, t0, ymn=v1hat, slope=v2hat, sigma=v3hat, xi=v4hat)
    
    # return
    return {
        'ml_params': ml_params,
        'ml_pdf': ml_pdf,
        'ml_cdf': ml_cdf
    }

