import numpy as np
from scipy import stats, special, optimize
from sklearn.linear_model import LinearRegression
import warnings

from . import genextreme_p12_derivs
from . import utils as cp_utils


def rgev_p12_minmax(nx, mu, sigma, xi, t1, t2, minxi=-0.45, maxxi=0.45, centering=True):
    """
    rgev for gev_p12 but with maxlik xi within bounds
    
    Parameters:
    nx : int
    mu : float
    sigma : float  
    xi : float
    t1 : array-like
    t2 : array-like
    minxi : float, default -0.45
    maxxi : float, default 0.45
    centering : bool, default True
    
    Returns:
    numpy.ndarray : Vector
    """
    xihat = -9999
    
    if centering:
        t1 = t1 - np.mean(t1)
        t2 = t2 - np.mean(t2)
    
    while (xihat < minxi) or (xihat > maxxi):  # 0.46 also works...0.47 doesn't
        # Generate random GEV values using scipy (note: xi -> -xi conversion for scipy)
        xx = stats.genextreme.rvs(c=-xi, loc=mu, scale=sigma, size=nx)
        
        ics = gev_p12_setics(xx, t1, t2, np.array([0, 0, 0, 0, 0]))
        
        # Use scipy.optimize.minimize instead of optim (maximizing = minimizing negative)
        def neg_loglik(params):
            return -gev_p12_loglik(params, xx, t1, t2)
        
        opt1 = optimize.minimize(neg_loglik, ics, method='BFGS')
        xihat = opt1.x[4]
    
    return xx

def gev_p12_waic(waicscores, x, t1, t2, v1hat, v2hat, v3hat, v4hat, v5hat,
                 lddi, lddd, lambdad):
    """
    Waic
    
    Parameters:
    waicscores : bool
    x : array-like
    t1 : array-like
    t2 : array-like
    v1hat : float
    v2hat : float
    v3hat : float
    v4hat : float
    v5hat : float
    lddi : array-like
    lddd : array-like
    lambdad : array-like
    
    Returns:
    dict : Dictionary with waic1 and waic2
    """
    if waicscores:
        f1f = genextreme_p12_derivs.gev_p12_f1fw(x, t1, t2, v1hat, v2hat, v3hat, v4hat, v5hat)
        f2f = genextreme_p12_derivs.gev_p12_f2fw(x, t1, t2, v1hat, v2hat, v3hat, v4hat, v5hat)
        fhatx = dgev_p12(x, t1, t2, ymn=v1hat, slope=v2hat, sigma1=v3hat, sigma2=v4hat, xi=v5hat, log=False)
        waic = cp_utils.make_waic(x, fhatx, lddi, lddd, f1f, lambdad, f2f, dim=5)
        waic1 = waic['waic1']
        waic2 = waic['waic2']
    else:
        waic1 = "waicscores not selected"
        waic2 = "waicscores not selected"
    
    return {'waic1': waic1, 'waic2': waic2}

def gev_p12_predictordata(predictordata, x, t1, t2, t01, t02, params):
    """
    Predicted Parameter and Generalized Residuals
    
    Parameters:
    predictordata : bool
    x : array-like
    t1 : array-like
    t2 : array-like
    t01 : float or array-like
    t02 : float or array-like
    params : array-like
    
    Returns:
    dict : Dictionary with predictedparameter and adjustedx
    """
    if predictordata:
        #
        # calculate the probabilities of the data using the fitted model
        #
        # t is always a matrix
        # t0 is always a vector
        a = params[0]
        b = params[1]
        sc1 = params[2]
        sc2 = params[3]
        sh = params[4]
        
        mu = a + b * t1
        sigma = np.exp(sc1 + sc2 * t2)
        
        # Calculate CDF using scipy genextreme (note: xi -> -xi conversion)
        px = stats.genextreme.cdf(x, c=-sh, loc=mu, scale=sigma)
        
        #
        # calculate the quantiles for those probabilities at t01,t02
        #
        mu0 = a + b * t01
        sigma0 = np.exp(sc1 + sc2 * t02)
        
        # Calculate quantiles using scipy genextreme (note: xi -> -xi conversion)
        qx = stats.genextreme.ppf(px, c=-sh, loc=mu0, scale=sigma0)
        
        predictedparameter = mu
        adjustedx = qx
    else:
        predictedparameter = "predictordata not selected"
        adjustedx = "predictordata not selected"
    
    return {'predictedparameter': predictedparameter, 'adjustedx': adjustedx}

def gev_p12_logf(params, x, t1, t2):
    """
    Logf for RUST
    
    Parameters:
    params : array-like
    x : array-like
    t1 : array-like
    t2 : array-like
    
    Returns:
    float : Log likelihood value
    """
    a = params[0]
    b = params[1]
    sc1 = params[2]
    sc2 = params[3]
    sh = params[4]
    
    # if(is.vector(t)){
    #     mu=a+b*t1
    #     sigma=exp(sc1+sc2*t2)
    # } else {
    #     mu=a+b*t1
    #     sigma=exp(sc1+sc2*t2)
    # }
    
    mu = a + b * t1
    sigma = np.exp(sc1 + sc2 * t2)
    
    # Calculate log PDF using scipy genextreme (note: xi -> -xi conversion)
    logf = np.sum(stats.genextreme.logpdf(x, c=-sh, loc=mu, scale=sigma))
    
    return logf

def gev_p12_setics(x, t1, t2, ics):
    """
    Set initial conditions
    
    Parameters:
    x : array-like
    t1 : array-like
    t2 : array-like
    ics : array-like
    
    Returns:
    numpy.ndarray : Vector
    """
    # t is always a matrix
    nx = len(x)
    
    if (ics[0] == 0) and (ics[1] == 0) and (ics[2] == 0) and (ics[3] == 0) and (ics[4] == 0):
        # Use sklearn LinearRegression instead of R's lm
        reg = LinearRegression()
        t1_reshaped = np.array(t1).reshape(-1, 1)
        reg.fit(t1_reshaped, x)
        
        ics[0] = reg.intercept_
        ics[1] = reg.coef_[0]
        
        xhat = ics[0] + ics[1] * t1
        ics[2] = 0
        ics[3] = 0  # zero because it's inside an exponential
        ics[4] = 0
    
    return ics

def gev_p12_loglik(vv, x, t1, t2):
    """
    observed log-likelihood function
    
    Parameters:
    vv : array-like
    x : array-like
    t1 : array-like
    t2 : array-like
    
    Returns:
    float : Log likelihood value
    """
    # t is always a matrix
    n = len(x)
    
    mu = vv[0] + vv[1] * t1  # so mean is a vector, just like x
    sigma = np.exp(vv[2] + vv[3] * t2)
    
    # Calculate log PDF using scipy genextreme (note: xi -> -xi conversion)
    loglik = np.sum(stats.genextreme.logpdf(x, c=-vv[4], loc=mu, scale=sigma))
    
    return loglik

def gev_p12_checkmle(ml_params, minxi=-1, maxxi=1):
    """
    Check MLE
    
    Parameters:
    ml_params : array-like
    minxi : float, default -1
    maxxi : float, default 1
    
    Returns:
    None : No return value (just a message to the screen).
    """
    # currently not used, because instead I revert2ml
    v1hat = ml_params[0]
    v2hat = ml_params[1]
    v3hat = ml_params[2]
    v4hat = ml_params[3]
    v5hat = ml_params[4]
    
    if np.isnan(v1hat):
        raise RuntimeError()
    if np.isnan(v2hat):
        raise RuntimeError()
    if np.isnan(v3hat):
        raise RuntimeError()
    if np.isnan(v4hat):
        raise RuntimeError()
    if np.isnan(v5hat):
        raise RuntimeError()
        
    if v5hat < minxi:
        warnings.warn(f"\n***v5hat={v5hat}=> execution halted because maxlik shape parameter <{minxi}***")
        raise RuntimeError()
    if v5hat > maxxi:
        warnings.warn(f"\n***v5hat={v5hat}=> execution halted because maxlik shape parameter >{maxxi}***")
        raise RuntimeError()

def qgev_p12(p, t1, t2, ymn, slope, sigma1, sigma2, xi):
    """
    GEVD-with-p1: Quantile function
    
    Parameters:
    p : array-like
    t1 : array-like
    t2 : array-like
    ymn : float
    slope : float
    sigma1 : float
    sigma2 : float
    xi : float
    
    Returns:
    numpy.ndarray : Vector
    """
    # t is sometimes a vector, sometimes a matrix
    
    # if(is.vector(t)){
    #     mu=ymn+slope*t1
    #     sigma=exp(sigma1+sigma2*t2)
    # } else {
    #     mu=ymn+slope*t1
    #     sigma=exp(sigma1+sigma2*t2)
    # }
    
    mu = ymn + slope * t1
    sigma = np.exp(sigma1 + sigma2 * t2)
    
    # Calculate quantiles using scipy genextreme (note: xi -> -xi conversion)
    return stats.genextreme.ppf(p, c=-xi, loc=mu, scale=sigma)

def dgev_p12(x, t1, t2, ymn, slope, sigma1, sigma2, xi, log=False):
    """
    GEVD-with-p1: Density function
    
    Parameters:
    x : array-like
    t1 : array-like
    t2 : array-like
    ymn : float
    slope : float
    sigma1 : float
    sigma2 : float
    xi : float
    log : bool, default False
    
    Returns:
    numpy.ndarray : Vector
    """
    # t is sometimes a vector, sometimes a matrix
    
    # if(is.vector(t)){
    #     mu=ymn+slope*t1
    #     sigma=exp(sigma1+sigma2*t2)
    # } else {
    #     mu=ymn+slope*t1
    #     sigma=exp(sigma1+sigma2*t2)
    # }
    
    mu = ymn + slope * t1
    sigma = np.exp(sigma1 + sigma2 * t2)
    
    # Calculate PDF using scipy genextreme (note: xi -> -xi conversion)
    if log:
        return stats.genextreme.logpdf(x, c=-xi, loc=mu, scale=sigma)
    else:
        return stats.genextreme.pdf(x, c=-xi, loc=mu, scale=sigma)

def pgev_p12(y, t1, t2, ymn, slope, sigma1, sigma2, xi):
    """
    GEVD-with-p1: Distribution function
    
    Parameters:
    y : array-like
    t1 : array-like
    t2 : array-like
    ymn : float
    slope : float
    sigma1 : float
    sigma2 : float
    xi : float
    
    Returns:
    numpy.ndarray : Vector
    """
    # t is sometimes a vector, sometimes a matrix
    
    # if(is.vector(t)){
    #     mu=ymn+slope*t1
    #     sigma=exp(sigma1+sigma2*t2)
    # } else {
    #     mu=ymn+slope*t1
    #     sigma=exp(sigma1+sigma2*t2)
    # }
    
    mu = ymn + slope * t1
    sigma = np.exp(sigma1 + sigma2 * t2)
    
    # Calculate CDF using scipy genextreme (note: xi -> -xi conversion)
    return stats.genextreme.cdf(y, c=-xi, loc=mu, scale=sigma)

def gev_p12_means(means, t01, t02, ml_params, nx):
    """
    Analytical expressions for Predictive Means
    RHP mean based on the expectation of DMGS equation 2.1
    
    Parameters:
    means : bool
    t01 : float or array-like
    t02 : float or array-like
    ml_params : array-like
    nx : int
    
    Returns:
    dict : Dictionary with ml_mean, crhp_mle_mean, and pu_mean
    """
    if means:
        # intro
        eulerconstant = 0.57721566490153286060651209008240243104215933593992
        ymn = ml_params[0]
        slope = ml_params[1]
        sigma1 = ml_params[2]
        sigma2 = ml_params[3]
        sigma = np.exp(sigma1 + sigma2 * t02)
        xi = ml_params[4]
        
        if ml_params[4] == 0:
            # xi=0 case
            ml_mean = ymn + slope * t01 + sigma * eulerconstant
        else:
            # xi!=0 case
            g0 = special.gamma(1 - xi)
            g1 = g0 * special.digamma(1 - xi)
            g2 = (special.polygamma(1, 1 - xi) * g0 * g0 + g1 * g1) / g0
            ml_mean = ymn + slope * t01 + sigma * (g0 - 1) / xi
        
        # return
        crhp_mle_mean = "not yet implemented"
        pu_mean = np.inf
    else:
        pu_mean = "means not selected"
        ml_mean = "means not selected"
        crhp_mle_mean = "means not selected"
    
    return {'ml_mean': ml_mean, 'crhp_mle_mean': crhp_mle_mean, 'pu_mean': pu_mean}

def dgev_p12sub(x, t1, t2, y, t01, t02, ics, minxi, maxxi, debug, extramodels=False):
    """
    Densities for 5 predictions
    
    Parameters:
    x : array-like
    t1 : array-like
    t2 : array-like
    y : array-like
    t01 : float or array-like
    t02 : float or array-like
    ics : array-like
    minxi : float
    maxxi : float
    debug : bool
    extramodels : bool, default False
    
    Returns:
    dict : Dictionary with ml_params, ml_pdf, and ml_cdf
    """
    nx = len(x)
    
    ics = gev_p12_setics(x, t1, t2, ics)
    
    # Use scipy.optimize.minimize instead of optim (maximizing = minimizing negative)
    def neg_loglik(params):
        return -gev_p12_loglik(params, x, t1, t2)
    
    opt = optimize.minimize(neg_loglik, ics, method='BFGS')
    
    v1hat = opt.x[0]
    v2hat = opt.x[1]
    v3hat = opt.x[2]
    v4hat = opt.x[3]
    v5hat = np.minimum(maxxi, np.maximum(minxi, opt.x[4]))
    ml_params = np.array([v1hat, v2hat, v3hat, v4hat, v5hat])
    
    # now that I've dropped dmgs d and p, I don't think I need this any more
    # muhat0=v1hat+v2hat*t01
    # sghat0=exp(v3hat+v4hat*t02)
    # y=fixgevrange(y,muhat0,sghat0,v5hat)
    
    # mle
    ml_pdf = dgev_p12(y, t01, t02, ymn=v1hat, slope=v2hat, sigma1=v3hat, sigma2=v4hat, xi=v5hat)
    ml_cdf = pgev_p12(y, t01, t02, ymn=v1hat, slope=v2hat, sigma1=v3hat, sigma2=v4hat, xi=v5hat)
    
    # return
    return {'ml_params': ml_params, 'ml_pdf': ml_pdf, 'ml_cdf': ml_cdf}

