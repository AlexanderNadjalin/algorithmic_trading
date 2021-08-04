import matplotlib.pyplot as plt
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
