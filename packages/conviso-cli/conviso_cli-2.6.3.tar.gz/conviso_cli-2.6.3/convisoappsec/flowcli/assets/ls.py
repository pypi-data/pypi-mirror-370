from json import dumps as json_dumps

import click
import click_log

from convisoappsec.flowcli import help_option
from convisoappsec.flowcli.common import on_http_error
from convisoappsec.flowcli.context import pass_flow_context
from convisoappsec.logger import LOGGER

click_log.basic_config(LOGGER)


@click.command()
@click_log.simple_verbosity_option(LOGGER)
@click.option(
    '-c',
    '--company-id',
    type=int,
    required=True,
    help="The company ID to have its resources used.",
)
@click.option(
    '-p',
    '--page',
    type=int,
    default=1,
    show_default=True,
    required=False,
    help="Page to be consulted",
)
@click.option(
    '-l',
    '--limit',
    type=int,
    default=32,
    show_default=True,
    required=False,
    help="Items limit per page.",
)
@help_option
@pass_flow_context
def ls(flow_context, company_id, asset_name="", page=1, limit=32):
    try:
        conviso_api = flow_context.create_conviso_graphql_client()

        perform_command(conviso_api, company_id, asset_name, page, limit)

    except Exception as exception:
        on_http_error(exception)
        raise click.ClickException(str(exception)) from exception


def perform_command(conviso_api, company_id, asset_name="", page=1, limit=32):
    assets_found = conviso_api.assets.get_by_company_id_or_name(
        company_id,
        asset_name,
        page,
        limit
    )

    indented_output = json_dumps(assets_found, indent=2)
    print(indented_output)
