import click

from convisoappsec.flowcli import help_option

from .context import pass_tag_tracker_context
from .sort_by import sort_by


@click.group()
@help_option
@click.option(
    "-r",
    "--repository-dir",
    required=False,
    type=click.Path(exists=True, resolve_path=True),
    default='.',
    show_default=True,
    help="Repository dir to track version tags.",
)
@pass_tag_tracker_context
def tag_tracker(tag_tracker_context, repository_dir):
    tag_tracker_context.repository_dir = repository_dir


tag_tracker.add_command(sort_by)

tag_tracker.epilog = '''
  Run flow deploy create with tag-tracker COMMAND --help for
  more information on a command.
'''
