import requests
from tako.types.common.errors import (
    APIErrorType,
    BaseAPIError,
    RateLimitExceededError,
    RelevantResultsNotFoundError,
    PaymentRequiredError,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
)


class APIException(Exception):
    def __init__(self, error: BaseAPIError):
        self.error = error

    def __str__(self):
        return self.error.error_message


class RelevantResultsNotFoundException(APIException):
    def __init__(self, error: RelevantResultsNotFoundError):
        self.error = error

    def __str__(self):
        return self.error.error_message


class RateLimitExceededException(APIException):
    def __init__(self, error: RateLimitExceededError):
        self.error = error

    def __str__(self):
        return self.error.error_message


class PaymentRequiredException(APIException):
    def __init__(self, error: PaymentRequiredError):
        self.error = error

    def __str__(self):
        return self.error.error_message


class AuthenticationErrorException(APIException):
    def __init__(self, error: AuthenticationError):
        self.error = error

    def __str__(self):
        return self.error.error_message


class BadRequestException(APIException):
    def __init__(self, error: BadRequestError):
        self.error = error

    def __str__(self):
        return self.error.error_message


class InternalServerErrorException(APIException):
    def __init__(self, error: InternalServerError):
        self.error = error

    def __str__(self):
        return self.error.error_message


def raise_exception_from_response(response: requests.Response):
    if response.status_code == 401:
        raise AuthenticationErrorException(
            AuthenticationError(
                error_type=APIErrorType.AUTHENTICATION_ERROR,
                error_message="Invalid API key",
            )
        )
    elif response.status_code != 200:
        raise_exception_from_error(BaseAPIError.model_validate(response.json()))
    return


def raise_exception_from_error(error: BaseAPIError):
    """
    Raise the appropriate exception based on the error type.

    Python 3.9 does not support match statements so we need to do it this way.
    """
    if error.error_type == APIErrorType.PAYMENT_REQUIRED:
        raise PaymentRequiredException(error)
    elif error.error_type == APIErrorType.RATE_LIMIT_EXCEEDED:
        raise RateLimitExceededException(error)
    elif error.error_type == APIErrorType.RELEVANT_RESULTS_NOT_FOUND:
        raise RelevantResultsNotFoundException(error)
    elif error.error_type == APIErrorType.INTERNAL_SERVER_ERROR:
        raise InternalServerErrorException(error)
    elif error.error_type == APIErrorType.AUTHENTICATION_ERROR:
        raise AuthenticationErrorException(error)
    elif error.error_type == APIErrorType.BAD_REQUEST:
        raise BadRequestException(error)
    else:
        raise ValueError(f"Unknown error type: {error.error_type}")
