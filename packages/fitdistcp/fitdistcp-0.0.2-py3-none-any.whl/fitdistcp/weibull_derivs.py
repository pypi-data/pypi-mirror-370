import numpy as np
from scipy.stats import weibull_min


def weibull_fd(x, v1, v2): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,i] = -v1*(x/v2)**v1*(x/v2)**(v1 - 1)*np.exp(-(x/v2)**v1)*np.log(x/v2)/v2 + v1*(x/v2)**(v1 - 1)*np.exp(-(x/v2)**v1)*np.log(x/v2)/v2 + (x/v2)**(v1 - 1)*np.exp(-(x/v2)**v1)/v2 
		result[1,i] = v1**2*(x/v2)**v1*(x/v2)**(v1 - 1)*np.exp(-(x/v2)**v1)/v2**2 - v1*(x/v2)**(v1 - 1)*(v1 - 1)*np.exp(-(x/v2)**v1)/v2**2 - v1*(x/v2)**(v1 - 1)*np.exp(-(x/v2)**v1)/v2**2 
	if len(x_all) == 1:
		result = result[:,0]
	return result 

def weibull_fdd(x, v1, v2): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim,dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,0,i] = (x/v2)**(v1 - 1)*(v1*(x/v2)**v1*((x/v2)**v1 - 1)*np.log(x/v2) - 2*v1*(x/v2)**v1*np.log(x/v2) + v1*np.log(x/v2) - 2*(x/v2)**v1 + 2)*np.exp(-(x/v2)**v1)*np.log(x/v2)/v2
		result[0,1,i] = (x/v2)**(v1 - 1)*(-v1**2*(x/v2)**(2*v1)*np.log(x/v2) + 2*v1**2*(x/v2)**v1*np.log(x/v2) + v1*(x/v2)**v1*(v1 - 1)*np.log(x/v2) + v1*(x/v2)**v1*np.log(x/v2) + 2*v1*(x/v2)**v1 - v1*(v1 - 1)*np.log(x/v2) - v1*np.log(x/v2) - 2*v1)*np.exp(-(x/v2)**v1)/v2**2
		result[1,0,i] = (x/v2)**(v1 - 1)*(-v1**2*(x/v2)**(2*v1)*np.log(x/v2) + 2*v1**2*(x/v2)**v1*np.log(x/v2) + v1*(x/v2)**v1*(v1 - 1)*np.log(x/v2) + v1*(x/v2)**v1*np.log(x/v2) + 2*v1*(x/v2)**v1 - v1*(v1 - 1)*np.log(x/v2) - v1*np.log(x/v2) - 2*v1)*np.exp(-(x/v2)**v1)/v2**2
		result[1,1,i] = v1*(x/v2)**(v1 - 1)*(-2*v1*(x/v2)**v1*(v1 - 1) - v1*(x/v2)**v1*(-v1*(x/v2)**v1 + v1 + 1) - 2*v1*(x/v2)**v1 + v1*(v1 - 1) + 2*v1)*np.exp(-(x/v2)**v1)/v2**3
	if len(x_all) == 1:
		result = result[:,:,0]
	return result 

def weibull_pd(x, v1, v2): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,i] = (x/v2)**v1*np.exp(-(x/v2)**v1)*np.log(x/v2) 
		result[1,i] = -v1*(x/v2)**v1*np.exp(-(x/v2)**v1)/v2 
	if len(x_all) == 1:
		result = result[:,0]
	return result 

def weibull_pdd(x, v1, v2): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim,dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,0,i] = (x/v2)**v1*(1 - (x/v2)**v1)*np.exp(-(x/v2)**v1)*np.log(x/v2)**2
		result[0,1,i] = (x/v2)**v1*(v1*(x/v2)**v1*np.log(x/v2) - v1*np.log(x/v2) - 1)*np.exp(-(x/v2)**v1)/v2
		result[1,0,i] = (x/v2)**v1*(v1*(x/v2)**v1*np.log(x/v2) - v1*np.log(x/v2) - 1)*np.exp(-(x/v2)**v1)/v2
		result[1,1,i] = v1*(x/v2)**v1*(-v1*(x/v2)**v1 + v1 + 1)*np.exp(-(x/v2)**v1)/v2**2
	if len(x_all) == 1:
		result = result[:,:,0]
	return result 

def weibull_logfdd(x, v1, v2): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim,dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,0,i] = -((x/v2)**v1*np.log(x/v2)**2 + v1**(-2))
		result[0,1,i] = (v1*(x/v2)**v1*np.log(x/v2) + (x/v2)**v1 - 1)/v2
		result[1,0,i] = (v1*(x/v2)**v1*np.log(x/v2) + (x/v2)**v1 - 1)/v2
		result[1,1,i] = (-v1**2*(x/v2)**v1 - v1*(x/v2)**v1 + v1)/v2**2
	if len(x_all) == 1:
		result = result[:,:,0]
	return result 

def weibull_logfddd(x, v1, v2): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim, dim, dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,0,0,i] = -(x/v2)**v1*np.log(x/v2)**3 + 2/v1**3 
		result[0,0,1,i] = (x/v2)**v1*(v1*np.log(x/v2) + 2)*np.log(x/v2)/v2 
		result[0,1,0,i] = (x/v2)**v1*(v1*np.log(x/v2) + 2)*np.log(x/v2)/v2 
		result[0,1,1,i] = (-v1**2*(x/v2)**v1*np.log(x/v2) - v1*(x/v2)**v1*np.log(x/v2) - 2*v1*(x/v2)**v1 - (x/v2)**v1 + 1)/v2**2 
		result[1,0,0,i] = (x/v2)**v1*(v1*np.log(x/v2) + 2)*np.log(x/v2)/v2 
		result[1,0,1,i] = (-v1**2*(x/v2)**v1*np.log(x/v2) - v1*(x/v2)**v1*np.log(x/v2) - 2*v1*(x/v2)**v1 - (x/v2)**v1 + 1)/v2**2 
		result[1,1,0,i] = (-v1**2*(x/v2)**v1*np.log(x/v2) - v1*(x/v2)**v1*np.log(x/v2) - 2*v1*(x/v2)**v1 - (x/v2)**v1 + 1)/v2**2 
		result[1,1,1,i] = (v1**3*(x/v2)**v1 + 3*v1**2*(x/v2)**v1 + 2*v1*(x/v2)**v1 - 2*v1)/v2**3 
	if len(x_all) == 1:
		result = result[:,:,:,0]
	return result 


def weibull_f1fa(x, v1, v2):
    f1 = weibull_fd(x, v1, v2)
    return f1

def weibull_f2fa(x, v1, v2):
    f2 = weibull_fdd(x, v1, v2)
    return f2

def weibull_p1fa(x, v1, v2):
    p1 = weibull_pd(x, v1, v2)
    return p1

def weibull_p2fa(x, v1, v2):
    p2 = weibull_pdd(x, v1, v2)
    return p2

def weibull_mu1fa(alpha, v1, v2):
    x = weibull_min.ppf((1-alpha), c=v1, scale=v2)
    mu1 = -weibull_pd(x, v1, v2)
    return mu1

def weibull_mu2fa(alpha, v1, v2):
    x = weibull_min.ppf((1-alpha), c=v1, scale=v2)
    mu2 = -weibull_pdd(x, v1, v2)
    return mu2

def weibull_ldda(x, v1, v2):
    nx = len(x)
    temp1 = weibull_logfdd(x, v1, v2)
    ldd = np.sum(temp1, axis=-1) / nx
    return ldd

def weibull_lddda(x, v1, v2):
    nx = len(x)
    temp1 = weibull_logfddd(x, v1, v2)
    lddd = np.sum(temp1, axis=-1) / nx
    return lddd