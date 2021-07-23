import matplotlib.pyplot as plt
import pandas as pd
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

    def returns_plot(self,
                     x_labels: list,
                     y_labels: list,
                     titles: list,
                     save=False) -> None:
        """

        Single plot for maximum two time series.
        :param x_labels: X-axis label name(s).
        :param y_labels: Y-axis label name(s).
        :param titles: Title for plot.
        :param save: True to save to file.
        :return: None.
        """
        fig, ax = plt.subplots(figsize=(10, 7))

        self.records.iloc[:, self.cols[0]].plot(lw=1,
                                                color='black',
                                                alpha=0.60,
                                                ax=ax,
                                                label=titles[0])
        if self.cols[1]:
            self.records.iloc[:, self.cols[1]].plot(lw=1,
                                                    color='green',
                                                    alpha=0.60,
                                                    ax=ax,
                                                    label=titles[1])

        ax.set_ylabel(y_labels[0])
        ax.set_xlabel(x_labels[0])
        ax.set_title(titles[0])

        self.plot_look(ax=ax,
                       look_nr=1)

        fig.tight_layout()
        plt.show()

        if save:
            self.save_plot(name=self.bt.pf.pf_id + '_returns.png',
                           fig=fig)

    def drawdowns_plot(self,
                       save=False) -> None:
        """

        Dual plot with cumulative portfolio returns and benchmark returns above, and drawdowns below.
        :param save: True to save to file.
        :return: None
        """
        p1 = self.records.columns.get_loc('pf_cum_rets')
        p2 = self.bt.pf.records.columns.get_loc('bm_cum_rets')
        p3 = self.records.columns.get_loc('drawdown')

        title_dd = 'Drawdowns (maximum duration: ' + str(self.records['duration'].max()) + ' days)'

        fig, axes = plt.subplots(2, 1, figsize=(10, 7))
        ax1 = plt.subplot(211)
        ax2 = plt.subplot(212)

        self.bt.pf.records.iloc[:, p1].plot(lw=1, color='black', alpha=0.60, ax=ax1, label='Portfolio')
        self.bt.pf.records.iloc[:, p2].plot(lw=1, color='green', alpha=0.60, ax=ax1, label='Benchmark')
        self.bt.pf.records.iloc[:, p3].plot(lw=1, color='black', alpha=0.60, ax=ax2, label='Drawdowns')

        ax1.set_xlabel('Date')
        ax1.set_title('Cumulative returns')
        self.plot_look(ax=ax1,
                       look_nr=1)

        ax2.set_xlabel('Date')
        ax2.set_title(title_dd)
        self.plot_look(ax=ax2,
                       look_nr=1)

        fig.tight_layout()
        plt.show()

        if save:
            self.save_plot(name=self.bt.pf.pf_id + 'drawdown_plot.png',
                           fig=fig)

    def dual_plot(self,
                  x_labels: list,
                  y_labels: list,
                  titles: list,
                  save=False) -> None:
        """
        Plots two plots. Generic function to be used with various time series contents.
        :param x_labels: Labels for x-axis.
        :param y_labels: Labels for y-axis.
        :param titles: Titles for plots.
        :param save: True to save to file.
        :return: None.
        """

        fig, axes = plt.subplots(2, 1, figsize=(10, 7))
        ax1 = plt.subplot(211)
        ax2 = plt.subplot(212)

        self.bt.pf.records.iloc[:, self.cols[0]].plot(lw=1, color='black', alpha=0.60, ax=ax1, label=titles[0])
        self.bt.pf.records.iloc[:, self.cols[1]].plot(lw=1, color='green', alpha=0.60, ax=ax2, label=titles[1])

        ax1.set_ylabel(y_labels[0])
        ax1.set_xlabel(x_labels[0])
        ax1.set_title(titles[0])
        self.plot_look(ax=ax1,
                       look_nr=1)

        ax2.set_ylabel(y_labels[1])
        ax2.set_xlabel(x_labels[1])
        ax2.set_title(titles[1])
        self.plot_look(ax=ax2,
                       look_nr=1)

        fig.tight_layout()
        plt.show()

        if save:
            self.save_plot(name=self.bt.pf.pf_id + 'dual_plot.png',
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
