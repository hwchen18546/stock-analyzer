import numpy as np

class MA:
    ma20 = 0
    ma60 = 0
    ma120 = 0
    diff = 0
    macd = 0
    def moving_average(self, x, n, type='simple'):
        """ 
        compute an n period moving average.
        type is 'simple' | 'exponential'
        """
        x = np.asarray(x)
        if type == 'simple':
            weights = np.ones(n)
        else:
            weights = np.exp(np.linspace(-1., 0., n)) 

        weights /= weights.sum()

        a = np.convolve(x, weights, mode='full')[:len(x)]
        a[:n] = a[n]
        return a

    def moving_average_convergence(self, x, nslow, nfast, nday):
        """ 
        compute the MACD (Moving Average Convergence/Divergence) using a fast and slow exponential moving avg'
        return value is emaslow, emafast, macd which are len(x) arrays
        """
        emaslow = self.moving_average(x, nslow, type='exponential')
        emafast = self.moving_average(x, nfast, type='exponential')
        diff = emafast - emaslow
        macd = self.moving_average(diff, nday, type='exponential')
        return diff, macd
