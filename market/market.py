from loguru import logger
import configparser as cp
from pathlib import Path
import pandas as pd


class Market:
    def __init__(self,
                 market_file_name: str,
                 fill_missing_method: str):
        """

        Market class object.
        :param market_file_name: File name as string.
        :param fill_missing_method: Fill missing values method as string.
        """
        self.config = self.config()
        self.market_file_name = market_file_name
        self.fill_missing_method = fill_missing_method
        self.data = pd.DataFrame()
        self.read_csv(input_file_name=self.market_file_name)
        self.data_valid()
        self.columns = self.data.columns.to_list()
        logger.info('Market created.')

    @logger.catch
    def config(self) -> cp.ConfigParser:
        """

        Read market_config file and return a config object. Used to designate target directories for data and models.
        Config.ini file is located in project base directory.

        :return: A ConfigParser object.
        """
        conf = cp.ConfigParser()
        conf.read('market/market_config.ini')

        logger.success('I/O info read from market_config.ini file.')

        return conf

    @logger.catch
    def read_csv(self,
                 input_file_name: str) -> None:
        """

        Read config.ini file. Read specified input .csv file.
        :param input_file_name: Filename including suffix.
        :return: pandas dataframe.
        """

        input_file_directory = Path(self.config['input_files']['input_file_directory'])
        input_file_path = Path.joinpath(input_file_directory, input_file_name)

        raw_data = pd.DataFrame()

        if self.file_valid(input_file_path):
            try:
                raw_data = pd.read_csv(input_file_path, sep=',')
            except ValueError as e:
                logger.error('File read failed with the following exception:')
                logger.error('   ' + str(e))
                logger.info('Aborted.')
                quit()
            else:
                logger.success('Data file "' + input_file_name + '" read.')

        # raw_data['DATE'].apply(lambda x: x.strftime('%Y-%m-%d'))
        raw_data = raw_data.set_index(['DATE'])

        self.data = raw_data

        self.data.dropna(axis=0,
                         how='any',
                         thresh=None,
                         subset=None,
                         inplace=True
                         )

    @logger.catch
    def file_valid(self,
                   file_path: Path):
        """

        Check if file path is valid. Otherwise Abort.
        :param file_path: File Path object (directory + file name).
        :return: Boolean.
        """
        if file_path.exists():
            return True
        else:
            logger.critical('File directory or file name is incorrect. Aborted')
            quit()

    @logger.catch
    def data_valid(self) -> None:
        """

        Check for NaN, empty values and non-floats.
        Fill missing values.
        :return: None
        """
        cols = list(self.data.columns)
        emptys = 0
        nans = 0
        floats = 0
        for col in cols:
            col_emptys = len(self.data[self.data[col] == ''])
            col_nans = self.data[col].isna().sum()
            if self.data[col].dtypes != 'float64':
                floats += 1
            emptys += col_emptys
            nans += col_nans

            if col_emptys > 0:
                logger.warning('Column ' + col + ' has ' + str(col_emptys) + ' number of empty values.')
                self.fill_missing(col_name=col)
            if col_nans > 0:
                logger.warning('Column ' + col + ' has ' + str(col_nans) + ' number of NaN values.')
            if floats > 0:
                logger.warning('Column ' + col + ' has one or more non-float values.')

        if (emptys == 0) and (nans == 0) and (floats == 0):
            logger.info('No empty, NaN or non-float values in imported file.')

    def fill_missing(self,
                     col_name: str) -> None:
        """

        Fill missing values in a column of self.data with given method.
        :param col_name: Column name. Passing "None" does nothing.
        :return: None.
        """
        if self.fill_missing_method == 'forward':
            self.data[col_name].fillna(method='ffill', inplace=True)
            logger.info('Column ' + col_name + ' forward-filled.')
        elif self.fill_missing_method == 'backward':
            self.data[col_name].fillna(method='bfill', inplace=True)
            logger.info('Column ' + col_name + ' backward-filled.')
        elif self.fill_missing_method == 'interpolate':
            self.data[col_name].interpolate(method='polynomial')
            logger.info('Column ' + col_name + ' filled by interpolation.')
        elif self.fill_missing_method is None:
            pass
        else:
            logger.critical('Fill method ' + self.fill_missing_method + ' not implemented. Aborted.')
            quit()

    def select(self,
               columns: list,
               start_date: str,
               end_date: str) -> pd.DataFrame:
        """

        Select a subset of market data between start_date and end_date.
        :param columns: List of column names.
        :param start_date: Start date (oldest date, included in selection).
        :param end_date:End date (newest date, included in selection)
        :return: Pandas dataframe.
        """
        if any(item in self.columns for item in columns):
            if start_date not in self.data.index.values:
                logger.critical('Selected start date not in market data. Aborted.')
                quit()
            if end_date not in self.data.index.values:
                logger.critical('Selected end date not in market data. Aborted.')
                quit()
            mask = (self.data.index.values >= start_date) & (self.data.index.values <= end_date)
            df = self.data.loc[mask]
            return df[columns]
        else:
            logger.critical('Selected column name not in market data. Aborted.')
            quit()

    def date_from_index(self,
                        current_date: str,
                        index_loc: int) -> str:
        mask = (self.data.index.values >= current_date)
        df = self.data.loc[mask]
        date = df.iloc[[index_loc]].index.values[0]
        return date
