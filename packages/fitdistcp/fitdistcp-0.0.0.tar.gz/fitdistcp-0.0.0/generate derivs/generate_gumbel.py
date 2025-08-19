import scipy
import sympy
import numpy as np
import autodiff

x, v1, v2 = sympy.symbols('x v1 v2')

f = (1/v2)*sympy.exp(-( ((x-v1)/v2) + sympy.exp(-((x-v1)/v2))))
p = sympy.exp(-(sympy.exp(-((x-v1)/v2))))
logf = -sympy.log(v2)-(x-v1)/v2-sympy.exp(-(x-v1)/v2)
                                 
with open('output_gumbel.py', 'w') as file:
    file.write('import numpy as np\n')
    file.write(autodiff.diff_to_code(f, [v1, v2], 'gumbel_fd', 1))
    file.write(autodiff.diff_to_code(f, [v1, v2], 'gumbel_fdd', 2))
    file.write(autodiff.diff_to_code(p, [v1, v2], 'gumbel_pd', 1))
    file.write(autodiff.diff_to_code(p, [v1, v2], 'gumbel_pdd', 2))
    file.write(autodiff.diff_to_code(logf, [v1, v2], 'gumbel_logfdd', 2))
    file.write(autodiff.diff_to_code(logf, [v1, v2], 'gumbel_logfddd', 3))

file.close()