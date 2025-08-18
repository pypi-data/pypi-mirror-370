import json
import traceback
from typing import Union

from schemas.rfc7807_model import RFC7807ResponseModel
from .logger import logger
from custom_enum.enums import ExceptionCode, ExceptionStatus
from schemas.response_model import ResponseModel

GLOBAL_LOG: bool = True


def set_global_log(should_log: bool) -> None:
    """Enable/disable all library logging globally."""
    global GLOBAL_LOG
    GLOBAL_LOG = bool(should_log)



class APIException(Exception):
    """
    Custom Exception Class for handling exceptions in a standardized way.

    Attributes:
    -----------
    - error_code : ExceptionCode
        An instance of ExceptionCode, representing the error type.
    - http_status_code : int
        HTTP status code for the exception, defaults to 400 if not specified.
    - status : ExceptionStatus
        Status of the exception, defaults to FAIL.
    - message : str
        Message to be displayed for the exception, defaults to the message from error_code.
    - description : str
        Detailed description of the exception, defaults to the description from error_code.
    """

    def __init__(self,
                 error_code: ExceptionCode,
                 http_status_code: int = 400,
                 status: ExceptionStatus = ExceptionStatus.FAIL,
                 message: str = None,
                 description: str = None,
                 log_exception: bool = True,
                 log_message: Union[str | dict] = None):
        """
        Initializes an APIException with a specific error code, HTTP status, and optional message and description.

        Parameters:
        -----------
        - error_code : ExceptionCode
            The error code enum instance defining error type, message, and description.
        - http_status_code : int, optional
            HTTP status code for the response, defaults to 400 if not specified.
        - status : ExceptionStatus, optional
            Status of the exception, defaults to ExceptionStatus.FAIL.
        - message : str, optional
            Optional custom message for the exception. Defaults to the message from error_code if None.
        - description : str, optional
            Optional custom detailed description. Defaults to description from error_code if None.
        - log_exception : bool, optional
            If True, logs the exception details. Defaults to True.
        - log_message : str, optional
            Optional custom log message. If provided, it will be logged along with the exception details.
            Defaults to None, meaning no additional log message will be added.

        """
        # Use provided message or default to the message from the error code
        self.message = message if message else error_code.message
        self.error_code = error_code.error_code
        self.description = description if description else error_code.description
        self.status = status
        self.http_status_code = http_status_code or DEFAULT_HTTP_CODES.get(status, 400)
        self.log_exception = log_exception
        self.log_message = log_message                  # If you want to add more log message. It can be dict or str.
        self.rfc7807_type = error_code.rfc7807_type
        self.rfc7807_instance = error_code.rfc7807_instance

        if GLOBAL_LOG and self.log_exception:
            # Log the exception details
            self.__log__()


    def __log__(self) -> None:
        """
        Logs the exception details with file and line number where the exception was raised.
        """
        frame = traceback.extract_stack()[-3]  # Capture the frame where the exception is raised
        logger.error(f"Exception Raised in {frame.filename}, line {frame.lineno}")
        logger.error(
            f"Code: {self.error_code}, Status: {self.status}, Message: {self.message}, Description: {self.description}")

        if self.log_message is not None:
            if isinstance(self.log_message, str):
                logger.error(f"Log Message: {self.log_message}")
            elif isinstance(self.log_message, dict):
                logger.error(f"Log Message: {json.dumps(self.log_message)}")





    def to_response(self) -> dict:
        """
        Converts the exception to a response dictionary.
        Useful for returning standardized JSON responses in an API.

        Returns:
        --------
        dict: A dictionary containing the error_code, status, message, and description.
        """
        return {
            "data": None,
            "error_code": self.error_code,
            "status": self.status.value,
            "message": self.message,
            "description": self.description
        }

    def to_rfc7807_response(self) -> RFC7807ResponseModel:
        """
        Converts the exception to a response dictionary.
        Useful for returning standardized JSON responses in an API.

        Returns:
        --------
        RFC7807ResponseModel: An instance of RFC7807ResponseModel containing the type, instance, title, status, detail.
        """
        return RFC7807ResponseModel(
            type=self.rfc7807_type,
            instance=self.rfc7807_instance,
            title=self.message,
            status=self.http_status_code,
            detail=self.description
        )

    def to_response_model(self,
                          data=None) -> ResponseModel:
        """
        Converts the exception to a ResponseModel instance.
        Useful for returning standardized API responses.

        Returns:
        --------
        ResponseModel: An instance of ResponseModel containing the error details.
        """
        return ResponseModel(
            data=data,
            status=self.status,
            message=self.message,
            error_code=self.error_code,
            description=self.description
        )

    def __str__(self):
        return f"[{self.error_code}] {self.message} (Status: {self.status}, Description: {self.description})"


# Default HTTP status codes mapped by status
DEFAULT_HTTP_CODES = {
    ExceptionStatus.SUCCESS: 200,
    ExceptionStatus.WARNING: 400,
    ExceptionStatus.FAIL: 400,
}


def set_default_http_codes(new_map: dict):
    """
    Allows overriding the default HTTP status codes.
    """
    DEFAULT_HTTP_CODES.update(new_map)
