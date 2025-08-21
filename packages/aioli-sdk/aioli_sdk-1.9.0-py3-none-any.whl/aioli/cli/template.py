# © Copyright 2024-2025 Hewlett Packard Enterprise Development LP
from argparse import Namespace
from typing import Any, List

import aiolirest
from aioli import cli
from aioli.cli import render
from aioli.common.api import authentication
from aioli.common.api.errors import NotFoundException
from aioli.common.declarative_argparse import Arg, ArgsDescription, Cmd, Group
from aiolirest.models.auto_scaling_template import AutoScalingTemplate
from aiolirest.models.auto_scaling_template_request import AutoScalingTemplateRequest
from aiolirest.models.autoscaling import Autoscaling
from aiolirest.models.configuration_resources import ConfigurationResources
from aiolirest.models.resource_profile import ResourceProfile
from aiolirest.models.resources_template import ResourcesTemplate
from aiolirest.models.resources_template_request import ResourcesTemplateRequest


@authentication.required
def list_resource_templates(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.TemplatesApi(session)
        response = api_instance.templates_resources_get()

    def format_resource_template(rt: ResourcesTemplate) -> List[Any]:
        assert rt is not None
        assert rt.resources is not None
        assert rt.resources.requests is not None
        assert rt.resources.requests.cpu is not None
        assert rt.resources.requests.gpu is not None
        assert rt.resources.requests.memory is not None
        assert rt.resources.limits is not None
        assert rt.resources.limits.cpu is not None
        assert rt.resources.limits.gpu is not None
        assert rt.resources.limits.memory is not None

        result = [
            rt.name,
            rt.description,
            "Request: " + rt.resources.requests.cpu + ", Limit: " + rt.resources.limits.cpu,
            "Request: " + rt.resources.requests.memory + ", Limit: " + rt.resources.limits.memory,
            "Request: " + rt.resources.requests.gpu + ", Limit: " + rt.resources.limits.gpu,
            rt.resources.gpu_type,
        ]
        return result

    if args.json:
        render.print_json([r.to_dict() for r in response])
    elif args.yaml:
        print(render.format_object_as_yaml([r.to_dict() for r in response]))
    else:
        headers = ["Name", "Description", "CPU", "Memory", "GPU", "GPU Type"]
        values = [format_resource_template(rt) for rt in response]
        render.tabulate_or_csv(headers, values, args.csv)


def lookup_resource_template(name: str, api: aiolirest.TemplatesApi) -> ResourcesTemplate:
    for rt in api.templates_resources_get():
        if rt.name == name:
            return rt
    raise NotFoundException(f"resource template {name} not found")


@authentication.required
def show_resource_template(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.TemplatesApi(session)

    resource_template = lookup_resource_template(args.name, api_instance)

    rtd = resource_template.to_dict()
    if args.json:
        render.print_json(rtd)
    else:
        print(render.format_object_as_yaml(rtd))


@authentication.required
def create_resource_template(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.TemplatesApi(session)

        rt = ResourcesTemplateRequest(
            description=args.description,
            name=args.name,
            resources=ConfigurationResources(
                gpuType=args.gpu_type,
                limits=ResourceProfile(
                    cpu=args.limits_cpu, gpu=args.limits_gpu, memory=args.limits_memory
                ),
                requests=ResourceProfile(
                    cpu=args.requests_cpu, gpu=args.requests_gpu, memory=args.requests_memory
                ),
            ),
        )
        api_instance.templates_resources_post(rt)


@authentication.required
def update_resource_template(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.TemplatesApi(session)
        found = lookup_resource_template(args.templatename, api_instance)

        assert found is not None
        assert found.resources is not None
        assert found.resources.limits is not None
        assert found.resources.requests is not None

        request = ResourcesTemplateRequest(
            name=found.name,
            description=found.description,
            resources=ConfigurationResources(
                gpuType=found.resources.gpu_type,
                limits=ResourceProfile(
                    cpu=found.resources.limits.cpu,
                    gpu=found.resources.limits.gpu,
                    memory=found.resources.limits.memory,
                ),
                requests=ResourceProfile(
                    cpu=found.resources.requests.cpu,
                    gpu=found.resources.requests.gpu,
                    memory=found.resources.requests.memory,
                ),
            ),
        )

        assert request is not None
        assert request.resources is not None
        assert request.resources.limits is not None
        assert request.resources.requests is not None

        orig_name = found.name

        if args.name is not None:
            request.name = args.name

        if args.description is not None:
            request.description = args.description

        if args.gpu_type is not None:
            request.resources.gpu_type = args.gpu_type

        if args.limits_cpu is not None:
            request.resources.limits.cpu = args.limits_cpu

        if args.limits_memory is not None:
            request.resources.limits.memory = args.limits_memory

        if args.limits_gpu is not None:
            request.resources.limits.gpu = args.limits_gpu

        if args.requests_cpu is not None:
            request.resources.requests.cpu = args.requests_cpu

        if args.requests_memory is not None:
            request.resources.requests.memory = args.requests_memory

        if args.requests_gpu is not None:
            request.resources.requests.gpu = args.requests_gpu

        headers = {"Content-Type": "application/json"}
        assert orig_name is not None
        api_instance.templates_resources_name_put(orig_name, request, _headers=headers)


@authentication.required
def delete_resource_template(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.TemplatesApi(session)
        found = lookup_resource_template(args.name, api_instance)
        assert found.name is not None
        api_instance.templates_resources_name_delete(found.name)


@authentication.required
def list_autoscaling_templates(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.TemplatesApi(session)
        response = api_instance.templates_autoscaling_get()

    def format_autoscaling_template(at: AutoScalingTemplate) -> List[Any]:
        assert at is not None
        assert at.description is not None
        assert at.auto_scaling is not None

        result = [
            at.name,
            at.description,
            at.auto_scaling.min_replicas,
            at.auto_scaling.max_replicas,
            at.auto_scaling.metric,
            at.auto_scaling.target,
        ]
        return result

    if args.json:
        render.print_json([r.to_dict() for r in response])
    elif args.yaml:
        print(render.format_object_as_yaml([r.to_dict() for r in response]))
    else:
        headers = ["Name", "Description", "MinReplicas", "MaxReplicas", "Metric", "Target"]
        values = [format_autoscaling_template(at) for at in response]
        render.tabulate_or_csv(headers, values, args.csv)


def lookup_autoscaling_template(name: str, api: aiolirest.TemplatesApi) -> AutoScalingTemplate:
    for at in api.templates_autoscaling_get():
        if at.name == name:
            return at
    raise NotFoundException(f"autoscaling template {name} not found")


@authentication.required
def show_autoscaling_template(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.TemplatesApi(session)

    autoscaling_template = lookup_autoscaling_template(args.name, api_instance)

    atd = autoscaling_template.to_dict()
    if args.json:
        render.print_json(atd)
    else:
        print(render.format_object_as_yaml(atd))


@authentication.required
def create_autoscaling_template(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.TemplatesApi(session)

        at = AutoScalingTemplateRequest(
            autoScaling=Autoscaling(
                maxReplicas=args.autoscaling_max_replicas,
                metric=args.autoscaling_metric,
                minReplicas=args.autoscaling_min_replicas,
                target=args.autoscaling_target,
            ),
            description=args.description,
            name=args.name,
        )
        api_instance.templates_autoscaling_post(at)


@authentication.required
def update_autoscaling_template(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.TemplatesApi(session)
        found = lookup_autoscaling_template(args.templatename, api_instance)

        assert found is not None
        assert found.auto_scaling is not None

        request = AutoScalingTemplateRequest(
            autoScaling=Autoscaling(
                maxReplicas=found.auto_scaling.max_replicas,
                metric=found.auto_scaling.metric,
                minReplicas=found.auto_scaling.min_replicas,
                target=found.auto_scaling.target,
            ),
            description=found.description,
            name=found.name,
        )

        orig_name = found.name

        assert request is not None
        assert request.auto_scaling is not None

        if args.name is not None:
            request.name = args.name

        if args.description is not None:
            request.description = args.description

        if args.autoscaling_min_replicas is not None:
            request.auto_scaling.min_replicas = args.autoscaling_min_replicas

        if args.autoscaling_max_replicas is not None:
            request.auto_scaling.max_replicas = args.autoscaling_max_replicas

        if args.autoscaling_metric is not None:
            request.auto_scaling.metric = args.autoscaling_metric

        if args.autoscaling_target is not None:
            request.auto_scaling.target = args.autoscaling_target

        headers = {"Content-Type": "application/json"}
        assert orig_name is not None
        api_instance.templates_autoscaling_name_put(orig_name, request, _headers=headers)


@authentication.required
def delete_autoscaling_template(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.TemplatesApi(session)
        found = lookup_autoscaling_template(args.name, api_instance)
        assert found.name is not None
        api_instance.templates_autoscaling_name_delete(found.name)


common_resource_template_args: ArgsDescription = [
    Arg("--description", help="Description of the resource template."),
    Arg("--gpu-type", help="GPU type required"),
    Arg("--limits-cpu", help="CPU limit"),
    Arg("--limits-memory", help="Memory limit"),
    Arg("--limits-gpu", help="GPU limit"),
    Arg("--requests-cpu", help="CPU request"),
    Arg("--requests-memory", help="Memory request"),
    Arg("--requests-gpu", help="GPU request"),
]

main_cmd = Cmd(
    "template|s",
    None,
    "manage templates",
    [
        Cmd(
            "resource|s",
            None,
            "manage resource templates",
            [
                Cmd(
                    "list ls",
                    list_resource_templates,
                    "list resource templates",
                    [
                        Group(
                            Arg("--csv", action="store_true", help="print as CSV"),
                            Arg("--json", action="store_true", help="print as JSON"),
                            Arg("--yaml", action="store_true", help="print as YAML"),
                        ),
                    ],
                ),
                Cmd(
                    "show",
                    show_resource_template,
                    "show a resource template",
                    [
                        Arg("name", help="The name of the resource template."),
                        Group(
                            Arg("--yaml", action="store_true", help="print as YAML", default=True),
                            Arg("--json", action="store_true", help="print as JSON"),
                        ),
                    ],
                ),
                Cmd(
                    "create",
                    create_resource_template,
                    "create a resource template",
                    [
                        Arg(
                            "name",
                            help="The name of the resource resource template. Must begin "
                            + "with a letter, but may contain letters, numbers, "
                            + "underscore, and hyphen.",
                        ),
                    ]
                    + common_resource_template_args,
                ),
                Cmd(
                    "delete",
                    delete_resource_template,
                    "delete a resource template",
                    [Arg("name", help="The name of the resource template.")],
                ),
                Cmd(
                    "update",
                    update_resource_template,
                    "update a resource template",
                    [
                        Arg("templatename", help="The name of the resource template."),
                        Arg(
                            "--name",
                            help="The new name of the resource template. Must begin "
                            "with a letter, but may contain letters, numbers, and hyphen.",
                        ),
                    ]
                    + common_resource_template_args,
                ),
            ],
        ),
        Cmd(
            "autoscaling|s",
            None,
            "manage autoscaling templates",
            [
                Cmd(
                    "list ls",
                    list_autoscaling_templates,
                    "list autoscaling templates",
                    [
                        Group(
                            Arg("--csv", action="store_true", help="print as CSV"),
                            Arg("--json", action="store_true", help="print as JSON"),
                            Arg("--yaml", action="store_true", help="print as YAML"),
                        ),
                    ],
                ),
                Cmd(
                    "show",
                    show_autoscaling_template,
                    "show an autoscaling template",
                    [
                        Arg("name", help="The name of the autoscaling template."),
                        Group(
                            Arg("--yaml", action="store_true", help="print as YAML", default=True),
                            Arg("--json", action="store_true", help="print as JSON"),
                        ),
                    ],
                ),
                Cmd(
                    "create",
                    create_autoscaling_template,
                    "create an autoscaling template",
                    [
                        Arg(
                            "name",
                            help="The name of the autoscaling template. Must begin with a letter, "
                            + "but may contain letters, numbers, underscore, and hyphen.",
                        ),
                        Arg("--description", help="Description of the autoscaling template."),
                        Arg(
                            "--autoscaling-min-replicas",
                            help="Minimum number of replicas.",
                            required="true",
                            type=int,
                        ),
                        Arg(
                            "--autoscaling-max-replicas",
                            help="Maximum number of replicas.",
                            required="true",
                            type=int,
                        ),
                        Arg(
                            "--autoscaling-metric",
                            help="Metric name which controls autoscaling. Possible values include "
                            + "concurrency, rps, cpu, or memory.",
                            required="true",
                        ),
                        Arg(
                            "--autoscaling-target",
                            help="Metric target value.",
                            required="true",
                            type=int,
                        ),
                    ],
                ),
                Cmd(
                    "delete",
                    delete_autoscaling_template,
                    "delete an autoscaling template",
                    [Arg("name", help="The name of the autoscaling template.")],
                ),
                Cmd(
                    "update",
                    update_autoscaling_template,
                    "update an autoscaling template",
                    [
                        Arg("templatename", help="The name of the autoscaling template."),
                        Arg(
                            "--name",
                            help="The name of the autoscaling template. Must begin with a letter, "
                            + "but may contain letters, numbers, underscore, and hyphen.",
                        ),
                        Arg("--description", help="Description of the autoscaling template."),
                        Arg(
                            "--autoscaling-min-replicas",
                            help="Minimum number of replicas.",
                            type=int,
                        ),
                        Arg(
                            "--autoscaling-max-replicas",
                            help="Maximum number of replicas.",
                            type=int,
                        ),
                        Arg(
                            "--autoscaling-metric",
                            help="Metric name which controls autoscaling. "
                            + "Possible values include concurrency, rps, cpu, or memory.",
                        ),
                        Arg("--autoscaling-target", help="Metric target value.", type=int),
                    ],
                ),
            ],
        ),
    ],
)

args_description = [main_cmd]  # type: List[Any]
