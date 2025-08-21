# © Copyright 2023-2025 Hewlett Packard Enterprise Development LP
import enum


class PageOpts(str, enum.Enum):
    single = "1"
    all = "all"


# HTTP status codes that will force request retries.
# Bad Gateway, Service Unavailable, Gateway Timeout
RETRY_STATUSES = [502, 503, 504]

# Default max number of times to retry a request.
MAX_RETRIES = 5
