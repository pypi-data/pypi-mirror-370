import sympy as sp
import numpy as np


def diff_to_functions(func, symbols, order):
    ''' Passed a symbolic function and symbols, differentiates and returns a matrix of derivatives. '''
    dim = len(symbols)
    if order == 1:
        result = np.empty(dim, dtype=object)
        for i in range(dim):
            result[i] = sp.diff(func, symbols[i])
    elif order == 2:
        result = np.empty((dim, dim), dtype=object)
        for i in range(dim):
            for j in range(dim):
                result[i, j] = sp.diff(func, symbols[i], symbols[j])
    elif order == 3:
        result = np.empty((dim, dim, dim), dtype=object)
        for i in range(dim):
            for j in range(dim):
                for k in range(dim):
                    result[i, j, k] = sp.diff(func, symbols[i], symbols[j], symbols[k])
    else:
        raise ValueError("Orders other than 1,2,3 are not supported.")
    return result


def numpify(text):
    '''Replaced exp and log in a string with np.exp and np.log'''
    return text.replace('exp(', 'np.exp(').replace('log(', 'np.log(')


def diff_to_code(func, symbols, func_title, order, xt=False):
    ''' Passed a symbolic function and symbols, differentiates once and returns a string of runnable Python code.'''
    func_deriv = diff_to_functions(func, symbols, order)       #vector of functions
    dim = len(symbols)

    string = '\n'
    diff_params = ''
    for i in range(len(symbols)):
        diff_params += ', v'+str(i+1)
    if not xt:
        string += ('def {}(x{}): \n'.format(func_title, diff_params))
    else:
        string += ('def {}(x, t{}): \n'.format(func_title, diff_params))
    string += '\t#Automatically generated code.\n'
    string += '\tdim={} \n'.format(dim)

    # vectorised, but works for non-vector input as well
    if xt:
        string += '\tt_is_vector = isinstance(t, list) or isinstance(t, np.ndarray)\n'
        string += '\tif t_is_vector:\n'
        string += '\t\tt_all = t\n'
    string += '\tif not (isinstance(x, list) or isinstance(x, np.ndarray)):\n'
    string += '\t\tx_all=[x]\n'
    string += '\telse:\n'
    string += '\t\tx_all=x\n'    

    if order == 1:
        string += '\tresult = np.zeros((dim, len(x_all)))\n'
        string += '\tfor i in range(len(x_all)):\n'
        string += '\t\tx = x_all[i]\n'
        if xt:
            string += '\t\tif t_is_vector:\n'
            string += '\t\t\tt = t_all[i]\n'
        for i in range(dim):
            string += '\t\tresult[{},i] = {} \n'.format(i, func_deriv[i])
        string += '\tif len(x_all) == 1:\n'
        string += '\t\tresult = result[:,0]\n'
        
    elif order == 2:
        string += '\tresult = np.zeros((dim,dim, len(x_all)))\n'
        string += '\tfor i in range(len(x_all)):\n'
        string += '\t\tx = x_all[i]\n'
        if xt:
            string += '\t\tif t_is_vector:\n'
            string += '\t\t\tt = t_all[i]\n'
        for i in range(dim):
            for j in range(dim):
                string += '\t\tresult[{},{},i] = {}\n'.format(i, j, func_deriv[i, j])
        string += '\tif len(x_all) == 1:\n'
        string += '\t\tresult = result[:,:,0]\n'

    elif order == 3:
        string += '\tresult = np.zeros((dim, dim, dim, len(x_all)))\n'
        string += '\tfor i in range(len(x_all)):\n'
        string += '\t\tx = x_all[i]\n'
        if xt:
            string += '\t\tif t_is_vector:\n'
            string += '\t\t\tt = t_all[i]\n'
        for i in range(dim):
            for j in range(dim):
                for k in range(dim):
                    string += '\t\tresult[{},{},{},i] = {} \n'.format(i, j, k, func_deriv[i, j, k])
        string += '\tif len(x_all) == 1:\n'
        string += '\t\tresult = result[:,:,:,0]\n'
    else:
        raise ValueError("Orders other than 1,2,3 are not supported.")
    
    string += '\treturn result \n'
    return numpify(string)


def diff_to_file(file, func, symbols, func_title, order, xt=False):
    ''' Passed an open file, appends Python code for the derivative function.
        symbols argument used to indicate which parameters to differentiate by (must be a list of sympy symbol objects).
        Options:
            xt=False:   the functions are of x only (vector or float)
            xt=True:    the functions are of x, t and works for 3 cases:
                1. x, t both floats
                2. x array and t a float (would be t0)
                3. x, t arrays of the same size.
        Returns a matrix with the last index corresponding to the x value.
    '''
    code = diff_to_code(func, symbols, func_title, order, xt=xt)
    file.write(code)


example = True
if example:
    # f is a symbolic function of x, v1, v2, v3, but only differentiate wrt v1, v2, v3
    x, t, v1, v2, v3 = sp.symbols('x t v1 v2 v3')
    f = x*v1**3+3*x*v1*v2**2*v3 + t*v2
    with open('autodiff_example_vectorised.py', 'w') as file:
        file.write('import numpy as np\n\n')
        diff_to_file(file, f, [v1, v2, v3], 'deriv_1', 1, xt=True)
        diff_to_file(file, f, [v1, v2, v3], 'deriv_2', 2, xt=True)
        diff_to_file(file, f, [v1, v2, v3], 'deriv_3', 3, xt=True)
    file.close()