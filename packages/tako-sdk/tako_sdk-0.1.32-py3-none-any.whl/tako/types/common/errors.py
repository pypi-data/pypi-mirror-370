from enum import Enum

from pydantic import BaseModel


class APIErrorType(str, Enum):
    BAD_REQUEST = "BAD_REQUEST"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    RELEVANT_RESULTS_NOT_FOUND = "RELEVANT_RESULTS_NOT_FOUND"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    PAYMENT_REQUIRED = "PAYMENT_REQUIRED"


class BaseAPIError(BaseModel):
    error_message: str
    error_type: APIErrorType


class AuthenticationError(BaseAPIError):
    error_type: APIErrorType = APIErrorType.AUTHENTICATION_ERROR


class BadRequestError(BaseAPIError):
    error_type: APIErrorType = APIErrorType.BAD_REQUEST


class InternalServerError(BaseAPIError):
    error_type: APIErrorType = APIErrorType.INTERNAL_SERVER_ERROR


class RelevantResultsNotFoundError(BaseAPIError):
    error_type: APIErrorType = APIErrorType.RELEVANT_RESULTS_NOT_FOUND


class RateLimitExceededError(BaseAPIError):
    error_type: APIErrorType = APIErrorType.RATE_LIMIT_EXCEEDED


class PaymentRequiredError(BaseAPIError):
    error_type: APIErrorType = APIErrorType.PAYMENT_REQUIRED
