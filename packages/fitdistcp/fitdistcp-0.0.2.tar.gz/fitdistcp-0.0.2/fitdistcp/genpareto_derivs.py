from scipy.stats import genpareto
import numpy as np

from . import utils as cp_utils


def gpd_k1_fd(x, v1, v2, v3): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,i] = -1/(v2**2*(1 + v3*(-v1 + x)/v2)**((v3 + 1)/v3)) + (-v1 + x)*(v3 + 1)/(v2**3*(1 + v3*(-v1 + x)/v2)*(1 + v3*(-v1 + x)/v2)**((v3 + 1)/v3)) 
		result[1,i] = ((-1/v3 + (v3 + 1)/v3**2)*np.log(1 + v3*(-v1 + x)/v2) - (-v1 + x)*(v3 + 1)/(v2*v3*(1 + v3*(-v1 + x)/v2)))/(v2*(1 + v3*(-v1 + x)/v2)**((v3 + 1)/v3)) 
	if len(x_all) == 1:
		result = result[:,0]
	return result 

def gpd_k1_fdd(x, v1, v2, v3): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim,dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,0,i] = (2 + (v1 - x)*(v3 + 1)*(2 + v3*(v1 - x)/(v2*(1 - v3*(v1 - x)/v2)) + (v1 - x)*(v3 + 1)/(v2*(1 - v3*(v1 - x)/v2)))/(v2*(1 - v3*(v1 - x)/v2)) + 2*(v1 - x)*(v3 + 1)/(v2*(1 - v3*(v1 - x)/v2)))/(v2**3*(1 - v3*(v1 - x)/v2)**((v3 + 1)/v3))
		result[0,1,i] = (((1 - (v3 + 1)/v3)*np.log(1 - v3*(v1 - x)/v2) - (v1 - x)*(v3 + 1)/(v2*(1 - v3*(v1 - x)/v2)))/v3 - (v1 - x)/(v2*(1 - v3*(v1 - x)/v2)) + (v1 - x)*(v3 + 1)*((1 - (v3 + 1)/v3)*np.log(1 - v3*(v1 - x)/v2) - (v1 - x)*(v3 + 1)/(v2*(1 - v3*(v1 - x)/v2)))/(v2*v3*(1 - v3*(v1 - x)/v2)) - (v1 - x)**2*(v3 + 1)/(v2**2*(1 - v3*(v1 - x)/v2)**2))/(v2**2*(1 - v3*(v1 - x)/v2)**((v3 + 1)/v3))
		result[1,0,i] = (((1 - (v3 + 1)/v3)*np.log(1 - v3*(v1 - x)/v2) - (v1 - x)*(v3 + 1)/(v2*(1 - v3*(v1 - x)/v2)))/v3 - (v1 - x)/(v2*(1 - v3*(v1 - x)/v2)) + (v1 - x)*(v3 + 1)*((1 - (v3 + 1)/v3)*np.log(1 - v3*(v1 - x)/v2) - (v1 - x)*(v3 + 1)/(v2*(1 - v3*(v1 - x)/v2)))/(v2*v3*(1 - v3*(v1 - x)/v2)) - (v1 - x)**2*(v3 + 1)/(v2**2*(1 - v3*(v1 - x)/v2)**2))/(v2**2*(1 - v3*(v1 - x)/v2)**((v3 + 1)/v3))
		result[1,1,i] = (2*(1 - (v3 + 1)/v3)*np.log(1 - v3*(v1 - x)/v2)/v3 + ((1 - (v3 + 1)/v3)*np.log(1 - v3*(v1 - x)/v2) - (v1 - x)*(v3 + 1)/(v2*(1 - v3*(v1 - x)/v2)))**2/v3 + (1 - (v3 + 1)/v3)*(v1 - x)/(v2*(1 - v3*(v1 - x)/v2)) + (v1 - x)/(v2*(1 - v3*(v1 - x)/v2)) - (v1 - x)*(v3 + 1)/(v2*v3*(1 - v3*(v1 - x)/v2)) + (v1 - x)**2*(v3 + 1)/(v2**2*(1 - v3*(v1 - x)/v2)**2))/(v2*v3*(1 - v3*(v1 - x)/v2)**((v3 + 1)/v3))
	if len(x_all) == 1:
		result = result[:,:,0]
	return result 

def gpd_k1_pd(x, v1, v2, v3): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,i] = -(-v1 + x)/(v2**2*(1 + v3*(-v1 + x)/v2)*(1 + v3*(-v1 + x)/v2)**(1/v3)) 
		result[1,i] = -(np.log(1 + v3*(-v1 + x)/v2)/v3**2 - (-v1 + x)/(v2*v3*(1 + v3*(-v1 + x)/v2)))/(1 + v3*(-v1 + x)/v2)**(1/v3) 
	if len(x_all) == 1:
		result = result[:,0]
	return result 

def gpd_k1_pdd(x, v1, v2, v3): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim,dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,0,i] = -(v1 - x)*(2 + v3*(v1 - x)/(v2*(1 - v3*(v1 - x)/v2)) + (v1 - x)/(v2*(1 - v3*(v1 - x)/v2)))/(v2**3*(1 - v3*(v1 - x)/v2)*(1 - v3*(v1 - x)/v2)**(1/v3))
		result[0,1,i] = (v1 - x)*((np.log(1 - v3*(v1 - x)/v2)/v3 + (v1 - x)/(v2*(1 - v3*(v1 - x)/v2)))/v3 + (v1 - x)/(v2*(1 - v3*(v1 - x)/v2)))/(v2**2*(1 - v3*(v1 - x)/v2)*(1 - v3*(v1 - x)/v2)**(1/v3))
		result[1,0,i] = (v1 - x)*((np.log(1 - v3*(v1 - x)/v2)/v3 + (v1 - x)/(v2*(1 - v3*(v1 - x)/v2)))/v3 + (v1 - x)/(v2*(1 - v3*(v1 - x)/v2)))/(v2**2*(1 - v3*(v1 - x)/v2)*(1 - v3*(v1 - x)/v2)**(1/v3))
		result[1,1,i] = (-(np.log(1 - v3*(v1 - x)/v2)/v3 + (v1 - x)/(v2*(1 - v3*(v1 - x)/v2)))**2/v3 + 2*np.log(1 - v3*(v1 - x)/v2)/v3**2 + 2*(v1 - x)/(v2*v3*(1 - v3*(v1 - x)/v2)) - (v1 - x)**2/(v2**2*(1 - v3*(v1 - x)/v2)**2))/(v3*(1 - v3*(v1 - x)/v2)**(1/v3))
	if len(x_all) == 1:
		result = result[:,:,0]
	return result 

def gpd_k1_logfdd(x, v1, v2, v3): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim,dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,0,i] = (1 + 2*(v1 - x)*(v3 + 1)/(v2*(1 - v3*(v1 - x)/v2)) + v3*(v1 - x)**2*(v3 + 1)/(v2**2*(1 - v3*(v1 - x)/v2)**2))/v2**2
		result[0,1,i] = -(1 + (v1 - x)*(v3 + 1)/(v2*(1 - v3*(v1 - x)/v2)))*(v1 - x)/(v2**2*(1 - v3*(v1 - x)/v2))
		result[1,0,i] = -(1 + (v1 - x)*(v3 + 1)/(v2*(1 - v3*(v1 - x)/v2)))*(v1 - x)/(v2**2*(1 - v3*(v1 - x)/v2))
		result[1,1,i] = (2*np.log(1 - v3*(v1 - x)/v2)/v3 - 2*(v3 + 1)*np.log(1 - v3*(v1 - x)/v2)/v3**2 + 2*(v1 - x)/(v2*(1 - v3*(v1 - x)/v2)) - 2*(v1 - x)*(v3 + 1)/(v2*v3*(1 - v3*(v1 - x)/v2)) + (v1 - x)**2*(v3 + 1)/(v2**2*(1 - v3*(v1 - x)/v2)**2))/v3
	if len(x_all) == 1:
		result = result[:,:,0]
	return result 

def gpd_k1_logfddd(x, v1, v2, v3): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim, dim, dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,0,0,i] = -2*(1 + 3*(v1 - x)*(v3 + 1)/(v2*(1 - v3*(v1 - x)/v2)) + 3*v3*(v1 - x)**2*(v3 + 1)/(v2**2*(1 - v3*(v1 - x)/v2)**2) + v3**2*(v1 - x)**3*(v3 + 1)/(v2**3*(1 - v3*(v1 - x)/v2)**3))/v2**3 
		result[0,0,1,i] = (v1 - x)*(2 + v3*(v1 - x)/(v2*(1 - v3*(v1 - x)/v2)) + 3*(v1 - x)*(v3 + 1)/(v2*(1 - v3*(v1 - x)/v2)) + 2*v3*(v1 - x)**2*(v3 + 1)/(v2**2*(1 - v3*(v1 - x)/v2)**2))/(v2**3*(1 - v3*(v1 - x)/v2)) 
		result[0,1,0,i] = (v1 - x)*(2 + v3*(v1 - x)/(v2*(1 - v3*(v1 - x)/v2)) + 3*(v1 - x)*(v3 + 1)/(v2*(1 - v3*(v1 - x)/v2)) + 2*v3*(v1 - x)**2*(v3 + 1)/(v2**2*(1 - v3*(v1 - x)/v2)**2))/(v2**3*(1 - v3*(v1 - x)/v2)) 
		result[0,1,1,i] = -2*(1 + (v1 - x)*(v3 + 1)/(v2*(1 - v3*(v1 - x)/v2)))*(v1 - x)**2/(v2**3*(1 - v3*(v1 - x)/v2)**2) 
		result[1,0,0,i] = (v1 - x)*(2 + v3*(v1 - x)/(v2*(1 - v3*(v1 - x)/v2)) + 3*(v1 - x)*(v3 + 1)/(v2*(1 - v3*(v1 - x)/v2)) + 2*v3*(v1 - x)**2*(v3 + 1)/(v2**2*(1 - v3*(v1 - x)/v2)**2))/(v2**3*(1 - v3*(v1 - x)/v2)) 
		result[1,0,1,i] = -2*(1 + (v1 - x)*(v3 + 1)/(v2*(1 - v3*(v1 - x)/v2)))*(v1 - x)**2/(v2**3*(1 - v3*(v1 - x)/v2)**2) 
		result[1,1,0,i] = -2*(1 + (v1 - x)*(v3 + 1)/(v2*(1 - v3*(v1 - x)/v2)))*(v1 - x)**2/(v2**3*(1 - v3*(v1 - x)/v2)**2) 
		result[1,1,1,i] = (-6*np.log(1 - v3*(v1 - x)/v2)/v3**2 + 6*(v3 + 1)*np.log(1 - v3*(v1 - x)/v2)/v3**3 - 6*(v1 - x)/(v2*v3*(1 - v3*(v1 - x)/v2)) + 6*(v1 - x)*(v3 + 1)/(v2*v3**2*(1 - v3*(v1 - x)/v2)) + 3*(v1 - x)**2/(v2**2*(1 - v3*(v1 - x)/v2)**2) - 3*(v1 - x)**2*(v3 + 1)/(v2**2*v3*(1 - v3*(v1 - x)/v2)**2) + 2*(v1 - x)**3*(v3 + 1)/(v2**3*(1 - v3*(v1 - x)/v2)**3))/v3 
	if len(x_all) == 1:
		result = result[:,:,:,0]
	return result 



############################################################
#' The first derivative of the density
def gpd_k1_f1fa(x,v1,v2,kloc):
# the v1 coming in here is sigma, and the v2 is lambda, following my cp code
	v2=cp_utils.movexiawayfromzero(v2)
	f1=gpd_k1_fd(x,kloc,v1,v2)
	return f1


############################################################
#' The second derivative of the density
def gpd_k1_f2fa(x,v1,v2,kloc):
# the v1 coming in here is sigma, and the v2 is lambda, following my cp code
	f2=gpd_k1_fdd(x,kloc,v1,v2,)
	return f2


############################################################
#' Minus the first derivative of the cdf, at alpha
def gpd_k1_mu1fa(alpha,v1,v2,kloc):
# the v1 coming in here is sigma, and the v2 is lambda, following my cp code
	#x=extraDistr::qgpd((1-alpha),mu=kloc,sigma=v1,xi=v2)
	c=-v2
	x=genpareto.ppf(1-alpha, v2, loc=kloc, scale=v1)
	v2=cp_utils.movexiawayfromzero(v2)
	mu1=-gpd_k1_pd(x,kloc,v1,v2)
	return mu1


############################################################
#' Minus the second derivative of the cdf, at alpha
def gpd_k1_mu2fa(alpha,v1,v2,kloc):
# the v1 coming in here is sigma, and the v2 is lambda, following my cp code
	#x=extraDistr::qgpd((1-alpha),mu=kloc,sigma=v1,xi=v2)
	c=-v2   #=-xi
	x=genpareto.ppf(1-alpha,v2,loc=kloc,scale=v1)
	v2=cp_utils.movexiawayfromzero(v2)
	mu2=-gpd_k1_pdd(x,kloc,v1,v2)
	return mu2


############################################################
#' The second derivative of the normalized log-likelihood
def gpd_k1_ldda(x,v1,v2,kloc):
# the v1 coming in here is sigma, and the v2 is lambda, following my cp code
	nx=len(x)
	v2=cp_utils.movexiawayfromzero(v2)
	temp1=gpd_k1_logfdd(x,kloc,v1,v2) 
	ldd = np.sum(temp1, axis=-1) / nx
	return ldd


############################################################
#' The third derivative of the normalized log-likelihood
def gpd_k1_lddda(x,v1,v2,kloc):
# the v1 coming in here is sigma, and the v2 is lambda, following my cp code
# I have to switch because my cp code orders sigma and lambda differently
	nx=len(x)
	v2=cp_utils.movexiawayfromzero(v2)
	temp1=gpd_k1_logfddd(x,kloc,v1,v2)
	lddd=np.sum(temp1,axis=-1)/nx
	return lddd