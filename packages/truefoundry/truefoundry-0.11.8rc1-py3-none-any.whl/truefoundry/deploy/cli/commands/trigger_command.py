from typing import Optional, Sequence

import rich_click as click
from click import ClickException

from truefoundry.cli.const import COMMAND_CLS, GROUP_CLS
from truefoundry.cli.util import handle_exception_wrapper
from truefoundry.deploy.lib.dao import application


@click.group(name="trigger", cls=GROUP_CLS)
def trigger_command():
    """
    Trigger a Job asynchronously
    """
    pass


@click.command(
    name="job",
    cls=COMMAND_CLS,
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@click.option(
    "--application-fqn",
    "--application_fqn",
    type=click.STRING,
    required=True,
    help="FQN of the deployment of the Job. This can be found on the Job details page.",
)
@click.option("--command", type=click.STRING, required=False, help="Command to run")
@click.argument(
    "params",
    type=click.STRING,
    nargs=-1,
    required=False,
)
@click.option(
    "--run-name-alias",
    "--run_name_alias",
    type=click.STRING,
    required=False,
    help="Alias for the job run name.",
)
@handle_exception_wrapper
def trigger_job(
    application_fqn: str,
    params,
    command: Optional[Sequence[str]],
    run_name_alias: Optional[str],
):
    """
    Trigger a Job on TrueFoundry asynchronously

        [b]tfy trigger job --application-fqn "my-cluster:my-workspace:my-job"[/]

    \n
    Additionally, you can either pass `--command` or params (if defined in the spec)\n


    Passing a command:

        [b]tfy trigger job --application-fqn "my-cluster:my-workspace:my-job" --command "python run.py"[/]
    \n

    Passing params:

        [b]tfy trigger job --application-fqn "my-cluster:my-workspace:my-job" -- --param1_name param1_value --param2_name param2_value ...[/]
    \n

    passing run_name_alias:
        [b]tfy trigger job --application-fqn "my-cluster:my-workspace:my-job" --run_name_alias "my_run_alias"[/]
    """
    if params:
        params_dict = {}
        if len(params) % 2 != 0:
            raise ClickException(
                f"Found odd number of argument pairs: {params}. "
                "Perhaps you forgot to pass a value for one of the params? "
                "Job params should be passed in the "
                "format `--param1_name param1_value --param2_name param2_value ...`"
            )
        for i in range(0, len(params), 2):
            key = params[i]
            value = params[i + 1]
            if not key.startswith("--"):
                raise ClickException(
                    f"Got ambiguous argument {key!r} in params: {params}. "
                    f"Param names should be prefixed with '--' i.e. "
                    "Job params should be passed in the "
                    "format `--param1_name param1_value --param2_name param2_value ...`"
                )
            key = key.lstrip("-")
            params_dict[key] = value

    application.trigger_job(
        application_fqn=application_fqn,
        command=command,
        params=params,
        run_name_alias=run_name_alias,
    )


@click.command(
    name="workflow",
    cls=COMMAND_CLS,
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@click.option(
    "--application-fqn",
    "--application_fqn",
    type=click.STRING,
    required=True,
    help="FQN of the workflow application",
)
@click.argument(
    "inputs",
    type=click.STRING,
    nargs=-1,
    required=False,
)
@handle_exception_wrapper
def trigger_workflow(application_fqn: str, inputs):
    """
    Trigger a Workflow on TrueFoundry

        [b]tfy trigger workflow --application-fqn "my-cluster:my-workspace:my-workflow"[/]

    \n
    Additionally, you can pass inputs (if defined in the workflow)\n\n

    Passing inputs:

        [b]tfy trigger workflow --application-fqn "my-cluster:my-workspace:my-workflow" -- --input1_name input1_value --input2_name input2_value ...[/]
    """
    if inputs:
        inputs_dict = {}
        if len(inputs) % 2 != 0:
            raise ClickException(
                f"Found odd number of argument pairs: {inputs}. "
                "Perhaps you forgot to pass a value for one of the inputs? "
                "inputs for workflow should be passed in the "
                "format `--input1_name input1_value --input2_name input2_value ...`"
            )
        for i in range(0, len(inputs), 2):
            key = inputs[i]
            value = inputs[i + 1]
            if not key.startswith("--"):
                raise ClickException(
                    f"Got ambiguous argument {key!r} in inputs: {inputs}. "
                    f"input names should be prefixed with '--' i.e. "
                    "inputs for workflow should be passed in the "
                    "format `--input1_name input1_value --input2_name input2_value ...`"
                )
            key = key.lstrip("-")
            inputs_dict[key] = value

    application.trigger_workflow(application_fqn=application_fqn, inputs=inputs)


def get_trigger_command():
    trigger_command.add_command(trigger_job)
    trigger_command.add_command(trigger_workflow)
    return trigger_command
