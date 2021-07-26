import pandas as pd
import numpy as np
from loguru import logger
import configparser as cp
from holdings.portfolio import Portfolio


class Metric:
    """

    Metric object.
    Calculates portfolio metrics for performance, risk, returns etc.
    """
    def __init__(self):
        self.config = self.config()

    @logger.catch
    def config(self) -> cp.ConfigParser:
        """

        Read metric_config file and return a config object. Used to set default parameters for metric calculations.
        :return: A ConfigParser object.
        """
        conf = cp.ConfigParser()
        conf.read('metric/metric_config.ini')

        logger.info('Info read from metric_config.ini file.')

        return conf

    @staticmethod
    def calc_returns(pf: Portfolio):
        """
        Add columns for returns of portfolio (pf) and benchmark (bm).
        :param pf: Portfolio for which to calculate returns.
        :return: None.
        """
        pf.records = pf.history.copy()
        pf.records['pf_1d_pct_rets'] = pf.records['total_market_value'].pct_change()
        col_idx = pf.records.columns.get_loc('pf_1d_pct_rets')
        pf.records.iloc[0, col_idx] = pf.records['total_market_value'].iloc[0] / pf.init_cash - 1
        pf.records['pf_cum_rets'] = np.cumprod(1 + pf.records['pf_1d_pct_rets']) - 1
        pf.records.loc[:, 'pf_cum_rets'] *= 100

        # If benchmark exists
        if pf.benchmark == '':
            pass
        else:
            pf.records['bm_1d_pct_rets'] = pf.records['benchmark_value'].pct_change()
            col_idx = pf.records.columns.get_loc('bm_1d_pct_rets')
            pf.records.iloc[0, col_idx] = 0
            pf.records['bm_cum_rets'] = np.cumprod(1 + pf.records['bm_1d_pct_rets']) - 1
            pf.records.loc[:, 'bm_cum_rets'] *= 100
        pf.records.set_index('current_date', inplace=True)
        pf.records.fillna(0, inplace=True)
        logger.info('Metrics calculated for returns.')

    @staticmethod
    def create_drawdowns(pf: Portfolio):
        """

        Calculates maximum drawdown and maximum drawdown duration.
        Maximum drawdown is the largest peak-to-trough drop.
        Maximum drawdown duration is defined as the number of periods over which the maximum drawdown occurs.
        :param pf: Portfolio object.
        :return: None.
        """
        high_water_mark = [0]
        equity_curve = pf.records['total_market_value']
        eq_idx = pf.records.index
        drawdown = pd.Series(index=eq_idx)
        duration = pd.Series(index=eq_idx)

        for t in range(1, len(eq_idx)):
            cur_hwm = max(high_water_mark[t - 1], equity_curve[t])
            high_water_mark.append(cur_hwm)
            drawdown[t] = (equity_curve[t] / high_water_mark[t] - 1) * 100
            duration[t] = 0 if drawdown[t] == 0 else duration[t - 1] + 1
        pf.records['drawdown'] = drawdown
        pf.records['duration'] = duration
        pf.records['drawdown'].fillna(0, inplace=True)
        pf.records['duration'].fillna(0, inplace=True)
        logger.info('Metrics calculated for drawdowns.')

    def create_rolling_sharpe_ratio(self,
                                    pf: Portfolio) -> None:
        """
        Calculates the 6m Sharpe ratio for the strategy and the benchmark.
        :param pf: Portfolio object.
        :return: None.
        """
        period = int(self.config['rolling_sharpe_ratio']['period'])
        if len(pf.records.index) < period:
            data_len = len(pf.records.index)
            logger.warning('Chosen backtesting period has ' + str(data_len) +
                           ' data points. Rolling Sharpe ratio needs ' + str(period) +
                           ' data points. Adjust backtesting dates or period parameter in backtest_config.ini')
        else:
            # equity TimeSeries only
            eq_rets = pf.records['pf_1d_pct_rets']
            eq_rolling = eq_rets.rolling(window=period)
            eq_rolling_sharpe = np.sqrt(period) * eq_rolling.mean() / eq_rolling.std()
            eq_rolling_sharpe.fillna(0, inplace=True)
            pf.records['pf_sharpe_ratio'] = eq_rolling_sharpe

            # benchmark TimeSeries included
            if pf.benchmark != '':
                bm_rets = pf.records['bm_1d_pct_rets']
                bm_rolling = bm_rets.rolling(window=period)
                bm_rolling_sharpe = np.sqrt(period) * bm_rolling.mean() / bm_rolling.std()
                bm_rolling_sharpe.fillna(0, inplace=True)
                pf.records['bm_sharpe_ratio'] = bm_rolling_sharpe
                logger.info('Metrics calculated for rolling Sharpe ratio.')
            else:
                logger.warning('No benchmark selected for portfolio ' + pf.pf_id +
                               '. Rolling Sharpe ratio not calculated.')

            pf.records.fillna(0, inplace=True)

    def create_rolling_beta(self,
                            pf: Portfolio) -> None:
        """

        Rolling beta.
        :param pf: Portfolio object.
        :return: None.
        """
        period = int(self.config['rolling_beta']['period'])
        if len(pf.records.index) < period:
            data_len = len(pf.records.index)
            logger.warning('Chosen backtesting period has ' + str(data_len) +
                           ' data points. Rolling beta needs ' + str(period) +
                           ' data points. Adjust backtesting dates or period parameter in backtest_config.ini')
        else:
            if pf.benchmark != '':
                pf_idx = pf.records.columns.get_loc('pf_1d_pct_rets')
                bm_idx = pf.records.columns.get_loc('bm_1d_pct_rets')
                pf_ = pf.records.iloc[:, pf_idx]
                bm_ = pf.records.iloc[:, bm_idx]
                roll_pf = pf_.rolling(window=period)
                roll_bm = bm_.rolling(window=period)
                roll_var = roll_pf.var()
                roll_cov = roll_pf.cov(roll_bm)

                # Periods longer than "period" of no variance makes for division by zero. Floor to low non-zero value.
                roll_var = roll_var.apply(lambda x: x if x > 1.e-05 else 0.00001)
                rolling_beta = roll_cov / roll_var
                rolling_beta.dropna(inplace=True)
                pf.records['rolling_beta'] = rolling_beta

                pf.records.fillna(0, inplace=True)

                logger.info('Metrics calculated for rolling beta.')
            else:
                logger.warning('No benchmark selected for portfolio ' + pf.pf_id + '. Rolling beta not calculated.')

    def calc_all(self,
                 pf: Portfolio) -> None:
        """

        Calculate all metrics.
        :param pf: Portfolio object.
        :return: None.
        """
        self.calc_returns(pf=pf)
        self.create_drawdowns(pf=pf)
        self.create_rolling_sharpe_ratio(pf=pf)
        self.create_rolling_beta(pf=pf)
