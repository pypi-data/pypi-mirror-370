import os

import click
import click_log
from convisoappsec.flow import api
from convisoappsec.flow.util.ci_provider import CIProvider
from convisoappsec.flowcli import help_option
from convisoappsec.flowcli.common import process_ci_provider_option
from convisoappsec.flowcli.iac.entrypoint import iac
from convisoappsec.logger import LOGGER
from convisoappsec.version import __version__

from .ast import ast
from .context import pass_flow_context
from .findings import findings
from .sast import sast
from .sca import sca
from .vulnerability import vulnerability
from .assets import assets
from .sbom import sbom
from .container import container

click_log.basic_config(LOGGER)

@click.group()
@click_log.simple_verbosity_option(LOGGER, '-l', '--verbosity')
@click.option(
    '-k',
    '--api-key',
    show_envvar=True,
    envvar=("CONVISO_API_KEY", "FLOW_API_KEY"),
    help="The api key to access Conviso Platform resources.",
)
@click.option(
    '-u',
    '--api-url',
    show_envvar=True,
    envvar=("CONVISO_API_URL", "FLOW_API_URL"),
    default=api.DEFAULT_API_URL,
    show_default=True,
    help='The api url to access Conviso Platform resources.',
)
@click.option(
    '-i',
    '--api-insecure',
    show_envvar=True,
    envvar=("CONVISO_API_INSECURE", "FLOW_API_INSECURE"),
    default=False,
    show_default=True,
    is_flag=True,
    help='HTTPS requests to untrusted hosts is enable.',
)
@click.option(
    '-c',
    '--ci-provider-name',
    show_envvar=True,
    envvar="CI_PROVIDER_NAME",
    type=click.Choice(CIProvider.names()),
    default=None,
    show_default=True,
    required=False,
    help="The ci provider used by project. "
         "When not informed, an automatic search will be performed."
)
@click.option(
    '--experimental',
    default=False,
    is_flag=True,
    hidden=True,
    help="Enable experimental features.",
)
@help_option
@click.version_option(
    __version__,
    '-v',
    '--version',
    message='%(prog)s %(version)s'
)
@pass_flow_context
def cli(flow_context, api_key, api_url, api_insecure, experimental, ci_provider_name):
    flow_context.key = api_key
    flow_context.url = api_url
    flow_context.insecure = api_insecure
    flow_context.experimental = experimental

    ci_provider = process_ci_provider_option(ci_provider_name, os.environ)
    flow_context.ci_provider = ci_provider
    LOGGER.debug('CI provider name detected: {}'.format(flow_context.ci_provider.name))


cli.add_command(findings)
cli.add_command(sast)
cli.add_command(sca)
cli.add_command(vulnerability)
cli.add_command(ast)
cli.add_command(iac)
cli.add_command(assets)
cli.add_command(sbom)
cli.add_command(container)

cli.epilog = '''
  Run conviso COMMAND --help for more information on a command.
'''
