import numpy as np


def format_data_a(actual_p_ml, actual_p_cp, p):
    x = []
    y_ml = []
    y_cp = []
    for i in range(len(p)):
        x.append(p[len(p)-1-i])
        y_ml.append(actual_p_ml[len(p)-1-i])
        y_cp.append(actual_p_cp[len(p)-1-i])
    x_range = (x[0], x[-1])
    y_range = (y_ml[0], y_ml[-1])
    return {'xlabel': 'Nominal Probability',  'ylabel': 'PCP', 'x':x, 'y_ml':y_ml, 'y_cp':y_cp, 
            'title': '(a) PCP vs NP', 'benchmark':{'x': x_range, 'y': x_range}, 'limits': {'x': x_range, 'y': y_range}}


def format_data_b(actual_p_ml, actual_p_cp, p):
    x = []
    y_ml = []
    y_cp = []
    for p_val in 0.0001 * np.asarray(range(1000,-1,-1)):
        x.append(p_val)
        y_ml.append(actual_p_ml[int(p_val*10000)])
        y_cp.append(actual_p_cp[int(p_val*10000)])
    x_range = (x[0], x[-1])
    y_range = x_range
    return {'xlabel': 'Nominal Probability',  'ylabel': 'PCP', 'x':x, 'y_ml':y_ml, 'y_cp':y_cp, 
            'title': '(b) PCP vs NP (tail)', 'benchmark':{'x': x_range, 'y': x_range}, 'limits': {'x': x_range, 'y': y_range}}


def format_data_d(actual_p_ml, actual_p_cp, p):
    x = []
    y_ml = []
    y_cp = []
    cut_off_index = 200 # since graph peaks sharply, can ignore first (p smallest) n points
    for i in range(len(p) - cut_off_index):
        i_rev = len(p) - 1 - i
        x.append(p[i_rev])
        y_ml.append(actual_p_ml[i_rev]/p[i_rev])
        y_cp.append(actual_p_cp[i_rev]/p[i_rev])
    x_range = (x[0], x[-1])
    y_range = (y_ml[0], y_ml[-1])
    return {'xlabel': 'Nominal Probability',  'ylabel': 'Prob Ratio', 'x':x, 'y_ml':y_ml, 'y_cp':y_cp, 
            'title': '(d) PCP/NP vs NP', 'benchmark':{'x': x_range, 'y': (1,1)}, 'limits': {'x': x_range, 'y': y_range}}


def format_data_h(actual_p_ml, actual_p_cp, p):
    x = []
    y_ml = []
    y_cp = []
    cut_off_index = 30
    for i in range(len(p) - cut_off_index):
        i_rev = len(p) - 1 - i
        x.append(1/p[i_rev])
        y_ml.append(1/actual_p_ml[i_rev])
        y_cp.append(1/actual_p_cp[i_rev])
    x_range = (x[0], x[-1])
    return {'xlabel': '1/Nominal Probability',  'ylabel': '1/PCP', 'x':x, 'y_ml':y_ml, 'y_cp':y_cp, 
            'title': '(h) 1/PCP vs 1/NP', 'benchmark':{'x': x_range, 'y': x_range}, 'limits': {'x': x_range, 'y': x_range}}


def format_data_i(actual_p_ml, actual_p_cp, p):
    x = []
    y_ml = []
    y_cp = []
    cut_off_index = 40  # cut off both the highest and lowest p values
    for i in range(len(p) - 2*cut_off_index):
        i_rev = len(p)-1-i-cut_off_index
        np = p[i_rev]
        pcp_ml = actual_p_ml[i_rev]
        pcp_cp = actual_p_cp[i_rev]
        x.append(1/np - 1/(1-np))
        y_ml.append(1/pcp_ml - 1/(1-pcp_ml))
        y_cp.append(1/pcp_cp - 1/(1-pcp_cp))
    x_range = (x[0], x[-1])
    return {'xlabel': '1/NP-1/(1-NP)',  'ylabel': '1/PCP-1/(1-PCP)', 'x':x, 'y_ml':y_ml, 'y_cp': y_cp,
            'title': '(h) PCP vs NP', 'benchmark':{'x': x_range, 'y': x_range}, 'limits': {'x': x_range, 'y': x_range}}


