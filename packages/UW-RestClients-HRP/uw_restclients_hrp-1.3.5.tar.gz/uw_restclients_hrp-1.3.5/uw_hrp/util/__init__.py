# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from restclients_core.util.decorators import use_mock
from uw_hrp.dao import HRP_DAO

fdao_hrp_override = use_mock(HRP_DAO())
