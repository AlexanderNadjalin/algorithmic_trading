import queue
from loguru import logger
import configparser as cp
from event import event
from market.market import Market
from holdings.portfolio import Portfolio
from strategy.strategy import Strategy
from metric.metric import Metric


class Backtest:
    """

    Main backtest class. Holds a Portfolio, Market and Metric object.
    """
    def __init__(self,
                 market: Market,
                 pf: Portfolio,
                 start_date: str,
                 end_date: str,
                 verbose=False):
        self.config = self.config()

        self.events = queue.Queue()
        self.event = None

        self.cont_backtest = True
        self.market = market
        self.pf = pf

        self.verbose = verbose
        self.metric = Metric()
        self.strategy = None

        self.start_date = start_date
        self.end_date = end_date
        self.validate_date(date=self.start_date)
        self.validate_date(date=self.end_date)
        self.start_index = self.market.data.index.get_loc(self.start_date)

        self.end_index = self.market.data.index.get_loc(self.end_date)

        self.current_date = self.start_date
        self.current_index = self.start_index

        # self.pf.update_all_market_values(date=self.current_date,
        #                                  market_data=self.market)

    @logger.catch
    def config(self) -> cp.ConfigParser:
        """

        Read backtest_config file and return a config object. Used to set default parameters for backtesting objects.

        :return: A ConfigParser object.
        """
        conf = cp.ConfigParser()
        conf.read('backtest/backtest_config.ini')

        logger.info('Info read from backtest_config.ini file.')

        return conf

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

    def add_strategy(self,
                     strategy=Strategy) -> None:
        """

        Add a strategy to a backest.
        Strategies require information about Market and Portfolio and can't be initialized before the backest.
        :param strategy: Strategy object.
        :return: None.
        """
        self.strategy = strategy

    def run(self) -> None:
        """

        Runs the backtest as an infinite outer loop for handling dates, and an inner loop for handling events.
        :return: None.
        """
        logger.info('Backtest running from ' + self.start_date + ' to ' + self.end_date + '.')

        # Infinite outer loop for handling each date in backtest period
        while True:
            if self.cont_backtest:
                market_ev = event.Market(date=self.current_date)
                self.events.put(item=market_ev)

                # Infinite inner loop for handling events
                while True:
                    try:
                        # Get event from queue.
                        self.event = self.events.get(False)
                    except queue.Empty:
                        # Break inner loop if no events in queue
                        break

                    if self.event.type == 'MARKET':
                        self.pf.update_all_market_values(date=self.event.date,
                                                         market_data=self.market)
                        self.events.task_done()

                        if self.strategy is not None:
                            calc_signal_ev = event.CalcSignal(date=self.current_date)
                            self.events.put(item=calc_signal_ev)

                        if self.verbose:
                            logger.info(self.event.details)

                    if self.event.type == 'CALCSIGNAL':
                        # Different strategies require different ways to handle calculation of signals.
                        if self.strategy.name == 'Periodic re-balancing':
                            # Get market data for specific date.
                            cols = list(self.strategy.id_weight.keys())
                            df = self.market.select(columns=cols,
                                                    start_date=self.event.date,
                                                    end_date=self.event.date)
                            # Start-of-month re-balance.
                            if df['is_som'].iloc[0] == 1 and self.strategy.period == 'som':
                                self.strategy.calc_signal(events=self.events,
                                                          data=df,
                                                          idx=self.current_index,
                                                          pf=self.pf)
                            # End-of-month re-balance.
                            elif df['is_eom'].iloc[0] == 1 and self.strategy.period == 'eom':
                                self.strategy.calc_signal(events=self.events,
                                                          data=df,
                                                          idx=self.current_index,
                                                          pf=self.pf)
                            # Start-of-week re-balance.
                            elif df['is_sow'].iloc[0] == 1 and self.strategy.period == 'sow':
                                self.strategy.calc_signal(events=self.events,
                                                          data=df,
                                                          idx=self.current_index,
                                                          pf=self.pf)
                            # End-of-week re-balance.
                            elif df['is_eow'].iloc[0] == 1 and self.strategy.period == 'eow':
                                self.strategy.calc_signal(events=self.events,
                                                          data=df,
                                                          idx=self.current_index,
                                                          pf=self.pf)
                        else:
                            pass

                        if self.verbose:
                            logger.info(self.event.details)

                        self.events.task_done()

                    if self.event.type == 'TRANSACTION':
                        self.pf.transact_security(trans=self.event.trans)
                        if self.verbose:
                            logger.info(self.event.details)

                        self.events.task_done()

                self.current_index += 1

                # End backtest when end_date is reached.
                if self.current_index > self.end_index:
                    # Calculate metrics.
                    self.metric.calc_all(self.pf)

                    self.cont_backtest = False

                    self.metric.calc_all(pf=self.pf)

                    logger.success('Backtest completed.')
                else:
                    self.current_date = \
                        self.market.data.iloc[self.current_index, :].to_frame().transpose().index.values[0]
            else:
                break
