# © Copyright 2023-2025 Hewlett Packard Enterprise Development LP
import re
from argparse import Namespace
from typing import Any, Dict, List, Optional

from pydantic import StrictInt

import aiolirest
from aioli import cli
from aioli.cli import render
from aioli.cli.registry import lookup_registry_by_id
from aioli.common import api
from aioli.common.api import authentication
from aioli.common.api.errors import NotFoundException
from aioli.common.declarative_argparse import Arg, ArgsDescription, Cmd, Group
from aioli.common.util import (
    construct_arguments,
    construct_environment,
    construct_metadata,
    launch_dashboard,
)
from aiolirest.models.configuration_resources import ConfigurationResources
from aiolirest.models.deployment_model_version import DeploymentModelVersion
from aiolirest.models.packaged_model import PackagedModel
from aiolirest.models.packaged_model_request import PackagedModelRequest
from aiolirest.models.resource_profile import ResourceProfile


@authentication.required
def list_models(args: Namespace) -> None:
    def format_json(
        response: List[PackagedModel],
        registries_api: aiolirest.RegistriesApi,
        proj_api: aiolirest.ProjectsApi,
    ) -> List[Dict[str, str]]:
        models = []
        for m in response:
            # Don't use the m.to_json() method as it adds backslash escapes for double quote
            d = m.to_dict()
            d.pop("id")
            d.pop("modifiedAt")
            if "registry" in d:
                registry = lookup_registry_by_id(d["registry"], registries_api)
                d["registry"] = registry.name
                d["registryProject"] = registry.project
            models.append(d)

        return models

    def format_models(
        response: List[PackagedModel],
        args: Namespace,
        registries_api: aiolirest.RegistriesApi,
        proj_api: aiolirest.ProjectsApi,
    ) -> None:
        def format_model(e: PackagedModel, reg_api: aiolirest.RegistriesApi) -> List[Any]:
            pname = ""
            rname = ""
            rpname = ""
            if e.project:
                pname = e.project
            if e.registry:
                registry = lookup_registry_by_id(e.registry, reg_api)
                rname = registry.name
                if registry.project:
                    rpname = registry.project

            result = [
                pname,
                e.name,
                e.description,
                e.version,
                e.url,
                e.image,
                rpname,
                rname,
            ]
            return result

        headers = [
            "Project",
            "Name",
            "Description",
            "Version",
            "URI",
            "Image",
            "Registry Project",
            "Registry",
        ]
        values = [format_model(r, registries_api) for r in response]
        render.tabulate_or_csv(headers, values, args.csv)

    with cli.setup_session(args) as session:
        api_instance = aiolirest.PackagedModelsApi(session)
        response = None
        # Get all models
        if args.all:
            response = api_instance.models_get()
        # Get all versions of specified model
        elif args.name is not None:
            response = api_instance.models_get(name=args.name)
        # Get latest version of each model (default)
        else:
            response = api_instance.models_get(latest="")

    registries_api = aiolirest.RegistriesApi(session)
    projects_api = aiolirest.ProjectsApi(session)

    if args.json:
        render.print_json(format_json(response, registries_api, projects_api))
    elif args.yaml:
        print(render.format_object_as_yaml(format_json(response, registries_api, projects_api)))
    else:
        format_models(response, args, registries_api, projects_api)


@authentication.required
def create(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.PackagedModelsApi(session)
        requests = ResourceProfile(
            cpu=args.requests_cpu, gpu=args.requests_gpu, memory=args.requests_memory
        )
        limits = ResourceProfile(
            cpu=args.limits_cpu, gpu=args.limits_gpu, memory=args.limits_memory
        )
        resources = ConfigurationResources(gpuType=args.gpu_type, requests=requests, limits=limits)
        r = PackagedModelRequest(
            name=args.name,
            description=args.description,
            url=args.url,
            image=args.image,
            registry=args.registry,
            resources=resources,
            metadata=construct_metadata(args, {}),
            environment=construct_environment(args),
            modelFormat=args.format,
            arguments=construct_arguments(args),
            project=args.project,
        )

        if args.enable_caching:
            r.caching_enabled = True

        if args.disable_caching:
            r.caching_enabled = False

        api_instance.models_post(r)


def get_models(name: str, api: aiolirest.PackagedModelsApi) -> List[PackagedModel]:
    """
    Fetch a list of PackagedModel objects matching a given name.

    Args:
       name: The name of the model. The version can also be optionally specified
         with the model name. It can be represented as <model_name>.[vV]n
         example: a model whose name is fb125m-model and version is 1 can be
         represented as fb125m-model.v1 or fb125m-model.V1
         When the version is passed with the model name, it will be parsed from the
         name and lookup done for deployments to match the model name and version.
       api: An API object used to make calls to the controller.

    Returns:
       List of PackagedModel objects matching the model name. The version can be
       passed implicitly along with the model name. If it is passed implicitly,
       the version is parsed out from the name and used to lookup for matching
       deployments.

    Raises:
       NotFoundException: If no model is found that matches the name of the
         model, an exception will be raised. If the version is implicitly passed,
         and no models are found after parsing out the version from the model
         name, an exception will be raised.
    """
    packaged_models: List[PackagedModel] = api.models_get()

    # Check if the version suffix was provided in the model name
    version: Optional[str] = None
    m = re.match(r"^(.+)\.[Vv](\d+)$", name)
    if m:
        name = m.group(1)
        version = m.group(2)
    models = [r for r in packaged_models if r.name == name]

    # If list is empty, we did not find models matching the criteria.
    if len(models) == 0:
        raise NotFoundException(f"model {name} not found")

    # if there is an explicit version specified, then use that
    if version:
        for r in models:
            if r.name == name:
                if r.version == StrictInt(version):
                    return [r]
        raise NotFoundException(f"model {name} version {version} not found")

    # If no version suffix is provided, we return a list all the model versions
    # for the deployment.
    return models


def lookup_model(name: str, api: aiolirest.PackagedModelsApi) -> PackagedModel:
    # From the database, get the model record. If the model exists in multiple versions,
    # then sufficient version information must be part of the request.
    models: List[PackagedModel] = api.models_get(name)
    if len(models):
        return models[0]

    raise NotFoundException(
        f"model {name} not found. Model versions may optionally be specified "
        "using the suffix '.v#', for example, '.v1', '.v100'"
    )


@authentication.required
def dashboard(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.PackagedModelsApi(session)

    model = lookup_model(args.name, api_instance)

    assert model.id is not None
    observability = api_instance.models_id_observability_get(model.id)
    launch_dashboard(args, observability.dashboard_url)


@authentication.required
def show_model(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.PackagedModelsApi(session)

    # By default, show latest (maximum) version
    model = api_instance.models_get(model_ref=args.name, latest="")[0]
    registries_api = aiolirest.RegistriesApi(session)

    d = model.to_dict()

    if model.registry:
        registry = lookup_registry_by_id(model.registry, registries_api)
        d["registry"] = registry.name or ""
        d["registryProject"] = registry.project

    if args.json:
        render.print_json(d)
    else:
        print(render.format_object_as_yaml(d))


@authentication.required
def update(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.PackagedModelsApi(session)
        found = lookup_model(args.modelname, api_instance)
        request = PackagedModelRequest(
            description=found.description,
            image=found.image,
            name=found.name,
            registry=found.registry,
            url=found.url,
            arguments=found.arguments,
            resources=found.resources,
            environment=found.environment,
            metadata=found.metadata,
            modelFormat=found.format,
            cachingEnabled=found.caching_enabled,
            project=found.project,
        )

        if (
            request.resources is None
            or request.resources.requests is None
            or request.resources.limits is None
        ):
            # Not likely, but testing these prevents complaints from mypy
            raise api.errors.BadResponseException("Unexpected null result")

        if args.limits_gpu is not None and args.requests_gpu is None:
            args.requests_gpu = args.limits_gpu

        if args.limits_gpu is None and args.requests_gpu is not None:
            args.limits_gpu = args.requests_gpu

        if args.name is not None:
            request.name = args.name

        if args.description is not None:
            request.description = args.description

        if args.url is not None:
            request.url = args.url

        if args.image is not None:
            request.image = args.image

        if args.registry is not None:
            request.registry = args.registry

        if args.format is not None:
            request.format = args.format

        if args.requests_cpu is not None:
            request.resources.requests.cpu = args.requests_cpu

        if args.requests_memory is not None:
            request.resources.requests.memory = args.requests_memory

        if args.requests_gpu is not None:
            request.resources.requests.gpu = args.requests_gpu

        if args.limits_cpu is not None:
            request.resources.limits.cpu = args.limits_cpu

        if args.limits_memory is not None:
            request.resources.limits.memory = args.limits_memory

        if args.limits_gpu is not None:
            request.resources.limits.gpu = args.limits_gpu

        if args.gpu_type is not None:
            request.resources.gpu_type = args.gpu_type

        if args.env is not None:
            request.environment = construct_environment(args)

        if args.arg is not None:
            request.arguments = construct_arguments(args)

        if args.metadata is not None:
            request.metadata = construct_metadata(args, found.metadata)

        if args.enable_caching:
            request.caching_enabled = True

        if args.disable_caching:
            request.caching_enabled = False

        if args.project is not None:
            request.project = args.project

        headers = {"Content-Type": "application/json"}

        assert found.id is not None
        api_instance.models_id_put(found.id, request, _headers=headers)


@authentication.required
def delete_model(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.PackagedModelsApi(session)
        found = lookup_model(args.name, api_instance)

        assert found.id is not None
        api_instance.models_id_delete(found.id)


@authentication.required
def list_deployments(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.PackagedModelsApi(session)

        # For listing models, if no model version with model name,
        # we want to list all the versions of the deployed model
        models = get_models(args.name, api_instance)

        response: List[DeploymentModelVersion] = []
        for m in models:
            for d in api_instance.models_versions_get(m.id):
                response.append(d)

    def format_deployments(e: DeploymentModelVersion) -> List[Any]:
        result = [
            e.deployed,
            e.native_app_name,
            e.model,
            e.mdl_version,
            e.canary_traffic_percent,
        ]
        return result

    headers = [
        "Deployed",
        "Native App Name",
        "Model",
        "Model\nVersion",
        "Traffic",
    ]

    if args.json:
        render.print_json([r.to_dict() for r in response])
    elif args.yaml:
        print(render.format_object_as_yaml([r.to_dict() for r in response]))
    else:
        values = [format_deployments(r) for r in response]
        render.tabulate_or_csv(headers, values, args.csv)


common_model_args: ArgsDescription = [
    Arg("--description", help="Description of the packaged model"),
    Arg("--url", help="Reference within the specified registry"),
    Arg("--registry", help="The name or ID of the packaged model registry"),
    Arg(
        "--format",
        "--modelformat",
        help="Model format for downloaded models (bento-archive, openllm, nim, unspecified)",
    ),
    Group(
        Arg("--enable-caching", action="store_true", help="Enable caching for the packaged model"),
        Arg(
            "--disable-caching", action="store_true", help="Disable caching for the packaged model"
        ),
    ),
    Arg(
        "-a",
        "--arg",
        nargs="?",
        help="Argument to be added to the service command line. "
        "If specifying an argument that starts with a '-', use the form --arg=<your-argument>. "
        "Specifying any --arg replaces prior args with the arguments on this invocation. "
        "Use a single --arg with no value to clear all arguments.",
        action="append",
    ),
    Arg(
        "-e",
        "--env",
        nargs="?",
        help="Specifies an environment variable & value as name=value, "
        "to be passed to the launched container. "
        "Specifying any --env replaces prior environment vars with those on this invocation. "
        "Use a single --env with no value to clear all environment vars.",
        action="append",
    ),
    Arg("--gpu-type", help="GPU type required"),
    Arg("--limits-cpu", help="CPU limit"),
    Arg("--limits-memory", help="Memory limit"),
    Arg("--limits-gpu", help="GPU limit"),
    Arg("--requests-cpu", help="CPU request"),
    Arg("--requests-memory", help="Memory request"),
    Arg("--requests-gpu", help="GPU request"),
]

VERSIONED_MODEL_HELP_MSG = (
    "The packaged model id, name or versioned-name (evaluated in that order). "
    "A versioned-name is the package model name with suffix of the version "
    "with the format 'name.V###' where '###' is the version number. For example, "
    "a model named 'my-model' with a version of '23' would be represented by "
    "versioned-name of: my-model.V23"
)

main_cmd = Cmd(
    "m|odel|s",
    None,
    "manage packaged models",
    [
        # Inspection commands.
        Cmd(
            "list ls",
            list_models,
            "list only the latest version of each packaged model",
            [
                Group(
                    Arg("--all", action="store_true", help="show all models"),
                    Arg("--name", help="list all versions of model, if specified"),
                ),
                Group(
                    Arg("--csv", action="store_true", help="print as CSV"),
                    Arg("--json", action="store_true", help="print as JSON"),
                    Arg("--yaml", action="store_true", help="print as YAML"),
                ),
            ],
            is_default=True,
        ),
        # Create command.
        Cmd(
            "create",
            create,
            "create a packaged model",
            [
                Arg(
                    "name",
                    help="The name of the packaged model. Must begin with a letter, but may "
                    "contain letters, numbers, and hyphen",
                ),
                Arg("--image", help="Docker container image servicing the packaged model"),
                Arg(
                    "-m",
                    "--metadata",
                    nargs="?",
                    help="Specifies a metadata variable and value as name=value.",
                    action="append",
                ),
                Arg("--project", help="The project this packaged model belongs to"),
            ]
            + common_model_args,
        ),
        # dashboard command.
        Cmd(
            "dashboard",
            dashboard,
            "launch the packaged model dashboard",
            [
                Arg(
                    "name",
                    help=VERSIONED_MODEL_HELP_MSG,
                ),
            ],
        ),
        # Show command.
        Cmd(
            "show",
            show_model,
            "show a packaged model",
            [
                Arg(
                    "name",
                    help=VERSIONED_MODEL_HELP_MSG,
                ),
                Group(
                    Arg("--yaml", action="store_true", help="print as YAML", default=True),
                    Arg("--json", action="store_true", help="print as JSON"),
                ),
            ],
        ),
        # Update command
        Cmd(
            "update",
            update,
            "modify a packaged model",
            [
                Arg(
                    "modelname",
                    help=VERSIONED_MODEL_HELP_MSG,
                ),
                Arg(
                    "--name",
                    help="The new name of the packaged model. Must begin with a letter, but may "
                    "contain letters, numbers, and hyphen",
                ),
                Arg("--image", help="Docker container image servicing the packaged model"),
                Arg(
                    "-m",
                    "--metadata",
                    nargs="?",
                    help="Specifies a metadata variable and value as name=value. "
                    "Specifying --metadata name=value appends to the current set of metadata. "
                    "Specifying --metadata name removes the valiable with specified name. "
                    "Use --metadata with no value to clear all metadata.",
                    action="append",
                ),
                Arg("--project", help="The project this packaged model belongs to"),
            ]
            + common_model_args,
        ),
        Cmd(
            "delete",
            delete_model,
            "delete a packaged model",
            [
                Arg(
                    "name",
                    help=VERSIONED_MODEL_HELP_MSG,
                ),
            ],
        ),
        Cmd(
            "list-deployments",
            list_deployments,
            "list of deployment versions for a packaged model",
            [
                Arg(
                    "name",
                    help=VERSIONED_MODEL_HELP_MSG,
                ),
                Group(
                    Arg("--csv", action="store_true", help="print as CSV"),
                    Arg("--json", action="store_true", help="print as JSON"),
                    Arg("--yaml", action="store_true", help="print as YAML"),
                ),
            ],
        ),
    ],
)

args_description = [main_cmd]  # type: List[Any]
