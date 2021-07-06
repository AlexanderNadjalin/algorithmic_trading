from loguru import logger
import pandas as pd


class Portfolio:
    def __init__(self,
                 init_cash: float,
                 benchmark: str):
        self.init_cash = init_cash
        self.current_cash = self.init_cash
        self.positions = []
        self.benchmark = benchmark
        self.market_value = self.init_cash
        self.history = pd.DataFrame()
        logger.info('Portfolio created.')


class Position:
    def __init__(self,
                 name: str,
                 quantity: float,
                 entry_price: float,
                 date: str):
        self.name = name
        self.quantity = quantity
        self.entry_price = entry_price
        self.date = date
        logger.info('Position ' + str(quantity) + '@ ' + str(self.entry_price) + ' ' + self.name + ' created.')
