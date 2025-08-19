from enum import Enum
from http import HTTPStatus

USER_ERROR_PREFIX = "4"
SERVER_ERROR_PREFIX = "5"

SUCCESS_STATUS_CODES = [HTTPStatus.OK.value, HTTPStatus.CREATED.value, HTTPStatus.ACCEPTED.value]

UTF8 = "utf-8"


class AutoDeleteAccess(Enum):
    ADMIN = "ADMIN"
    USERS = "USERS"


class WorkspaceRole(Enum):
    ADMIN = "ADMIN"
    USER = "USER"
