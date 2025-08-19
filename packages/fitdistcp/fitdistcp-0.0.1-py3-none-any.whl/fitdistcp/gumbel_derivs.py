import numpy as np
from scipy.stats import gumbel_r

def gumbel_fd(x, v1, v2): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,i] = (1/v2 - np.exp(-(-v1 + x)/v2)/v2)*np.exp(-np.exp(-(-v1 + x)/v2) - (-v1 + x)/v2)/v2 
		result[1,i] = ((-v1 + x)/v2**2 - (-v1 + x)*np.exp(-(-v1 + x)/v2)/v2**2)*np.exp(-np.exp(-(-v1 + x)/v2) - (-v1 + x)/v2)/v2 - np.exp(-np.exp(-(-v1 + x)/v2) - (-v1 + x)/v2)/v2**2 
	if len(x_all) == 1:
		result = result[:,0]
	return result 

def gumbel_fdd(x, v1, v2): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim,dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,0,i] = ((np.exp((v1 - x)/v2) - 1)**2 - np.exp((v1 - x)/v2))*np.exp(-np.exp(-(-v1 + x)/v2) - (-v1 + x)/v2)/v2**3
		result[0,1,i] = (2*np.exp((v1 - x)/v2) - 2 - (v1 - x)*(np.exp((v1 - x)/v2) - 1)**2/v2 + (v1 - x)*np.exp((v1 - x)/v2)/v2)*np.exp(-np.exp(-(-v1 + x)/v2) - (-v1 + x)/v2)/v2**3
		result[1,0,i] = (2*np.exp((v1 - x)/v2) - 2 - (v1 - x)*(np.exp((v1 - x)/v2) - 1)**2/v2 + (v1 - x)*np.exp((v1 - x)/v2)/v2)*np.exp(-np.exp(-(-v1 + x)/v2) - (-v1 + x)/v2)/v2**3
		result[1,1,i] = (2 - 2*(v1 - x)*(np.exp((v1 - x)/v2) - 1)/v2 - (v1 - x)*(2*np.exp((v1 - x)/v2) - 2 - (v1 - x)*(np.exp((v1 - x)/v2) - 1)**2/v2 + (v1 - x)*np.exp((v1 - x)/v2)/v2)/v2)*np.exp(-np.exp(-(-v1 + x)/v2) - (-v1 + x)/v2)/v2**3
	if len(x_all) == 1:
		result = result[:,:,0]
	return result 

def gumbel_pd(x, v1, v2): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,i] = -np.exp(-(-v1 + x)/v2)*np.exp(-np.exp(-(-v1 + x)/v2))/v2 
		result[1,i] = -(-v1 + x)*np.exp(-(-v1 + x)/v2)*np.exp(-np.exp(-(-v1 + x)/v2))/v2**2 
	if len(x_all) == 1:
		result = result[:,0]
	return result 

def gumbel_pdd(x, v1, v2): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim,dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,0,i] = (np.exp((v1 - x)/v2) - 1)*np.exp((v1 - x)/v2)*np.exp(-np.exp((v1 - x)/v2))/v2**2
		result[0,1,i] = (1 - (v1 - x)*np.exp((v1 - x)/v2)/v2 + (v1 - x)/v2)*np.exp((v1 - x)/v2)*np.exp(-np.exp((v1 - x)/v2))/v2**2
		result[1,0,i] = (1 - (v1 - x)*np.exp((v1 - x)/v2)/v2 + (v1 - x)/v2)*np.exp((v1 - x)/v2)*np.exp(-np.exp((v1 - x)/v2))/v2**2
		result[1,1,i] = (v1 - x)*(-2 + (v1 - x)*np.exp((v1 - x)/v2)/v2 - (v1 - x)/v2)*np.exp((v1 - x)/v2)*np.exp(-np.exp((v1 - x)/v2))/v2**3
	if len(x_all) == 1:
		result = result[:,:,0]
	return result 

def gumbel_logfdd(x, v1, v2): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim,dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,0,i] = -np.exp((v1 - x)/v2)/v2**2
		result[0,1,i] = (np.exp((v1 - x)/v2) - 1 + (v1 - x)*np.exp((v1 - x)/v2)/v2)/v2**2
		result[1,0,i] = (np.exp((v1 - x)/v2) - 1 + (v1 - x)*np.exp((v1 - x)/v2)/v2)/v2**2
		result[1,1,i] = (1 - 2*(v1 - x)*np.exp((v1 - x)/v2)/v2 + 2*(v1 - x)/v2 - (v1 - x)**2*np.exp((v1 - x)/v2)/v2**2)/v2**2
	if len(x_all) == 1:
		result = result[:,:,0]
	return result 

def gumbel_logfddd(x, v1, v2): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim, dim, dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,0,0,i] = -np.exp((v1 - x)/v2)/v2**3 
		result[0,0,1,i] = (2 + (v1 - x)/v2)*np.exp((v1 - x)/v2)/v2**3 
		result[0,1,0,i] = (2 + (v1 - x)/v2)*np.exp((v1 - x)/v2)/v2**3 
		result[0,1,1,i] = (-2*np.exp((v1 - x)/v2) + 2 - 4*(v1 - x)*np.exp((v1 - x)/v2)/v2 - (v1 - x)**2*np.exp((v1 - x)/v2)/v2**2)/v2**3 
		result[1,0,0,i] = (2 + (v1 - x)/v2)*np.exp((v1 - x)/v2)/v2**3 
		result[1,0,1,i] = (-2*np.exp((v1 - x)/v2) + 2 - 4*(v1 - x)*np.exp((v1 - x)/v2)/v2 - (v1 - x)**2*np.exp((v1 - x)/v2)/v2**2)/v2**3 
		result[1,1,0,i] = (-2*np.exp((v1 - x)/v2) + 2 - 4*(v1 - x)*np.exp((v1 - x)/v2)/v2 - (v1 - x)**2*np.exp((v1 - x)/v2)/v2**2)/v2**3 
		result[1,1,1,i] = (-2 + 6*(v1 - x)*np.exp((v1 - x)/v2)/v2 - 6*(v1 - x)/v2 + 6*(v1 - x)**2*np.exp((v1 - x)/v2)/v2**2 + (v1 - x)**3*np.exp((v1 - x)/v2)/v2**3)/v2**3 
	if len(x_all) == 1:
		result = result[:,:,:,0]
	return result 


############################################################
#' The first derivative of the density
def gumbel_f1fa(x,v1,v2):
	f1=gumbel_fd(x,v1,v2)
	return f1

############################################################
#' The second derivative of the density
def gumbel_f2fa(x,v1,v2):
	f2=gumbel_fdd(x,v1,v2)
	return f2

############################################################
#' The first derivative of the cdf
def gumbel_p1fa(x,v1,v2):
	p1=gumbel_pd(x,v1,v2)
	return p1

############################################################
#' The second derivative of the cdf
def gumbel_p2fa(x,v1,v2):
	p2=gumbel_pdd(x,v1,v2)
	return p2

############################################################
#' Minus the first derivative of the cdf, at alpha
def gumbel_mu1fa(alpha,v1,v2):
	x=gumbel_r.ppf((1-alpha),loc=v1,scale=v2)
	mu1=-gumbel_pd(x,v1,v2)
	return mu1

############################################################
#' Minus the second derivative of the cdf, at alpha
def gumbel_mu2fa(alpha,v1,v2):
	x=gumbel_r.ppf((1-alpha),loc=v1,scale=v2)
	mu2=-gumbel_pdd(x,v1,v2)
	return mu2

############################################################
#' The second derivative of the normalized log-likelihood
def gumbel_ldda(x,v1,v2):
	nx=len(x)
	temp1=gumbel_logfdd(x,v1,v2)
	ldd=np.sum(temp1, axis=-1) / nx
	return ldd

############################################################
#' The third derivative of the normalized log-likelihood
def gumbel_lddda(x,v1,v2):
	nx=len(x)
	temp1=gumbel_logfddd(x,v1,v2)
	lddd=np.sum(temp1, axis=-1) / nx
	return lddd
