"""
All Custom exception you will need in your life
"""

from datetime import datetime, timezone
import uuid
from errorhub.models import ErrorDetail, ErrorSeverity, EnvironmentEnum
import logging


LOGGER = logging.getLogger(__name__)


class ErrorHubException(Exception):
    def __init__(
        self,
        service: str,
        error_type: str,
        message: str,
        code: int = 500,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        environment: EnvironmentEnum = EnvironmentEnum.DEVELOPMENT,
        trace_id: str | None = None,
        context: dict = {},
    ):
        """
        Super Exception Inherited by every custom Excetion in error hub
        """
        self.error_detail = ErrorDetail(
            service=service,
            error_type=error_type,
            message=message,
            code=code,
            severity=severity,
            environment=environment,
            trace_id=trace_id or str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            context=context,
        )
        super().__init__(message)
        self._log_error()

    def _log_error(self):
        if self.error_detail.severity == ErrorSeverity.HIGH:
            LOGGER.error("High Error occurred: %s", self.to_dict())
        elif self.error_detail.severity == ErrorSeverity.MEDIUM:
            LOGGER.warning("Medium Error occurred: %s", self.to_dict())
        else:
            LOGGER.info("Low Error occurred: %s", self.to_dict())

    def to_dict(self):
        """Return the structured error as a dictionary."""
        return self.error_detail.model_dump()

    def __str__(self):
        return f"[{self.error_detail.service}] {self.error_detail.error_type}: {self.error_detail.code} | {self.error_detail.message}"


class NotFoundException(ErrorHubException):
    def __init__(self, service: str, message: str = "Resource not found", **kwargs):
        super().__init__(service=service, error_type="NotFound", message=message, code=404, **kwargs)


class UnauthorizedException(ErrorHubException):
    def __init__(self, service: str, message: str = "Unauthorized", **kwargs):
        super().__init__(service=service, error_type="Unauthorized", message=message, code=401, **kwargs)


class BadRequestException(ErrorHubException):
    def __init__(self, service: str, message: str = "Bad request", **kwargs):
        super().__init__(service=service, error_type="BadRequest", message=message, code=400, **kwargs)


class InternalServerErrorException(ErrorHubException):
    def __init__(self, service: str, message: str = "Internal server error", **kwargs):
        super().__init__(service=service, error_type="InternalServerError", message=message, code=500, **kwargs)


class ForbiddenException(ErrorHubException):
    def __init__(self, service: str, message: str = "Forbidden", **kwargs):
        super().__init__(service=service, error_type="Forbidden", message=message, code=403, **kwargs)


class ConflictException(ErrorHubException):
    def __init__(self, service: str, message: str = "Conflict", **kwargs):
        super().__init__(service=service, error_type="Conflict", message=message, code=409, **kwargs)


class UnprocessableEntityException(ErrorHubException):
    def __init__(self, service: str, message: str = "Unprocessable entity", **kwargs):
        super().__init__(service=service, error_type="UnprocessableEntity", message=message, code=422, **kwargs)


class ServiceUnavailableException(ErrorHubException):
    def __init__(self, service: str, message: str = "Service unavailable", **kwargs):
        super().__init__(service=service, error_type="ServiceUnavailable", message=message, code=503, **kwargs)


class GatewayTimeoutException(ErrorHubException):
    def __init__(self, service: str, message: str = "Gateway timeout", **kwargs):
        super().__init__(service=service, error_type="GatewayTimeout", message=message, code=504, **kwargs)
