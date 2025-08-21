# © Copyright 2024-2025 Hewlett Packard Enterprise Development LP

import argparse
import sys
from typing import Any, Dict

import termcolor
from packaging import version
from urllib3.exceptions import MaxRetryError, SSLError

import aioli
import aioli.cli
import aiolirest
from aioli import cli
from aioli.cli import render
from aioli.common.declarative_argparse import ArgsDescription, Cmd


def get_version(controller: str) -> Dict[str, Any]:
    client_info = {"version": aioli.__version__}

    controller_info = {"version": ""}

    with cli.setup_session_no_auth(controller) as session:
        api_instance = aiolirest.InformationApi(session)

        try:
            response = api_instance.version_get()
            controller_info["version"] = response
        except MaxRetryError as ex:
            # Most connection errors mean that the controller is unreachable, which this
            # function handles. An SSLError, however, means it was reachable but something
            # went wrong, so let that error propagate out.
            if ex.__cause__ and isinstance(ex.__cause__, SSLError):
                raise ex.__cause__
        except Exception:
            # Exceptions get a pass here so that the code in check_version can complete.
            pass

    return {
        "client": client_info,
        "controller": controller_info,
        "controller_address": controller,
    }


def check_version(controller: str) -> None:
    info = get_version(controller)

    if not info["controller"]["version"]:
        print(
            termcolor.colored(
                "Controller not found at {}. "
                "Hint: Remember to set the AIOLI_CONTROLLER environment variable "
                "to the correct controller IP and port, for example, "
                "export AIOLI_CONTROLLER=http://$AIOLI_IP:80. Or use the '-c' flag.".format(
                    controller
                ),
                "yellow",
            ),
            file=sys.stderr,
        )
        return

    controller_version = version.Version(info["controller"]["version"])
    client_version = version.Version(info["client"]["version"])

    if controller_version < version.Version("1.4.0") and client_version >= version.Version("1.4.0"):
        # Starting in 1.4.0 we are removing obsolete APIs that no longer
        # apply for AIE.  Give a more pointed error message to assist users
        # to stay on the older aioli-sdk version if they accidentally install the latest aioli-sdk.
        print(
            termcolor.colored(
                "CLI version {} is higher than controller version {}. "
                "Install 'aioli-sdk<=1.3.0' for compatibility with your controller.".format(
                    client_version, controller_version
                ),
                "red",
            ),
            file=sys.stderr,
        )
    elif client_version.release[0:2] < controller_version.release[0:2]:
        print(
            termcolor.colored(
                "CLI version {} is less than controller version {}. "
                "Consider upgrading the CLI.".format(client_version, controller_version),
                "yellow",
            ),
            file=sys.stderr,
        )
    elif client_version.release[0:2] > controller_version.release[0:2]:
        print(
            termcolor.colored(
                "Controller version {} is less than CLI version {}. "
                "This CLI may utilize features not supported by an older "
                "controller. Install a compatible CLI with: "
                " pip install aioli-sdk=={}".format(
                    controller_version, client_version, controller_version
                ),
                "yellow",
            ),
            file=sys.stderr,
        )


def describe_version(parsed_args: argparse.Namespace) -> None:
    info = get_version(parsed_args.controller)
    print(render.format_object_as_yaml(info))


args_description: ArgsDescription = [
    Cmd("version", describe_version, "show version information", [])
]
