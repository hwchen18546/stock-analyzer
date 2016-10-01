import numpy as np

class KD:
    k = 0
    d = 0

    def get_n_maxmin(self, high, low, n):
        maxn = np.zeros_like(high)
        minn = np.zeros_like(low)
        for i in range(n, len(high) + 1):
            maxn[i - 1] = high[i - n:i].max()
            minn[i - 1] = low[i - n:i].min()

        return (maxn, minn)

    def get_rsv_result(self, raw, n):
        close = raw.close
        maxn, minn = self.get_n_maxmin(raw.high, raw.low, n)
        rsv = np.zeros_like(close)
        rsv[n - 1:] = (close[n - 1:] - minn[n - 1:]) / (maxn[n - 1:] - minn[n - 1:]) * 100
        return rsv

    def stochastic_oscillator(self, raw, n):
        rsv = self.get_rsv_result(raw, n)
        k = np.zeros_like(rsv)
        d = np.zeros_like(rsv)
        k[n - 2], d[n - 2] = (50, 50)
        for i in range(n - 1, len(rsv)):
            k[i] = 0.67 * k[i - 1] + 0.33 * rsv[i]
            d[i] = 0.67 * d[i - 1] + 0.33 * k[i]
        return (k, d)

