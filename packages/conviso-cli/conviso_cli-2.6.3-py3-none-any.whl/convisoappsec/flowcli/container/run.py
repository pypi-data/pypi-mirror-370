import traceback
import click
import json
import subprocess
import shutil
import os
import datetime
from convisoappsec.flowcli import help_option
from convisoappsec.flowcli.context import pass_flow_context
from convisoappsec.logger import log_and_notify_ast_event
from convisoappsec.flowcli.requirements_verifier import RequirementsVerifier
from copy import deepcopy as clone
from convisoappsec.flowcli.common import asset_id_option
from convisoappsec.flowcli.vulnerability.container_vulnerability_manager import ContainerVulnerabilityManager

DEBUG_MODE = False


@click.command()
@asset_id_option(required=False)
@click.option(
    '--debug',
    is_flag=True,
    help='Enable debug mode.'
)
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
    hidden=True,
    help="""Enable or disable the ability of send analysis result
    reports to flow.""",
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
@click.argument('image_name')
@help_option
@pass_flow_context
@click.pass_context
def run(
        context, flow_context, asset_id, debug, company_id, repository_dir,
        send_to_flow, asset_name, vulnerability_auto_close, image_name,

):
    """ Run command for container vulnerability scan focused on OS vulnerabilities """
    global DEBUG_MODE
    DEBUG_MODE = debug
    start_time = datetime.datetime.now()

    if send_to_flow:
        prepared_context = RequirementsVerifier.prepare_context(clone(context))

        if debug:
            debug_message(f"Context after being prepared: {prepared_context.params}")

        params_to_copy = [
            'asset_id', 'send_to_flow', 'asset_name', 'vulnerability_auto_close',
            'repository_dir', 'company_id'
        ]

        for param_name in params_to_copy:
            context.params[param_name] = (
                    locals()[param_name] or prepared_context.params[param_name]
            )

        asset_id = context.params['asset_id']
        company_id = context.params['company_id']
    else:
        # this just verify if the api key is valid.
        RequirementsVerifier.list_assets(company_id=company_id, asset_name='example', scan_type='SAST')

        if debug:
            debug_message("User validated!")

    if command_exists('trivy'):
        if debug:
            debug_message("Trivy already installed.")

        scan_command = f"trivy image --pkg-types os --format json --output result.json {image_name}"
    else:
        if debug:
            debug_message("Installing trivy ...")

        subprocess.run(
            "curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b conviso/ v0.57.1",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if debug:
            debug_message("Trivy has been installed successfully!")

        scan_command = [f"./conviso/trivy image --pkg-types os --format json --output result.json {image_name}"]

    try:
        log_func(f"🔧 Scanning image {image_name} ...")

        if debug:
            debug_message(f"Running the following command: {scan_command}")

        run_command(scan_command)
        log_func("✅ Scan completed successfully.")

        directory = 'conviso/'
        if os.path.isdir(directory):
            if debug:
                debug_message(f"Removing the trivy installation dir, {directory}")
            shutil.rmtree(directory)

        if send_to_flow:
            send_to_conviso_plataform(flow_context, asset_id, company_id)
        else:
            output_results()

        end_time = datetime.datetime.now()

        if debug:
            execution_time = end_time - start_time
            debug_message(f"Total execution time: {execution_time.total_seconds():.2f} seconds.")

        try:
            if vulnerability_auto_close is True:
                vulnerability_manager = ContainerVulnerabilityManager()
                vulnerability_manager.close_vulnerability()
        except Exception:
            log_func("An issue occurred while attempting to fix vulnerabilities. Our technical team has been notified.")
            return

    except Exception as error:
        log_func(f"❌ Scan failed: {error}")


def run_command(command):
    """
    Runs a shell command and logs its execution.

    Args:
        command (str): The scan command to execute.

    Returns:
        The result of a subproccess execution.
    """
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return result

def send_to_conviso_plataform(flow_context, asset_id, company_id):
    """
    Process and send result to conviso platform.

    This method read the result file, parse and try to send all founded vulnerabilities
    If in any part of the process receive an error, should notify the ast-channel on conviso slack.

    Args:
        conviso_api (object): Responsable to comunicate with conviso graphql api.
        flow_content (object): Some helper methods.
        asset_id (int): The asset where the result will be sended.
        company_id (int): The user company on conviso platform.

    Returns:
        str: Could return a message inform about no vulnerabilities or None
    """
    log_func("🔧 Processing results ...")
    result_file = "result.json"

    try:
        vulnerabilities = extract_vulnerabilities(result_file)

        if vulnerabilities:
            log_func("🔍 Sending vulnerabilities to conviso platform.")
            api_key = flow_context.key
            conviso_api = flow_context.create_conviso_graphql_client()
            conviso_api.container.send_container_file(
                company_id=company_id, asset_id=asset_id, file_path=result_file, api_key=api_key
            )
            log_func("✅ Successfully!")
        else:
            log_func("✅ No vulnerabilities found.")

    except FileNotFoundError:
        log_func(f"❌ {result_file} not found. Ensure the scan was successful.")
        full_trace = traceback.format_exc()
        log_and_notify_ast_event(
            flow_context=flow_context, company_id=company_id, asset_id=asset_id, ast_log=full_trace
        )
    except json.JSONDecodeError:
        log_func(f"❌ Failed to parse {result_file}. Ensure it is valid JSON.")
        full_trace = traceback.format_exc()
        log_and_notify_ast_event(
            flow_context=flow_context, company_id=company_id, asset_id=asset_id, ast_log=full_trace
        )
    except Exception:
        full_trace = traceback.format_exc()
        log_func(f"❌ An error occurred while processing results: {full_trace}")
        log_and_notify_ast_event(
            flow_context=flow_context, company_id=company_id, asset_id=asset_id, ast_log=full_trace
        )


def output_results():
    """
    Output the scan result in case the user don't want to send to conviso platform.
    """
    result_file = "result.json"

    try:
        vulnerabilities = extract_vulnerabilities(result_file)

        if vulnerabilities:
            log_func(f"🔍 Found: {len(vulnerabilities)} vulnerabilities!")
        else:
            log_func("✅ No vulnerabilities found.")

    except Exception:
        full_trace = traceback.format_exc()
        log_func(f"❌ An error occurred while processing results: {full_trace}")


def command_exists(command):
    """
    Validates if a command exists.

    Args: command (str): Command to validate.
    Returns:
        bool: True if the command exists.
    """
    return shutil.which(command) is not None

def extract_vulnerabilities(result_file):
    """Reads a JSON scan result file and extracts vulnerabilities."""
    with open(result_file, 'r') as file:
        scan_results = json.load(file)

    results = scan_results.get("Results", [])
    if results and isinstance(results, list) and len(results) > 0:
        return results[0].get("Vulnerabilities", [])

    return []


def log_func(msg, new_line=True):
    """
    Output a message to the console with styled formatting.

    This function uses `click` to output a styled message to the console. It supports
    controlling whether the message ends with a newline and writes the output to `stderr`.

    Args:
        msg (str): The message to log.
        new_line (bool, optional): Whether to append a newline at the end of the message.
            Defaults to True.

    Returns:
        str: The output of the message.
    """
    click.echo(click.style(msg), nl=new_line, err=True)


def debug_message(msg, new_line=True):
    """
    If debug mode is enabled, this function should be
    used for all debug messages and the message will be styled in orange.
    Otherwise, it uses the default styling.

        Args:
        msg (str): The message to log.
        new_line (bool, optional): Whether to append a newline at the end of the message.
            Defaults to True.

    Returns:
        str: The output of the message.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    style = {"fg": "bright_yellow"} if DEBUG_MODE else {}
    click.echo(click.style(f"🪲 [{timestamp}] DEBUG: {msg}", **style), nl=new_line, err=True)
