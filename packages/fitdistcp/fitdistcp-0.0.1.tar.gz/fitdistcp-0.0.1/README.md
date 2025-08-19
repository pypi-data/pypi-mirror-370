# fitdistcp

fitdistcp is a free Python package for fitting statistical models using calibrating priors, with the goal of making reliable predictions. The functions provided for each distribution (GEV, GEV with 1 predictor, and GPD) accept sample data x as an argument and return a dict of the relevant results, such as quantiles, cdf, pdf, and maximum likelihood parameters. Install using >pip install fitdistcp.

fitdistcp implements the method developed in *Reducing Reliability Bias in Assessments of Extreme Weather Risk using Calibrating Priors*, S. Jewson, T. Sweeting and L. Jewson (2024): https://doi.org/10.5194/ascmo-11-1-2025.

More information and examples are available at https://www.fitdistcp.info, including the equivalent (more comprehensive) R package.

Development of this package was funded by the Lighthill Risk Network: https://lighthillrisknetwork.org.


### Tests
- The cdf and pdf can be estimated for a set of data, using the ML (Maximum Likelihood) or CP (Calibrating Priors) method, and plotted.
- Reliability tests are provided. A reliability test involves generating a sample from a known distribution, and calculating the quantiles using the ML, or CP method. The actual quantiles can be plotted against the estimated quantiles, in various different ways, to judge the reliability of the method.


### Example: Fitting a GEV distribution
```python
import numpy as np
import scipy.stats
import matplotlib.pyplot as plt
import fitdistcp.genextreme

x = scipy.stats.genextreme.rvs(0, size=20)                  # make some example training data 
p = np.arange(0.001,0.999,0.001)                            # define the probabilities at which we wish to calculate the quantiles
q = fitdistcp.genextreme.ppf(x,p)                           # this command calculates two sets of predictive quantiles for the GEV, 
                                                            # one based on maxlik, and one that includes parameter uncertainty based on a calibrating prior
print(q['ml_params'])                                       # have a look at the maxlik parameters
plt.plot(q['ml_quantiles'],p, label='ML')                   # plot the maxlik quantiles
plt.plot(q['cp_quantiles'],p,color='red', label='CP')       # plot the quantiles that include parameter uncertainty
plt.legend()
plt.show()
```
