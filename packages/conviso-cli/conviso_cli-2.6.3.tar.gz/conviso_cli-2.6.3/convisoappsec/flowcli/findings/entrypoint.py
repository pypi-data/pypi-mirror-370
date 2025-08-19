import click

from convisoappsec.flowcli import help_option
from .create import create
from .import_sarif import import_sarif


@click.group()
@help_option
def findings():
    pass


findings.add_command(create)
findings.add_command(import_sarif)

findings.epilog = '''
  Run flow findings COMMAND --help for more information on a command.
'''
