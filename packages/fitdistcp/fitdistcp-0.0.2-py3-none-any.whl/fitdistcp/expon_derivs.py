import numpy as np

def exp_fd(x, v1): 
	#Automatically generated code.
	dim=1 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,i] = -v1*x*np.exp(-v1*x) + np.exp(-v1*x) 
	if len(x_all) == 1:
		result = result[:,0]
	return result 

def exp_fdd(x, v1): 
	#Automatically generated code.
	dim=1 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim,dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,0,i] = x*(v1*x - 2)*np.exp(-v1*x)
	if len(x_all) == 1:
		result = result[:,:,0]
	return result 

def exp_pd(x, v1): 
	#Automatically generated code.
	dim=1 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,i] = x*np.exp(-v1*x) 
	if len(x_all) == 1:
		result = result[:,0]
	return result 

def exp_pdd(x, v1): 
	#Automatically generated code.
	dim=1 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim,dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,0,i] = -x**2*np.exp(-v1*x)
	if len(x_all) == 1:
		result = result[:,:,0]
	return result 

def exp_logfdd(x, v1): 
	#Automatically generated code.
	dim=1 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim,dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,0,i] = -1/v1**2
	if len(x_all) == 1:
		result = result[:,:,0]
	return result 

def exp_logfddd(x, v1): 
	#Automatically generated code.
	dim=1 
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim, dim, dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		result[0,0,0,i] = 2/v1**3 
	if len(x_all) == 1:
		result = result[:,:,:,0]
	return result 


# The first derivative of the density
def exp_f1fa(x,v1):
	nx=len(x)
	f1=np.zeros((1,nx))
	f1[0,:]=exp_fd(x,v1)
	return f1

# The second derivative of the density
def exp_f2fa(x,v1):
	nx=len(x)
	f2 = np.zeros((1, 1, nx))
	f2[0,0,:] = exp_fdd(x,v1)
	return f2

# The first derivative of the cdf
def exp_p1fa(x,v1):
	nx=len(x)
	p1 = np.zeros((1, nx))
	p1[0,:]=exp_pd(x,v1)
	return p1

# The second derivative of the cdf
def exp_p2fa(x,v1):
	nx=len(x)
	p2=np.zeros((1,1,nx))
	p2[0,0,:]=exp_pdd(x,v1)
	return p2

# The second derivative of the normalized log-likelihood
def exp_ldda(x,v1):
	nx=len(x)
	ldd=np.zeros((1,1))
	ldd[0,0]=np.sum(exp_logfdd(x,v1), axis=-1)/nx
	return ldd

# The third derivative of the normalized log-likelihood
def exp_lddda(x,v1):
	nx=len(x)
	lddd = np.zeros((1,1,1))
	lddd[0,0,0]=np.sum(exp_logfddd(x,v1), axis=-1)/nx
	return lddd
