from http import HTTPStatus

from fovus.exception.status_code_exception import StatusException


class UserException(StatusException):
    def __str__(self):
        return "Error: " + super().__str__()


class RateLimitException(UserException):
    def __init__(self, source=None):
        super().__init__(HTTPStatus.TOO_MANY_REQUESTS, source, message="Rate limit exceeded. Please try again later.")


class NotSignedInException(UserException):
    def __init__(self, source=None):
        super().__init__(
            HTTPStatus.UNAUTHORIZED, source, message="You are not signed in. Please run 'fovus auth login' to login."
        )
