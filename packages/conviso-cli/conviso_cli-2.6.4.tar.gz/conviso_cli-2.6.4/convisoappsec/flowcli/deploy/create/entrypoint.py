import click

from convisoappsec.flowcli import help_option
from convisoappsec.flowcli.common import DeployFormatter

from .context import pass_create_context
from .with_ import with_


@click.group()
@click.option(
    '-f',
    '--output-format',
    required=False,
    type=click.Choice(DeployFormatter.FORMATS()),
    default=DeployFormatter.DEFAULT,
    show_default=True,
)
@help_option
@pass_create_context
def create(create_context, output_format):
    create_context.output_formatter = DeployFormatter(
        format=output_format,
    )


create.add_command(with_)

create.epilog = '''
  Run flow deploy create COMMAND --help for more information on a command.
'''
