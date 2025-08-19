import sympy
import autodiff

x, t1, t2, v1, v2, v3, v4, v5 = sympy.symbols('x t1 t2 v1 v2 v3 v4 v5')

f = (sympy.exp(-v3-v4*t2))*((1+v5*((x-v1-v2*t1)*sympy.exp(-v3-v4*t2)))**(-1/v5-1))*sympy.exp(-((1+v5*(x-v1-v2*t1)*sympy.exp(-v3-v4*t2))**(-1/v5)))
p = sympy.exp(-((1+v5*(x-v1-v2*t1)*sympy.exp(-v3-v4*t2))**(-1/v5)))
logf = -v3-v4*t2-(1+1/v5)*sympy.log(1+v5*(x-v1-v2*t1)*sympy.exp(-v3-v4*t2))-(1+v5*(x-v1-v2*t1)*sympy.exp(-v3-v4*t2))**(-1/v5)
                                 
with open('output_gev_p12.py', 'w') as file:
    file.write('import numpy as np\n')
    autodiff.diff_to_file(file, f, [v1, v2, v3, v4, v5], 'gev_p12_fd', 1, xt=True)
    autodiff.diff_to_file(file, f, [v1, v2, v3, v4, v5], 'gev_p12_fdd', 2, xt=True)
    autodiff.diff_to_file(file, p, [v1, v2, v3, v4, v5], 'gev_p12_pd', 1, xt=True)
    autodiff.diff_to_file(file, p, [v1, v2, v3, v4, v5], 'gev_p12_pdd', 2, xt=True)
    autodiff.diff_to_file(file, logf, [v1, v2, v3, v4, v5], 'gev_p12_logfdd', 2, xt=True)
    autodiff.diff_to_file(file, logf, [v1, v2, v3, v4, v5], 'gev_p12_logfddd', 3, xt=True)

file.close()