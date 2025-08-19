# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from unittest import TestCase
from uw_hrp.dao import HRP_DAO


class DaoTest(TestCase):

    def test_dao(self):
        dao = HRP_DAO()
        self.assertEqual(dao.service_name(), "hrpws")
        self.assertTrue(len(dao.service_mock_paths()) > 0)
        self.assertTrue(dao.is_using_file_dao())
