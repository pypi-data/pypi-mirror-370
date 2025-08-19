import scipy
import sympy
import numpy as np
import autodiff

x, v1= sympy.symbols('x v1')

f = v1*sympy.exp(-v1*x)
p = 1-sympy.exp(-v1*x)
logf = sympy.log(v1)-v1*x
                                 
with open('output_exp.py', 'w') as file:
    file.write('import numpy as np\n')
    file.write(autodiff.diff_to_code(f, [v1], 'exp_fd', 1))
    file.write(autodiff.diff_to_code(f, [v1], 'exp_fdd', 2))
    file.write(autodiff.diff_to_code(p, [v1], 'exp_pd', 1))
    file.write(autodiff.diff_to_code(p, [v1], 'exp_pdd', 2))
    file.write(autodiff.diff_to_code(logf, [v1], 'exp_logfdd', 2))
    file.write(autodiff.diff_to_code(logf, [v1], 'exp_logfddd', 3))

file.close()