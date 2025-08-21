import click
import click_log

from convisoappsec.common.git_data_parser import GitDataParser
from convisoappsec.flow.graphql_api.v1.models.asset import AssetInput
from convisoappsec.flowcli import help_option
from convisoappsec.flowcli.common import on_http_error
from convisoappsec.flowcli.context import pass_flow_context
from convisoappsec.logger import LOGGER

click_log.basic_config(LOGGER)


def parse_repository_name(repository_dir, asset_name=None):
    has_user_input = asset_name != None
    if has_user_input:
        return asset_name

    return GitDataParser(repository_dir).parse_name()


@click.command()
@click_log.simple_verbosity_option(LOGGER)
@click.option(
    "-c",
    "--company-id",
    type=int,
    required=True,
    help="The Company ID from your organization in Conviso Platform.",
)
@click.option(
    "-r",
    "--repository-dir",
    type=click.Path(exists=True, resolve_path=True),
    default=".",
    show_default=True,
    required=True,
    help="The directory path for the asset.",
)
@click.option(
    "--name",
    type=str,
    default=None,
    show_default=False,
    required=False,
    help="Customize the Asset name.",
)
@click.option(
    "--scan-type",
    type=str,
    default="None",
    show_default=True,
    required=False,
    help="Customize the Asset scan type.",
)
@help_option
@pass_flow_context
def create(flow_context, company_id, repository_dir, name, scan_type):
    try:
        conviso_api = flow_context.create_conviso_graphql_client()

        perform_command(conviso_api, company_id, repository_dir, name, scan_type)

    except Exception as exception:
        on_http_error(exception)
        raise click.ClickException(str(exception)) from exception


def perform_command(
    conviso_api,
    company_id,
    repository_dir,
    name,
    scan_type,
):
    asset_name = parse_repository_name(repository_dir, name)

    asset_model = AssetInput(
        company_id,
        asset_name,
        scan_type,
    )

    print('Creating new asset to repository: "{}"'.format(repository_dir))
    asset = conviso_api.assets.create_asset(asset_model)

    asset_url = conviso_api.assets.get_asset_url(company_id, asset["id"])
    print("The created Asset is available at Conviso Platform: {}".format(asset_url))
