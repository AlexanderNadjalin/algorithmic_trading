from holdings.position import Position
from collections import OrderedDict
from holdings.transaction import Transaction


class PositionHandler:
    """

    Helper class to handle position operations in a Portfolio object.
    """
    def __init__(self):
        self.positions = OrderedDict()

    def transact_position(self,
                          trans: Transaction) -> None:
        """

        Execute transaction and update position.
        :param trans: Transaction.
        :return: None.
        """
        security = trans.name
        if security in self.positions:
            self.positions[security].transact_position(trans)
        else:
            position = Position()
            position.transact_position(trans)
            self.positions[security] = position

        if self.positions[security].net_quantity == 0:
            del self.positions[security]

    def total_market_value(self) -> float:
        """

        Calculate total market value for all positions.
        :return: Market value.
        """
        return sum(pos.market_value for asset, pos in self.positions.items())

    def total_unrealized_pnl(self) -> float:
        """

        Calculate total unrealized PnL for all positions.
        :return: Unrealized PnL.
        """
        return sum(pos.unrealized_pnl for asset, pos in self.positions.items())

    def total_realized_pnl(self) -> float:
        """

        Calculate total realized PnL for all positions.
        :return: Realized PnL.
        """
        return sum(pos.realized_pnl for asset, pos in self.positions.items())

    def total_pnl(self) -> float:
        """

        Calculate total PnL for all positions.
        :return: PnL.
        """
        return sum(pos.total_pnl for asset, pos in self.positions.items())
