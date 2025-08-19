import numpy as np
from scipy import stats
from scipy.stats import lognorm


def lnorm_fd(x, v1, v2): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,i] = -np.sqrt(2)*(2*v1 - 2*np.log(x))*np.exp(-(-v1 + np.log(x))**2/(2*v2**2))/(4*np.sqrt(np.pi)*v2**3*x) 
		result[1,i] = -np.sqrt(2)*np.exp(-(-v1 + np.log(x))**2/(2*v2**2))/(2*np.sqrt(np.pi)*v2**2*x) + np.sqrt(2)*(-v1 + np.log(x))**2*np.exp(-(-v1 + np.log(x))**2/(2*v2**2))/(2*np.sqrt(np.pi)*v2**4*x) 
	if len(x_all) == 1:
		result = result[:,0]
	return result 

def lnorm_fdd(x, v1, v2): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim,dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,0,i] = -np.sqrt(2)*(1 - (v1 - np.log(x))**2/v2**2)*np.exp(-(v1 - np.log(x))**2/(2*v2**2))/(2*np.sqrt(np.pi)*v2**3*x)
		result[0,1,i] = np.sqrt(2)*(3 - (v1 - np.log(x))**2/v2**2)*(v1 - np.log(x))*np.exp(-(v1 - np.log(x))**2/(2*v2**2))/(2*np.sqrt(np.pi)*v2**4*x)
		result[1,0,i] = np.sqrt(2)*(3 - (v1 - np.log(x))**2/v2**2)*(v1 - np.log(x))*np.exp(-(v1 - np.log(x))**2/(2*v2**2))/(2*np.sqrt(np.pi)*v2**4*x)
		result[1,1,i] = np.sqrt(2)*(1 - (3 - (v1 - np.log(x))**2/v2**2)*(v1 - np.log(x))**2/(2*v2**2) - (v1 - np.log(x))**2/v2**2)*np.exp(-(v1 - np.log(x))**2/(2*v2**2))/(np.sqrt(np.pi)*v2**3*x)
	if len(x_all) == 1:
		result = result[:,:,0]
	return result



def lnorm_pd(x, v1, v2):    
    e2 = np.log(x) - v1
    e4 = stats.norm.pdf(e2/v2, 0, 1)
    return np.array([-(e4/v2), -(e4 * e2/(v2**2))])


def lnorm_pdd(x, v1, v2):
    e2 = np.log(x) - v1
    e3 = v2**2
    e5 = stats.norm.pdf(e2/v2, 0, 1)
    e7 = e2**2/e3
    e8 = -((e7 - 1) * e5/e3)
    e9 = v2**3
    return np.array([[-(e5 * e2/e9), e8], [e8, -((e7 - 2) * e5 * e2/e9)]])


def lnorm_logfdd(x, v1, v2): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim,dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,0,i] = -1/v2**2
		result[0,1,i] = 2*(v1 - np.log(x))/v2**3
		result[1,0,i] = 2*(v1 - np.log(x))/v2**3
		result[1,1,i] = (1 - 3*(v1 - np.log(x))**2/v2**2)/v2**2
	if len(x_all) == 1:
		result = result[:,:,0]
	return result 

def lnorm_logfddd(x, v1, v2): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim, dim, dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,0,0,i] = 0 
		result[0,0,1,i] = 2/v2**3 
		result[0,1,0,i] = 2/v2**3 
		result[0,1,1,i] = -6*(v1 - np.log(x))/v2**4 
		result[1,0,0,i] = 2/v2**3 
		result[1,0,1,i] = -6*(v1 - np.log(x))/v2**4 
		result[1,1,0,i] = -6*(v1 - np.log(x))/v2**4 
		result[1,1,1,i] = 2*(-1 + 6*(v1 - np.log(x))**2/v2**2)/v2**3 
	if len(x_all) == 1:
		result = result[:,:,:,0]
	return result 




def lnorm_f1fa(x, v1, v2):
    f1 = lnorm_fd(x, v1, v2)
    return f1

def lnorm_f2fa(x, v1, v2):
    nx = len(x)
    f2 = lnorm_fdd(x, v1, v2)
    return f2

def lnorm_p1fa(x, v1, v2):
    p1 = lnorm_pd(x, v1, v2)
    return p1

def lnorm_p2fa(x, v1, v2):
    nx = len(x)
    p2 = lnorm_pdd(x, v1, v2)
    return p2

def lnorm_mu1fa(alpha, v1, v2):
    x = lognorm.ppf(1-alpha, s=v2, scale=np.exp(v1))
    mu1 = -lnorm_pd(x, v1, v2)
    return mu1

def lnorm_mu2fa(alpha, v1, v2):
    x = lognorm.ppf(1-alpha, s=v2, scale=np.exp(v1))
    nx = len(x)
    mu2 = -lnorm_pdd(x, v1, v2)
    return mu2

def lnorm_ldda(x, v1, v2):
    nx = len(x)
    temp1 = lnorm_logfdd(x, v1, v2)
    ldd = np.sum(temp1, axis=-1) / nx
    return ldd

def lnorm_lddda(x, v1, v2):
    nx = len(x)
    temp1 = lnorm_logfddd(x, v1, v2)
    lddd = np.sum(temp1, axis=-1) / nx
    return lddd
