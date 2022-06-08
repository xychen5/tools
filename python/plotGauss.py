import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as mpl
  
# Let's create a function to model and create data
def func(x, a, x0, sigma):
    return a*np.exp(-(x-x0)**2/(2*sigma**2))
  
# Generating clean data
x = np.linspace(0, 10, 100)
# deviation is sigma: 2
# mean is u: 5
# scale is a: 1
y = func(x, 1, 5, 2)
y2 = func(x, 1, 5, 1)
y3 = func(x, 1, 5, 4)
  
# Adding noise to the data
yn = y + 0.2 * np.random.normal(size=len(x))
  
# Plot out the current state of the data and model
fig = mpl.figure()
ax = fig.add_subplot(111)
ax.plot(x, y, c='k', label='Function sigma: 2')
ax.plot(x, y2, c='g', label='Function2 sigma: 1')
ax.plot(x, y3, c='b', label='Function3 sigma: 4')
ax.scatter(x, yn)
  
# Executing curve_fit on noisy data
popt, pcov = curve_fit(func, x, yn)
  
#popt returns the best fit values for parameters of the given model (func)
print (popt)
  
ym = func(x, popt[0], popt[1], popt[2])
ax.plot(x, ym, c='r', label='Best fit')
ax.legend()

fig.savefig('model_fit.png')
