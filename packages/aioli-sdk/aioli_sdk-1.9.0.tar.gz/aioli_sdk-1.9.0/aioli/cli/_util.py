# © Copyright 2023-2025 Hewlett Packard Enterprise Development LP
import argparse
from typing import Optional

import aiolirest
from aioli.common import api, util
from aioli.common.api import authentication


def setup_session_no_auth(host: str) -> aiolirest.ApiClient:
    host = util.prepend_protocol(host)

    return aiolirest.ApiClient(authentication.get_rest_config(host))


def setup_session(
    args: argparse.Namespace, controller: Optional[str] = None
) -> aiolirest.ApiClient:
    # Defining the host is optional and defaults to http://localhost:8080
    # See configuration.py for a list of all supported configuration parameters.
    if controller is not None:
        host = controller
    else:
        host = args.controller

    host = util.prepend_protocol(host)

    configuration = authentication.get_rest_config(host)

    token: Optional[str] = None

    if authentication.cli_auth is not None:
        token = authentication.cli_auth.get_session_token()
    if token is None:
        token = util.get_aioli_user_token_from_env()
        # Until something more permanent is available, import a token from the environment.
        if token is None:
            raise api.errors.NotFoundException("AIOLI_USER_TOKEN not defined")

    configuration.api_key["ApiKeyAuth"] = "Bearer " + token

    return aiolirest.ApiClient(configuration)
