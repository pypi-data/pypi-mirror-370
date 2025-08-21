"""
Basic unit of errorhub life...everything depends on this model
"""

from enum import Enum
from pydantic import BaseModel
from datetime import datetime


class ErrorSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EnvironmentEnum(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class ErrorDetail(BaseModel):
    service: str
    error_type: str
    code: int
    message: str
    timestamp: datetime
    trace_id: str | None = None
    severity: ErrorSeverity
    environment: EnvironmentEnum
    context: dict = {}
