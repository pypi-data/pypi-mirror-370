import subprocess
import traceback
import click
from convisoappsec.flowcli import help_option
from convisoappsec.flowcli.common import CreateDeployException, DeployFormatter, PerformDeployException, asset_id_option
from convisoappsec.flowcli.deploy.create.context import pass_create_context
from convisoappsec.flowcli.deploy.create.with_.values import values
from convisoappsec.flowcli.requirements_verifier import RequirementsVerifier
from convisoappsec.flowcli.sast import sast
from convisoappsec.flowcli.sca import sca
from convisoappsec.flowcli.iac import iac
from convisoappsec.flowcli.vulnerability import vulnerability
from copy import deepcopy as clone
from convisoappsec.flow import GitAdapter
from convisoappsec.flowcli.context import pass_flow_context
from convisoappsec.logger import LOGGER, log_and_notify_ast_event
from convisoappsec.common.cleaner import Cleaner


def get_default_params_values(cmd_params):
    """ Further information in https://click.palletsprojects.com/en/8.1.x/api/?highlight=params#click.Command.params

    Args:
        cmd_params (List[click.core.Parameter]):

    Returns:
        dict: default params values dictionarie
    """
    default_params = {}
    for param in cmd_params:
        unwanted = param.name in ['help', 'verbosity']
        if not unwanted:
            default_params.update({param.name: param.default})
    return default_params


def parse_params(ctx_params: dict, expected_params: list):
    """ Parse the params from the context extracting the expected params values to the context.

    Args:
        ctx_params (dict): context params: Further information at https://click.palletsprojects.com/en/8.1.x/api/?highlight=context%20param#click.Context.params
        expected_params (list): Further information at https://click.palletsprojects.com/en/8.1.x/api/?highlight=params#click.Command.params

    Returns:
        dict: parsed_params: parsed params as key and value
    """
    parsed_params = get_default_params_values(expected_params)
    for param in ctx_params:
        if param in parsed_params:
            parsed_params.update({param: ctx_params.get(param)})
    return parsed_params


def perform_sast(context, control_sync_status_id) -> None:
    """Setup and runs the "sast run" command.

    Args:
        context (<class 'click.core.Context'>): cloned context
        control_sync_status_id (str): control sync status id
    """
    sast_run = sast.commands.get('run')

    specific_params = {
        "deploy_id": context.obj.deploy['deploy_id'],
        "start_commit": context.obj.deploy['previous_commit'],
        "end_commit": context.obj.deploy['current_commit'],
        "control_sync_status_id": control_sync_status_id
    }
    context.params.update(specific_params)
    context.params = parse_params(context.params, sast_run.params)
    try:
        LOGGER.info(
            'Running SAST on deploy ID "{deploy_id}"...'
            .format(deploy_id=context.params["deploy_id"])
        )
        sast_run.invoke(context)

    except Exception as err:
        raise click.ClickException(str(err)) from err


def perform_sca(context, control_sync_status_id) -> None:
    """Setup and runs the "sca run" command.

    Args:
        context (<class 'click.core.Context'>): cloned context
        control_sync_status_id (str): control sync status id
    """
    sca_run = sca.commands.get('run')
    context.params.update(
        {"deploy_id": context.obj.deploy['deploy_id'],
        "control_sync_status_id": control_sync_status_id}
    )

    context.params = parse_params(context.params, sca_run.params)
    try:
        LOGGER.info(
            'Running SCA on deploy ID "{deploy_id}"...'
            .format(deploy_id=context.params["deploy_id"])
        )
        sca_run.invoke(context)

    except Exception as err:
        raise click.ClickException(str(err)) from err


def perform_iac(context, control_sync_status_id) -> None:
    """Setup and runs the "iac run" command.

    Args:
        context (<class 'click.core.Context'>): clonned context
        control_sync_status_id (str): control sync status id
    """
    iac_run = iac.commands.get('run')
    context.params.update(
        {"deploy_id": context.obj.deploy['deploy_id'],
        "control_sync_status_id": control_sync_status_id}
    )
    context.params = parse_params(context.params, iac_run.params)

    try:
        LOGGER.info(
            'Running IAC on deploy ID "{deploy_id}"...'
            .format(deploy_id=context.params["deploy_id"])
        )
        iac_run.invoke(context)
    except Exception as err:
        raise click.ClickException(str(err)) from err


def perform_vulnerabilities_service(context, company_id) -> None:
    auto_close_run = vulnerability.commands.get('run')

    specific_params = {
        "deploy_id": context.obj.deploy['deploy_id'],
        "start_commit": context.obj.deploy['previous_commit'],
        "end_commit": context.obj.deploy['current_commit'],
        "company_id": context.params['company_id'] or company_id
    }
    context.params.update(specific_params)
    context.params = parse_params(context.params, auto_close_run.params)

    try:
        LOGGER.info("[*] Verifying if any vulnerability was fixed...")
        auto_close_run.invoke(context)
    except Exception as err:
        raise click.ClickException(str(err)) from err


def perform_deploy(context, flow_context, prepared_context):
    context.obj.output_formatter = DeployFormatter(format=DeployFormatter.DEFAULT)
    context.params = parse_params(context.params, values.params)
    repository_dir = context.params['repository_dir']

    try:
        LOGGER.info("Creating new deploy...")
        created_deploy = values.invoke(context)

        if created_deploy is None:
            LOGGER.warning("Deploy with same commits already exists")
            return None

        asset_id = prepared_context.params.get('asset_id')
        if not asset_id:
            raise PerformDeployException("Asset ID is required")

        conviso_api = flow_context.create_conviso_graphql_client()
        api_key = flow_context.key
        git_adapter = GitAdapter(repository_dir)

        branch_name = get_branch_name(git_adapter, repository_dir)

        LOGGER.info(f"Creating deploy: asset_id={asset_id}, "
                    f"previous={created_deploy['previous_commit']}, "
                    f"current={created_deploy['current_commit']}")

        response = conviso_api.deploys.create_deploy(
            asset_id=asset_id,
            previous_commit=created_deploy['previous_commit'],
            current_commit=created_deploy['current_commit'],
            branch_name=branch_name,
            api_key=api_key,
            commit_history=created_deploy['commit_history']
        )

        response_deploy_id = response['createDeploy']['deploy']['id']
        deploy_params = {
            "deploy_id": response_deploy_id,
            "current_commit": created_deploy['current_commit'],
            "previous_commit": created_deploy['previous_commit'],
        }
        created_deploy.update(deploy_params)

        return created_deploy

    except CreateDeployException as err:
        LOGGER.error(f"Error creating deploy: {str(err)}")
        raise PerformDeployException(err)

    except Exception as err:
        error_message = str(err)
        LOGGER.error(f"Unexpected error creating deploy: {error_message}")

        if "A deploy with the same previous and current commit already exists" in error_message:
            LOGGER.warning("Deploy with same commits already exists")
            return None
        else:
            raise PerformDeployException(f"Failed to create deploy: {error_message}") from err


def get_branch_name(git_adapter, repository_dir):
    """Gets branch name"""
    try:
        return git_adapter.get_branch_name()
    except Exception as e:
        LOGGER.warning(f"HEAD is detached or error getting branch: {e}")
        LOGGER.info("Looking for most recent branch...")

        try:
            result = subprocess.run(
                ["git", "for-each-ref", "--sort=-creatordate",
                 "--format=%(refname:short)", "refs/heads/"],
                cwd=repository_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                timeout=10
            )
            branches = result.stdout.decode().strip().splitlines()
            if branches:
                branch_name = branches[0]
                LOGGER.info(f"Using branch: {branch_name}")
                return branch_name
            else:
                LOGGER.warning("No branches found")
                return "unknown"
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            LOGGER.error(f"Error executing git command: {e}")
            return "unknown"


@click.command(
    context_settings=dict(
        allow_extra_args=True,
        ignore_unknown_options=True
    )
)
@asset_id_option(required=False)
@click.option(
    "--send-to-flow/--no-send-to-flow",
    default=True,
    show_default=True,
    required=False,
    help="""Enable or disable the ability of send analysis result
    reports to flow.""",
    hidden=True
)
@click.option(
    '-r',
    '--repository-dir',
    default=".",
    show_default=True,
    type=click.Path(exists=True, resolve_path=True),
    required=False,
    help="""The source code repository directory.""",
)
@click.option(
    "-c",
    "--current-commit",
    required=False,
    help="If no value is given the HEAD commit of branch is used. [DEPLOY]",
)
@click.option(
    "-p",
    "--previous-commit",
    required=False,
    help="""If no value is given, the value is retrieved from the lastest
    deploy at flow application. [DEPLOY]""",
)
@click.option(
    "--company-id",
    required=False,
    envvar=("CONVISO_COMPANY_ID", "FLOW_COMPANY_ID"),
    help="Company ID on Conviso Platform",
)
@click.option(
    '--asset-name',
    required=False,
    envvar=("CONVISO_ASSET_NAME", "FLOW_ASSET_NAME"),
    help="Provides a asset name.",
)
@click.option(
    '--vulnerability-auto-close',
    default=False,
    is_flag=True,
    help="Enable auto fixing vulnerabilities on cp.",
)
@click.option(
    '--cleanup',
    default=False,
    is_flag=True,
    show_default=True,
    help="Clean up system resources, including temporary files, stopped containers, unused Docker images and volumes.",
)
@help_option
@pass_flow_context
@pass_create_context
@click.pass_context
def run(context, create_context, flow_context, **kwargs):
    """ AST - Application Security Testing. Unifies deploy issue, SAST and SCA analyses.  """
    increase_success_count = 1
    increase_failure_count = 1

    try:
        prepared_context = RequirementsVerifier.prepare_context(clone(context), from_ast=True)

        # After ensuring we have both asset and user permissions, AST is ready to start. We then create a control sync status
        # on the Conviso platform, which will appear on the scans page and in the recent scans list.
        conviso_api = flow_context.create_conviso_graphql_client()
        control_sync_status = conviso_api.control_sync_status.create_control_sync_status(
            asset_id=prepared_context.params['asset_id']
        )

        try:
            prepared_context.obj.deploy = perform_deploy(clone(prepared_context), flow_context, prepared_context)

            if prepared_context.obj.deploy is None:
                return

            perform_sast(clone(prepared_context), control_sync_status_id=control_sync_status['id'])
            perform_sca(clone(prepared_context), control_sync_status_id=control_sync_status['id'])
            perform_iac(clone(prepared_context), control_sync_status_id=control_sync_status['id'])

            company_id = prepared_context.params['company_id']

            if context.params['vulnerability_auto_close'] is True:
                try:
                    perform_vulnerabilities_service(clone(prepared_context), company_id)
                except Exception:
                    LOGGER.info("An issue occurred while attempting to fix vulnerabilities. Our technical team has been notified.")
                    full_trace = traceback.format_exc()
                    log_and_notify_ast_event(flow_context=flow_context, company_id=company_id,
                                             asset_id=prepared_context.params['asset_id'], ast_log=full_trace)
                    return

            if context.params.get('cleanup'):
                try:
                    LOGGER.info("🧹 Cleaning up ...")
                    cleaner = Cleaner()
                    cleaner.cleanup()
                except Exception as e:
                    LOGGER.info(f"An error occurred while cleaning up. Our technical team has been notified.")
                    full_trace = traceback.format_exc()
                    log_and_notify_ast_event(
                        flow_context=flow_context, company_id=company_id, asset_id=prepared_context.params['asset_id'],
                        ast_log=full_trace
                    )
                    return

            conviso_api.control_sync_status.update_control_sync_status(control_sync_status_id=control_sync_status['id'])

            # increase success_count by one just to match external_vulnerability_count when ast runs successfully and if
            # success count and external_vulnerability_count are equals, the scan status will be moved from pending to success.
            conviso_api.control_sync_status.increase_count(
                control_sync_status_id=control_sync_status['id'],
                asset_id=prepared_context.params['asset_id'],
                success_count=increase_success_count
            )

        except PerformDeployException as err:
            conviso_api.control_sync_status.increase_count(
                control_sync_status_id=control_sync_status['id'],
                asset_id=prepared_context.params['asset_id'],
                success_count=increase_success_count
            )
            LOGGER.warning(err)

        except Exception as err:
            conviso_api.control_sync_status.increase_count(
                control_sync_status_id=control_sync_status['id'],
                asset_id=prepared_context.params['asset_id'],
                failure_count=increase_failure_count,
                failure_reason=str(err)
            )
            raise click.ClickException(str(err)) from err

    except Exception as err:
        LOGGER.error(f"AST initialization failed. Please contact support with the following error: {err}")
        raise click.ClickException(str(err)) from err


@click.group()
def ast():
    pass


ast.add_command(run)
