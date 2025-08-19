import sympy
import autodiff

x, v1, v2, v3 = sympy.symbols('x v1 v2 v3')

# v1=mu, v2=sigma, v3=xi

f = (1/v2)*(1+v3*((x-v1)/v2))**(-((v3+1)/v3))
p = 1-(1+v3*((x-v1)/v2))**(-1/v3)
logf = -sympy.log(v2)-((1+v3)/v3)*sympy.log(1+v3*(x-v1)/v2)
                                 
with open('output_gpd.py', 'w') as file:
    file.write('import numpy as np\n')
    autodiff.diff_to_file(file, f, [v2, v3], 'gpd_k1_fd', 1)
    autodiff.diff_to_file(file, f, [v2, v3], 'gpd_k1_fdd', 2)
    autodiff.diff_to_file(file, p, [v2, v3], 'gpd_k1_pd', 1)
    autodiff.diff_to_file(file, p, [v2, v3], 'gpd_k1_pdd', 2)
    autodiff.diff_to_file(file, logf, [v2, v3], 'gpd_k1_logfdd', 2)
    autodiff.diff_to_file(file, logf, [v2, v3], 'gpd_k1_logfddd', 3)

file.close()