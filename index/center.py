import numpy as np
from index import ma
from index import kd

class STRATEGY:
    dhandho = 1
    passivation = 2
    bias = 3

class CENTER:
    dhandho_score = 0
    passivation_scroe = 0
    bias_scroe = 0
    def get_backtest_result(self, prices, score, hit_score, day):
        hit, win, rate, ar = 0.0, 0.0, 0.0, 0.0
        for i in range(0, len(prices)-day):
            if score[i] == hit_score:
                hit += 1
                diff = prices[i+day] - prices[i]
                ar += diff
                if diff > 0 and hit_score > 0:
                    win += 1
                elif diff < 0 and hit_score < 0:
                    win += 1
                print "    %.2f -> %.2f (%.2f)" %(prices[i], prices[i+day], diff)
        if hit > 0:
            rate = win/hit *100
            ar /= hit
        if hit_score < 0:
            ar *= -1
        return hit, rate, ar

    def get_mkt_score(self, m, k, p):
        ma_score = self.get_ma_score(STRATEGY.dhandho ,p, m.ma20, m.ma60, m.ma120)
        macd_score = self.get_macd_score(STRATEGY.dhandho, m.diff, m.macd)
        kd_score = self.get_kd_score(STRATEGY.dhandho, k.k, k.d)
        self.dhandho_score = 1.0*ma_score + 1.0*macd_score + 2.0*kd_score

        ma_score = self.get_ma_score(STRATEGY.passivation ,p, m.ma20, m.ma60, m.ma120)
        macd_score = self.get_macd_score(STRATEGY.passivation, m.diff, m.macd)
        kd_score = self.get_kd_score(STRATEGY.passivation, k.k, k.d)
        self.passivation_score = 1.0*ma_score + 1.0*macd_score + 2.0*kd_score

        ma_score = self.get_ma_score(STRATEGY.bias ,p, m.ma20, m.ma60, m.ma120)
        kd_score = self.get_kd_score(STRATEGY.bias, k.k, k.d)
        self.bias_score = 2.0*ma_score + 2.0*kd_score

    def get_macd_score(self, strategy, fast, slow):
        score = np.zeros_like(fast)
        floor = fast.min()
        ceiling = fast.max()
        tf_bull = np.logical_and((fast > 0) ,(slow > 0))
        tf_bear = np.logical_and((fast < 0) ,(slow < 0))
        if strategy == STRATEGY.dhandho:
            # Bull Martket
            tf = np.logical_and(tf_bull ,(fast > slow))
            score[tf] = 0
            tf = np.logical_and(tf_bull ,(fast < slow))
            tf = np.logical_and(tf ,(ceiling-fast)/ceiling < 0.7)
            score[tf] = 0
            # Bear Martket 
            tf = np.logical_and(tf_bear ,(fast < slow))
            score[tf] = 0
            tf = np.logical_and(tf_bear ,(fast > slow))
            tf = np.logical_and(tf ,(floor-fast)/floor < 0.7)
            score[tf] = 100
        elif strategy == STRATEGY.passivation:
            score[tf_bull] = 100
            score[tf_bear] = -100
        return score

    def get_ma_score(self, strategy, p, ma20, ma60, ma120):
        score = np.zeros_like(ma20)
        if strategy == STRATEGY.dhandho:
            # Bull/Bear order
            tf = np.logical_and((ma20 > ma60), (ma60 > ma120))
            score[tf] = 0
            tf = np.logical_and((ma20 < ma60), (ma60 < ma120))
            score[tf] = 100
        elif strategy == STRATEGY.passivation:
            # Bull/Bear order
            tf = ma20 > ma60
            score[tf] = 100
            tf = ma60 > ma20
            score[tf] = -100
        elif strategy == STRATEGY.bias:
            bias = (p - ma60)/ma60*100
            # Bull/Bear order
            tf = bias > 15
            score[tf] -= 100
            tf = bias < -15
            score[tf] += 100
        return score

    def get_kd_score(self, strategy, k, d):
        score = np.zeros_like(k)
        if strategy == STRATEGY.dhandho:
            threshold = 5
            # Bull Martket
            tf_bull = np.logical_and((k > 80) ,(d > 80))
            tf = np.logical_and(tf_bull ,(k-d) > threshold)
            score[tf] = 0
            tf = np.logical_and(tf_bull ,(k-d) < threshold)
            score[tf] = 0
            # Bear Martket 
            tf_bear = np.logical_and((k < 30) ,(d < 30))
            tf = np.logical_and(tf_bear ,(k-d) > threshold)
            score[tf] = 100
            tf = np.logical_and(tf_bear ,(k-d) < threshold)
            score[tf] = 0
        elif strategy == STRATEGY.passivation:
            # High blunt
            tf_bull = np.logical_and((k > 80) ,(d > 80))
            keep = self.get_keep_result(tf_bull)
            tf = keep == 3
            score[tf] = 100
            # Low blunt
            tf_bear = np.logical_and((k < 20) ,(d < 20))
            keep = self.get_keep_result(tf_bear)
            tf = keep == 3
            score[tf] = -100
        elif strategy == STRATEGY.bias:
            # High blunt
            tf_bull = np.logical_and((k > 80) ,(d > 80))
            keep = self.get_keep_result(tf_bull)
            tf = keep > 6
            score[tf_bull] = -100
            # Low blunt
            tf_bear = np.logical_and((k < 20) ,(d < 20))
            keep = self.get_keep_result(tf_bear)
            tf = keep < 6
            score[tf_bear] = 100
        return score

    def get_keep_result(self, value):
        keep = np.zeros(len(value))
        keep[0] = 0 
        for i in range(1, len(value)):
            if value[i] == True:
                keep[i] = keep[i-1] + 1
            else:
                keep[i] = 0 
        return keep

    def get_index_data(self, raw):
        prices = raw.adj_close
        # Calc MA line
        m = ma.MA()
        k = kd.KD()
        m.ma20 = m.moving_average(prices, 20, type='simple')
        m.ma60 = m.moving_average(prices, 60, type='simple')
        m.ma120 = m.moving_average(prices, 120, type='simple')
        # Calc MACD line
        m.diff, m.macd = m.moving_average_convergence(prices, nslow=26, nfast=12, nday=9)
        return score

    def get_keep_result(self, value):
        keep = np.zeros(len(value))
        keep[0] = 0 
        for i in range(1, len(value)):
            if value[i] == True:
                keep[i] = keep[i-1] + 1
            else:
                keep[i] = 0 
        return keep

    def get_index_data(self, raw):
        prices = raw.adj_close
        # Calc MA line
        m = ma.MA()
        k = kd.KD()
        m.ma20 = m.moving_average(prices, 20, type='simple')
        m.ma60 = m.moving_average(prices, 60, type='simple')
        m.ma120 = m.moving_average(prices, 120, type='simple')
        # Calc MACD line
        m.diff, m.macd = m.moving_average_convergence(prices, nslow=26, nfast=12, nday=9)
        # Calc KD line
        k.k, k.d = k.stochastic_oscillator(raw, 20)

        m.ma_score = self.get_ma_result(prices, m.ma20, m.ma60, m.ma120)
        m.macd_score = self.get_macd_result(m.diff, m.macd)
        k.kd_score = self.get_kd_result(k.k, k.d)
        return m, k


