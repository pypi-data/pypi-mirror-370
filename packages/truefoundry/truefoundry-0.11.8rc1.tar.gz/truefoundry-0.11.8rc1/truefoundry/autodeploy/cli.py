import os
import re
import sys
from typing import Dict, Optional

import click
import docker
import questionary
import requests
import yaml
from dotenv import dotenv_values
from openai import OpenAI
from rich.console import Console
from rich.prompt import Prompt
from rich.status import Status

from truefoundry.autodeploy.agents.developer import Developer
from truefoundry.autodeploy.agents.project_identifier import (
    ComponentType,
    ProjectIdentifier,
)
from truefoundry.autodeploy.agents.tester import Tester
from truefoundry.autodeploy.constants import (
    ABOUT_AUTODEPLOY,
    AUTODEPLOY_OPENAI_API_KEY,
    AUTODEPLOY_OPENAI_BASE_URL,
    AUTODEPLOY_TFY_BASE_URL,
)
from truefoundry.autodeploy.exception import InvalidRequirementsException
from truefoundry.autodeploy.tools.ask import AskQuestion
from truefoundry.autodeploy.tools.commit import CommitConfirmation
from truefoundry.autodeploy.tools.docker_run import DockerRun, DockerRunLog
from truefoundry.autodeploy.utils.client import get_git_binary
from truefoundry.cli.const import COMMAND_CLS
from truefoundry.common.session import Session
from truefoundry.deploy import Build, DockerFileBuild, Job, LocalSource, Port, Service
from truefoundry.deploy.lib.clients.servicefoundry_client import (
    ServiceFoundryServiceClient,
)


def _get_openai_client() -> OpenAI:
    if AUTODEPLOY_OPENAI_BASE_URL is not None and AUTODEPLOY_OPENAI_API_KEY is not None:
        return OpenAI(
            api_key=AUTODEPLOY_OPENAI_API_KEY, base_url=AUTODEPLOY_OPENAI_BASE_URL
        )
    try:
        session = Session.new()
        resp = requests.get(
            f"{AUTODEPLOY_TFY_BASE_URL}/api/svc/v1/llm-gateway/access-details",
            headers={
                "Authorization": f"Bearer {session.access_token}",
            },
        )
        resp.raise_for_status()
        resp = resp.json()
        return OpenAI(api_key=resp["jwtToken"], base_url=resp["inferenceBaseURL"])
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code in [401, 403]:
            raise InvalidRequirementsException(
                message="Unauthorized access to TrueFoundry server. "
                "Please verify your credentials and ensure you have the necessary access rights."
                "\nIf you wish to proceed without TrueFoundry AI, "
                "you need to either have a truefoundry.yaml file in your project root "
                'or pass the path to a yaml file using the "--file file_name" option.'
            ) from http_error

        raise http_error

    except Exception as e:
        raise InvalidRequirementsException(message=str(e)) from e


def _get_service_port(name: str, workspace_fqn: str, port: int) -> Port:
    client = ServiceFoundryServiceClient()
    workspaces = client.get_workspace_by_fqn(workspace_fqn=workspace_fqn)
    if len(workspaces) == 0:
        raise click.UsageError("Invalid workspace")
    workspace = workspaces[0]
    cluster = client.get_cluster(cluster_id=workspace.clusterId)

    generated_name = name + "-" + workspace.name
    base_domain_urls = cluster["metadata"].get("baseDomainURLs")
    if not base_domain_urls:
        return Port(port=port, expose=False)

    base_domain_url = base_domain_urls[0]

    if "*" in base_domain_url:
        return Port(
            port=port, host=base_domain_url.replace("*", generated_name).strip("/")
        )

    return Port(port=port, host=base_domain_url, path=f"/{generated_name}/")


def deploy_component(
    workspace_fqn: str,
    project_root_path: str,
    dockerfile_path: str,
    component_type: ComponentType,
    name: str,
    env: Dict,
    command: Optional[str] = None,
    port: Optional[int] = None,
):
    if not os.path.exists(os.path.join(project_root_path, dockerfile_path)):
        raise FileNotFoundError("Dockerfile not found in the project.")

    image = Build(
        build_spec=DockerFileBuild(
            dockerfile_path=dockerfile_path,
            command=command,
        ),
        build_source=LocalSource(project_root_path=project_root_path),
    )
    if component_type == ComponentType.SERVICE:
        if port is None:
            raise ValueError("Port is required for deploying service")
        service_port = _get_service_port(
            name=name, workspace_fqn=workspace_fqn, port=port
        )

        app = Service(
            name=name,
            image=image,
            ports=[service_port],
            env=env,
        )
    else:
        app = Job(name=name, image=image, env=env)
    with open("truefoundry.yaml", "w") as application_spec:
        yaml.dump(app.dict(), application_spec, indent=2)
    app.deploy(workspace_fqn=workspace_fqn)


def _parse_env(project_root_path: str, env_path: str) -> Dict:
    if not os.path.isabs(env_path):
        env_path = os.path.join(project_root_path, env_path)

    if os.path.exists(env_path):
        return dotenv_values(env_path)

    raise FileNotFoundError(f"Invalid path {env_path!r}")


def _check_repo(project_root_path: str, console: Console):
    git = get_git_binary()
    try:
        repo = git.Repo(path=project_root_path, search_parent_directories=True)
        if repo.is_dirty():
            console.print(
                "[bold red]Error:[/] The repository has uncommitted changes. "
                "Please commit or stash them before proceeding."
            )
            sys.exit(1)
        current_active_branch = repo.active_branch.name
        console.print(
            f"[bold magenta]TrueFoundry:[/] Current branch [green]{current_active_branch!r}[/]"
        )
        branch_name = Prompt.ask(
            "[bold magenta]TrueFoundry:[/] Enter a branch name if you want to checkout to a new branch. "
            f"Press enter to continue on [green]{current_active_branch!r}[/]",
            console=console,
        )
        if branch_name:
            repo.git.checkout("-b", branch_name)
            console.print(
                f"[bold magenta]TrueFoundry:[/] Switched to branch: [green]{repo.active_branch}[/]"
            )
        else:
            console.print(
                f"[bold magenta]TrueFoundry:[/] Continuing on [green]{current_active_branch!r}[/]"
            )

    except git.exc.InvalidGitRepositoryError:
        console.print(
            "[red]Error:[/] This operation can only be performed inside a Git repository.\n"
            "Execute 'git init' to create a new repository."
        )
        sys.exit(1)

    except git.GitCommandError as gce:
        console.print(
            f"Command execution failed due to the following error:[red]{gce.stderr}[/]".replace(
                "\n  stderr:", ""
            )
        )
        console.print(
            "[bold red]Error:[/] Unable to switch to the new branch. It's possible that this branch already exists."
        )
        sys.exit(1)


def _update_status(event, status: Status, component_type: ComponentType):
    if isinstance(event, (AskQuestion, CommitConfirmation)):
        status.stop()

    if isinstance(
        event, (Developer.Request, ProjectIdentifier.Response, Tester.Response)
    ):
        status.update(
            "[bold magenta]TrueFoundry[/] is currently building the project. Please wait..."
        )

    if isinstance(event, ProjectIdentifier.Request):
        status.update(
            "[bold magenta]TrueFoundry[/] is currently identifying the project..."
        )

    if isinstance(event, (Tester.Request, DockerRun.Response)):
        status.update(
            "[bold magenta]TrueFoundry[/] is currently running tests on the project..."
        )

    if isinstance(event, DockerRunLog):
        if component_type == ComponentType.SERVICE:
            status.update(
                "[bold cyan]Running:[/] [bold magenta]TrueFoundry[/] is running your app in a Docker container. "
                "Press ctrl+c once your app is ready for testing."
            )
        else:
            status.update(
                "[bold cyan]Running:[/] [bold magenta]TrueFoundry[/] is running your app in a Docker container "
                "and waiting for completion."
            )


def _get_default_project_name(project_root_path: str):
    path = os.path.abspath(project_root_path).rstrip(os.path.sep)
    name = path.split(os.path.sep)[-1].lower()
    name = re.sub(r"[^a-z0-9]", "-", name)
    name = "-".join(n for n in name.split("-") if n)[:30]
    return name


def _get_docker(console: Console) -> docker.DockerClient:
    try:
        return docker.from_env()
    except Exception as e:
        raise InvalidRequirementsException(
            message="Could not connect to Docker, please check whether the Docker daemon is running."
        ) from e


def cli(project_root_path: str, deploy: bool, workspace_fqn: str = None):
    console = Console()
    openai_client = _get_openai_client()
    docker_client = _get_docker(console)
    project_root_path = os.path.abspath(project_root_path)
    console.print(ABOUT_AUTODEPLOY)
    console.print(
        "[bold reverse]You will need to have Docker and Git installed on your machine for this to work[/]"
    )
    if AUTODEPLOY_OPENAI_BASE_URL is not None and AUTODEPLOY_OPENAI_API_KEY is not None:
        console.print(
            "[bold green]OpenAI credentials found in environment variables.[/]"
        )
        console.print(
            "This operation will use tokens from your provided OpenAI account and may incur costs.",
        )
    else:
        console.print(
            "[dim]To use your own LLM, "
            "set the environment variables [dim italic green]AUTODEPLOY_OPENAI_BASE_URL[/],[/]",
            "[dim][dim italic green]AUTODEPLOY_OPENAI_API_KEY[/], "
            "and [dim italic green]AUTODEPLOY_MODEL_NAME[/] for URL, API key, and LLM model name respectively.[/]",
        )
    console.print(
        "[bold cyan]Note:[/] All changes will be committed to a new branch. Please ensure you have a repository."
    )
    console.print("[bright_green]Let's get started[/]")
    _check_repo(project_root_path=project_root_path, console=console)

    choices = {
        "Service: An application that runs continuously. "
        "Example: web servers, workers polling a job queue, etc.": "SERVICE",
        "Job: An application that runs once and then stops. "
        "Example: Training an ML model, running a script, etc.": "JOB",
    }
    component = questionary.select(
        "TrueFoundry: Is your project a", choices=list(choices.keys())
    ).ask()
    component_type = ComponentType[choices[component]]
    while True:
        name = Prompt.ask(
            "[bold magenta]TrueFoundry:[/] Name of deployment, or press [green]Enter[/] to select default. "
            f"default: [green]{_get_default_project_name(project_root_path)}",
            console=console,
            default=_get_default_project_name(project_root_path),
            show_default=False,
        )
        if not re.match(r"^[a-z][a-z0-9\-]{1,30}[a-z0-9]$", name):
            console.print(
                "[bold magenta]TrueFoundry:[/] The name should be between 2-30 alphanumeric"
                " characters and '-'. The first character should not be a digit."
            )
        else:
            break
    command = Prompt.ask(
        "[bold magenta]TrueFoundry:[/] Command to run the application or press [green]Enter[/] to skip",
        console=console,
        show_default=False,
        default=None,
    )

    env_path = Prompt.ask(
        "[bold magenta]TrueFoundry:[/] Enter .env file location for environment variables, "
        "or press [green]Enter[/] to skip.",
        console=console,
    )
    if workspace_fqn is None:
        workspace_fqn = Prompt.ask(
            "[bold magenta]TrueFoundry:[/] Enter the Workspace FQN where you would like to deploy, [dim]"
            "Ex: cluster-name:workspace-name[/]"
        )
    env = {}
    while True:
        try:
            env = _parse_env(project_root_path, env_path) if env_path else {}
            break
        except FileNotFoundError:
            console.print("[red]Invalid location for .env[/]")
            env_path = Prompt.ask(
                "[bold magenta]TrueFoundry:[/]Please provide the correct path,"
                "or press [green]Enter[/] to skip.",
                console=console,
            )
            continue
    status = console.status(
        "[bold cyan]Starting up:[/] [bold magenta]TrueFoundry[/] is initializing. Please wait..."
    )
    with status:
        developer = Developer(
            project_root_path=project_root_path,
            openai_client=openai_client,
            docker_client=docker_client,
            environment=env,
        )
        developer_run = developer.run(developer.Request(command=command, name=name))
        inp = None
        response = None
        while True:
            try:
                status.start()
                event = developer_run.send(inp)
                _update_status(
                    event=event, status=status, component_type=component_type
                )
                inp = event.render(console)
            except StopIteration as ex:
                response = ex.value
                break

    if deploy:
        console.rule("[bold green]Deploying to TrueFoundry[/]")
        deploy_component(
            workspace_fqn=workspace_fqn,
            project_root_path=project_root_path,
            dockerfile_path=response.dockerfile_path,
            name=name,
            component_type=component_type,
            env=env,
            command=response.command,
            port=response.port,
        )


@click.command(name="auto-deploy", cls=COMMAND_CLS)
@click.option(
    "--path", type=click.STRING, required=True, help="The root path of the project"
)
@click.option(
    "--deploy",
    type=click.BOOL,
    is_flag=True,
    default=True,
    show_default=True,
    help="Deploy the project after successfully building it.",
)
def autodeploy_cli(path: str, deploy: bool):
    """
    Build and deploy projects using TrueFoundry
    """
    cli(
        project_root_path=path,
        deploy=deploy,
    )
