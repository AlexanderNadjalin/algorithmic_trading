from loguru import logger
import configparser as cp
from pathlib import Path
import pandas as pd


class Market:
    def __init__(self, market_file_name):
        self.config = self.config()
        self.market_file_name = market_file_name
        self.data = pd.DataFrame()
        self.read_csv(input_file_name=self.market_file_name)

    @logger.catch
    def config(self) -> cp.ConfigParser:
        """

        Read config file and return a config object. Used to designate target directories for data and models.
        Config.ini file is located in project base directory.

        :return: A ConfigParser object.
        """
        conf = cp.ConfigParser()
        conf.read('market/market_config.ini')

        logger.success('I/O info read from config.ini file.')

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
                raw_data = pd.read_csv(input_file_path, sep=',', parse_dates=['DATE'])
            except ValueError as e:
                logger.error('File read failed with the following exception:')
                logger.error('   ' + str(e))
                logger.info('Aborted.')
                quit()
            else:
                logger.success('Data file "' + input_file_name + '" read.')

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
