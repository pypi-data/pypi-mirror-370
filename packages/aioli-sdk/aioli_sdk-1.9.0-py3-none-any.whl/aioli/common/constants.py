# © Copyright 2024-2025 Hewlett Packard Enterprise Development LP
# The maximum size of a WebSocket message that can be sent or received
# by the Determined agent and trial-runner. The master uses a different limit,
# because it uses the uwsgi WebSocket implementation; see
# `websocket-max-size` in `uwsgi.ini`.
MAX_WEBSOCKET_MSG_SIZE = 128 * 1024 * 1024

# The maximum HTTP request size that will be accepted by the master. This
# is intended as a safeguard to quickly drop overly large HTTP requests.
MAX_HTTP_REQUEST_SIZE = 128 * 1024 * 1024
