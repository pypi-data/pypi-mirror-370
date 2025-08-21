# © Copyright 2023-2025 Hewlett Packard Enterprise Development LP
import hashlib
import json
import os
import socket
import ssl
import sys
import urllib.parse
from argparse import ArgumentDefaultsHelpFormatter, ArgumentError, ArgumentParser
from typing import List, Optional, Sequence, Union, cast

import argcomplete
import argcomplete.completers
from OpenSSL import SSL, crypto
from termcolor import colored
from urllib3.exceptions import MaxRetryError, SSLError

import aioli
from aioli.cli import render
from aioli.cli.deployment import args_description as deployment_args_description
from aioli.cli.model import args_description as model_args_description
from aioli.cli.project import args_description as project_args_description
from aioli.cli.registry import args_description as registry_args_description
from aioli.cli.sso import args_description as sso_args_description
from aioli.cli.template import args_description as template_args_description
from aioli.cli.version import args_description as version_args_description
from aioli.cli.version import check_version
from aioli.common import api
from aioli.common.api import certs
from aioli.common.check import check_not_none
from aioli.common.declarative_argparse import Arg, ArgsDescription, add_args
from aioli.common.util import chunks, debug_mode, get_default_controller_address
from aiolirest.rest import ApiException

from .errors import CliError, FeatureFlagDisabled

args_description: ArgsDescription = [
    Arg("-u", "--user", help="run as the given user", metavar="username", default=None),
    Arg(
        "-c",
        "--controller",
        help="controller address",
        metavar="address",
        default=get_default_controller_address(),
    ),
    Arg(
        "-v",
        "--version",
        action="version",
        help="print CLI version and exit",
        version="%(prog)s {}".format(aioli.__version__),
    ),
]
all_args_description: ArgsDescription = (
    args_description
    + project_args_description
    + registry_args_description
    + model_args_description
    + deployment_args_description
    + version_args_description
    + sso_args_description
    + template_args_description
)


def make_parser() -> ArgumentParser:
    return ArgumentParser(
        description="Aioli command-line client",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )


def die(message: str, always_print_traceback: bool = False, exit_code: int = 1) -> None:
    if always_print_traceback or debug_mode():
        import traceback

        traceback.print_exc(file=sys.stderr)

    print(colored(message, "red"), file=sys.stderr, end="\n")
    exit(exit_code)


def main(
    args: List[str] = sys.argv[1:],
) -> None:
    if sys.platform == "win32":
        # Magic incantation to make a Windows 10 cmd.exe process color-related ANSI escape codes.
        os.system("")

    # we lazily import "det deploy" but in the future we'd want to lazily import everything.
    parser = make_parser()
    add_args(parser, all_args_description)

    try:
        argcomplete.autocomplete(parser)

        parsed_args = parser.parse_args(args)
        parsed_args.controller = parsed_args.controller.rstrip("/")
        url = urllib.parse.urlparse(parsed_args.controller)
        if url.netloc:
            parsed_args.controller = url.scheme + "://" + url.netloc

        v = vars(parsed_args)
        if not v.get("func"):
            parser.print_usage()
            parser.exit(2, "{}: no subcommand specified\n".format(parser.prog))

        try:
            configure_certificate_for_controller(parsed_args.controller)
            parsed_args.func(parsed_args)
        except KeyboardInterrupt as e:
            raise e
        except (
            api.errors.BadRequestException,
            api.errors.BadResponseException,
            MaxRetryError,
        ) as e:
            die(f"Failed to {parsed_args.func.__name__}: {e}")
        except api.errors.CorruptTokenCacheException:
            die(
                "Failed to login: Attempted to read a corrupted token cache. "
                "The store has been deleted; please try again."
            )
        except FeatureFlagDisabled as e:
            die(f"controller does not support this operation: {e}")
        except CliError as e:
            die(e.message, exit_code=e.exit_code)
        except ArgumentError as e:
            die(e.message, exit_code=2)
        except ApiException as e:
            if "Client sent an HTTP request to an HTTPS server" in e.body:
                die(f"Ensure the controller address includes 'https://': {e.reason}: {e.body}")
            else:
                message = extract_message(e)
                if message is not None and len(message) > 1:
                    # The first character of the message may/should be capitalized.
                    # In this context however it looks better if in lower case.
                    message = message[0].lower() + message[1 : len(message)]
                    die(f"Failed to {parsed_args.func.__name__}: {message}")

                die(
                    f"Failed on REST API operation, status {e.status}, reason: "
                    f"{e.reason}, body: {e.body}"
                )
        except Exception:
            die(f"Failed to {parsed_args.func.__name__}", always_print_traceback=True)
    except KeyboardInterrupt:
        die("Interrupting...", exit_code=3)


def configure_certificate_for_controller(controller: str) -> None:
    # Configure the CLI's Cert singleton.
    certs.cli_cert = certs.default_load(controller)

    try:
        # check_version doesn't require credentials, so we can use it to verify the certificate.
        check_version(controller)
    except SSLError:
        # An SSLError usually means that we queried a controller over HTTPS and got an
        # untrusted cert, so allow the user to store and trust the current cert. (It
        # could also mean that we tried to talk HTTPS on the HTTP port, but distinguishing
        # that based on the exception is annoying, and we'll figure that out in the next
        # step anyway.)
        addr = api.parse_master_address(controller)
        check_not_none(addr.hostname)
        check_not_none(addr.port)
        try:
            ctx = SSL.Context(SSL.TLSv1_2_METHOD)
            conn = SSL.Connection(ctx, socket.socket())
            conn.set_tlsext_host_name(cast(str, addr.hostname).encode())
            conn.connect(cast(Sequence[Union[str, int]], (addr.hostname, addr.port)))
            conn.do_handshake()
            peer_cert_chain = conn.get_peer_cert_chain()
            if peer_cert_chain is None or len(peer_cert_chain) == 0:
                # Peer presented no cert.  It seems unlikely that this is possible after
                # do_handshake() succeeded, but checking for None makes mypy happy.
                raise crypto.Error()
            cert_pem_data = [
                crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode()
                for cert in peer_cert_chain
            ]
        except crypto.Error:
            die(
                "Tried to connect over HTTPS but couldn't get a certificate from the "
                "controller; consider using HTTP"
            )

        # Compute the fingerprint of the certificate; this is the same as the output of
        # `openssl x509 -fingerprint -sha256 -inform pem -noout -in <cert>`.
        cert_hash = hashlib.sha256(ssl.PEM_cert_to_DER_cert(cert_pem_data[0])).hexdigest()
        cert_fingerprint = ":".join(chunks(cert_hash, 2))

        if not render.yes_or_no(
            "The controller sent an untrusted certificate chain with this SHA256 "
            "fingerprint:\n"
            "{}\nDo you want to ignore this error and continue anyway?".format(cert_fingerprint)
        ):
            die("Unable to verify controller certificate")

        # save noverify for this address
        certs.CertStore(certs.default_store()).set_cert(controller, "noverify")
        # Reconfigure the CLI's Cert singleton, but preserve the certificate name.
        old_cert_name = certs.cli_cert.name

        certs.cli_cert = certs.Cert(noverify=True, name=old_cert_name)

        try:
            # let's try that again now that we have reconfigured with the certificate
            # information supplied by the controller.
            check_version(controller)
        except SSLError:
            die("Failed to verify the controller certificate")


def extract_message(e: ApiException) -> Optional[str]:
    decoder = json.JSONDecoder()
    try:
        body_obj = decoder.decode(e.body)
        return str(body_obj["message"])
    except json.JSONDecodeError:
        return None
