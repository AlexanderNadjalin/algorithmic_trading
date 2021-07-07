from loguru import logger
from portfolio.transaction import Transaction


class Position:
    def __init__(self,
                 trans: Transaction):
        self.name = ''
        self.quantity = 0
        self.wap = 0
        self.total_commission = trans.commission
        self.transaction_history = []
        self.transact_position(trans)

        logger.info('Transaction: ' + trans.direction + ' ' + trans.name + '' + str(trans.quantity) + ' @' + str(
            trans.price) + ' created.')

    def add_history(self,
                    trans: Transaction):
        self.transaction_history.append(trans)

    def transact_position(self,
                          trans: Transaction):
        self.add_history(trans)
        self.name = trans.name
        self.calc_wap()

        if trans.direction == 'B':
            self.quantity += trans.quantity
        else:
            self.quantity -= trans.quantity

        logger.info('Transaction: ' + trans.direction + ' ' + trans.name + '' + str(trans.quantity) + ' @' + str(trans.price) + ' created.')

    def calc_wap(self):
        # Weighted average price
        cost = 0
        quantity = 0
        for t in self.transaction_history:
            cost += t.price * t.quantity
            quantity += t.quantity
        self.wap = cost/quantity
