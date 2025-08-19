import sympy
import autodiff

x, t, v1, v2, v3, v4 = sympy.symbols('x t v1 v2 v3 v4')

f_gev_p1_density = (1/v3)*((1+v4*((x-v1-v2*t)/v3))**(-1/v4-1))*sympy.exp(-((1+v4*(x-v1-v2*t)/v3)**(-1/v4)))
f_gev_p1_cdf = sympy.exp(-((1+v4*(x-v1-v2*t)/v3)**(-1/v4)))
f_gev_p1_log_density = -sympy.log(v3)-(1+1/v4)*sympy.log(1+v4*(x-v1-v2*t)/v3)-(1+v4*(x-v1-v2*t)/v3)**(-1/v4)
                                 
with open('gev_p1_autodiff_output.py', 'w') as f:
    f.write('import numpy as np\n')
    autodiff.diff_to_file(f, f_gev_p1_density, [v1, v2, v3, v4], 'gev_p1_fd', 1, xt=True)
    autodiff.diff_to_file(f, f_gev_p1_density, [v1, v2, v3, v4], 'gev_p1_fdd', 2, xt=True)
    autodiff.diff_to_file(f, f_gev_p1_cdf, [v1, v2, v3, v4], 'gev_p1_pd', 1, xt=True)
    autodiff.diff_to_file(f, f_gev_p1_cdf, [v1, v2, v3, v4], 'gev_p1_pdd', 2, xt=True)
    autodiff.diff_to_file(f, f_gev_p1_log_density, [v1, v2, v3, v4], 'gev_p1_logfdd', 2, xt=True)
    autodiff.diff_to_file(f, f_gev_p1_log_density, [v1, v2, v3, v4], 'gev_p1_logfddd', 3, xt=True)

f.close()