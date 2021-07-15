from loguru import logger
import configparser as cp
import pandas as pd
from holdings.transaction import Transaction
from holdings.position import Position
from holdings.position_handler import PositionHandler


class Portfolio:
    def __init__(self,
                 inception_date: str
                 ):
        self.config = self.config()
        self.commission = self.config['commission']['commission_scheme']
        self.init_cash = self.config['init_cash']['init_cash']
        self.currency = self.config['portfolio_information']['currency']
        self.current_cash = self.init_cash
        self.inception_date = inception_date
        self.pf_id = self.config['portfolio_information']['pf_id']
        self.positions = []
        self.position_handler = PositionHandler()
        self.market_value = self.init_cash
        self.history = pd.DataFrame()
        logger.info('Portfolio ' + self.pf_id + ' created.')

    @logger.catch
    def config(self) -> cp.ConfigParser:
        """

        Read portfolio_config file and return a config object. Used to set default parameters for holdings objects.

        :return: A ConfigParser object.
        """
        conf = cp.ConfigParser()
        conf.read('holdings/portfolio_config.ini')

        logger.success('Info read from portfolio_config.ini file.')

        return conf

    def add_position(self,
                     position: Position):
        self.positions.append(position)

    def market_value(self) -> float:
        if self.positions:
            mv = 0
            for pos in self.positions:
                mv += pos.market_value
            self.market_value = mv
        else:
            return self.current_cash
