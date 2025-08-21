"""
Handle External Calls Responses(eg calling an external endpoint from your service )
Use this to handle the response
"""

import requests

from errorhub.exceptions import (
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ConflictException,
    UnprocessableEntityException,
    InternalServerErrorException,
    ServiceUnavailableException,
    GatewayTimeoutException,
)
from errorhub.models import EnvironmentEnum, ErrorSeverity

HTTP_EXCEPTION_MAP = {
    400: BadRequestException,
    401: UnauthorizedException,
    403: ForbiddenException,
    404: NotFoundException,
    409: ConflictException,
    422: UnprocessableEntityException,
    500: InternalServerErrorException,
    503: ServiceUnavailableException,
    504: GatewayTimeoutException,
}


def raise_for_status_sync(
    response: requests.Response, service_name: str, env: EnvironmentEnum, trace: str | None = None
):
    """
    Checks a requests.Response object and raises an appropriate ErrorHubException
    if the response status code indicates an error.
    """
    if response.status_code in (200, 201, 202):
        return  # all good

    exception_cls = HTTP_EXCEPTION_MAP.get(response.status_code, InternalServerErrorException)  # default fallback

    # Raise the exception with details
    raise exception_cls(
        service=service_name,
        message=f"{response.text}",
        severity=ErrorSeverity.MEDIUM,
        environment=env,
        code=response.status_code,
        trace=trace,  # Optional trace for debugging
    )


async def raise_for_status_async(response, service_name: str, env: EnvironmentEnum, trace: str | None = None):
    """
    Async version: Accepts an httpx.Response or similar async response object.
    Raises an appropriate ErrorHubException if status code indicates error.
    """
    status = response.status_code
    content = ""

    # Some async clients require await to get text
    if hasattr(response, "aread") or hasattr(response, "atext"):
        try:
            content = await response.text()
        except Exception:
            content = "<could not read response content>"
    else:
        content = getattr(response, "text", str(response))

    if status in (200, 201, 202):
        return

    exception_cls = HTTP_EXCEPTION_MAP.get(status, InternalServerErrorException)

    raise exception_cls(
        service=service_name,
        message=f"{content}",
        severity=ErrorSeverity.MEDIUM,
        environment=env,
        code=status,
        trace=trace,
    )
