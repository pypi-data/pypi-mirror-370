import click
from pathlib import Path

from convisoappsec.flow.version_control_system_adapter import GitAdapter
from convisoappsec.flowcli.context import pass_flow_context
from convisoappsec.flowcli import help_option


def finding_report_files_validation(_, __, finding_report_files):
    allowed_extensions = ['.json']
    allowed_extensions_str = '[{0}]'.format(
        '|'.join(allowed_extensions)
    )

    for report_file in finding_report_files:
        file_name = report_file.name

        if Path(file_name).suffix not in allowed_extensions:
            raise click.BadParameter(
                'Allowed file extensions {0}. File given: {1}'.format(
                    allowed_extensions_str,
                    file_name
                )
            )

    return finding_report_files


@click.command()
@click.argument(
    "finding-report-files",
    nargs=-1,
    required=False,
    type=click.File('r'),
    callback=finding_report_files_validation
)
@click.option(
    '-c',
    '--current-commit',
    required=False,
    help="""The hash of current commit. If no value is set
    so the HEAD commit will be used.""",
)
@click.option(
    "-r",
    "--repository-dir",
    required=False,
    type=click.Path(exists=True),
    default=".",
    show_default=True,
    help='The root dir of repository.',
)
@click.option(
    "-t",
    "--default-report-type",
    required=False,
    help="""This value is used when report type attribute is missing.
    This not override an existing value at report file""",
)
@help_option
@pass_flow_context
def version_tracker(
    flow_context, finding_report_files,
    repository_dir, current_commit, default_report_type
):
    try:
        if not finding_report_files:
            click.echo(
                "Nothing to be done, finding report files argument empty"
            )

            return

        git = GitAdapter(repository_dir)
        current_commit = current_commit or git.head_commit
        commit_refs = git.show_commit_refs(current_commit)
        finding_report_files_prog_bar_ctx = click.progressbar(
            finding_report_files,
            label='Sending finding reports'
        )

        flow = flow_context.create_conviso_rest_api_client()

        with finding_report_files_prog_bar_ctx as reports_with_progressbar:
            for finding_report in reports_with_progressbar:
                flow.findings.create(
                    commit_refs,
                    finding_report,
                    default_report_type=default_report_type
                )

    except Exception as e:
        raise click.ClickException(str(e)) from e
