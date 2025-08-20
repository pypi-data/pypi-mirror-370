import click
# TODO: refactoring. all deploy create share some behavior
from convisoappsec.flow.util import project_metrics
from convisoappsec.flowcli.context import pass_flow_context
from convisoappsec.flow.version_searchers import SortedByVersioningStyle
from convisoappsec.flow.version_control_system_adapter import GitAdapter
from convisoappsec.flowcli import help_option
from convisoappsec.flowcli.common import on_http_error
from convisoappsec.flowcli.deploy.create.context import pass_create_context

from convisoappsec.flowcli.deploy.create.with_.tag_tracker.context import (
    pass_tag_tracker_context
)


@click.command()
@click.option(
    '-c',
    '--current-tag',
    required=False,
    help="""This value is used to ignore versions
    bigger than this value if exists"""
)
@click.option(
    '-i',
    '--ignore-prefix',
    required=False,
    default='v',
    show_default=True,
    help="Prefix to be ignored on parsing to versioning style.",
)
@click.option(
    '-s',
    '--style',
    required=False,
    type=click.Choice(SortedByVersioningStyle.STYLES),
    default=SortedByVersioningStyle.SEMANTIC_VERSIONING_STYLE,
    show_default=True,
    help="Versioning style type used at repository.",
)
@click.option(
    "--attach-diff/--no-attach-diff",
    default=True,
    show_default=True,
    required=False,
)
@help_option
@pass_tag_tracker_context
@pass_create_context
@pass_flow_context
def versioning_style(
    flow_context, create_context, tag_tracker_context, ignore_prefix, style,
    current_tag, attach_diff
):
    try:
        repository_dir = tag_tracker_context.repository_dir
        git_adapter = GitAdapter(repository_dir)

        searcher = SortedByVersioningStyle(
            git_adapter,
            ignore_prefix,
            style,
            current_tag,
        )

        result = searcher.find_current_and_previous_version()
        current_version = result.current_version
        previous_version = result.previous_version
        diff_content = None

        current_commit = current_version.get('commit')
        previous_commit = previous_version.get('commit')

        if previous_commit == current_commit:
            import sys
            click.echo(
                "Previous commit ({0}) and Current commit ({1}) are the same, nothing to do.".format(
                    previous_commit, current_commit
                ),
                file=sys.stderr
            )
            return

        if attach_diff:
            diff_content = git_adapter.diff(
                previous_commit,
                current_commit,
            )

        deploy_metrics = git_adapter.diff_stats(
            previous_commit,
            current_commit,
        ).dict

        flow = flow_context.create_conviso_rest_api_client()

        authors_data = git_adapter.get_commit_authors_by_range(
            previous_commit, current_commit
        )

        deploy = flow.deploys.create(
            current_version=current_version,
            previous_version=previous_version,
            diff_content=diff_content,
            metrics=deploy_metrics,
            project_metrics=project_metrics(repository_dir),
            commit_authors=authors_data
        )

        click.echo(
            create_context.output_formatter.format(deploy)
        )
    except Exception as e:
        on_http_error(e)
        raise click.ClickException(str(e)) from e
