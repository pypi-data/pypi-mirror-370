"""
Tired of implementing try catch for Http reponses? Use this decorator
Avoiding repetitive code and improving readability.
dont worry about error handling, just Focus on Core Logic
"""

from functools import wraps
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from errorhub.exceptions import ErrorHubException


def api_exception_handler(route_func):
    """
    Decorator for FastAPI endpoints to catch exceptions and return structured responses.
    """

    @wraps(route_func)
    async def wrapper(*args, **kwargs):
        try:
            return await route_func(*args, **kwargs)
        except ErrorHubException as e:
            # Already structured error, just map to HTTPResponse
            return JSONResponse(status_code=e.error_detail.code, content=e.to_dict())
        except HTTPException as http_exc:
            # Handle FastAPI HTTPExceptions
            return JSONResponse(status_code=http_exc.status_code, content={"detail": http_exc.detail})
        except Exception as exc:
            return JSONResponse(
                status_code=500,
                content={
                    "service": "Unknown",
                    "error_type": type(exc).__name__,
                    "code": 500,
                    "message": str(exc),
                    "trace": "traceback",
                },
            )

    return wrapper
