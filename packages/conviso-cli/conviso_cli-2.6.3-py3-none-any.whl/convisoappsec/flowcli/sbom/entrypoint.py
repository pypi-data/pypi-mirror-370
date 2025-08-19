import click

from convisoappsec.flowcli import help_option
from .generate import generate


@click.group()
@help_option
def sbom():
    pass


sbom.add_command(generate)

sbom.epilog = '''
  Run conviso sbom COMMAND --help for more information on a command.
'''
