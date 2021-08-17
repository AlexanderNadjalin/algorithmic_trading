import abc
import pandas as pd
from loguru import logger
from holdings.portfolio import Portfolio, Transaction as t
from event.event import Transaction


class Strategy(metaclass=abc.ABCMeta):
    """

    Abstract base class including an event and the date index for which to calculate a signal.
    """
    @abc.abstractmethod
    def calc_signal(self,
                    events,
                    data,
                    idx: str,
                    pf: Portfolio):
        pass

    @abc.abstractmethod
    def description(self):
        pass


class PeriodicRebalancing(Strategy):
    """

    Re-balance the portfolio on either:
    * end-of-month (eom)
    * start-of-month (som)
    * end-of-week (eow)
    * start-of-week (sow)
    Last business day counts as last day of month.
    """
    def __init__(self,
                 period: str,
                 id_weight: dict):
        """

        Set parameters for
        :param period: Either: end-of-month (eom), start-of-month (som), end-of-week (eow) or
        start-of-week (sow).
        :param id_weight: Dictionary with {position name: weight}. Weight between 0 ans 1.0.
        """
        self.pf = None
        if period in ['som', 'eom', 'sow', 'eow']:
            if period == 'sow':
                p = 'start-of-week'
            elif period == 'eow':
                p = 'end-of-week'
            elif period == 'som':
                p = 'start-of-month'
            else:
                p = 'end-of-month'
            self.name = 'Periodic re-balancing'
            self.p = p
            self.period = period
            self.id_weight = id_weight

            for key, item in self.id_weight.items():
                if item < 0 or item > 1.0:
                    logger.critical('Weight for ' + key + ' is ' + str(item) + '. Should be between 0 and 1.0. '
                                                                               'Aborted.')
                    quit()
        else:
            logger.critical('PeriodicRebalancing strategy given parameter period = "'
                            + period + '". Should be either "som", "eom", "sow" or "eow". Aborted.')
            quit()

    def calc_signal(self,
                    events,
                    data: pd.DataFrame,
                    idx: str,
                    pf: Portfolio) -> None:
        """

        Calculate if we need to buy more or sell to match target weight.
        :param events: Event queue.
        :param data: Market data from Backtest.
        :param idx: Index from date in Backtest.
        :param pf: Portfolio from Backtest.
        :return: None.
        """
        self.pf = pf
        for key, item in self.id_weight.items():
            positions = self.pf.position_handler.positions
            # No positions in portfolio. Buy to match target weight.
            if not list(positions.items()):
                price = data[key].iloc[0]
                date = pf.current_date
                quantity = int(item * self.pf.total_market_value / price)
                trans = t(name=key,
                          direction='B',
                          quantity=quantity,
                          price=price,
                          commission_scheme=self.pf.commission,
                          date=date)
                trans_ev = Transaction(date=pf.current_date,
                                       trans=trans)
                events.put(item=trans_ev)
            # Existing positions. Buy or sell to match target weight.
            else:
                pos_mv = pf.position_handler.positions[key].market_value
                pf_mv = pf.total_market_value
                pos_weight = pos_mv / pf_mv
                diff = pos_weight - item

                price = data[key].iloc[0]
                date = pf.current_date

                quantity = int(diff * pf_mv / price)

                if quantity > 0:
                    # Sell excess weight.
                    trans = t(name=key,
                              direction='S',
                              quantity=quantity,
                              price=price,
                              commission_scheme=self.pf.commission,
                              date=date)
                else:
                    # Buy the difference in weight.
                    trans = t(name=key,
                              direction='B',
                              quantity=quantity * -1,
                              price=price,
                              commission_scheme=self.pf.commission,
                              date=date)
                trans_ev = Transaction(date=pf.current_date,
                                       trans=trans)
                events.put(item=trans_ev)

    def description(self) -> str:
        """

        Get {position name: weight} as string with line break in between.
        :return: String.
        """
        p = ''
        if self.period in ['som', 'eom', 'sow', 'eow']:
            if self.period == 'sow':
                p = 'start-of-week'
            elif self.period == 'eow':
                p = 'end-of-week'
            elif self.period == 'som':
                p = 'start-of-month'
            else:
                p = 'end-of-month'
        desc_str = 'Periodic re-balancing at ' + p + ':' + '\n\n'
        for key, item in self.id_weight.items():
            desc_str = desc_str + key + ': ' + str(100 * float(item)) + ' %' + '\n\n'
        return desc_str
