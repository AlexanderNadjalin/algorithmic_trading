import matplotlib.pyplot as plt
from matplotlib import cm
import seaborn as sns
import pandas as pd
import numpy as np
from loguru import logger
from backtest.backtest import Backtest


class Plot:
    """

    Plot object to visualize different metrics.
    Requires that Metric.calc_all() method has been run.
    """

    def __init__(self,
                 bt: Backtest):
        self.bt = bt
        self.records = bt.pf.records
        self.save_location = bt.config['output_files']['output_file_directory']

    def rolling_sharpe_beta_plot(self,
                                 save=False) -> None:
        """

        Dual plot with rolling Sharpe ratio above, and rolling beta below.
        :param save: True ito save to file.
        :return: None.
        """
        p1 = self.records.columns.get_loc('pf_sharpe_ratio')
        p2 = self.records.columns.get_loc('rolling_beta')

        fig, axes = plt.subplots(2, 1, figsize=(10, 7))
        ax1 = plt.subplot(211)
        ax2 = plt.subplot(212)

        self.bt.pf.records.iloc[:, p1].plot(lw=1, color='black', alpha=0.60, ax=ax1, label='Sharpe ratio')
        self.bt.pf.records.iloc[:, p2].plot(lw=1, color='green', alpha=0.60, ax=ax2, label='Beta')

        # Include strategy name in title
        title_sharpe = 'Rolling ' + str(self.bt.metric.config['rolling_sharpe_ratio']['period']) + ' days Sharpe ratio'
        title_beta = 'Rolling ' + str(self.bt.metric.config['rolling_beta']['period']) + ' days Beta'
        if self.bt.strategy.name == 'Periodic re-balancing':
            title_strat = 'Strategy: ' + self.bt.strategy.name + ' ' + self.bt.strategy.p
        else:
            title_strat = 'Strategy: ' + self.bt.strategy.name
        ax1.set_title(title_sharpe + '\n' + title_strat)

        ax1.set_xlabel('Date')
        self.plot_look(ax=ax1,
                       look_nr=1)

        ax2.set_title(title_beta)
        self.plot_look(ax=ax2,
                       look_nr=1)

        fig.tight_layout()
        plt.show()

        if save:
            self.save_plot(name=self.bt.pf.pf_id + 'rolling_sharpe_beta_plot.png',
                           fig=fig)

    def drawdowns_plot(self,
                       save=False) -> None:
        """

        Dual plot with cumulative portfolio returns and benchmark returns above, and drawdowns below.
        Includes portfolio and benchmark returns of ver backtest period, and maximum drawdown duration.
        :param save: True to save to file.
        :return: None
        """
        p1 = self.records.columns.get_loc('pf_cum_rets')
        p2 = self.bt.pf.records.columns.get_loc('bm_cum_rets')
        p3 = self.records.columns.get_loc('drawdown')

        title_dd = 'Drawdowns (maximum duration: ' + str(int(self.records['duration'].max())) + ' days)'

        fig, axes = plt.subplots(2, 1, figsize=(10, 7))
        ax1 = plt.subplot(211)
        ax2 = plt.subplot(212)

        self.bt.pf.records.iloc[:, p1].plot(lw=1, color='black', alpha=0.60, ax=ax1, label='Portfolio')
        self.bt.pf.records.iloc[:, p2].plot(lw=1, color='green', alpha=0.60, ax=ax1, label='Benchmark')
        self.bt.pf.records.iloc[:, p3].plot(lw=1, color='black', alpha=0.60, ax=ax2, label='Drawdowns')

        ax1.set_xlabel('Date')
        ax1.set_ylabel('%')
        pf_tot_rets = str(format(self.records['pf_cum_rets'].iloc[-1], ".2f"))
        bm_tot_rets = str(format(self.records['bm_cum_rets'].iloc[-1], ".2f"))

        # Include strategy name in title
        title_str = 'Cumulative returns (Portfolio: ' + pf_tot_rets + '%, Benchmark: ' + bm_tot_rets + '%)'
        if self.bt.strategy.name == 'Periodic re-balancing':
            title_strat = 'Strategy: ' + self.bt.strategy.name + ' ' + self.bt.strategy.p
        else:
            title_strat = 'Strategy: ' + self.bt.strategy.name
        ax1.set_title(title_str + '\n' + title_strat)

        self.plot_look(ax=ax1,
                       look_nr=1)

        ax2.set_xlabel('Date')
        ax2.set_ylabel('%')
        ax2.set_title(title_dd)
        self.plot_look(ax=ax2,
                       look_nr=1)

        fig.tight_layout()
        plt.show()

        if save:
            self.save_plot(name=self.bt.pf.pf_id + 'drawdown_plot.png',
                           fig=fig)

    @staticmethod
    def plot_look(ax: plt.subplots,
                  look_nr: int):
        if look_nr == 1:
            ax.minorticks_on()
            ax.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
            ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.4)
            ax.legend(loc='best', prop={'size': 8})
            plt.setp(ax.get_xticklabels(), visible=True, rotation=45, ha='center')

    def aggr_rets(self,
                  rets: pd.DataFrame,
                  period: str) -> np.array:
        """

        Convert daily returns to aggregated returns per given period - yearly, monthly and weekly.
        :param rets: Market data from Backtest.
        :param period:
        :return: Numpy array with converted returns.
        """
        def cumulate_rets(x):
            return np.exp(np.log(1 + x).cumsum())[-1] - 1

        if period == 'weekly':
            return rets.groupby(
                [lambda x: x.year,
                 lambda x: x.month,
                 lambda x: x.isocalendar()[1]]).apply(cumulate_rets)
        elif period == 'monthly':
            return rets.groupby(
                [lambda x: x.year, lambda x: x.month]).apply(cumulate_rets)
        elif period == 'yearly':
            return rets.groupby(
                [lambda x: x.year]).apply(cumulate_rets)
        else:
            logger.critical('Chosen aggregated period "' + period + '" is not implemented. Aborted.')
            quit()

    def returns_hm(self) -> plt.axis:
        """

        Calculate monthly returns as a Seaborn heatmap.
        Requires Metrics.calc_returns() to have been run.
        :return: Matplotlib axis.
        """
        # Get data from backtest results.
        df = self.bt.pf.records.copy()
        df['dt'] = pd.to_datetime(df.index,
                                  format='%Y-%m-%d')
        df.reset_index(inplace=True)
        df.set_index(keys='dt',
                     inplace=True)

        rets = df['pf_1d_pct_rets']
        ax = plt.gca()

        # Use help function for aggregation.
        monthly_rets = self.aggr_rets(rets=rets,
                                      period='monthly')
        monthly_rets = monthly_rets.unstack()
        monthly_rets = np.round(monthly_rets, 3)

        # Rename month names.
        monthly_rets.rename(
            columns={1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
                     5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
                     9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'},
            inplace=True
        )

        # Create Seaborn heatmap and set look.
        sns.heatmap(
            monthly_rets.fillna(0) * 100.0,
            annot=True,
            fmt="0.1f",
            annot_kws={"size": 8},
            alpha=1.0,
            center=0.0,
            cbar=False,
            cmap=cm.RdYlGn,
            ax=ax)
        ax.set_title('Monthly Returns (%)')
        ax.set_ylabel('')
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
        ax.set_xlabel('')

        return ax

    def save_plot(self,
                  name: str,
                  fig) -> None:
        file_name = self.save_location + '/' + name
        try:
            fig.savefig(file_name,
                        bbox_inches='tight')
            logger.success('Plot saved at: ' + file_name + '.')
        except FileNotFoundError:
            logger.warning('File destination incorrect. Check backtest_config.ini file. Plot not saved.')
