# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from uw_bridge.util import parse_date


class TestUtil(TestCase):

    def test_parse_date(self):
        self.assertIsNone(parse_date(None))
        self.assertEqual(str(parse_date("2019-07-23T14:06:01.250-07:00")),
                         "2019-07-23 14:06:01.250000-07:00")
