import numpy as np

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
