import numpy as np

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
