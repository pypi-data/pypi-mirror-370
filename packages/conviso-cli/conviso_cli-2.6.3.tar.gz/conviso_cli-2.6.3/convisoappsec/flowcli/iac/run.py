import json
import click
import click_log
import traceback
from convisoappsec.common.retry_handler import RetryHandler
from copy import deepcopy as clone
from convisoappsec.common.box import ContainerWrapper
from convisoappsec.flow.graphql_api.beta.models.issues.iac import CreateIacFindingInput
from convisoappsec.flowcli import help_option
from convisoappsec.flowcli.common import asset_id_option, on_http_error
from convisoappsec.flowcli.context import pass_flow_context
from convisoappsec.logger import LOGGER, log_and_notify_ast_event
from convisoappsec.flowcli.requirements_verifier import RequirementsVerifier
from convisoappsec.flow import GitAdapter
from convisoappsec.common.graphql.errors import ResponseError
from convisoappsec.common.cleaner import Cleaner

click_log.basic_config(LOGGER)


@click.command()
@click_log.simple_verbosity_option(LOGGER)
@asset_id_option(required=False)
@click.option(
    '-r',
    '--repository-dir',
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
    "--send-to-flow/--no-send-to-flow",
    default=True,
    show_default=True,
    required=False,
    help="""Enable or disable the ability of send analysis result
    reports to flow.""",
    hidden=True
)
@click.option(
    "--scanner-timeout",
    hidden=True,
    required=False,
    default=7200,
    type=int,
    help="Set timeout for each scanner"
)
@click.option(
    "--parallel-workers",
    hidden=True,
    required=False,
    default=2,
    type=int,
    help="Set max parallel workers"
)
@click.option(
    "--deploy-id",
    default=None,
    required=False,
    hidden=True,
    envvar=("CONVISO_DEPLOY_ID", "FLOW_DEPLOY_ID")
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
@click.option(
    '--control-sync-status-id',
    required=False,
    hidden=True,
    help="Control sync status id.",
)
@help_option
@pass_flow_context
@click.pass_context
def run(context, flow_context, asset_id, company_id, repository_dir, send_to_flow, scanner_timeout,
        parallel_workers, deploy_id, experimental, asset_name, from_ast, cleanup, control_sync_status_id):
    """
      This command will perform IAC analysis at the source code. The analysis
      results can be reported or not to flow application.
    """
    if not from_ast:
        prepared_context = RequirementsVerifier.prepare_context(clone(context))

        params_to_copy = [
            'asset_id', 'company_id', 'repository_dir', 'send_to_flow',
            'deploy_id', 'scanner_timeout', 'parallel_workers', 'experimental', 'cleanup'
        ]

        for param_name in params_to_copy:
            context.params[param_name] = (
                    locals()[param_name] or prepared_context.params[param_name]
            )

    perform_command(
        flow_context, context.params['asset_id'], context.params['company_id'], context.params['repository_dir'],
        context.params['send_to_flow'], context.params['scanner_timeout'], context.params['deploy_id'],
        context.params['experimental'], context.params['cleanup'], from_ast, control_sync_status_id
    )


def deploy_results_to_conviso(
        conviso_api, results_filepaths, asset_id, company_id, flow_context, deploy_id, commit_ref=None, control_sync_status_id=None
):
    results_context = click.progressbar(results_filepaths, label="Sending results to the Conviso Platform...")

    with results_context as reports:
        for report_path in reports:
            try:
                with open(report_path) as report_file:
                    data = parse_data(json.load(report_file))
            except Exception:
                LOGGER.warn(f"⚠️ Error processing report file. Our technical team has been notified.")
                full_trace = traceback.format_exc()
                log_and_notify_ast_event(
                    flow_context=flow_context, company_id=company_id, asset_id=asset_id,
                    ast_log=str(full_trace)
                )
                continue

            for issue in data:
                try:
                    issue_model = CreateIacFindingInput(
                        asset_id=asset_id,
                        file_name=issue.get("file_name"),
                        vulnerable_line=issue.get("vulnerable_line"),
                        title=issue.get("title"),
                        description=issue.get("description"),
                        severity=issue.get("severity"),
                        code_snippet=parse_code_snippet(issue.get("code_snippet")),
                        reference=parse_conviso_references(issue.get("reference", "")),
                        first_line=issue.get("first_line"),
                        category=format_cwe_id(issue.get("cwe")),
                        original_issue_id_from_tool=issue.get('hash_issue', []),
                        solution=issue.get("solution"),
                        control_sync_status_id=control_sync_status_id
                    )

                    conviso_api.issues.create_iac(issue_model)

                except ResponseError as error:
                    if error.code == 'RECORD_NOT_UNIQUE':
                        continue
                    else:
                        retry_handler = RetryHandler(
                            flow_context=flow_context, company_id=company_id, asset_id=asset_id
                        )
                        retry_handler.execute_with_retry(conviso_api.issues.create_iac, issue_model)
                except Exception:
                    retry_handler = RetryHandler(
                        flow_context=flow_context, company_id=company_id, asset_id=asset_id
                    )
                    retry_handler.execute_with_retry(conviso_api.issues.create_iac, issue_model)

                    continue


def perform_command(
        flow_context, asset_id, company_id, repository_dir, send_to_flow, scanner_timeout,
        deploy_id, experimental, cleanup, from_ast, control_sync_status_id
):

    if send_to_flow and experimental and not asset_id:
        raise click.MissingParameter(
            "It is required when sending reports to Conviso Platform using experimental API.",
            param_type="option",
            param_hint="--asset-id",
        )

    try:
        REQUIRED_CODEBASE_PATH = '/code'
        IAC_IMAGE_NAME = 'iac_scanner_checkov'
        IAC_SCAN_FILENAME = '/{}.json'.format(IAC_IMAGE_NAME)
        containers_map = {
            IAC_IMAGE_NAME: {
                'repository_dir': repository_dir,
                'repository_name': IAC_IMAGE_NAME,
                'tag': 'unstable',
                'command': [
                    '-c', REQUIRED_CODEBASE_PATH,
                    '-o', IAC_SCAN_FILENAME,
                ],
            },
        }

        LOGGER.info('💬 Preparing Environment...')
        conviso_rest_api = flow_context.create_conviso_rest_api_client()
        token = conviso_rest_api.docker_registry.get_sast_token()
        scanners_wrapper = ContainerWrapper(
            token=token,
            containers_map=containers_map,
            logger=LOGGER,
            timeout=scanner_timeout
        )

        LOGGER.info('💬 Starting IaC...')
        scanners_wrapper.run()

        results_filepaths = []
        for r in scanners_wrapper.scanners:
            report_filepath = r.results
            if report_filepath:
                results_filepaths.append(report_filepath)

        LOGGER.info('💬 Processing Results...')
        if send_to_flow:
            git_adapater = GitAdapter(repository_dir)
            end_commit = git_adapater.head_commit
            conviso_beta_api = flow_context.create_conviso_api_client_beta()

            deploy_results_to_conviso(
                conviso_beta_api, results_filepaths, asset_id, company_id, flow_context, deploy_id=deploy_id,
                commit_ref=end_commit, control_sync_status_id=control_sync_status_id
            )
        LOGGER.info('✅ IaC Scan Finished.')

        if cleanup and from_ast == False:
            LOGGER.info("🧹 Cleaning up ...")
            cleaner = Cleaner()
            cleaner.cleanup()

    except Exception as e:
        on_http_error(e)
        raise click.ClickException(str(e)) from e


def parse_conviso_references(references=[]):
    DIVIDER = "\n"

    return DIVIDER.join(references)


def parse_code_snippet(code_snippet):
    lines = code_snippet.split("\n")
    cleaned_lines = [line.rstrip() for line in lines if line.strip()]
    code_snippet = "\n".join(cleaned_lines)

    return code_snippet


def format_cwe_id(cwe_input):
    cwe_str = str(cwe_input).strip()

    if cwe_str.upper().startswith("CWE-"):
        return cwe_str
    return f"CWE-{cwe_str}"


def parse_data(sarif_result):
    vulnerabilities = []

    for result in sarif_result['runs'][0]['results']:
        
        vulnerability = {
            'file_name': result['locations'][0]['physicalLocation']['artifactLocation']['uri'],
            'vulnerable_line': result['locations'][0]['physicalLocation']['region']['startLine'],
            'code_snippet': result['locations'][0]['physicalLocation']['contextRegion']['snippet']['text'],
            'title': sarif_result['runs'][0]['tool']['driver']['rules'][result['ruleIndex']]['name'],
            'description': result['message']['text'],
            'severity': result['level'],
            'first_line': result['locations'][0]['physicalLocation']['contextRegion']['startLine'],
            'cwe': result['properties']['cweId'],
            'solution': result['properties']['solution'],
            'hash_issue': result['partialFingerprints']['hashIssueV2']
        }
        vulnerabilities.append(vulnerability)

    return vulnerabilities


EPILOG = '''
Examples:

  \b
  1 - Reporting the results to Conviso Platform API:
    1.1 - Running an analysis at all commit range:
      $ export CONVISO_API_KEY='your-api-key'
      $ {command}

'''  # noqa: E501

SHORT_HELP = "Perform Infrastructure Code analysis"

command = 'conviso iac run'
run.short_help = SHORT_HELP
run.epilog = EPILOG.format(
    command=command,
)
