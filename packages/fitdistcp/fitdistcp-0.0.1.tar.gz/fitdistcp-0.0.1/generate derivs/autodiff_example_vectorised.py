import numpy as np


def deriv_1(x, t, v1, v2, v3): 
	#Automatically generated code.
	dim=3 
	t_is_vector = isinstance(t, list) or isinstance(t, np.ndarray)
	if t_is_vector:
		t_all = t
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		if t_is_vector:
			t = t_all[i]
		result[0,i] = 3*v1**2*x + 3*v2**2*v3*x 
		result[1,i] = t + 6*v1*v2*v3*x 
		result[2,i] = 3*v1*v2**2*x 
	if len(x_all) == 1:
		result = result[:,0]
	return result 

def deriv_2(x, t, v1, v2, v3): 
	#Automatically generated code.
	dim=3 
	t_is_vector = isinstance(t, list) or isinstance(t, np.ndarray)
	if t_is_vector:
		t_all = t
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim,dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		if t_is_vector:
			t = t_all[i]
		result[0,0,i] = 6*v1*x
		result[0,1,i] = 6*v2*v3*x
		result[0,2,i] = 3*v2**2*x
		result[1,0,i] = 6*v2*v3*x
		result[1,1,i] = 6*v1*v3*x
		result[1,2,i] = 6*v1*v2*x
		result[2,0,i] = 3*v2**2*x
		result[2,1,i] = 6*v1*v2*x
		result[2,2,i] = 0
	if len(x_all) == 1:
		result = result[:,:,0]
	return result 

def deriv_3(x, t, v1, v2, v3): 
	#Automatically generated code.
	dim=3 
	t_is_vector = isinstance(t, list) or isinstance(t, np.ndarray)
	if t_is_vector:
		t_all = t
	if not (isinstance(x, list) or isinstance(x, np.ndarray)):
		x_all=[x]
	else:
		x_all=x
	result = np.zeros((dim, dim, dim, len(x_all)))
	for i in range(len(x_all)):
		x = x_all[i]
		if t_is_vector:
			t = t_all[i]
		result[0,0,0,i] = 6*x 
		result[0,0,1,i] = 0 
		result[0,0,2,i] = 0 
		result[0,1,0,i] = 0 
		result[0,1,1,i] = 6*v3*x 
		result[0,1,2,i] = 6*v2*x 
		result[0,2,0,i] = 0 
		result[0,2,1,i] = 6*v2*x 
		result[0,2,2,i] = 0 
		result[1,0,0,i] = 0 
		result[1,0,1,i] = 6*v3*x 
		result[1,0,2,i] = 6*v2*x 
		result[1,1,0,i] = 6*v3*x 
		result[1,1,1,i] = 0 
		result[1,1,2,i] = 6*v1*x 
		result[1,2,0,i] = 6*v2*x 
		result[1,2,1,i] = 6*v1*x 
		result[1,2,2,i] = 0 
		result[2,0,0,i] = 0 
		result[2,0,1,i] = 6*v2*x 
		result[2,0,2,i] = 0 
		result[2,1,0,i] = 6*v2*x 
		result[2,1,1,i] = 6*v1*x 
		result[2,1,2,i] = 0 
		result[2,2,0,i] = 0 
		result[2,2,1,i] = 0 
		result[2,2,2,i] = 0 
	if len(x_all) == 1:
		result = result[:,:,:,0]
	return result 
