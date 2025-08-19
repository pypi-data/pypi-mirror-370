import numpy as np


def bayesian_dq_4terms_v1(lddi, lddd, mu1, pidopi1, pidopi2, mu2, dim):
    """
    Evaluate DMGS equation 3.3
    
    Parameters:
    lddi: inverse of second derivative of observed log-likelihood
    lddd: third derivative of observed log-likelihood  
    mu1: DMGS mu1 vector
    pidopi1: first part of the prior term
    pidopi2: second part of the prior term
    mu2: DMGS mu2 matrix
    dim: number of parameters
    
    Returns:
    Vector
    """
    nalpha = mu1.shape[1]  # length(mu1[1,])
    beps1 = np.zeros(nalpha)  # rep(0, nalpha)
    beps2 = np.zeros(nalpha)
    beps3 = np.zeros(nalpha)
    beps4 = np.zeros(nalpha)
    
    # beps1
    for t in range(dim):  # 1:dim becomes 0:dim
        for j in range(dim):
            for r in range(dim):
                for s in range(dim):
                    beps1 = beps1 + 0.5 * lddi[s, t] * lddi[j, r] * lddd[j, r, s] * mu1[t, :]
    
    # beps2
    for t in range(dim):
        for s in range(dim):
            beps2 = beps2 - lddi[s, t] * pidopi1[s] * mu1[t, :]  # this has to be negative because ldd is the opposite sign to c
    
    # beps3
    for t in range(dim):
        for s in range(dim):
            beps3 = beps3 - lddi[s, t] * pidopi2[s] * mu1[t, :]  # this has to be negative because ldd is the opposite sign to c
    
    # beps4
    for j in range(dim):
        for r in range(dim):
            beps4 = beps4 - 0.5 * lddi[j, r] * mu2[j, r, :]  # this has to be negative because ldd is the opposite sign to c
    
    beps = beps1 + beps2 + beps3 + beps4
    return beps


def dmgs(lddi, lddd, mu1, pidopi, mu2, dim):
    # the inputs must have the correct number of dimensions, even if the last one is empty:
    if isinstance(pidopi, float):
        pidopi = np.asarray([pidopi])
    if len(mu1.shape) == 1:     
        mu1 = np.expand_dims(mu1, axis=-1)
    if len(mu2.shape) == 2:
        mu2 = np.expand_dims(mu2, axis=-1)

    pidopi1 = 2*pidopi
    pidopi2 = -1*pidopi
    
    nalpha = mu1.shape[1]
    beps1 = np.zeros(nalpha)
    beps2 = np.zeros(nalpha)
    beps3 = np.zeros(nalpha)
    beps4 = np.zeros(nalpha)
    # beps1
    for t in range(dim):
        for j in range(dim):
            for r in range(dim):
                for s in range(dim):
                    beps1 = beps1+0.5 * lddi[s, t] * lddi[j, r] * lddd[j, r, s] * mu1[t, :]
    
    # beps2
    for t in range(dim):
        for s in range(dim):
            beps2 = beps2- lddi[s, t] * pidopi1[s] * mu1[t, :]  # this has to be negative because ldd is the opposite sign to c
    
    # beps3
    for t in range(dim):
        for s in range(dim):
            beps3 = beps3- lddi[s, t] * pidopi2[s] * mu1[t, :]  # this has to be negative because ldd is the opposite sign to c
    
    # beps4
    for j in range(dim):
        for r in range(dim):
            beps4 = beps4 - 0.5 * lddi[j, r] * mu2[j, r, :]  # this has to be negative because ldd is the opposite sign to c
    
    beps = beps1 + beps2 + beps3 + beps4
    return beps
