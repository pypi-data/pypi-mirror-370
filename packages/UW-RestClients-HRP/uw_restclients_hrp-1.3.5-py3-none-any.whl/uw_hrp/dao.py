# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


import logging
import os
from os.path import abspath, dirname
from restclients_core.dao import DAO


class HRP_DAO(DAO):
    def service_name(self):
        return 'hrpws'

    def service_mock_paths(self):
        return [abspath(os.path.join(dirname(__file__), "resources"))]

    def is_using_file_dao(self):
        return self.get_implementation().is_mock()
