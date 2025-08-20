import shutil
import click
import subprocess
import tempfile
import os
from convisoappsec.flowcli.context import pass_flow_context
from datetime import datetime
from convisoappsec.flowcli.requirements_verifier import RequirementsVerifier
from convisoappsec.flowcli import help_option
from convisoappsec.flowcli.common import asset_id_option


@click.command()
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
    "--custom-sca-tags",
    hidden=True,
    required=False,
    multiple=True,
    type=(str, str),
    help="""It should be passed as <repository_name> <image_tag>. It accepts multiple values"""
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
    '--control-sync-status-id',
    required=False,
    hidden=True,
    help="Control sync status id.",
)
@help_option
@pass_flow_context
@click.pass_context
def generate(context, flow_context, asset_id, company_id, repository_dir, send_to_flow, custom_sca_tags,
             scanner_timeout, parallel_workers, deploy_id, experimental, asset_name, vulnerability_auto_close,
             from_ast, control_sync_status_id):
    # Prepare context if not coming from AST
    if not from_ast:
        try:
            prepared_context = RequirementsVerifier.prepare_context(context)
        except Exception as e:
            log_func(f"⚠️ Error preparing context: {e}. Exiting.")
            return

        # Copy parameters from locals or prepared_context
        params_to_copy = [
            'asset_id', 'company_id', 'repository_dir', 'send_to_flow',
            'deploy_id', 'custom_sca_tags', 'scanner_timeout', 'parallel_workers',
            'experimental', 'asset_name', 'vulnerability_auto_close'
        ]
        for param_name in params_to_copy:
            context.params[param_name] = (
                locals()[param_name] or prepared_context.params[param_name]
            )

    # Generate SBOM file
    log_func("💬 Generating SBOM file...")
    try:
        asset_name = context.params['asset_name']
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        sanitized_asset_name = (asset_name or "").replace(" ", "_").replace("(", "").replace(")", "")
        file_name = os.path.join(temp_dir, f"sbom_{sanitized_asset_name}_{timestamp}.json")

        command = f"cdxgen -o {file_name}"

        catalogers = [
            '-github-actions',
            '-python-installed-package-cataloger',
            '-sbom-cataloger',
            '-file-content-cataloger',
            '-file-digest-cataloger',
            '-file-executable-cataloger',
            '-file-metadata-cataloger'
        ]

        try:
            if command_exists('cdxgen'):
                subprocess.run(command, shell=True, check=True, capture_output=True)
            else:
                raise FileNotFoundError("cdxgen not found")

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"[!] cdxgen failed ({e}), falling back to syft...")
            subprocess.run(
                "curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b conviso/",
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            command = [f"./conviso/syft scan {repository_dir} -o cyclonedx-json={file_name} "
                       f"--select-catalogers '{','.join(catalogers)}'"]

            subprocess.run(command, shell=True, check=True, capture_output=True)

        directory = 'conviso/'
        if os.path.isdir(directory):
            shutil.rmtree(directory)

        log_func("✅ SBOM file generated successfully!")
    except subprocess.CalledProcessError as error:
        log_func(f"⚠️ Error generating SBOM file: {error}.")
        return
    except Exception as e:
        log_func(f"⚠️ Unexpected error during SBOM generation: {e}")
        return

    # Ensure asset_id and company_id is available
    asset_id = asset_id or context.params.get('asset_id')
    company_id = company_id or context.params.get('company_id')

    if not asset_id:
        log_func(f"⚠️ Missing asset_id. Unable to send SBOM.")
        return

    # Send SBOM file to CSC (Conviso Platform)
    try:
        send_sbom_file_to_csc(company_id=company_id, asset_id=asset_id, file=file_name)
    except Exception as e:
        log_func(f"⚠️ Error sending SBOM file to Conviso: {e}")
        return


@pass_flow_context
def send_sbom_file_to_csc(flow_context, company_id, asset_id, file):
    try:
        conviso_api = flow_context.create_conviso_graphql_client()
        api_key = flow_context.key

        log_func("💬 Sending SBOM to the Conviso Platform...")
        conviso_api.sbom.send_sbom_file(company_id=company_id, asset_id=asset_id, file_path=file, api_key=api_key)
        log_func("✅ SBOM file sent successfully!")
    except Exception as e:
        log_func(f"⚠️ Failed to send SBOM file: {e}")


def command_exists(command):
    return shutil.which(command) is not None


def log_func(msg, new_line=True):
    click.echo(click.style(msg), nl=new_line, err=True)
