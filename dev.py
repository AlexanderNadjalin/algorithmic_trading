from market.market import Market
from portfolio.transaction import Transaction
from portfolio.position import Position


market_file_ane = 'test_data_ETF.csv'


def dev():
    # market = Market(market_file_name=market_file_ane,
    #                     fill_missing_method='forward')
    # print(market.select(['XACTOMXS30.ST'], '2021-05-01', '2021-05-06'))

    t1 = Transaction(name='AMZ', direction='B', quantity=25.0, price=150.0, commission_scheme='', date='2021-07-07')
    t2 = Transaction(name='AMZ', direction='S', quantity=25.0, price=151.0, commission_scheme='', date='2021-07-08')
    t3 = Transaction(name='AMZ', direction='B', quantity=10.0, price=300.0, commission_scheme='avanza_medium', date='2021-07-09')
    t4 = Transaction(name='AMZ', direction='B', quantity=10.0, price=400.0, commission_scheme='avanza_medium', date='2021-07-10')

    p = Position()
    p.transact_position(t1)
    p.transact_position(t2)
    # p.transact_position(t3)
    # p.transact_position(t4)
    pass


if __name__ == '__main__':
    dev()
