from typing import Optional


class ZohoCRMClientException(Exception):
    """
    Zoho CRM custom exceptions
    """

    _status_code: Optional[int] = None
    _message: Optional[str] = None

    def __init__(self, status_code: int, message: str):
        super(Exception, self).__init__(message)
        self._message = message
        self._status_code = status_code

    @property
    def status_code(self) -> int:
        """The status_code property."""
        return self._status_code or 0

    @property
    def message(self) -> str:
        """The error message property."""
        return self._message or ""

    def _params_to_string(self, params):
        if not params or len(params) == 0:
            return ""
        params_msg = ""
        for key, value in params.items():
            params_msg = params_msg + "{}: {}\n".format(key, value)
        return params_msg


class ErrorCreatingSession(ZohoCRMClientException):
    def __init__(self, status_code: int, error_msg: str):
        message = "Error creating the session with the next error message: {}".format(
            error_msg
        )
        super(ErrorCreatingSession, self).__init__(status_code, message)


class CRMNotFoundError(ZohoCRMClientException):
    def __init__(self, status_code: int, error_msg: str, params: Optional[dict] = None):
        title_message = "Error searching with the next error message:"
        param_message = self._params_to_string(params)

        message = "{}\n\t{}\n{}".format(title_message, error_msg, param_message)
        super(CRMNotFoundError, self).__init__(status_code, message)


class CRMNotCreated(ZohoCRMClientException):
    def __init__(self, status_code: int, error_msg: str, params: Optional[dict] = None):
        title_message = "Error creating with the next error message:"
        param_message = self._params_to_string(params)

        message = "{}\n\t{}\n{}".format(title_message, error_msg, param_message)

        super(CRMNotCreated, self).__init__(status_code, message)


class CRMNotUpdated(ZohoCRMClientException):
    def __init__(self, status_code: int, error_msg: str, params: Optional[dict] = None):
        title_message = "Error updating with the next error message:"
        param_message = self._params_to_string(params)

        message = "{}\n\t{}\n{}".format(title_message, error_msg, param_message)

        super(CRMNotUpdated, self).__init__(status_code, message)


class CRMNotDeleted(ZohoCRMClientException):
    def __init__(self, status_code: int, error_msg: str, params: Optional[dict] = None):
        title_message = "Error deleting with the next error message:"
        param_message = self._params_to_string(params)

        message = "{}\n\t{}\n{}".format(title_message, error_msg, param_message)

        super(CRMNotDeleted, self).__init__(status_code, message)
