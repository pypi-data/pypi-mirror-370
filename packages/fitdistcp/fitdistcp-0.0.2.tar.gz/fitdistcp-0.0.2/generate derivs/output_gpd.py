import numpy as np

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
