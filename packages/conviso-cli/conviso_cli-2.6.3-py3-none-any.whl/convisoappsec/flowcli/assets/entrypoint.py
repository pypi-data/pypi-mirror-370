import click

from convisoappsec.flowcli import help_option
from .ls import ls
from .create import create


@click.group()
@help_option
def assets():
    pass


assets.add_command(ls)
assets.add_command(create)


assets.epilog = '''
  Run 'conviso assets COMMAND --help' for more information on a command.
'''
