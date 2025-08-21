# © Copyright 2024-2025 Hewlett Packard Enterprise Development LP
from argparse import Namespace
from typing import Any, Dict, List

import aiolirest
from aioli import cli
from aioli.cli import render
from aioli.common.api import authentication
from aioli.common.api.errors import NotFoundException
from aioli.common.declarative_argparse import Arg, Cmd, Group
from aiolirest.models.project import Project


@authentication.required
def list_projects(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.ProjectsApi(session)
        response = api_instance.projects_get()

    if args.json:
        render.print_json(format_json(response))
    elif args.yaml:
        print(render.format_object_as_yaml(format_json(response)))
    else:
        headers = ["Name", "Description", "Owner"]
        values = [[p.name, p.description, p.owner] for p in response]
        values.sort()  # sort values by the first column
        render.tabulate_or_csv(headers, values, args.csv)


def format_json(response: List[Project]) -> List[Dict[str, str]]:
    return [project_to_dict(r) for r in response]


def project_to_dict(project: Project) -> Dict[str, str]:
    # Don't use the r.to_json() method as it adds backslash escapes for double quotes
    d: Dict[str, str] = project.to_dict()
    d.pop("id")
    d.pop("modifiedAt")
    return d


main_cmd = Cmd(
    "projects p|roject",
    None,
    "Manage projects",
    [
        Cmd(
            "list ls",
            list_projects,
            "list all projects",
            [
                Group(
                    Arg("--csv", action="store_true", help="print as CSV"),
                    Arg("--json", action="store_true", help="print as JSON"),
                    Arg("--yaml", action="store_true", help="print as YAML"),
                ),
            ],
            is_default=True,
        ),
    ],
)

args_description = [main_cmd]  # type: List[Any]
