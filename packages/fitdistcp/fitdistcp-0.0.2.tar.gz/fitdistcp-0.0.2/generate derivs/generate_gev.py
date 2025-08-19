import scipy
import sympy
import numpy as np
import autodiff

x, v1, v2, v3 = sympy.symbols('x v1 v2 v3')

f_gev_density = (1/v2)*((1+v3*((x-v1)/v2))**(-1/v3-1))*sympy.exp(-((1+v3*(x-v1)/v2)**(-1/v3)))
f_gev_cdf = sympy.exp(-((1+v3*(x-v1)/v2)**(-1/v3)))
f_gev_log_density = -sympy.log(v2)-(1+1/v3)*sympy.log(1+v3*(x-v1)/v2)-(1+v3*(x-v1)/v2)**(-1/v3)
                                 
with open('gev_autodiff_python_ver.py', 'w') as f:
    f.write('import numpy as np\n')
    f.write(autodiff.diff_to_code(f_gev_density, [v1, v2, v3], 'gev_fd', 1))
    f.write(autodiff.diff_to_code(f_gev_density, [v1, v2, v3], 'gev_fdd', 2))
    f.write(autodiff.diff_to_code(f_gev_cdf, [v1, v2, v3], 'gev_pd', 1))
    f.write(autodiff.diff_to_code(f_gev_cdf, [v1, v2, v3], 'gev_pdd', 2))
    f.write(autodiff.diff_to_code(f_gev_log_density, [v1, v2, v3], 'gev_logfd', 1))
    f.write(autodiff.diff_to_code(f_gev_log_density, [v1, v2, v3], 'gev_logfdd', 2))
    f.write(autodiff.diff_to_code(f_gev_log_density, [v1, v2, v3], 'gev_logfddd', 3))

f.close()