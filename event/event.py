from holdings import transaction


class Event:
    """

    Base class for events.
    """
    pass


class Market(Event):
    """

    Market event indicates that a new day has passed and there is new market data.
    """
    def __init__(self,
                 date: str):
        self.type = 'MARKET'
        self.date = date

    @property
    def details(self) -> str:
        """

        Details for verbose logging.
        :return: String for logging.
        """
        return 'Market event [date: %s]' % self.date


class Transaction(Event):
    """

    Transaction event for a position in a portfolio.
    """
    def __init__(self,
                 date: str,
                 trans: transaction.Transaction):
        self.type = 'TRANSACTION'
        self.date = date
        self.trans = trans

    @property
    def details(self) -> str:
        """

        Details for verbose logging.
        :return: String for logging.
        """
        return 'Transaction event [date: %s, direction: %s, name: %s, quantity: %s, price: %s]' % (
            self.date, self.trans.direction, self.trans.name, self.trans.quantity, self.trans.price
        )
