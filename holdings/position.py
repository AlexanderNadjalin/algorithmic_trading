import pandas as pd
import numpy as np
from loguru import logger
from holdings.transaction import Transaction


class Position:
    """

    Position object. Is created by transaction.py objects.
    All transactions are separated into buy or sell to facilitate accounting.
    Short selling is supported.
    A Position "knows" its full history for all its transactions.

    Credit to Michael Halls-Moore @ QuantStart.com:
        https://github.com/mhallsmoore/qstrader/blob/master/qstrader/broker/portfolio/position.py
        I had trouble getting all the details correct and qstrader is a great source of knowledge for this.
        Thank you!
        Copyright (c) 2015-2021 QuantStart.com, QuarkGluon Ltd
    """
    def __init__(self):
        self.name = ''
        self.current_date = ''
        self.current_price = 0.0
        self.sell_quantity = 0.0
        self.avg_sold = 0.0
        self.sell_commission = 0.0
        self.buy_quantity = 0.0
        self.avg_bought = 0.0
        self.buy_commission = 0.0

        self.transaction_history = pd.DataFrame()
        self.create_history_table()

    def create_history_table(self) -> None:
        """

        Create pd.Dataframe to hold all transactions making up the Position.
        :return: None.
        """
        self.transaction_history = pd.DataFrame(columns=['current_date',
                                                         'current_price',
                                                         'buy_quantity',
                                                         'sell_quantity',
                                                         'net_quantity',
                                                         'avg_bought',
                                                         'avg_sold',
                                                         'avg_price',
                                                         'buy_commission',
                                                         'sell_commission',
                                                         'total_commission',
                                                         'realized_pnl',
                                                         'unrealized_pnl',
                                                         'total_pnl'])

    def add_history(self) -> None:
        """

        Add current transaction details to Position history.
        :return: None.
        """
        new_trans = {'current_date': self.current_date,
                     'current_price': self.current_price,
                     'buy_quantity': self.buy_quantity,
                     'sell_quantity': self.sell_quantity,
                     'net_quantity': self.net_quantity,
                     'avg_bought': self.avg_bought,
                     'avg_sold': self.avg_sold,
                     'avg_price': self.avg_price,
                     'buy_commission': self.buy_commission,
                     'sell_commission': self.sell_commission,
                     'total_commission': self.total_commission,
                     'realized_pnl': self.realized_pnl,
                     'unrealized_pnl': self.unrealized_pnl,
                     'total_pnl': self.total_pnl}

        self.transaction_history = self.transaction_history.append(new_trans,
                                                                   ignore_index=True)

    def transact(self,
                 trans: Transaction,
                 verbose=False) -> None:
        """

        Transacts the position with accounting.
        :param trans: Transaction object.
        :param verbose: If True, prints details of transaction.
        :return: None.
        """
        if trans.direction == 'B':
            self.transact_buy(quantity=trans.quantity,
                              price=trans.price,
                              commission=trans.commission)

        else:
            self.transact_sell(quantity=trans.quantity,
                               price=trans.price,
                               commission=trans.commission)

        self.update_current_market_price(trans.price,
                                         trans.date)
        self.add_history()

        if verbose:
            logger.info('Transaction: ' + trans.direction + ' ' + str(trans.quantity) + ' ' + trans.name + ' '
                        + ' @' + str(trans.price) + '.')

    def update_current_market_price(self,
                                    market_price: float,
                                    date: str) -> None:
        """

        Updates current market price and current date.
        :param market_price: New market price from market.py.
        :param date: Corresponding date for market_price.
        :return: None.
        """
        if market_price <= 0.0:
            logger.critical('Market price "%s" of asset "%s" must be positive to '
                            'update the position. Aborted.' % (market_price, self.name))
            quit()
        else:
            self.current_price = market_price
            self.current_date = date

    def transact_buy(self,
                     quantity: float,
                     price: float,
                     commission: float) -> None:
        """

        Accounting for a long position.
        :param quantity: Quantity bought.
        :param price: Price.
        :param commission: Commission.
        :return: None.
        """
        self.avg_bought = ((self.avg_bought * self.buy_quantity) + (quantity * price)) / (self.buy_quantity + quantity)
        self.buy_quantity += quantity
        self.buy_commission += commission

    def transact_sell(self,
                      quantity: float,
                      price: float,
                      commission: float) -> None:
        """

        Accounting for a short position.
        :param quantity: Quantity sold.
        :param price: Price.
        :param commission: Commission.
        :return: None.
        """
        self.avg_sold = ((self.avg_sold * self.sell_quantity) + (quantity * price)) / (self.sell_quantity + quantity)
        self.sell_quantity += quantity
        self.sell_commission += commission

    @property
    def direction(self) -> int:
        """

        Determine direction of transaction.
        :return: Returns 1 for buy transaction, -1 for sell transaction.
        """
        if self.net_quantity == 0:
            return 0
        else:
            return np.copysign(1, self.net_quantity)

    @property
    def market_value(self) -> float:
        """

        Calculate current market value.
        :return: Current market value.
        """
        return self.net_quantity * self.current_price

    @property
    def avg_price(self) -> float:
        """

        Calculate the average price for all long and short transactions.
        :return: Average price.
        """
        if self.net_quantity == 0.0:
            return 0.0
        elif self.net_quantity >= 0.0:
            return (self.avg_bought * self.buy_quantity + self.buy_commission) / self.buy_quantity
        else:
            return (self.avg_sold * self.sell_quantity - self.sell_commission) / self.sell_quantity

    @property
    def net_quantity(self) -> float:
        """

        Calculate net quantity.
        :return: Net quantity.
        """
        return self.buy_quantity - self.sell_quantity

    @property
    def total_bought(self) -> float:
        """

        Calculate the total average cost of buy transactions.
        :return:Total average cost for buys.
        """
        return self.avg_bought * self.buy_quantity

    @property
    def total_sold(self) -> float:
        """

        Calculate the total average cost of sell transactions.
        :return:Total average cost for sells.
        """
        return self.avg_sold * self.sell_quantity

    @property
    def total_net(self) -> float:
        """

        Calculate the total average cost of all transactions.
        :return:Total average cost.
        """
        return self.total_sold - self.total_bought

    @property
    def total_commission(self) -> float:
        """

        Calculate total commission for all transactions.
        :return: Total commission.
        """
        return self.buy_commission + self.sell_commission

    @property
    def net_incl_commission(self) -> float:
        """

        Calculate the total average cost of all transactions including commission.
        :return:
        """
        return self.total_net - self.total_commission

    @property
    def realized_pnl(self) -> float:
        """

        Calculate the profit-and-loss (pnl) for two opposing transaction in the position.
        :return: Realized pnl.
        """
        # Buys.
        if self.direction == 1:
            if self.sell_quantity == 0:
                return 0.0
            else:
                return (
                    ((self.avg_sold - self.avg_bought) * self.sell_quantity) -
                    ((self.sell_quantity / self.buy_quantity) * self.buy_commission) -
                    self.sell_commission
                )
        # Sells.
        elif self.direction == -1:
            if self.buy_quantity == 0:
                return 0.0
            else:
                return (
                    ((self.avg_sold - self.avg_bought) * self.buy_quantity) -
                    ((self.buy_quantity / self.sell_quantity) * self.sell_commission) -
                    self.buy_commission
                )
        else:
            return self.net_incl_commission

    @property
    def unrealized_pnl(self) -> float:
        """

        Calculate the profit-and-loss (pnl) for the remaining non-zero quantity for the current market price.
        :return: Unrealized pnl.
        """
        return (self.current_price - self.avg_price) * self.net_quantity

    @property
    def total_pnl(self) -> float:
        """

        Calculate the sum of realized and unrealized pnl.
        :return: Total net pnl.
        """
        return self.realized_pnl + self.unrealized_pnl
