"""Python wrapper to the SDCcc tool for testing SDC devices."""

from pysdccc._common import DEFAULT_STORAGE_DIRECTORY, check_requirements
from pysdccc._download import download, download_sync, is_downloaded, is_downloaded_sync
from pysdccc._result_parser import TestCase, TestSuite
from pysdccc._runner import SdcccRunner
from pysdccc._runner_sync import (
    SdcccRunnerSync,
)

__version__ = '1.0.0'

__all__ = [
    'DEFAULT_STORAGE_DIRECTORY',
    'SdcccRunner',
    'SdcccRunnerSync',
    'TestCase',
    'TestSuite',
    'check_requirements',
    'download',
    'download_sync',
    'is_downloaded',
    'is_downloaded_sync',
]
