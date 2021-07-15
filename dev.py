from market.market import Market
from holdings.transaction import Transaction
from holdings.position import Position
from holdings.portfolio import Portfolio


market_file_ane = 'test_data_ETF.csv'


def dev():
    market = Market(market_file_name=market_file_ane,
                    fill_missing_method='forward')

    t1 = Transaction(name='XACTOMXS30.ST',
                     direction='B',
                     quantity=10.0,
                     price=286.85,
                     commission_scheme='avanza_small',
                     date='2021-05-03')
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
    pf.transact_security(t1)
    pf.update_all_market_values(date=t1.date,
                                market_data=market)

    pf.transact_security(t2)
    pf.update_all_market_values(date=t2.date,
                                market_data=market)

    pf.transact_security(t3)
    pf.update_all_market_values(date=t3.date,
                                market_data=market)
    print(pf.total_realized_pnl)
    pass


if __name__ == '__main__':
    dev()
