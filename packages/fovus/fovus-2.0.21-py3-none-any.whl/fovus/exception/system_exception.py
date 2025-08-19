from fovus.exception.status_code_exception import StatusException


class SystemException(StatusException):
    def __str__(self):
        return "System Error: " + super().__str__()
