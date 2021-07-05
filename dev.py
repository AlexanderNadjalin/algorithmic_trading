from market.market import Market


market_file_ane = 'test_data_ETF.csv'


def dev():
    market = Market(market_file_name=market_file_ane,
                    fill_missing_method='forward')


if __name__ == '__main__':
    dev()
