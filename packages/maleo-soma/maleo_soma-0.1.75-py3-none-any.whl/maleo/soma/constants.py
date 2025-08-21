import re
from fastapi.security import HTTPBearer
from typing import Mapping
from maleo.soma.enums.operation import ResourceOperationStatusUpdateType
from maleo.soma.enums.status import DataStatus
from maleo.soma.types.base import (
    ListOfDataStatuses,
    SequenceOfStrings,
)

# Patterns
EMAIL_REGEX: str = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
SORT_COLUMN_REGEX = r"^[a-z_]+\.(asc|desc)$"
SORT_COLUMN_PATTERN = re.compile(SORT_COLUMN_REGEX)
DATE_FILTER_REGEX = r"^[a-z_]+(?:\|from::\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))?(?:\|to::\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))?$"
DATE_FILTER_PATTERN = re.compile(DATE_FILTER_REGEX)

# CORS
DEFAULT_ALLOW_METHODS: SequenceOfStrings = (
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
)
DEFAULT_ALLOW_HEADERS: SequenceOfStrings = (
    "Authorization",
    "Content-Type",
    "X-Operation-Id",
    "X-Request-Id",
    "X-Requested-At",
    "X-Signature",
)
DEFAULT_EXPOSE_HEADERS: SequenceOfStrings = (
    "X-New-Authorization",
    "X-Operation-Id",
    "X-Process-Time",
    "X-Request-Id",
    "X-Requested-At",
    "X-Responded-At",
    "X-Signature",
)

# Status
STATUS_UPDATE_ACTION_CRITERIAS: Mapping[
    ResourceOperationStatusUpdateType, ListOfDataStatuses
] = {
    ResourceOperationStatusUpdateType.DELETE: [DataStatus.INACTIVE, DataStatus.ACTIVE],
    ResourceOperationStatusUpdateType.RESTORE: [DataStatus.DELETED],
    ResourceOperationStatusUpdateType.DEACTIVATE: [
        DataStatus.ACTIVE,
    ],
    ResourceOperationStatusUpdateType.ACTIVATE: [
        DataStatus.INACTIVE,
    ],
}
STATUS_UPDATE_ACTION_RESULT: Mapping[ResourceOperationStatusUpdateType, DataStatus] = {
    ResourceOperationStatusUpdateType.DELETE: DataStatus.DELETED,
    ResourceOperationStatusUpdateType.RESTORE: DataStatus.ACTIVE,
    ResourceOperationStatusUpdateType.DEACTIVATE: DataStatus.INACTIVE,
    ResourceOperationStatusUpdateType.ACTIVATE: DataStatus.ACTIVE,
}
ALL_STATUSES: ListOfDataStatuses = [
    DataStatus.ACTIVE,
    DataStatus.INACTIVE,
    DataStatus.DELETED,
]
VISIBLE_STATUSES: ListOfDataStatuses = [
    DataStatus.ACTIVE,
    DataStatus.INACTIVE,
]

# Token
ACCESS_TOKEN_DURATION_MINUTES: int = 5
REFRESH_TOKEN_DURATION_DAYS: int = 7
TOKEN_COOKIE_KEY_NAME = "token"
TOKEN_SCHEME = HTTPBearer()
VOLATILE_TOKEN_FIELDS: SequenceOfStrings = ("iat", "iat_dt", "exp", "exp_dt")
