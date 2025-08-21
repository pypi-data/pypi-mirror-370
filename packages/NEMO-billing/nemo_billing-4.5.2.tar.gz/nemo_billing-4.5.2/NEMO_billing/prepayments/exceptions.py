from datetime import date

from NEMO.exceptions import ProjectChargeException
from NEMO.utilities import format_datetime


class ProjectFundsNotSetException(ProjectChargeException):
    def __init__(self, project, msg=None):
        new_msg = f"The project {project.name} does not have any funds set up."
        super().__init__(project, None, msg or new_msg)


class ProjectFundsFacilityNotAllowedException(ProjectChargeException):
    def __init__(self, project, only_facilities, msg=None):
        new_msg = f"The project {project.name} can only be used for the following core facilities: {', '.join(facility.name for facility in only_facilities)}."
        super().__init__(project, None, msg or new_msg)


class ProjectFundsExpiredException(ProjectChargeException):
    def __init__(self, project, msg=None):
        new_msg = f"All of the funds for {project.name} have expired."
        super().__init__(project, None, msg or new_msg)


class ProjectFundsInactiveException(ProjectChargeException):
    def __init__(self, project, check_date: date, msg=None):
        new_msg = f"Project {project.name} does not have any active funds for {format_datetime(check_date, 'F Y')}."
        super().__init__(project, None, msg or new_msg)


class ProjectInsufficientFundsException(ProjectChargeException):
    def __init__(self, project, msg=None):
        new_msg = f"Insufficient funds for {project.name}."
        super().__init__(project, None, msg or new_msg)
