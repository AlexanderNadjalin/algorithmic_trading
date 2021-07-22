from loguru import logger
import configparser as cp
import pandas as pd
from holdings.transaction import Transaction
from market.market import Market
from holdings.position_handler import PositionHandler


class Portfolio:
    """

    Portfolio object.
    Portfolio.history has information on positions, their market values, cash etc.
    Portfolio.records has calculated metrics, if the metrics.py functions are called.
    """
    def __init__(self,
                 inception_date: str
                 ):
        self.config = self.config()
        self.commission = self.config['commission']['commission_scheme']
        self.init_cash = float(self.config['init_cash']['init_cash'])
        self.currency = self.config['portfolio_information']['currency']
        self.current_cash = self.init_cash
        self.inception_date = inception_date
        self.current_date = self.inception_date
        self.benchmark = self.config['benchmark']['benchmark_name']
        self.pf_id = self.config['portfolio_information']['pf_id']
        self.position_handler = PositionHandler()
        self.history = pd.DataFrame()
        self.records = pd.DataFrame()
        self.create_history_table()
        logger.success('Portfolio ' + self.pf_id + ' created.')

    @logger.catch
    def config(self) -> cp.ConfigParser:
        """

        Read portfolio_config file and return a config object. Used to set default parameters for holdings objects.

        :return: A ConfigParser object.
        """
        conf = cp.ConfigParser()
        conf.read('holdings/portfolio_config.ini')

        logger.info('Info read from portfolio_config.ini file.')

        return conf

    def update_all_market_values(self,
                                 date: str,
                                 market_data: Market) -> None:
        """

        Update current date and prices of all positions in portfolio.
        Add to portfolio history.
        :param date: Date to update all prices for.
        :param market_data: Market object.
        :return: None.
        """
        for pos in self.position_handler.positions:
            price = market_data.select(columns=[pos],
                                       start_date=date,
                                       end_date=date)
            self.position_handler.positions[pos].update_current_market_price(date=date,
                                                                             market_price=price.iloc[0, 0])
        self.current_date = date
        self.add_history(date=date,
                         market_data=market_data)

        for pos in self.position_handler.positions:
            if self.position_handler.positions[pos].net_quantity == 0:
                del self.position_handler.positions[pos]

    def create_history_table(self) -> None:
        """

        Create pd.Dataframe to hold daily values of portfolio.
        :return: None.
        """
        if self.benchmark != '':
            self.history = pd.DataFrame(columns=['current_date',
                                                 'current_cash',
                                                 'total_commission',
                                                 'realized_pnl',
                                                 'unrealized_pnl',
                                                 'total_pnl',
                                                 'total_market_value',
                                                 'benchmark_value'])
        else:
            self.history = pd.DataFrame(columns=['current_date',
                                                 'current_cash',
                                                 'total_commission',
                                                 'realized_pnl',
                                                 'unrealized_pnl',
                                                 'total_pnl',
                                                 'total_market_value'])

    def add_history(self,
                    date: str,
                    market_data: Market) -> None:
        """

        Add portfolio values for a specific date to history.
        :param date: Date to add to portfolio history.
        :param market_data: Market data for benchmark values.
        :return:
        """
        if self.benchmark != '':
            bm_value = market_data.select(columns=[self.benchmark],
                                          start_date=self.current_date,
                                          end_date=self.current_date).iloc[0, 0]
            new_trans = {'current_date': date,
                         'current_cash': self.current_cash,
                         'total_commission': self.total_commission,
                         'realized_pnl': self.total_realized_pnl,
                         'unrealized_pnl': self.total_unrealized_pnl,
                         'total_pnl': self.total_pnl,
                         'total_market_value': self.total_market_value,
                         'benchmark_value': bm_value}
        else:
            new_trans = {'current_date': date,
                         'current_cash': self.current_cash,
                         'total_commission': self.total_commission,
                         'realized_pnl': self.total_realized_pnl,
                         'unrealized_pnl': self.total_unrealized_pnl,
                         'total_pnl': self.total_pnl,
                         'total_market_value': self.total_market_value}

        self.history = self.history.append(new_trans,
                                           ignore_index=True)

    def transact_security(self,
                          trans: Transaction) -> None:
        """

        Complete buy/sell operation in portfolio given a transaction.
        :param trans: Transaction object.
        :return: None.
        """
        trans_sec_cost = trans.price * trans.quantity
        trans_total_cost = trans_sec_cost + trans.commission

        if trans_total_cost > self.current_cash:
            logger.warning('Transaction total cost is larger than current cash.'
                           'Proceeding with negative cash balance.')
        self.position_handler.transact_position(trans=trans)
        if trans.direction == 'B':
            self.current_cash -= trans_total_cost
        else:
            self.current_cash += trans_total_cost

    @property
    def market_value(self) -> float:
        """

        Calculate the market value of all positions, excluding cash.
        :return: Market value.
        """
        return self.position_handler.total_market_value()

    @property
    def total_market_value(self) -> float:
        """

        Calculate the market value of all positions, including cash.
        :return: Market value.
        """
        return self.position_handler.total_market_value() + self.current_cash

    @property
    def total_pnl(self) -> float:
        """

        Calculate total PnL.
        :return: Total PnL.
        """
        return self.position_handler.total_pnl()

    @property
    def total_realized_pnl(self) -> float:
        """

        Calculate total realized PnL.
        :return: Realized PnL.
        """
        return self.position_handler.total_realized_pnl()

    @property
    def total_unrealized_pnl(self) -> float:
        """

        Calculate total unrealized PnL.
        :return: Unrealized PnL.
        """
        return self.position_handler.total_unrealized_pnl()

    @property
    def total_commission(self) -> float:
        """

        Calculate total commission.
        :return: Total commission.
        """
        return self.position_handler.total_commission()
