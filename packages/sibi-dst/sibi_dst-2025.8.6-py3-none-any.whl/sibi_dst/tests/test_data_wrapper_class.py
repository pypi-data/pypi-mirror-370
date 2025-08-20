import unittest
from unittest.mock import patch, MagicMock
import datetime
import pandas as pd
from sibi_dst.utils import Logger, ParquetSaver
from sibi_dst.utils.data_wrapper import DataWrapper
from threading import Lock

class TestDataWrapper(unittest.TestCase):

    def setUp(self):
        self.dataclass = MagicMock()
        self.date_field = "created_at"
        self.data_path = "/path/to/data"
        #self.data_path = "s3://your-bucket-name/path/to/data"
        self.parquet_filename = "data.parquet"
        self.start_date = "2022-01-01"
        self.end_date = "2022-12-31"
        self.filesystem_type = "file"
        self.filesystem_options = {
            #"key": "your_aws_access_key",
            #"secret": "your_aws_secret_key",
            #"client_kwargs": {"endpoint_url": "https://s3.amazonaws.com"}
        }
        self.logger = Logger.default_logger(logger_name="TestLogger")
        self._lock = Lock()

    def test_initialization(self):
        wrapper = DataWrapper(
            dataclass=self.dataclass,
            date_field=self.date_field,
            data_path=self.data_path,
            parquet_filename=self.parquet_filename,
            start_date=self.start_date,
            end_date=self.end_date,
            filesystem_type=self.filesystem_type,
            filesystem_options=self.filesystem_options,
            logger=self.logger
        )
        self.assertEqual(wrapper.dataclass, self.dataclass)
        self.assertEqual(wrapper.date_field, self.date_field)
        self.assertEqual(wrapper.data_path, "/path/to/data/")
        self.assertEqual(wrapper.parquet_filename, self.parquet_filename)
        self.assertEqual(wrapper.start_date, datetime.date(2022, 1, 1))
        self.assertEqual(wrapper.end_date, datetime.date(2022, 12, 31))
        self.assertEqual(wrapper.filesystem_type, self.filesystem_type)
        self.assertEqual(wrapper.filesystem_options, self.filesystem_options)
        self.assertEqual(wrapper.logger, self.logger)

    def test__convert_to_date(self):
        self.assertEqual(DataWrapper._convert_to_date("2022-01-01"), datetime.date(2022, 1, 1))
        self.assertEqual(DataWrapper._convert_to_date(datetime.date(2022, 1, 1)), datetime.date(2022, 1, 1))
        with self.assertRaises(ValueError):
            DataWrapper._convert_to_date("invalid-date")

    @patch('fsspec.filesystem')
    def test_is_file_older_than(self, mock_filesystem):
        mock_fs = mock_filesystem.return_value
        mock_fs.info.return_value = {'mtime': (datetime.datetime.now() - datetime.timedelta(minutes=1500)).timestamp()}

        wrapper = DataWrapper(
            dataclass=self.dataclass,
            date_field=self.date_field,
            data_path=self.data_path,
            parquet_filename=self.parquet_filename,
            start_date=self.start_date,
            end_date=self.end_date,
            filesystem_type=self.filesystem_type,
            filesystem_options=self.filesystem_options,
            logger=self.logger
        )

        #self.assertTrue(wrapper.is_file_older_than("some/file/path"))
        #mock_fs.info.return_value = {'mtime': (datetime.datetime.now() - datetime.timedelta(minutes=1000)).timestamp()}
        #self.assertFalse(wrapper.is_file_older_than("some/file/path"))


if __name__ == '__main__':
    unittest.main()