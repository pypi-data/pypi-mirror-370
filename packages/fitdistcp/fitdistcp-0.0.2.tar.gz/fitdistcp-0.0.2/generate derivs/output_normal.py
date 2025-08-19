import numpy as np
from scipy.stats import norm

def norm_fd(x, v1, v2): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,i] = -np.sqrt(2)*(2*v1 - 2*x)*np.exp(-(-v1 + x)**2/(2*v2**2))/(4*np.sqrt(np.pi)*v2**3) 
		result[1,i] = -np.sqrt(2)*np.exp(-(-v1 + x)**2/(2*v2**2))/(2*np.sqrt(np.pi)*v2**2) + np.sqrt(2)*(-v1 + x)**2*np.exp(-(-v1 + x)**2/(2*v2**2))/(2*np.sqrt(np.pi)*v2**4) 
	if len(x_all) == 1:
		result = result[:,0]
	return result 

def norm_fdd(x, v1, v2): 
	#Automatically generated code.
	dim=2 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim,dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,0,i] = -np.sqrt(2)*(1 - (v1 - x)**2/v2**2)*np.exp(-(v1 - x)**2/(2*v2**2))/(2*np.sqrt(np.pi)*v2**3)
		result[0,1,i] = np.sqrt(2)*(3 - (v1 - x)**2/v2**2)*(v1 - x)*np.exp(-(v1 - x)**2/(2*v2**2))/(2*np.sqrt(np.pi)*v2**4)
		result[1,0,i] = np.sqrt(2)*(3 - (v1 - x)**2/v2**2)*(v1 - x)*np.exp(-(v1 - x)**2/(2*v2**2))/(2*np.sqrt(np.pi)*v2**4)
		result[1,1,i] = np.sqrt(2)*(1 - (3 - (v1 - x)**2/v2**2)*(v1 - x)**2/(2*v2**2) - (v1 - x)**2/v2**2)*np.exp(-(v1 - x)**2/(2*v2**2))/(np.sqrt(np.pi)*v2**3)
	if len(x_all) == 1:
		result = result[:,:,0]
	return result 


def norm_pd(x, v1, v2):
    e1 = x - v1
    e3 = norm.pdf(e1/v2, 0, 1)
    result = np.column_stack([-(e3/v2), -(e3 * e1/v2**2)])
    return result


def norm_pdd(x, v1, v2):
    e1 = x - v1
    e2 = v2**2
    e4 = norm.pdf(e1/v2, 0, 1)
    e6 = e1**2/e2
    e7 = -((e6 - 1) * e4/e2)
    e8 = v2**3
    
    v1_v1 = -(e4 * e1/e8)
    v1_v2 = e7
    v2_v1 = e7
    v2_v2 = -((e6 - 2) * e4 * e1/e8)
    
    result = np.array([[v1_v1, v1_v2], 
                       [v2_v1, v2_v2]])
    return result


def norm_logfdd(x, v1, v2): 
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
		result[0,1,i] = 2*(v1 - x)/v2**3
		result[1,0,i] = 2*(v1 - x)/v2**3
		result[1,1,i] = (1 - 3*(v1 - x)**2/v2**2)/v2**2
	if len(x_all) == 1:
		result = result[:,:,0]
	return result 

def norm_logfddd(x, v1, v2): 
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
		result[0,1,1,i] = -6*(v1 - x)/v2**4 
		result[1,0,0,i] = 2/v2**3 
		result[1,0,1,i] = -6*(v1 - x)/v2**4 
		result[1,1,0,i] = -6*(v1 - x)/v2**4 
		result[1,1,1,i] = 2*(-1 + 6*(v1 - x)**2/v2**2)/v2**3 
	if len(x_all) == 1:
		result = result[:,:,:,0]
	return result 
