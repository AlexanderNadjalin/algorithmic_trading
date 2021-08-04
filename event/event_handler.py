import queue
from loguru import logger
from backtest.backtest import Backtest


class EventHandler:
    def __init__(self,
                 bt: Backtest,
                 verbose=False):
        self.event_queue = queue.Queue()
        self.bt = bt
        self.verbose = verbose

    def put_event(self,
                  event):
        self.event_queue.put(event)

    def get_event(self):
        return self.event_queue.get()

    def is_empty(self):
        return self.event_queue.empty()

    def handle_event(self):
        e = self.get_event()
        if e.type == 'MARKET':
            self.bt.pf.update_all_market_values(date=e.date,
                                                market_data=self.bt.market)
            if self.verbose:
                logger.info(e.details)

        if e.type == 'CALCSIGNAL':
            df = self.bt.market.select(columns=self.bt.pf.symbols,
                                       start_date=e.date,
                                       end_date=e.date)

        if self.verbose:
            logger.info(e.details)

        elif e.type == 'TRANSACTION':
            self.bt.pf.transact_security(trans=e.trans)
            if self.verbose:
                logger.info(e.details)
