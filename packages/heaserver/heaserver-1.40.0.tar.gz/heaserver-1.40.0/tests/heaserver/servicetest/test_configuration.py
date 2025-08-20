import unittest

import heaserver.service.defaults
from heaserver.service import runner
from unittest.mock import patch
from unittest.result import TestResult as _TestResult  # Keeps pytest from trying to parse it as a test case.
from typing import Optional
import sys


class TestConfiguration(unittest.TestCase):

    def run(self, result: Optional[_TestResult] = None) -> Optional[_TestResult]:
        """
        Patches sys.argv with an empty list before running each test. This keeps pytest command line argument parsing
        from conflicting with HEA command line argument parsing.

        :param result: a TestResult object for compiling which tests passed and failed.
        :return: the same TestResult object, with the results of another test recorded.
        """
        with patch.object(sys, 'argv', []):
            return super().run(result)

    def setUp(self) -> None:
        self.config = runner.init_cmd_line(description='foo')

    def test_default_base_url(self) -> None:
        self.assertEqual(heaserver.service.defaults.DEFAULT_BASE_URL, self.config.base_url)


