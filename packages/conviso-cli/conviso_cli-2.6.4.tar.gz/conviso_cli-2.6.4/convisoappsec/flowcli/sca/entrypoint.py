import click

from convisoappsec.flowcli import help_option
from .run import run


@click.group()
@help_option
def sca():
    pass


sca.add_command(run)

sca.epilog = '''
  Run flow sca COMMAND --help for more information on a command.
'''
