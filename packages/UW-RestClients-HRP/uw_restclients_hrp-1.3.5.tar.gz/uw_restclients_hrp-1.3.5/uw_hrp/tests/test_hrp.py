# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from unittest import TestCase
from restclients_core.exceptions import (
    DataFailureException, InvalidEmployeeID, InvalidRegID, InvalidNetID)
from uw_hrp import HRP, convert_bytes_str
from uw_hrp.util import fdao_hrp_override


@fdao_hrp_override
class HrpTest(TestCase):

    def test_convert_bytes_str(self):
        self.assertEqual(type(b'bytes'), bytes)
        self.assertEqual(type('bytes'), str)
        self.assertEqual(convert_bytes_str(b'bytes'), "bytes")
        self.assertEqual(convert_bytes_str('bytes'), "bytes")

    def test_get_person_by_netid(self):
        hrp = HRP()
        self.assertRaises(DataFailureException,
                          hrp.get_person_by_netid,
                          "None")
        self.assertRaises(InvalidNetID,
                          hrp.get_person_by_netid,
                          "")

        person = hrp.get_person_by_netid("faculty")
        self.assertIsNotNone(person)
        self.assertEqual(person.regid, "10000000000000000000000000000005")
        self.assertEqual(person.employee_id, "000000005")
        self.assertEqual(person.student_id, "1000005")
        self.assertTrue(person.is_active)
        self.assertEqual(person.primary_manager_id, "845007271")
        self.assertEqual(len(person.worker_details), 1)
        position = person.worker_details[0]
        self.assertEqual(len(position.other_active_positions), 0)
        self.maxDiff = None
        self.assertEqual(
            position.employee_status.to_json(),
            {
                'hire_date': '2006-05-16 00:00:00-07:00',
                'is_active': True,
                'is_retired': False,
                'is_terminated': False,
                'retirement_date': None,
                'status': 'Active',
                'termination_date': None
            })
        self.assertEqual(
            position.primary_position.to_json(),
            {
                'hr_org': 'Family Medicine',
                'end_date': None,
                'is_primary': True,
                'job_class': 'Academic Personnel',
                'job_profile': {
                    'description': 'Unpaid Academic',
                    'job_code': '21184'
                },
                'job_title': 'Clinical Associate Professor',
                'location': 'Seattle Campus',
                'org_code': 'SOM',
                'org_name': 'Family Medicine: King Pierce JM Academic',
                'org_unit_code': '',
                'pos_type': 'Unpaid Academic',
                'start_date': '2012-07-01 00:00:00-07:00',
                'supervisor_eid': '845007271'
            })

        person = hrp.get_person_by_netid("faculty", include_future=True)
        self.assertIsNotNone(person)

    def test_get_person_by_employee_id(self):
        hrp = HRP()
        person = hrp.get_person_by_employee_id("000000005")
        self.assertTrue(person.netid, 'faculty')

        self.assertRaises(InvalidEmployeeID,
                          hrp.get_person_by_employee_id,
                          "")

    def test_get_person_by_regid(self):
        hrp = HRP()
        person = hrp.get_person_by_regid("9136CCB8F66711D5BE060004AC494FFE")
        self.assertTrue(person.netid, 'javerage')
        self.assertTrue(person.is_active)
        self.assertEqual(person.primary_manager_id, "100000001")
        self.assertEqual(len(person.worker_details), 1)
        self.assertIsNotNone(person.to_json())
        json_worker_details = person.to_json()['worker_details']
        self.assertEqual(len(json_worker_details), 1)
        self.assertEqual(
            len(json_worker_details[0]['active_positions']), 2)
        position = person.worker_details[0]
        self.assertEqual(len(position.other_active_positions), 1)
        self.maxDiff = None
        self.assertEqual(
            position.other_active_positions[0].to_json(),
            {'hr_org': '',
             'end_date': None,
             'is_primary': False,
             'job_class': 'Undergraduate Student',
             'job_profile': {
                'description': 'Student Assistant - Grad (NE H)',
                'job_code': '10889'},
             'job_title': 'UW Press Marketing & Sales Student Associate',
             'location': 'Seattle, Non-Campus',
             'org_code': 'LIB',
             'org_name': 'UW Press: Marketing & Sales JM Student',
             'org_unit_code': '',
             'pos_type': 'Temporary (Fixed Term)',
             'start_date': '2022-07-27 00:00:00-07:00',
             'supervisor_eid': None}
        )

        self.assertRaises(InvalidRegID,
                          hrp.get_person_by_regid, "000")

    def test_person_search(self):
        hrp = HRP()
        persons = hrp.person_search(changed_since_date="2022-12-12")
        self.assertEqual(len(persons), 1)
        self.assertFalse(persons[0].is_active)
