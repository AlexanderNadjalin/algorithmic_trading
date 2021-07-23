from market.market import Market
from holdings.transaction import Transaction
from holdings.portfolio import Portfolio
from event import event, event_handler
from backtest.backtest import Backtest
from metric.metric import Metric
from plot.plot import Plot


market_file_ane = 'test_data_ETF.csv'


def dev():
    market = Market(market_file_name=market_file_ane,
                    fill_missing_method='forward')

    t1 = Transaction(name='XACTOMXS30.ST',
                     direction='B',
                     quantity=100.0,
                     price=223.5,
                     commission_scheme='avanza_small',
                     date='2020-02-03')
    t2 = Transaction(name='XACTOMXS30.ST',
                     direction='B',
                     quantity=10.0,
                     price=281.85,
                     commission_scheme='avanza_small',
                     date='2021-05-04')
    t3 = Transaction(name='XACTOMXS30.ST',
                     direction='S',
                     quantity=20.0,
                     price=291.15,
                     commission_scheme='avanza_small',
                     date='2021-05-05')

    t4 = Transaction(name='SXRT.TG',
                     direction='B',
                     quantity=10.0,
                     price=132.4,
                     commission_scheme='avanza_medium',
                     date='2021-05-03')

    pf = Portfolio(inception_date='2021-05-03')

    eh = event_handler.EventHandler(market=market,
                                    pf=pf)
    e2 = event.Market(date=t1.date)

    e1 = event.Transaction(date=t1.date,
                           trans=t1)
    eh.put_event(event=e1)
    # eh.put_event(event=e2)
    # pf.update_all_market_values(date=t1.date,
    #                             market_data=market)

    bt = Backtest(eh=eh,
                  market=market,
                  pf=pf,
                  start_date=t1.date,
                  end_date='2021-07-02')
    bt.run()

    p = Plot(bt=bt)
    p.drawdowns_plot()
    pass


if __name__ == '__main__':
    dev()
