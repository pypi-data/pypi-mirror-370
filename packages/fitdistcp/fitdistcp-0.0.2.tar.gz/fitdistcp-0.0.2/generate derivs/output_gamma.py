import numpy as np
import math
import scipy.special as sp

def gamma_fd(x, v1, v2): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,i] = -x**(v1 - 1)*np.exp(-x/v2)*np.log(v2)/(v2**v1*math.gamma(v1)) + x**(v1 - 1)*np.exp(-x/v2)*np.log(x)/(v2**v1*math.gamma(v1)) - x**(v1 - 1)*np.exp(-x/v2)*sp.polygamma(0, v1)/(v2**v1*math.gamma(v1)) 
		result[1,i] = -v1*x**(v1 - 1)*np.exp(-x/v2)/(v2*v2**v1*math.gamma(v1)) + x*x**(v1 - 1)*np.exp(-x/v2)/(v2**2*v2**v1*math.gamma(v1)) 
	if len(x_all) == 1:
		result = result[:,0]
	return result 

def gamma_fdd(x, v1, v2): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim,dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,0,i] = x**(v1 - 1)*(np.log(v2)**2 - 2*np.log(v2)*np.log(x) + 2*np.log(v2)*sp.polygamma(0, v1) + np.log(x)**2 - 2*np.log(x)*sp.polygamma(0, v1) + sp.polygamma(0, v1)**2 - sp.polygamma(1, v1))*np.exp(-x/v2)/(v2**v1*math.gamma(v1))
		result[0,1,i] = x**(v1 - 1)*(v1*np.log(v2) - v1*np.log(x) + v1*sp.polygamma(0, v1) - 1 - x*np.log(v2)/v2 + x*np.log(x)/v2 - x*sp.polygamma(0, v1)/v2)*np.exp(-x/v2)/(v2*v2**v1*math.gamma(v1))
		result[1,0,i] = x**(v1 - 1)*(v1*np.log(v2) - v1*np.log(x) + v1*sp.polygamma(0, v1) - 1 - x*np.log(v2)/v2 + x*np.log(x)/v2 - x*sp.polygamma(0, v1)/v2)*np.exp(-x/v2)/(v2*v2**v1*math.gamma(v1))
		result[1,1,i] = x**(v1 - 1)*(v1*(v1 + 1) - 2*v1*x/v2 - x*(2 - x/v2)/v2)*np.exp(-x/v2)/(v2**2*v2**v1*math.gamma(v1))
	if len(x_all) == 1:
		result = result[:,:,0]
	return result 

def gamma_logfdd(x, v1, v2): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim,dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,0,i] = -sp.polygamma(1, v1)
		result[0,1,i] = -1/v2
		result[1,0,i] = -1/v2
		result[1,1,i] = (v1 - 2*x/v2)/v2**2
	if len(x_all) == 1:
		result = result[:,:,0]
	return result 

def gamma_logfddd(x, v1, v2): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim, dim, dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,0,0,i] = -sp.polygamma(2, v1) 
		result[0,0,1,i] = 0 
		result[0,1,0,i] = 0 
		result[0,1,1,i] = v2**(-2) 
		result[1,0,0,i] = 0 
		result[1,0,1,i] = v2**(-2) 
		result[1,1,0,i] = v2**(-2) 
		result[1,1,1,i] = 2*(-v1 + 3*x/v2)/v2**3 
	if len(x_all) == 1:
		result = result[:,:,:,0]
	return result 
