import sys
import click
import traceback
import time
from copy import deepcopy as clone
from base64 import b64decode
from re import search as regex_search
from convisoappsec.flow import GitAdapter
from convisoappsec.flowcli import help_option
from convisoappsec.flowcli.common import (asset_id_option, on_http_error)
from convisoappsec.flowcli.context import pass_flow_context
from convisoappsec.sast.decision import Decision, Severity
from convisoappsec.sast.sastbox import SASTBox
from convisoappsec.flowcli.requirements_verifier import RequirementsVerifier
from docker.errors import APIError
from convisoappsec.logger import LOGGER
from convisoappsec.common.cleaner import Cleaner


def log_func(msg, new_line=True):
    click.echo(msg, nl=new_line, err=True)


def find_blocked_issues(
        results_filepaths, overall_threshold, severity_threshold, severity
):
    blocked_issues = []

    for result_path in results_filepaths:
        report_decision = Decision(result_path)

        overall_policy = report_decision.block_from_findings(overall_threshold)
        severity_policy = report_decision.block_from_severity(
            severity, severity_threshold
        )

        if overall_policy or severity_policy:
            blocked_issues.append(report_decision)
            click.echo(
                "Failing execution due one or more blocking flags", file=sys.stderr
            )

        click.echo(result_path)

    return blocked_issues


def print_blocked_issues(blocked_issues):
    for issue_decision in blocked_issues:
        issues = issue_decision.filtered_issues()

        for issue in issues:
            click.echo(
                "{issue_name}\n{filepath} at line {line_index}\n".format(
                    issue_name=issue["title"],
                    filepath=issue["filename"],
                    line_index=issue["line"],
                )
            )
    pass


def perform_sastbox_scan(
    conviso_rest_api, sastbox_registry, sastbox_repository_name, sastbox_tag, sastbox_skip_login, repository_dir, end_commit, start_commit, logger
):

    max_retries = 5
    retries = 0
    sastbox = SASTBox(registry=sastbox_registry, repository_name=sastbox_repository_name, tag=sastbox_tag)
    pull_progress_bar = click.progressbar(length=sastbox.size, label="Performing SAST download...")

    while retries < max_retries:
        try:
            if not sastbox_skip_login:
                logger("Checking SASTBox authorization...")
                token = conviso_rest_api.docker_registry.get_sast_token()
                sastbox.login(token)

            with pull_progress_bar as progressbar:
                for downloaded_chunk in sastbox.pull():
                    progressbar.update(downloaded_chunk)
            break
        except APIError as e:
            retries += 1
            logger(f"Retrying {retries}/{max_retries}...")
            time.sleep(1)

            if retries == max_retries:
                logger("Max retries reached. Failed to perform SAST download.")
                raise Exception(f"Max retries reached. Could not complete the SAST download. Error: {str(e)}")

    logger("Starting SAST scan diff...")

    reports = sastbox.run_scan_diff(repository_dir, end_commit, start_commit, log=logger)

    logger("SAST scan diff done.")

    results_filepaths = []
    for r in reports:
        try:
            file_path = str(r)
            results_filepaths.append(file_path)
        except Exception as e:
            click.echo(f"Error decoding file path: {r} with error {e}.", file=sys.stderr)

    return results_filepaths


def parse_conviso_references(references=[]):
    divider = "\n"

    references_to_join = []

    for reference in references:
        if reference:
            references_to_join.append(reference)

    return divider.join(references_to_join)


def parse_code_snippet(encoded_base64):
    try:
        decoded_text = b64decode(encoded_base64).decode("utf-8")
    except UnicodeDecodeError:
        try:
            decoded_text = b64decode(encoded_base64, validate=False).decode("latin-1")
        except Exception as e:
            print("Error handling decoding error:", e, file=sys.stderr)
            decoded_text = ''

    lines = decoded_text.split("\n")

    cleaned_lines = []
    for line in lines:
        cleaned_line = line.split(": ", 1)[-1]
        cleaned_lines.append(cleaned_line)

    code_snippet = "\n".join(cleaned_lines)

    return code_snippet


def parse_first_line_number(encoded_base64):
    try:
        decoded_text = b64decode(encoded_base64).decode("utf-8")
    except UnicodeDecodeError:
        try:
            decoded_text = b64decode(encoded_base64, validate=False).decode("latin-1")
        except Exception as e:
            print("Error handling decoding error:", e, file=sys.stderr)
            decoded_text = ''

    regex = r"^(\d+):"

    result = regex_search(regex, decoded_text)

    if result and result.group(1):
        return result.group(1)

    line_number_when_not_found = 1
    return line_number_when_not_found


def deploy_results_to_conviso_beta(
        flow_context, results_filepaths, asset_id, company_id, commit_ref=None, deploy_id=None, control_sync_status_id=None
):
    """Send SAST results to the Conviso platform."""

    results_context = click.progressbar(
        results_filepaths, label="🔧 Sending SAST report to the Conviso Platform ..."
    )

    with results_context as reports:
        for report_path in reports:
            api_key = flow_context.key
            max_retries = 5
            conviso_api = flow_context.create_conviso_graphql_client()

            for attempt in range(1, max_retries + 1):
                try:
                    conviso_api.issues.send_issues_file(
                        company_id=company_id, asset_id=asset_id, file_path=report_path, api_key=api_key,
                        vulnerability_type='SAST_FINDING',
                        deploy_id=deploy_id, commit_ref=commit_ref, control_sync_status_id=control_sync_status_id
                    )
                    break
                except Exception as e:
                    if attempt == max_retries:
                        print(f"Failed after {max_retries} attempts: {e}")
                    else:
                        wait_time = 2 ** attempt  # Exponential backoff (2s, 4s, 8s, 16s)
                        print(f"Retry {attempt}/{max_retries} failed. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)


@click.command()
@asset_id_option(required=False)
@click.option(
    "-s",
    "--start-commit",
    required=False,
    help="If no value is set so the empty tree hash commit is used.",
)
@click.option(
    "-e",
    "--end-commit",
    required=False,
    help="""If no value is set so the HEAD commit
    from the current branch is used""",
)
@click.option(
    "-r",
    "--repository-dir",
    default=".",
    show_default=True,
    type=click.Path(
        exists=True,
        resolve_path=True,
    ),
    required=False,
    help="The source code repository directory.",
)
@click.option(
    "--fail-on-severity-threshold",
    required=False,
    help="If the threshold of the informed severity and higher has reach, then the command will fail after send the results to AppSec Flow.\n \
    The severity levels are: UNDEFINED, INFO, LOW, MEDIUM, HIGH, CRITICAL.",
    type=click.Tuple([str, int]),
    default=(None, None),
)
@click.option(
    "--fail-on-threshold",
    required=False,
    help="If the threshold has reach then the command will fail after send the result to AppSec Flow",
    type=int,
    default=False,
)
@click.option(
    "--send-to-flow/--no-send-to-flow",
    default=True,
    show_default=True,
    required=False,
    hidden=True,
    help="""Enable or disable the ability of send analysis result
    reports to flow.""",
)
@click.option(
    "--deploy-id",
    default=None,
    required=False,
    hidden=True,
    envvar=("CONVISO_DEPLOY_ID", "FLOW_DEPLOY_ID")
)
@click.option(
    "--sastbox-registry",
    default="",
    required=False,
    hidden=True,
    envvar=("CONVISO_SASTBOX_REGISTRY", "FLOW_SASTBOX_REGISTRY"),
)
@click.option(
    "--sastbox-repository-name",
    default="",
    required=False,
    hidden=True,
    envvar=("CONVISO_SASTBOX_REPOSITORY_NAME", "FLOW_SASTBOX_REPOSITORY_NAME"),
)
@click.option(
    "--sastbox-tag",
    default=SASTBox.DEFAULT_TAG,
    required=False,
    hidden=True,
    envvar=("CONVISO_SASTBOX_TAG", "FLOW_SASTBOX_TAG"),
)
@click.option(
    "--sastbox-skip-login/--sastbox-no-skip-login",
    default=False,
    required=False,
    hidden=True,
    envvar=("CONVISO_SASTBOX_SKIP_LOGIN", "FLOW_SASTBOX_SKIP_LOGIN"),
)
@click.option(
    '--experimental',
    default=False,
    is_flag=True,
    hidden=True,
    help="Enable experimental features.",
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
    hidden=True,
    help="Enable auto fixing vulnerabilities on cp.",
)
@click.option(
    '--from-ast',
    default=False,
    is_flag=True,
    hidden=True,
    help="Internal use only.",
)
@click.option(
    '--cleanup',
    default=False,
    is_flag=True,
    show_default=True,
    help="Clean up system resources, including temporary files, stopped containers, unused Docker images and volumes.",
)
@click.option(
    '--control-sync-status-id',
    required=False,
    hidden=True,
    help="Control sync status id.",
)
@help_option
@pass_flow_context
@click.pass_context
def run(context, flow_context, asset_id, company_id, end_commit, start_commit, repository_dir, send_to_flow, deploy_id,
        sastbox_registry, sastbox_repository_name, sastbox_tag, sastbox_skip_login, fail_on_threshold, fail_on_severity_threshold,
        experimental, asset_name, vulnerability_auto_close, from_ast, cleanup, control_sync_status_id):
    """
    This command will perform SAST analysis at the source code. The analysis
    results can be reported or not to flow application. The analysis can be
    applied to specific commit range.

    This command will write the analysis reports files paths to stdout.
    """
    if not from_ast:
        prepared_context = RequirementsVerifier.prepare_context(clone(context))

        params_to_copy = [
            'asset_id', 'company_id', 'start_commit', 'end_commit',
            'repository_dir', 'send_to_flow', 'deploy_id', 'sastbox_registry',
            'sastbox_repository_name', 'sastbox_tag', 'sastbox_skip_login',
            'experimental', 'asset_name', 'vulnerability_auto_close', 'company_id',
            'cleanup'
        ]

        for param_name in params_to_copy:
            context.params[param_name] = (
                    locals()[param_name] or prepared_context.params[param_name]
            )

    perform_command(flow_context, context.params['asset_id'], context.params['deploy_id'], context.params['end_commit'], context.params['start_commit'],
                    context.params['repository_dir'], context.params['send_to_flow'], context.params['sastbox_registry'],
                    context.params['sastbox_repository_name'], context.params['sastbox_tag'], context.params['sastbox_skip_login'],
                    context.params['fail_on_threshold'], context.params['fail_on_severity_threshold'], context.params['experimental'],
                    context.params['company_id'], context.params['cleanup'], from_ast, control_sync_status_id)

def perform_command(flow_context, asset_id, deploy_id, end_commit, start_commit, repository_dir, send_to_flow, sastbox_registry, sastbox_repository_name, sastbox_tag,
                    sastbox_skip_login, fail_on_threshold, fail_on_severity_threshold, experimental, company_id, cleanup, from_ast, control_sync_status_id):

    if send_to_flow and experimental and not asset_id:
        raise click.MissingParameter(
            "It is required when sending reports to Conviso Platform using experimental API.",
            param_type="option",
            param_hint="--asset-id",
        )

    severity, severity_threshold = fail_on_severity_threshold
    overall_threshold = fail_on_threshold

    if severity and not Severity.has_value(severity):
        raise click.BadParameter(
            "{} is not a valid Severity. Use a valid Severity value:\n{}".format(
                severity, [severity.name for severity in Severity]
            ),
            param_hint="--fail-on-severity-threshold",
        )

    try:
        git_adapter = GitAdapter(repository_dir)

        end_commit = end_commit or git_adapter.head_commit

        start_commit = start_commit or git_adapter.empty_repository_tree_commit

        if start_commit == end_commit:
            click.echo(
                "Previous commit ({0}) and current commit ({1}) are the same; nothing to do.".format(
                    start_commit, end_commit
                ),
                file=sys.stderr,
            )
            return

        conviso_rest_api = flow_context.create_conviso_rest_api_client()

        results_filepaths = perform_sastbox_scan(
            conviso_rest_api, sastbox_registry, sastbox_repository_name, sastbox_tag, sastbox_skip_login, repository_dir, end_commit, start_commit, log_func,
        )

        if send_to_flow:
            deploy_results_to_conviso_beta(
                flow_context, results_filepaths, asset_id, company_id, commit_ref=end_commit, deploy_id=deploy_id, control_sync_status_id=control_sync_status_id
            )

        blocked_issues = find_blocked_issues(
            results_filepaths, overall_threshold, severity_threshold, severity
        )

        if blocked_issues:
            print_blocked_issues(blocked_issues)
            sys.exit(1)

        if cleanup and from_ast == False:
            LOGGER.info("🧹 Cleaning up ...")
            cleaner = Cleaner()
            cleaner.cleanup()

    except Exception as e:
        traceback.print_exc()
        on_http_error(e)
        raise click.ClickException(str(e)) from e


EPILOG = """
Examples:

  \b
  1 - Reporting the results to flow api:
    1.1 - Running an analysis at all commit range:
      $ export CONVISO_API_KEY='your-api-key'
      $ {command}

    \b
    1.2 - Running an analysis at specific commit range:
      $ export CONVISO_API_KEY='your-api-key'
      $ {command} --start-commit "$(git rev-parse HEAD~5)" --end-commit "$(git rev-parse HEAD)"

    \b
  2 - Using flags to break the job on findings ocurrence:
    2.1 - Running an analysis and break the build if there is 10 findings or more:
      $ export CONVISO_API_KEY='your-api-key'
      $ {command} --fail-on-threshold 10
    \b
    2.2 - Running an analysis and break the build if there is 5 findings with HIGH severity or higher
      $ export CONVISO_API_KEY='your-api-key'
      $ {command} --fail-on-severity-threshold HIGH 5
"""  # noqa: E501

SHORT_HELP = "Perform SAST analysis"

command = "conviso sast run"
run.short_help = SHORT_HELP
run.epilog = EPILOG.format(
    command=command,
)
