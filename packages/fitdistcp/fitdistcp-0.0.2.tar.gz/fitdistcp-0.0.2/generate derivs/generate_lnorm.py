import scipy.stats as sp
import sympy
import autodiff

x, v1, v2 = sympy.symbols('x v1 v2')

f = (1/sympy.sqrt(2*sympy.pi))*(1/v2)*(1/x)*sympy.exp(-(sympy.log(x)-v1)**2/(2*v2*v2))
logf = -0.5*sympy.log(2*sympy.pi)-sympy.log(v2)-sympy.log(x)-(sympy.log(x)-v1)**2/(2*v2*v2)

                                 
with open('output_lnormal.py', 'w') as file:
    file.write('import numpy as np\n')
    file.write(autodiff.diff_to_code(f, [v1, v2], 'lnorm_fd', 1))
    file.write(autodiff.diff_to_code(f, [v1, v2], 'lnorm_fdd', 2))
    file.write(autodiff.diff_to_code(logf, [v1, v2], 'lnorm_logfdd', 2))
    file.write(autodiff.diff_to_code(logf, [v1, v2], 'lnorm_logfddd', 3))

file.close()

# lnorm_pd and lnorm_pdd done manually