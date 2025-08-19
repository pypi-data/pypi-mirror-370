import click

from convisoappsec.flowcli import help_option

from .values import values
from .tag_tracker import tag_tracker


@click.group('with')
@help_option
def with_():
    pass


with_.add_command(values)
with_.add_command(tag_tracker)

with_.epilog = '''
  Run flow deploy create with COMMAND --help for more information on a command.
'''
