from loguru import logger
import configparser as cp
import pandas as pd
from transaction import Transaction
from position import Position


class Portfolio:
    def __init__(self,
                 init_cash: float,
                 benchmark: str):
        self.config = self.config()
        self.commission = self.config['commission_scheme']
        self.benchmark = self.config['benchmark']
        self.init_cash = init_cash
        self.current_cash = self.init_cash
        self.positions = []
        self.market_value = self.init_cash
        self.history = pd.DataFrame()
        logger.info('Portfolio created.')

    @logger.catch
    def config(self) -> cp.ConfigParser:
        """

        Read portfolio_config file and return a config object. Used to set default parameters for portfolio objects.

        :return: A ConfigParser object.
        """
        conf = cp.ConfigParser()
        conf.read('portfolio/portfolio_config.ini')

        logger.success('I/O info read from portfolio_config.ini file.')

        return conf

    def add_position(self,
                     position: Position):
        pass
