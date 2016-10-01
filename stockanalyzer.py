#!/usr/bin/python

import sys
import matplotlib
matplotlib.use('TkAgg')
import datetime
import numpy as np
import matplotlib.colors as colors
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from index import ma
from index import kd
from index import center
from api import yahoo
from Tkinter import *


class MyLocator(mticker.MaxNLocator):
    def __init__(self, *args, **kwargs):
        mticker.MaxNLocator.__init__(self, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        return mticker.MaxNLocator.__call__(self, *args, **kwargs)

class StockBot(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.grid()
        self.inputTicket = StringVar(value = '0050')
        self.inputViewdays = StringVar(value = '600')
        self.inputStart = StringVar(value = '2010,1,1')
        self.inputEnd = StringVar(value = '{:%Y,%m,%d}'.format(datetime.date.today()))
        self.gridCount = 0
        self.gridSpan = 5
        self.createWidgets()
        if len(sys.argv) > 1:
            self.inputTicket.set(sys.argv[1])
        self.analyze()

    def createWidgets(self):
        labLogo = Label(self, text='StockAnalyzer',
        font=("Verdana",15),fg="black")
        labLogo.grid(row=self.gridCount, column=0, columnspan=self.gridSpan)

        self.loglist = Listbox(self, width=35, height=40)
        self.loglist.grid(row=1, column=5, rowspan=4)

        self.gridCount+=3
        labTicker = Label(self, text='StockCode', font=("Verdana",13),fg="black")
        labTicker.grid(row=self.gridCount, column=0)
        labView = Label(self, text='ViewDays', font=("Verdana",13),fg="black")
        labView.grid(row=self.gridCount, column=1)
        labStart = Label(self, text='StartDate', font=("Verdana",13),fg="black")
        labStart.grid(row=self.gridCount, column=2)
        labEnd = Label(self, text='EndDate', font=("Verdana",13),fg="black")
        labEnd.grid(row=self.gridCount, column=3)
        self.gridCount+=1
        etyTicker = Entry(self, width=20, textvariable=self.inputTicket, justify='center')
        etyTicker.grid(row=self.gridCount, column=0)
        etyView = Entry(self, width=20, textvariable=self.inputViewdays, justify='center')
        etyView.grid(row=self.gridCount, column=1)
        etyStart = Entry(self, width=20, textvariable=self.inputStart, justify='center')
        etyStart.grid(row=self.gridCount, column=2)
        etyEnd = Entry(self, width=20, textvariable=self.inputEnd, justify='center')
        etyEnd.grid(row=self.gridCount, column=3)

        self.gridCount+=1
        btnAnalyze = Button(self, text='Analyze', command=self.analyze)
        btnAnalyze.grid(row=self.gridCount, column=1)
        btnQuit = Button(self, text='Quit', command=self.quit)
        btnQuit.grid(row=self.gridCount, column=2)

    def quit(self):
        root.quit()     # stops mainloop
        root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

    def get_plot_data(self):
        plt.rc('axes', grid=True)
        plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)

        f, (ax_main, ax_macd, ax_kd, ax_score) = plt.subplots(nrows=4, ncols=1, figsize=(12,5.5), dpi=100)
        plt.setp(ax_main.get_xticklabels(), visible=False)
        plt.setp(ax_macd.get_xticklabels(), visible=False)
        plt.setp(ax_kd.get_xticklabels(), visible=False)
        plt.tight_layout()

        # a tk.DrawingArea
        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().grid(row=1, column=0, columnspan=self.gridSpan-1)
        # Create an empty frame for Toolbar, because toolbar use pack instead of grid
        toolbar_frame = Frame(self)
        toolbar_frame.grid(row=2, column=0, columnspan=self.gridSpan)
        toolbar = NavigationToolbar2TkAgg(canvas, toolbar_frame)
        toolbar.update()
        return ax_main, ax_macd, ax_kd, ax_score

    def get_index_data(self, raw):
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
  
    def analyze(self):
        # Get user query
        if len(self.inputViewdays.get()) == 0:
            plot_last_n = -600
        else:
            plot_last_n = int(self.inputViewdays.get()) * -1
        if len(self.inputTicket.get()) == 0:
            ticker = '0050.TW'
        else:
            ticker = self.inputTicket.get() + '.TW'
        if len(self.inputStart.get()) == 0:
            start = datetime.date(2010, 1, 1)
        else:
            start = datetime.datetime.strptime(self.inputStart.get(), '%Y,%m,%d')
        if len(self.inputEnd.get()) == 0:
            end = datetime.date.today()
        else:
            end = datetime.datetime.strptime(self.inputEnd.get(), '%Y,%m,%d')

        # Get history data
        y = yahoo.YAHOO()
        raw = y.get_history_data(ticker, start, end.date())
        #twii = y.get_history_data('^TWII', start, end)
        if raw == 0:
            print "[%s] Not Found" %(ticker)
            ticker = ticker + 'O'
            raw = y.get_history_data(ticker, start, end.date())
            if raw == 0:
                print "[%s] Not Found" %(ticker)
                return 0

        # Get index data
        m, k, c = self.get_index_data(raw)
        ma20, ma60, ma120 = m.ma20, m.ma60, m.ma120
        diff, macd = m.diff, m.macd
        prices = raw.adj_close
        c.get_mkt_score(m, k, prices)
        c.bias_score = (c.bias_score - c.passivation_score) / 2

        # Get plot data
        ax_main, ax_macd, ax_kd, ax_score = self.get_plot_data()
        # Plot price line
        lineprice = ax_main.plot(raw.date[plot_last_n:], prices[plot_last_n:], color='black', lw=1, label='Price')
        #adj_twii = (twii.close-twii.close.min())/(twii.close.max()-twii.close.min()) * (prices.max()-prices.min()) + prices.min()
        #linetwii = ax_main.plot(raw.date[plot_last_n:], adj_twii[plot_last_n:], color='purple', lw=1, label='TWII')
        '''
        # Plot k line
        dx = raw.adj_close - raw.close
        low = raw.low + dx
        high = raw.high + dx
        deltas = np.zeros_like(prices)
        deltas[1:] = np.diff(prices)
        up = deltas > 0
        ax_main.vlines(raw.date[up], low[up], high[up], color='red', label='_nolegend_')
        ax_main.vlines(raw.date[~up], low[~up], high[~up], color='black', label='_nolegend_')
        '''
        # Plot MA line
        linema20 = ax_main.plot(raw.date[plot_last_n:], ma20[plot_last_n:], color='blue', lw=1, label='MA (20)')
        linema60 = ax_main.plot(raw.date[plot_last_n:], ma60[plot_last_n:], color='red', lw=1, label='MA (60)')
        linema120 = ax_main.plot(raw.date[plot_last_n:], ma120[plot_last_n:], color='green', lw=1, label='MA (120)')

        # Plot MACD line
        fillcolor = 'darkslategrey'
        ax_macd.plot(raw.date[plot_last_n:], diff[plot_last_n:], color='black', lw=2, label='DIFF(fast)')
        ax_macd.plot(raw.date[plot_last_n:], macd[plot_last_n:], color='blue', lw=1, label='MACD(slow)')
        ax_macd.fill_between(raw.date[plot_last_n:], diff[plot_last_n:] - macd[plot_last_n:], 0, alpha=0.5, facecolor=fillcolor, edgecolor=fillcolor)
        ax_macd.text(0.025, 0.95, 'MACD (12, 26, 9)' , va='top',
                 transform=ax_macd.transAxes, fontsize=9)

        # Plot KD line
        linemk = ax_kd.plot(raw.date[plot_last_n:], k.k[plot_last_n:], color='red', lw=2, label='K')
        linemd = ax_kd.plot(raw.date[plot_last_n:], k.d[plot_last_n:], color='blue', lw=2, label='D')
        ax_kd.set_ylim(0, 100)

        # Plot Score line
        linemktscore = ax_score.plot(raw.date[plot_last_n:], c.dhandho_score[plot_last_n:], color='red', lw=2, label='Dhandho')
        #linemktscore = ax_score.plot(raw.date[plot_last_n:], c.passivation_score[plot_last_n:], color='blue', lw=2, label='Passivation')
        linemktscore = ax_score.plot(raw.date[plot_last_n:], c.bias_score[plot_last_n:], color='green', lw=2, label='Bias')
        ax_score.set_ylim(-400, 400)

        # Print lapassivation price
        last = raw[-1]
        s = 'O:%1.2f H:%1.2f L:%1.2f C:%1.2f, V:%1.1fM Chg:%+1.2f' % (
        last.open, last.high,
        last.low, last.close,
        last.volume*1e-6,
        last.close - last.open)
        t4 = ax_main.text(0.3, 0.9, s, transform=ax_main.transAxes, fontsize=9)
        self.loglist.delete(0, END)
        name = y.get_ticker_name(ticker)
        self.write_log('[%s] %s' %(ticker, name))
        self.write_log('[%s] %s' %(ticker, last.date))
        self.write_log('[%s] O:%1.2f H:%1.2f L:%1.2f C:%1.2f' %(ticker, last.open, last.high, last.low, last.close))
        self.write_log('[%s] V:%1.1fM Chg:%+1.2f' %(ticker, last.volume*1e-6, last.close - last.open))

        self.write_log("[%s] dhan:%d, bias:%d" %(ticker, c.dhandho_score[-1], c.bias_score[-1]))
        days = np.array([1,2,3,5,7,10,20,40,60,120,240])
        for i in range(0, len(days)):
            self.print_backtest(ticker, prices, c, days[i])

        # Print legend
        props = font_manager.FontProperties(size=10)
        leg_main = ax_main.legend(loc='center left', shadow=True, fancybox=True, prop=props)
        leg_main.get_frame().set_alpha(0.5)
        leg_macd = ax_macd.legend(loc='center left', shadow=True, fancybox=True, prop=props)
        leg_macd.get_frame().set_alpha(0.5)
        leg_kd = ax_kd.legend(loc='center left', shadow=True, fancybox=True, prop=props)
        leg_kd.get_frame().set_alpha(0.5)
        leg_score = ax_score.legend(loc='center left', shadow=True, fancybox=True, prop=props)
        leg_score.get_frame().set_alpha(0.5)

        # Print volume         
        volume = (raw.close*raw.volume)/1e6  # dollar volume in millions
        axt_main = ax_main.twinx()
        vmax = volume.max()
        poly = axt_main.fill_between(raw.date[plot_last_n:], volume[plot_last_n:], 0, label='Volume', facecolor='darkgoldenrod', edgecolor='darkgoldenrod')
        axt_main.set_ylim(0, 5*vmax)
        axt_main.set_yticks([])
        ax_main.yaxis.set_major_locator(MyLocator(5, prune='both'))

    def write_log(self, content):
        print content
        self.loglist.insert(END, content)

    def print_backtest(self, ticker, prices, c ,day):
        self.write_log("[%s] ------- %d days -------" %(ticker, day))
        hit, rate, ar = c.get_backtest_result(prices, c.dhandho_score, 400, day)
        self.write_log("[%s] Dhan+ Hit:%d Win:%d%%, Ar:%.2f" %(ticker, hit, rate, ar))
        #hit, rate, ar = c.get_backtest_result(prices, c.passivation_score, 400, day)
        #self.write_log("[%s] Pass+ Hit:%d Win:%d%%, Ar:%.2f" %(ticker, hit, rate, ar))
        #hit, rate, ar = c.get_backtest_result(prices, c.passivation_score, -400, day)
        #self.write_log("[%s] Pass- Hit:%d Win:%d%%, Ar:%.2f" %(ticker, hit, rate, ar))
        hit, rate, ar = c.get_backtest_result(prices, c.bias_score, 400, day)
        self.write_log("[%s] Bias+ Hit:%d Win:%d%%, Ar:%.2f" %(ticker, hit, rate, ar))
        #hit, rate, ar = c.get_backtest_result(prices, c.bias_score, -400, day)
        #self.write_log("[%s] Bias- Hit:%d Win:%d%%, Ar:%.2f" %(ticker, hit, rate, ar))

if __name__ == '__main__':
    sys.stderr = sys.stdout
    root = Tk()
    root.resizable(width=FALSE, height=FALSE)
    app = StockBot(parent=root)
    app.master.title("StockAnalyzer")
    app.mainloop()

