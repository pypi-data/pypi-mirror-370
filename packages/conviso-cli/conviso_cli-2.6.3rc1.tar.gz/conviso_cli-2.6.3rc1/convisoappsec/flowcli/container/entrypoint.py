import click

from convisoappsec.flowcli import help_option
from .run import run


@click.group()
@help_option
def container():
    pass


container.add_command(run)

container.epilog = '''
  Run conviso container COMMAND --help for more information on a command.
'''
