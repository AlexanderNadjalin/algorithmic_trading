from loguru import logger
from event import event, event_handler
from market.market import Market
from holdings.portfolio import Portfolio
from event.event_handler import EventHandler


class Backtest:
    def __init__(self,
                 eh: EventHandler,
                 market: Market,
                 pf: Portfolio,
                 start_date: str,
                 end_date: str,
                 verbose=False):
        self.event_handler = event_handler.EventHandler(market=market,
                                                        pf=pf)
        self.cont_backtest = True
        self.eh = eh
        self.market = market
        self.pf = pf

        self.start_date = start_date
        self.start_index = self.market.data.index.get_loc(self.start_date)
        self.end_date = end_date
        self.end_index = self.market.data.index.get_loc(self.end_date)

        self.current_date = self.start_date
        self.current_index = self.start_index

        self.validate_date(date=self.start_date)
        self.validate_date(date=self.end_date)

    def validate_date(self,
                      date: str) -> bool:
        """

        Check if given date exists in market data.
        :param date: Start or end date.
        :return: True/False.
        """
        if date in self.market.data.index.values:
            return True
        else:
            logger.critical('Date ' + date + ' does not exist in market data files. Aborted.')
            quit()

    def run(self) -> None:
        logger.info('Backtest running from ' + self.start_date + ' to ' + self.end_date + '.')

        # Infinite outer loop for handling each date in backtest period
        while True:
            if self.cont_backtest:

                # Infinite inner loop for handling events
                while not self.eh.is_empty():
                    self.eh.handle_event()

                e = event.Market(date=self.current_date)
                self.eh.put_event(e)
                self.eh.handle_event()

                self.current_index += 1
                if self.current_index > self.end_index:
                    self.cont_backtest = False
                    logger.success('Backtest completed.')
                else:
                    self.current_date = self.market.data.iloc[self.current_index, :].to_frame().transpose().index.values[0]
            else:
                break
