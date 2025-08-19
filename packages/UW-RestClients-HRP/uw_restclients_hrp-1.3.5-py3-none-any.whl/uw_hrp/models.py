# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from dateutil.parser import parse
import json
from restclients_core import models


def date_to_str(d_obj):
    if d_obj is not None:
        return str(d_obj)
    return None


def parse_date(date_str):
    if date_str is not None:
        return parse(date_str)
    return None


def get_emp_program_job_class(job_classification_summaries):
    # process JobClassificationSummaries, extract employment program job code
    if job_classification_summaries and len(job_classification_summaries) > 0:
        for summary in job_classification_summaries:
            jcg = summary.get("JobClassificationGroup")
            if (jcg and jcg.get("Name") == "Employment Program" and
                    summary.get("JobClassification")):
                emp_program_name = summary["JobClassification"].get("Name")
                if " - " in emp_program_name:
                    emp_program_name = emp_program_name.split(" - ", 1)[1]
                if " (" in emp_program_name:
                    emp_program_name = emp_program_name.split(" (", 1)[0]
                return emp_program_name.strip()


def get_org_code_name(organization_name):
    org_code = ""
    org_name = organization_name
    if ": " in organization_name:
        (org_code, org_name) = organization_name.split(": ", 1)

    if " (" in org_name:
        org_name = org_name.split(" (", 1)[0]
    return org_code.strip(), org_name.strip()


class EmploymentStatus(models.Model):
    status = models.CharField(max_length=32)
    is_active = models.BooleanField(default=False)
    is_retired = models.BooleanField(default=False)
    is_terminated = models.BooleanField(default=False)
    hire_date = models.DateTimeField(null=True, default=None)
    retirement_date = models.DateTimeField(null=True, default=None)
    termination_date = models.DateTimeField(null=True, default=None)

    def to_json(self):
        return {'status': self.status,
                'hire_date': date_to_str(self.hire_date),
                'is_active': self.is_active,
                'is_retired': self.is_retired,
                'is_terminated': self.is_terminated,
                'retirement_date': date_to_str(self.retirement_date),
                'termination_date': date_to_str(self.termination_date)}

    def __init__(self, *args, **kwargs):
        data = kwargs.get("data")
        if data is None:
            return super(EmploymentStatus, self).__init__(*args, **kwargs)

        self.status = data.get("EmployeeStatus")
        self.is_active = data.get("Active")
        self.is_retired = data.get("Retired")
        self.is_terminated = data.get("Terminated")
        self.hire_date = parse_date(data.get("HireDate"))
        self.retirement_date = parse_date(data.get("RetirementDate"))
        self.termination_date = parse_date(data.get("TerminationDate"))

    def __str__(self):
        return json.dumps(self.to_json())


class JobProfile(models.Model):
    job_code = models.CharField(max_length=16, null=True, default=None)
    description = models.CharField(max_length=96, null=True, default=None)

    def to_json(self):
        return {
                'job_code': self.job_code,
                'description': self.description
                }

    def __init__(self, *args, **kwargs):
        data = kwargs.get("data")
        if data is None:
            return super(JobProfile, self).__init__(*args, **kwargs)

        self.description = data.get("Name")
        ids = data.get("IDs")
        if ids is not None and len(ids):
            for id_data in ids:
                if id_data.get("Type") == "Job_Profile_ID":
                    self.job_code = id_data.get("Value")

    def __str__(self):
        return json.dumps(self.to_json())


class EmploymentDetails(models.Model):
    start_date = models.DateTimeField(null=True, default=None)
    end_date = models.DateTimeField(null=True, default=None)
    hr_org = models.CharField(max_length=96, default="")
    job_class = models.CharField(max_length=128, null=True, default=None)
    job_title = models.CharField(max_length=128, null=True, default=None)
    is_primary = models.BooleanField(default=False)
    location = models.CharField(max_length=96, null=True, default=None)
    org_code = models.CharField(max_length=16, default="")
    org_name = models.CharField(max_length=128, default="")
    org_unit_code = models.CharField(max_length=10, default="")
    pos_type = models.CharField(max_length=64, null=True, default=None)
    supervisor_eid = models.CharField(max_length=16,
                                      null=True, default=None)

    def to_json(self):
        data = {
                'hr_org': self.hr_org,
                'end_date': date_to_str(self.end_date),
                'is_primary': self.is_primary,
                'job_title': self.job_title,
                'job_class': self.job_class,
                'location': self.location,
                'org_code': self.org_code,
                'org_name': self.org_name,
                'org_unit_code': self.org_unit_code,
                'pos_type': self.pos_type,
                'start_date': date_to_str(self.start_date),
                'supervisor_eid': self.supervisor_eid,
                'job_profile': None,
                }
        if self.job_profile is not None:
            data['job_profile'] = self.job_profile.to_json()
        return data

    def __str__(self):
        return json.dumps(self.to_json())

    def __init__(self, *args, **kwargs):
        data = kwargs.get("data")
        self.job_profile = None
        self.supervisory_org = None
        if data is None:
            return super(EmploymentDetails, self).__init__(*args, **kwargs)

        self.job_title = data.get("BusinessTitle")
        self.job_profile = JobProfile(data=data.get("JobProfile"))

        self.job_class = get_emp_program_job_class(
            data.get("JobClassificationSummaries"))

        if data.get("Location") is not None:
            self.location = data["Location"].get("Name")

        managers = data.get("Managers")
        if managers is not None and len(managers) > 0:
            ids = managers[0].get("IDs")
            for id_data in ids:
                if id_data.get("Type") == "Employee_ID":
                    self.supervisor_eid = id_data.get("Value")

        if (data.get("OrganizationDetails") is not None and
                len(data["OrganizationDetails"])):
            for org_det in data["OrganizationDetails"]:
                if (org_det.get("Organization") is not None and
                        org_det["Organization"].get("Name") is not None and
                        org_det.get("Type") is not None and
                        org_det["Type"].get("Name") == "HR Org"):
                    self.hr_org = org_det["Organization"]["Name"]

        if data.get("PositionWorkerType") is not None:
            self.pos_type = data["PositionWorkerType"].get("Name")

        self.is_primary = data.get("PrimaryPosition")
        self.end_date = parse_date(data.get("PositionVacateDate"))
        self.start_date = parse_date(data.get("StartDate"))

        if (data.get("SupervisoryOrganization") and
                data["SupervisoryOrganization"].get("Name") is not None):
            self.org_code, self.org_name = get_org_code_name(
                data["SupervisoryOrganization"]["Name"])


class WorkerDetails(models.Model):
    worker_wid = models.CharField(max_length=32)
    primary_job_title = models.CharField(
        max_length=128, null=True, default=None)
    primary_manager_id = models.CharField(
        max_length=16, null=True, default=None)

    def to_json(self):
        data = {
            'worker_wid': self.worker_wid,
            'employee_status': (
                self.employee_status.to_json() if self.employee_status
                else None),
            'primary_job_title': self.primary_job_title,
            'primary_manager_id': self.primary_manager_id,
            'active_positions': []
        }
        positions = []
        if self.primary_position is not None:
            positions.append(self.primary_position.to_json())
        for pos in self.other_active_positions:
            positions.append(pos.to_json())
        data['active_positions'] = positions
        return data

    def __str__(self):
        return json.dumps(self.to_json())

    def __init__(self, *args, **kwargs):
        data = kwargs.get("data")
        self.employee_status = None
        self.primary_position = None  # only 1 primary position
        self.other_active_positions = []  # include the future position

        if data is None:
            return super(WorkerDetails, self).__init__(*args, **kwargs)

        self.worker_wid = data.get("WID")

        self.employee_status = EmploymentStatus(
            data=data.get("EmploymentStatus"))

        if not (self.employee_status and self.employee_status.is_active):
            return

        for emp_detail in data.get("EmploymentDetails"):
            position = EmploymentDetails(data=emp_detail)
            if position and position.is_primary:
                self.primary_job_title = position.job_title
                self.primary_manager_id = position.supervisor_eid
                self.primary_position = position
            else:
                self.other_active_positions.append(position)


class Person(models.Model):
    netid = models.CharField(max_length=32)
    regid = models.CharField(max_length=32)
    employee_id = models.CharField(max_length=16)
    student_id = models.CharField(
        max_length=16, null=True, default=None)
    is_active = models.BooleanField(default=False)  # has active position
    primary_manager_id = models.CharField(
        max_length=16, null=True, default=None)

    def to_json(self):
        data = {
                "netid": self.netid,
                'regid': self.regid,
                'employee_id': self.employee_id,
                'student_id': self.student_id,
                'is_active': self.is_active,
                'primary_manager_id': self.primary_manager_id
                }
        workers = []
        for worker_detail in self.worker_details:
            workers.append(worker_detail.to_json())
        data['worker_details'] = workers
        return data

    def __str__(self):
        return json.dumps(self.to_json())

    def __init__(self, *args, **kwargs):
        data = kwargs.get("data")
        self.worker_details = []
        if data is None:
            return super(Person, self).__init__(*args, **kwargs)

        self.employee_id = data.get("EmployeeID")
        self.regid = data.get("RegID")

        for id in data.get("IDs"):
            if id.get("Type") == "NetID":
                self.netid = id.get("Value")
            if id.get("Type") == "StudentID":
                self.student_id = id.get("Value")

        for wk_detail in data.get("WorkerDetails"):
            worker_obj = WorkerDetails(data=wk_detail)
            if (worker_obj and worker_obj.employee_status and
                    worker_obj.employee_status.is_active):
                self.is_active = True
                self.worker_details.append(worker_obj)
            if worker_obj.primary_manager_id is not None:
                self.primary_manager_id = worker_obj.primary_manager_id
