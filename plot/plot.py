import matplotlib.pyplot as plt
import pandas as pd
from holdings.portfolio import Portfolio


class Plot:
    def __init__(self,
                 pf: Portfolio,
                 cols: list):
        self.records = pf.records
        self.cols = []
        for i in cols:
            self.cols.append(self.records.columns.get_loc(i))

    def returns_plot(self,
                     x_labels: list,
                     y_labels: list,
                     titles: list) -> None:

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

        self.ax_look(ax=ax,
                     look_nr=1)

        fig.tight_layout()
        plt.show()

    def dual_plot(self,
                  df: pd.DataFrame,
                  cols: list,
                  x_labels: list,
                  y_labels: list,
                  titles: list,
                  normalized=False) -> None:
        """
        Plots two plots. Generic function to be used with various time series contents.
        :param df: Pandas dataframe with data.
        :param cols: List of column numbers to be used from df.
        :param x_labels: Labels for x-axis.
        :param y_labels: Labels for y-axis.
        :param titles: Titles for plots.
        :param normalized: Plot normalized returns for pairs in uppre plot, index in lower.
        :return: None.
        """

        fig, axes = plt.subplots(2, 1, figsize=(10, 7))
        ax1 = plt.subplot(211)
        ax2 = plt.subplot(212)

        if normalized:
            df.iloc[:, cols[0]].plot(lw=1, color='black', alpha=0.60, ax=ax1, label=titles[0])
            df.iloc[:, cols[1]].plot(lw=1, color='green', alpha=0.60, ax=ax1, label=titles[1])
            df.iloc[:, cols[2]].plot(lw=1, color='blue', alpha=0.60, ax=ax2, label=titles[2])
        else:
            df.iloc[:, cols[0]].plot(lw=1, color='black', alpha=0.60, ax=ax1, label=titles[0])
            df.iloc[:, cols[1]].plot(lw=1, color='blue', alpha=0.60, ax=ax2, label=titles[1])

        ax1.minorticks_on()
        ax1.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
        ax1.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.4)
        ax1.set_ylabel(y_labels[0])
        ax1.set_xlabel(x_labels[0])
        ax1.set_title(titles[0])
        ax1.legend(loc='best', prop={'size': 8})
        plt.setp(ax1.get_xticklabels(), visible=True, rotation=45, ha='center')

        ax2.minorticks_on()
        ax2.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
        ax2.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.4)
        ax2.set_ylabel(y_labels[1])
        ax2.set_xlabel(x_labels[1])
        ax2.set_title(titles[1])
        ax2.legend(loc='best', prop={'size': 8})
        plt.setp(ax2.get_xticklabels(), visible=True, rotation=45, ha='center')

        fig.tight_layout()
        plt.show()

    @staticmethod
    def ax_look(ax: plt.subplots,
                look_nr: int):
        if look_nr == 1:
            ax.minorticks_on()
            ax.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
            ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.4)
            ax.legend(loc='best', prop={'size': 8})
            plt.setp(ax.get_xticklabels(), visible=True, rotation=45, ha='center')
