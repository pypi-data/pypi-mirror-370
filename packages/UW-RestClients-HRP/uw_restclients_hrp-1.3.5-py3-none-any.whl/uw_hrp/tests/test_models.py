# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from unittest import TestCase
from uw_hrp.models import (
    EmploymentStatus, JobProfile,
    EmploymentDetails, WorkerDetails, Person, parse_date,
    get_emp_program_job_class, get_org_code_name)
from uw_hrp.util import fdao_hrp_override


@fdao_hrp_override
class ModelsTest(TestCase):

    def test_parse_date(self):
        self.assertIsNotNone(parse_date("2017-09-16T07:00:00.000Z"))

    def test_get_emp_program_job_class(self):
        data = [
            {
                "JobClassification": {
                    "Name": "S - Stipend (Employment Program)",
                    "WID": ""
                },
                "JobClassificationGroup": {
                    "Name": "Employment Program",
                    "WID": ""
                }
            },
            {
                "JobClassification": {
                    "Name": "0180 - Hourly, Overt, Prem (Fina (Object-Codes))"
                },
                "JobClassificationGroup": {
                    "Name": "Financial Account Codes (Object-Codes)"
                }
            }
        ]
        self.assertEqual(get_emp_program_job_class(data), 'Stipend')

    def test_get_org_code_name(self):
        data = "CAS: Chemistry: Theberge JM Student (...())"
        code, name = get_org_code_name(data)
        self.assertEqual(code, "CAS")
        self.assertEqual(name, "Chemistry: Theberge JM Student")

        # exceptional case
        code, name = get_org_code_name("School of Law (Lawson, Tamara F)")
        self.assertEqual(code, "")
        self.assertEqual(name, "School of Law")

    def test_employment_status(self):
        emp_status0 = EmploymentStatus(status="Active", is_active=True)
        self.assertIsNotNone(emp_status0)
        self.assertEqual(
            emp_status0.to_json(),
            {
                'hire_date': None,
                'is_active': True,
                'is_retired': False,
                'is_terminated': False,
                'retirement_date': None,
                'status': 'Active',
                'termination_date': None
            })

        emp_status = EmploymentStatus(
            data={
                "HireDate": "2006-05-16T00:00:00-07:00",
                "OriginalHireDate": "2006-05-16T00:00:00-07:00",
                "ExpectedFixedTermEndDate": None,
                "FirstDayOfWork": "2006-05-16T00:00:00-07:00",
                "ActiveStatusDate": "2006-05-16T00:00:00-07:00",
                "Active": True,
                "EmployeeStatus": "Active",
                "Terminated": False,
                "TerminationDate": None,
                "TerminationInvoluntary": None,
                "TerminationReason": None,
                "Retired": False,
                "RetirementDate": None,
                "RetirementApplicationDate": None,
                "DisplayLeave": False,
                "LeaveStatusDetails": []
                })

        self.assertTrue(emp_status.is_active)
        self.assertEqual(
            emp_status.to_json(),
            {
                'hire_date': '2006-05-16 00:00:00-07:00',
                'is_active': True,
                'is_retired': False,
                'is_terminated': False,
                'retirement_date': None,
                'status': 'Active',
                'termination_date': None
            })
        self.assertIsNotNone(str(emp_status))

    def test_job_profile(self):
        job_prof = JobProfile(job_code="1", description="A")
        self.assertIsNotNone(job_prof)
        self.assertEqual(JobProfile(
            data={"Name": "Unpaid", "IDs": []}).to_json(),
            {
                'job_code': None, 'description': 'Unpaid'
            }
        )

        job_prof = JobProfile(data={
                "Name": "Unpaid Academic",
                "IDs": [
                    {
                        "Type": "Job_Profile_ID",
                        "Value": "21184"
                    },
                    {
                        "Type": "WID",
                        "Value": "d957207a306801fc5c30a8906f5c6b57"
                    }
                ]
            }
        )
        self.assertEqual(
            job_prof.to_json(),
            {
                'job_code': '21184', 'description': 'Unpaid Academic'
            }
        )
        self.assertIsNotNone(str(job_prof))

    def test_employment_details(self):
        emp_details = EmploymentDetails()
        self.assertIsNotNone(emp_details)
        emp_details = EmploymentDetails(
            data={
                "PrimaryPosition": True,
                "BusinessTitle": "Clinical Associate Professor",
                "JobScheduledWeeklyHours": 20.0,
                "StartDate": "2012-07-01T00:00:00-07:00",
                "PositionVacateDate": None,
                "JobProfile": {
                    "Name": "Unpaid Academic",
                },
                "PositionWorkerType": {
                    "Name": "Unpaid Academic",
                },
                "JobClassificationSummaries": [
                    {
                        "JobClassification": {
                            "Name": "F - Academic Personnel (Employment)"
                        },
                        "JobClassificationGroup": {
                            "Name": "Employment Program"
                        }
                    }
                ],
                "Location": {
                    "Name": "Seattle Campus",
                },
                "Managers": [
                    {
                        "Name": "Joj, Pop",
                        "WID": "",
                        "IDs": [
                                    {
                                        "Type": "Employee_ID",
                                        "Value": "123456789",
                                    }
                                ],
                    }
                ],
                "OrganizationDetails": [
                    {
                        "Type": {
                            "Name": "HR Org"
                        },
                        "Organization": {
                            "Name": "University Libraries and UW Press (Dept)"
                        }
                    }
                ],
                "SupervisoryOrganization": {
                    "Name": "SOM: Family Medicine (... (Inherited))",
                }
            }
        )
        self.maxDiff = None
        self.assertEqual(
            emp_details.to_json(),
            {
                'hr_org': 'University Libraries and UW Press (Dept)',
                'end_date': None,
                'is_primary': True,
                'job_class': 'Academic Personnel',
                'job_title': 'Clinical Associate Professor',
                'job_profile': {
                    'description': 'Unpaid Academic',
                    'job_code': None
                },
                'location': 'Seattle Campus',
                'org_code': 'SOM',
                'org_name': 'Family Medicine',
                'org_unit_code': '',
                'pos_type': 'Unpaid Academic',
                'start_date': '2012-07-01 00:00:00-07:00',
                'supervisor_eid': '123456789'
            }
        )
        self.assertIsNotNone(str(emp_details))

    def test_wwoker_details(self):
        pos = WorkerDetails(worker_wid="1b68136df25201c0710e3ddad462fa1d")
        self.assertIsNotNone(pos)
        self.assertEqual(
            pos.to_json(),
            {
                'active_positions': [],
                'employee_status': None,
                'primary_job_title': None,
                'primary_manager_id': None,
                'worker_wid': '1b68136df25201c0710e3ddad462fa1d'
            }
        )

        work_position = WorkerDetails(
            data={
                "WID": "1b68136df25201c0710e3ddad462fa1d",
                "EmploymentStatus": {
                    "HireDate": "2022-06-13T00:00:00-07:00",
                    "OriginalHireDate": "2022-06-13T00:00:00-07:00",
                    "ExpectedFixedTermEndDate": None,
                    "FirstDayOfWork": "2022-06-13T00:00:00-07:00",
                    "ActiveStatusDate": "2022-07-16T00:00:00-07:00",
                    "Active": False,
                    "EmployeeStatus": "Terminated",
                    "Terminated": True,
                    "TerminationDate": "2022-07-15T00:00:00-07:00",
                    "TerminationInvoluntary": None,
                    "TerminationReason": None,
                    "Retired": False,
                    "RetirementDate": None,
                    "RetirementApplicationDate": None,
                    "DisplayLeave": False,
                    "LeaveStatusDetails": []
                },
            }
        )
        self.assertEqual(
            work_position.to_json(),
            {
                'worker_wid': "1b68136df25201c0710e3ddad462fa1d",
                'primary_job_title': None,
                'primary_manager_id': None,
                'employee_status': {
                    'hire_date': '2022-06-13 00:00:00-07:00',
                    'is_active': False,
                    'is_retired': False,
                    'is_terminated': True,
                    'retirement_date': None,
                    'status': 'Terminated',
                    'termination_date': '2022-07-15 00:00:00-07:00',
                },
                'active_positions': [],
            }
        )
        self.assertIsNotNone(str(work_position))

    def test_worker(self):
        worker = Person(netid='none',
                        regid="10000000",
                        employee_id="100000115")
        self.assertIsNotNone(worker)

        data = {
            "Name": "Bill Faculty",
            "EmployeeID": "000000005",
            "RegID": "10000000000000000000000000000005",
            "IDs": [
                {
                    "Type": "NetID",
                    "Value": "bill"
                },
                {
                    "Type": "StudentID",
                    "Value": "1000005"
                },
                {
                    "Type": "PriorRegID",
                    "Value": "10000000000000000000000000000001"
                }
            ],
            "WorkerDetails": [
                {
                    "WID": "1b68136df25201c0710e3ddad462fa1d",
                    "EmploymentStatus": {
                        "HireDate": "2021-11-12T00:00:00-08:00",
                        "OriginalHireDate": "2021-11-12T00:00:00-08:00",
                        "ExpectedFixedTermEndDate": None,
                        "FirstDayOfWork": "2021-11-12T00:00:00-08:00",
                        "ActiveStatusDate": "2021-11-12T00:00:00-08:00",
                        "Active": True,
                        "EmployeeStatus": "Active",
                        "Terminated": False,
                        "TerminationDate": None,
                        "TerminationInvoluntary": None,
                        "TerminationReason": None,
                        "Retired": False,
                        "RetirementDate": None,
                        "RetirementApplicationDate": None,
                        "DisplayLeave": False,
                        "LeaveStatusDetails": []
                    },
                    "EmploymentDetails": [
                        {
                            "PrimaryPosition": True,
                            "BusinessTitle": "Student Assistant (NE H)",
                            "StartDate": "2021-11-12T00:00:00-08:00",
                            "PositionVacateDate": None,
                            "JobClassificationSummaries": [],
                            "SupervisoryOrganization": {
                                "Name": "CAS: Chemistry: JM student ()",
                            },
                        }
                    ],
                    "OrganizationDetails": [],
                    "ActiveAppointment": True,
                }
            ]
        }
        worker = Person(data=data)
        self.maxDiff = None
        self.assertEqual(
            worker.to_json(),
            {
                'employee_id': '000000005',
                'is_active': True,
                'netid': 'bill',
                'primary_manager_id': None,
                'regid': '10000000000000000000000000000005',
                'student_id': '1000005',
                'worker_details': [
                    {
                        'active_positions': [
                            {
                                'hr_org': '',
                                'is_primary': True,
                                'job_class': None,
                                'job_profile': {'description': None,
                                                'job_code': None},
                                'job_title': 'Student Assistant (NE H)',
                                'location': None,
                                'org_code': 'CAS',
                                'org_name': 'Chemistry: JM student',
                                'org_unit_code': '',
                                'pos_type': None,
                                'end_date': None,
                                'start_date': '2021-11-12 00:00:00-08:00',
                                'supervisor_eid': None
                            }
                        ],
                        'employee_status': {
                            'hire_date': '2021-11-12 00:00:00-08:00',
                            'is_active': True,
                            'is_retired': False,
                            'is_terminated': False,
                            'retirement_date': None,
                            'status': 'Active',
                            'termination_date': None
                        },
                        'primary_job_title': 'Student Assistant (NE H)',
                        'primary_manager_id': None,
                        'worker_wid': '1b68136df25201c0710e3ddad462fa1d'
                    }
                ]
            })
        self.assertIsNotNone(str(worker))
