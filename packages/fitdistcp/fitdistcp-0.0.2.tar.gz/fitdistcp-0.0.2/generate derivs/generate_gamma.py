import scipy
import sympy
import numpy as np
import autodiff

x, v1, v2 = sympy.symbols('x v1 v2')

f = (v2**(-v1))*(1/sympy.gamma(v1))*(x**(v1-1))*sympy.exp(-(x/v2))
logf = -v1*sympy.log(v2)-sympy.log(sympy.gamma(v1))+(v1-1)*sympy.log(x)-x/v2
                                 
with open('output_gamma.py', 'w') as file:
    file.write('import numpy as np\n')
    file.write(autodiff.diff_to_code(f, [v1, v2], 'gamma_fd', 1))
    file.write(autodiff.diff_to_code(f, [v1, v2], 'gamma_fdd', 2))
    file.write(autodiff.diff_to_code(logf, [v1, v2], 'gamma_logfdd', 2))
    file.write(autodiff.diff_to_code(logf, [v1, v2], 'gamma_logfddd', 3))

file.close()

# pd, pdd done manually