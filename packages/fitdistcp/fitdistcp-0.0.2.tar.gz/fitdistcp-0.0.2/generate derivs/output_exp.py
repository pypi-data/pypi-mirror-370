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
