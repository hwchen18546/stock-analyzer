#!/usr/bin/python

import sys
import time
import datetime
import numpy as np
from index import ma
from index import kd
from index import center
from api import yahoo

def get_index_data(raw):
    prices = raw.adj_close
    # Calc MA line
    m = ma.MA()
    k = kd.KD()
    c = center.CENTER()
    m.ma20 = m.moving_average(prices, 20, type='simple')
    m.ma60 = m.moving_average(prices, 60, type='simple')
    m.ma120 = m.moving_average(prices, 120, type='simple')
    # Calc MACD line
    m.diff, m.macd = m.moving_average_convergence(prices, nslow=26, nfast=12, nday=9)
    # Calc KD line
    k.k, k.d = k.stochastic_oscillator(raw, 20) 
    return m, k, c

def autoanalyze(db_name):
    y = yahoo.YAHOO()
    start = datetime.date(2010, 1, 1)
    end = datetime.date.today()
    try:
        db = open('%s' %(db_name), 'r')
    except:
        print "Can't open db file."
        return 0
    for ticker in db:
        # Get history data
        ticker = ticker.rstrip()
        raw = y.get_history_data(ticker, start, end)
        if raw == 0 or len(raw) < 300:
            time.sleep(1)
            #print "[%s] Not Found" %(ticker)
            continue
        # Get index data
        try:
            m, k, c = get_index_data(raw)
        except:
            continue
        # Get index data
        m, k, c = get_index_data(raw)
        prices = raw.adj_close
        c.get_mkt_score(m, k, prices)
        c.bias_score = (c.bias_score - c.passivation_score) / 2

        # Get final Score
        print "[%s] Today dhan:%d, bias:%d" %(ticker, c.dhandho_score[-1], c.bias_score[-1])
        date = '{:%Y_%m_%d}'.format(raw.date[-1])
        if c.dhandho_score[-1] == 400:
           print_backtest(ticker, c, prices, c.dhandho_score, 400, "Dhan+", date)
        #elif c.passivation_score[-1] == 400:
        #    print_backtest(ticker, c, prices, c.passivation_score, 400, "Pass+", date)
        #elif c.passivation_score[-1] == -400:
        #    print_backtest(ticker, c, prices, c.passivation_score, -400, "Pass-", date)
        elif c.bias_score[-1] == 400:
            print_backtest(ticker, c, prices, c.bias_score, 400, "Bias+", date)
        #elif c.bias_score[-1] == -400:
        #    print_backtest(ticker, c, prices, c.bias_score, -400, "Bias-", date)

def print_backtest(ticker, c, prices, score, hit_score, index, date):
    days = np.array([1,5,7,10,20,40,60,120])
    out = open('out/out_%s'%(date), 'a')
    for i in range(0, len(days)):
        hit, rate, ar = c.get_backtest_result(prices, score, hit_score, days[i])
        out.write("[%s] %s Hit:%d Win:%d%%, Ar:%.2f Day:%d\n" %(ticker, index, hit, rate, ar, days[i]))
    out.write("\n")
    out.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        autoanalyze(sys.argv[1])
    else:
        print "[USAGE] ./parser <db_file>"
