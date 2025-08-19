import sympy
import autodiff

x, v1, v2 = sympy.symbols('x v1 v2')

f = (v1/v2)*((x/v2)**(v1-1))*sympy.exp(-((x/v2)**v1))
p = 1-sympy.exp(-((x/v2)**v1))
logf = sympy.log(v1)-sympy.log(v2)+(v1-1)*sympy.log(x/v2)-(x/v2)**v1
                                 
with open('output_weibull.py', 'w') as file:
    file.write('import numpy as np\n')
    file.write(autodiff.diff_to_code(f, [v1, v2], 'weibull_fd', 1))
    file.write(autodiff.diff_to_code(f, [v1, v2], 'weibull_fdd', 2))
    file.write(autodiff.diff_to_code(p, [v1, v2], 'weibull_pd', 1))
    file.write(autodiff.diff_to_code(p, [v1, v2], 'weibull_pdd', 2))
    file.write(autodiff.diff_to_code(logf, [v1, v2], 'weibull_logfdd', 2))
    file.write(autodiff.diff_to_code(logf, [v1, v2], 'weibull_logfddd', 3))

file.close()