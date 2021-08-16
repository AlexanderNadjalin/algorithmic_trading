from market.market import Market
from holdings.portfolio import Portfolio
from backtest.backtest import Backtest
from strategy.strategy import PeriodicRebalancing
from plot.plot import Plot


market_file_ane = 'test_data_ETF.csv'


def dev():
    market = Market(market_file_name=market_file_ane,
                    fill_missing_method='forward')

    pf = Portfolio(inception_date='2017-07-27')

    s = PeriodicRebalancing(period='som',
                            id_weight={'XACTOMXS30.ST': 0.99})

    bt = Backtest(market=market,
                  pf=pf,
                  start_date=pf.inception_date,
                  end_date='2021-07-02')

    bt.add_strategy(strategy=s)
    bt.run()

    p = Plot(bt=bt)
    p.plot_text()
    # p.drawdowns_plot()
    # p.rolling_sharpe_beta_plot()
    # p.create_tear_sheet()


if __name__ == '__main__':
    dev()
