import click

from convisoappsec.flowcli import help_option

from .time_ import time_
from .versioning_style import versioning_style


@click.group()
@help_option
def sort_by():
    pass


sort_by.add_command(time_)
sort_by.add_command(versioning_style)

sort_by.epilog = '''
  Run flow deploy create with tag-tracker sort-by COMMAND --help
  for more information on a command.
'''
