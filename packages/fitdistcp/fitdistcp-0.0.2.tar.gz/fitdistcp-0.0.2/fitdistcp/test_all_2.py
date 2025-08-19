from scipy.stats import genextreme
import numpy as np
import genextreme as cp_genextreme
import genextreme_p1 as cp_genextreme_p1
import genextreme_p12 as cp_genextreme_p12
from pprint import pprint

t1 = range(1, 21)
t2 = range(11, 31)
x = []
for i in range(len(t1)):
    loc = -1 + 0.01*t1[i]
    scale = 0.01 * np.exp(0.2*t2[i])
    c = 0.2
    #x.append(genextreme.rvs(c, loc=loc, scale=scale))

x = [
    np.float64(-0.9913480238809794),
    np.float64(-0.9769235070688991),
    np.float64(-0.8621908965345157),
    np.float64(-0.7398677117373739),
    np.float64(-1.1516382552121482),
    np.float64(-0.8197479252398926),
    np.float64(-0.7681271113256107),
    np.float64(-1.3148460507732627),
    np.float64(-0.47137556796826374),
    np.float64(-0.9640522997831006),
    np.float64(-0.5531371188766323),
    np.float64(-1.4151054520409128),
    np.float64(-1.2289727692687278),
    np.float64(-1.7617925135393455),
    np.float64(-0.6226462562363477),
    np.float64(-0.785745191074492),
    np.float64(1.4346107813099191),
    np.float64(-1.269218100253865),
    np.float64(-2.0722151365158665),
    np.float64(6.571634964444661)]

q = cp_genextreme_p12.ppf(x, t1, t2, t01=0, t02=0)
r = cp_genextreme_p12.rvs(1, x, t1, t2, t01=0, t02=0)
d = cp_genextreme_p12.pdf(x, t1, t2, t01=0, t02=0)
p = cp_genextreme_p12.cdf(x, t1, t2, t01=0, t02=0)

#q = cp_genextreme_p1.ppf(x, t1, t0=0)
#r = cp_genextreme_p1.rvs(1, x, t1, t0=0)
#d = cp_genextreme_p1.pdf(x, t1, t0=0)
#p = cp_genextreme_p1.cdf(x, t1, t0=0)

#print(q['ml_params'])
#print(r['ml_params'])
#print(d['ml_params'])
#print(p['ml_params'])