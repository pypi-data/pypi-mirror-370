import click

from convisoappsec.flowcli import help_option

from .with_ import with_


@click.group()
@help_option
def create():
    pass


create.add_command(with_)

create.epilog = '''
  Run flow findings create COMMAND --help for more information on a command.
'''
