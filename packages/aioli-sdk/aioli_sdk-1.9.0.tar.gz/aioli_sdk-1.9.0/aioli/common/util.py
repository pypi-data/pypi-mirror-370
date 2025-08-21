# © Copyright 2023-2025 Hewlett Packard Enterprise Development LP
import functools
import os
import pathlib
import platform
import random
import warnings
from argparse import Namespace
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    TypeVar,
    Union,
    cast,
    overload,
)

T = TypeVar("T")


def sizeof_fmt(val: Union[int, float]) -> str:
    val = float(val)
    for unit in ("", "K", "M", "G", "T", "P", "E", "Z"):
        if abs(val) < 1024.0:
            return "%3.1f%sB" % (val, unit)
        val /= 1024.0
    return "%.1f%sB" % (val, "Y")


def get_default_controller_address() -> str:
    """
    Get the default controller address from the environment. Use variable AIOLI_CONTROLLER if set.
    Otherwise if the file /etc/secrets/ezua/.auth_token exist, return
    aioli-master-service-hpe-mlis.mlis.svc.cluster.local:8080 (the default controller
    address in a Kubernetes cluster).  If neither is set, return "localhost:8080".
    """
    if "AIOLI_CONTROLLER" in os.environ:
        return os.environ["AIOLI_CONTROLLER"]

    if os.path.exists("/etc/secrets/ezua/.auth_token"):
        # Default to the Kubernetes service address for the controller.
        return "aioli-master-service-hpe-mlis.mlis.svc.cluster.local:8080"

    # Default to localhost:8080 if no environment variable is set.
    return "localhost:8080"


def get_aioli_user_token_from_env() -> Optional[str]:
    """
    Get an auth token from the environment.  If the environment variable
    AIOLI_USER_TOKEN is set, it will be returned.  If the file
    /etc/secrets/ezua/.auth_token exists and is readable, the token
    will be read from that file and returned.  If neither is set, None is returned.
    """

    if "AIOLI_USER_TOKEN" in os.environ:
        return os.environ.get("AIOLI_USER_TOKEN")

    if os.path.exists("/etc/secrets/ezua/.auth_token"):
        with open("/etc/secrets/ezua/.auth_token", "r") as token_file:
            token = token_file.read().strip()
            if token:
                return token

    return None


def debug_mode() -> bool:
    return os.getenv("AIOLI_DEBUG", "").lower() in ("true", "1", "yes")


def preserve_random_state(fn: Callable) -> Callable:
    """A decorator to run a function with a fork of the random state."""

    @functools.wraps(fn)
    def wrapped(*arg: Any, **kwarg: Any) -> Any:
        state = random.getstate()
        try:
            return fn(*arg, **kwarg)
        finally:
            random.setstate(state)

    return wrapped


def get_config_path() -> pathlib.Path:
    if os.environ.get("AIOLI_DEBUG_CONFIG_PATH"):
        return pathlib.Path(os.environ["AIOLI_DEBUG_CONFIG_PATH"])

    system = platform.system()
    if "Linux" in system and "XDG_CONFIG_HOME" in os.environ:
        config_path = pathlib.Path(os.environ["XDG_CONFIG_HOME"])
    elif "Darwin" in system:
        config_path = pathlib.Path.home().joinpath("Library").joinpath("Application Support")
    elif "Windows" in system and "LOCALAPPDATA" in os.environ:
        config_path = pathlib.Path(os.environ["LOCALAPPDATA"])
    else:
        config_path = pathlib.Path.home().joinpath(".config")

    return config_path.joinpath("aioli")


U = TypeVar("U", bound=Callable[..., Any])


def deprecated(message: Optional[str] = None) -> Callable[[U], U]:
    def decorator(func: U) -> U:
        @functools.wraps(func)
        def wrapper_deprecated(*args: Any, **kwargs: Any) -> Any:
            warning_message = (
                f"{func.__name__} is deprecated and will be removed in a future version."
            )
            if message:
                warning_message += f" {message}."
            warnings.warn(warning_message, category=DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return cast(U, wrapper_deprecated)

    return decorator


def prepend_protocol(host: str) -> str:
    host = only_prepend_protocol(host)
    return f"{host}/api/v1"


def only_prepend_protocol(host: str) -> str:
    # If neither http nor https is specified, supply the default of http.
    if not (host.startswith("http://") or host.startswith("https://")):
        host = f"http://{host}"
    return host


@overload
def chunks(lst: str, chunk_size: int) -> Iterator[str]: ...


@overload
def chunks(lst: Sequence[T], chunk_size: int) -> Iterator[Sequence[T]]: ...


def chunks(
    lst: Union[str, Sequence[T]], chunk_size: int
) -> Union[Iterator[str], Iterator[Sequence[T]]]:
    """
    Collect data into fixed-length chunks or blocks.  Adapted from the
    itertools documentation recipes.

    e.g. chunks('ABCDEFG', 3) --> ABC DEF G
    """
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


def launch_dashboard(args: Namespace, dashboard_uri: Optional[str]) -> None:
    import webbrowser

    url = f"{only_prepend_protocol(args.controller)}{dashboard_uri}"
    if not webbrowser.open(url):
        print(f"Failed to open a browser window. Manually open the dashboard using: {url}")


def construct_metadata(args: Namespace, current_meta: Optional[Dict[str, str]]) -> Dict[str, str]:
    new_meta: Dict[str, str] = {}
    if current_meta is not None:
        new_meta = current_meta.copy()
    if args.metadata is None:
        return new_meta

    for entry in args.metadata:
        if entry is None:
            new_meta = {}
            continue  # bare --metadata
        the_split = entry.split("=", maxsplit=1)
        if len(the_split) == 1:
            new_meta.pop(the_split[0], None)
            continue  # --metadata key
        if len(the_split) > 1:
            new_meta[the_split[0]] = the_split[1]

    return new_meta


def construct_environment(args: Namespace) -> Dict[str, str]:
    environment: Dict[str, str] = {}
    if args.env is None:
        return environment

    for entry in args.env:
        if entry is None:
            continue
        # split to name & value
        the_split = entry.split("=", maxsplit=1)
        name: str = the_split[0]
        value: str = ""
        if len(the_split) > 1:
            value = the_split[1]
        environment[name] = value
    return environment


def construct_arguments(args: Namespace) -> List[str]:
    arguments: List[str] = []
    if args.arg is None:
        return arguments

    for entry in args.arg:
        if entry is None:
            continue
        arguments.append(entry.strip())
    return arguments


def strtobool(val: str) -> bool:
    """
    A port of the distutils.util.strtobool function, removed in python 3.12.

    The only difference in this function is that any non-falsy value which is a non-empty string is
    accepted as a true value.  That small difference gives us a small headstart on this todo:

    TODO(MLG-1520): we should instead treat any nonempty string as "true".
    """
    return bool(val and val.lower() not in ("n", "no", "f", "false", "off", "0"))
