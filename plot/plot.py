import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import gridspec
from matplotlib.ticker import FuncFormatter
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
                                 save=False) -> plt.figure():
        """

        Dual plot with rolling Sharpe ratio above, and rolling beta below.
        :param save: True ito save to file.
        :return: Matplotlib figure.
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

        if save:
            self.save_plot(name=self.bt.pf.pf_id + '_rolling_sharpe_beta.png',
                           fig=fig)
        plt.show()

    def drawdowns_plot(self,
                       save=False) -> plt.figure():
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

        pf_cum_rets_pct = self.bt.pf.records.iloc[:, p1] * 100
        bm_cum_rets_pct = self.bt.pf.records.iloc[:, p2] * 100
        dd_pct = self.bt.pf.records.iloc[:, p3]

        pf_cum_rets_pct.plot(lw=1, color='black', alpha=0.60, ax=ax1, label='Portfolio')
        bm_cum_rets_pct.plot(lw=1, color='green', alpha=0.60, ax=ax1, label='Benchmark')
        dd_pct.plot(lw=1, color='black', alpha=0.60, ax=ax2, label='Drawdowns')

        ax1.set_xlabel('Date')
        ax1.set_ylabel('%')
        pf_tot_rets = str(format(pf_cum_rets_pct.iloc[-1], ".2f"))
        bm_tot_rets = str(format(bm_cum_rets_pct.iloc[-1], ".2f"))

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

        if save:
            self.save_plot(name=self.bt.pf.pf_id + '_drawdowns.png',
                           fig=fig)
        plt.show()

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
                 lambda x: x.isocalendar()[1]]).apply(cumulate_rets) * 100
        elif period == 'monthly':
            return rets.groupby(
                [lambda x: x.year, lambda x: x.month]).apply(cumulate_rets) * 100
        elif period == 'yearly':
            return rets.groupby(
                [lambda x: x.year]).apply(cumulate_rets) * 100
        else:
            logger.critical('Chosen aggregated period "' + period + '" is not implemented. Aborted.')
            quit()

    def returns_hm(self,
                   ax: plt.axes,
                   period: str) -> plt.axis:
        """

        Calculate period returns as a Seaborn heatmap.
        Requires Metrics.calc_returns() to have been run.
        :param period: "yearly", "monthly" or "weekly".
        :param ax: Matplotlib axes object to plot on.
        :return: Matplotlib axes.
        """
        # Get data from backtest results.
        df = self.bt.pf.records.copy()
        df['dt'] = pd.to_datetime(df.index,
                                  format='%Y-%m-%d')
        df.reset_index(inplace=True)
        df.set_index(keys='dt',
                     inplace=True)

        rets = df['pf_1d_pct_rets']
        if ax is None:
            ax = plt.gca()

        # Use help function for aggregation.
        aggr_rets = self.aggr_rets(rets=rets,
                                   period=period)

        aggr_rets = np.round(aggr_rets, 3)
        frame = pd.DataFrame(aggr_rets) * 100

        # Rename column names.
        if period == 'monthly':
            frame = aggr_rets.unstack()
            frame.rename(
                columns={1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
                         5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
                         9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'},
                inplace=True
            )
            sns.heatmap(
                frame,
                fmt="0.1f",
                annot=True,
                annot_kws={"size": 4},
                alpha=1.0,
                center=0.0,
                cbar=False,
                cmap=cm.RdYlGn,
                square=True,
                linewidths=1,
                ax=ax)

        else:
            anotate_str = True
            x_ticks_str = False
            if period == 'weekly':
                frame = aggr_rets.unstack()
                anotate_str = False
                x_ticks_str = True
            sns.heatmap(
                frame,
                fmt="0.1f",
                annot=anotate_str,
                xticklabels=x_ticks_str,
                annot_kws={"size": 6},
                alpha=1.0,
                center=0.0,
                cbar=False,
                cmap=cm.RdYlGn,
                square=True,
                linewidths=1,
                ax=ax)

        rot = 0
        if period == 'yearly':
            title_str = 'Yearly returns (%)'
            y_lbl_str = 'Year'
            x_lbl_str = ''

        elif period == 'monthly':
            title_str = 'Monthly returns (%)'
            x_lbl_str = 'Month'
            y_lbl_str = 'Year'
        else:
            title_str = 'Weekly returns (%)'
            x_lbl_str = 'Week'
            y_lbl_str = 'Year'
            rot = 90
        ax.set_title(title_str)
        ax.set_ylabel(y_lbl_str,
                      fontsize=8)
        ax.set_xlabel(xlabel=x_lbl_str,
                      fontsize=8)
        ax.set_yticklabels(ax.get_yticklabels(),
                           rotation=0,
                           fontsize=6)
        ax.set_xticklabels(ax.get_xticklabels(),
                           rotation=rot,
                           fontsize=6)

        return ax

    def create_tear_sheet(self,
                          save=False):
        fig = plt.figure()
        gs = gridspec.GridSpec(2, 2)
        ax_yearly = plt.subplot(gs[0, 0])
        ax_monthly = plt.subplot(gs[0, 1])
        ax_weekly = plt.subplot(gs[1, :])
        self.returns_hm(ax=ax_yearly,
                        period='yearly')
        self.returns_hm(ax=ax_monthly,
                        period='monthly')
        self.returns_hm(ax=ax_weekly,
                        period='weekly')

        fig.suptitle('Period returns and metrics', fontsize=16)
        fig.tight_layout()

        if save:
            self.save_plot(name=self.bt.pf.pf_id + '_tear_sheet.png',
                           fig=fig)

        plt.show()

    def plot_text(self,
                  save=False):
        def format_perc(x, pos):
            return '%.0f%%' % x

        ax = plt.gca()

        ax.text(2,
                11,
                self.bt.strategy.name,
                fontweight='bold',
                horizontalalignment='right',
                fontsize=8,
                color='green')

        ax.grid(False)
        ax.spines['top'].set_linewidth(2.0)
        ax.spines['bottom'].set_linewidth(2.0)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().set_visible(False)
        ax.set_ylabel('')
        ax.set_xlabel('')

        ax.axis([0, 10, 0, 10])

        if save:
            self.save_plot(name=self.bt.pf.pf_id + '_tear_sheet.png',
                           fig=ax)
        plt.show()

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
