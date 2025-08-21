import click
import git
import time
import traceback
from convisoappsec.flowcli.context import pass_flow_context
from convisoappsec.flowcli import help_option
from convisoappsec.flow import GitAdapter
from convisoappsec.flowcli.common import on_http_error
from convisoappsec.logger import LOGGER

class SameCommitException(Exception):
    pass


@click.command()
@help_option
@click.option(
    "-c",
    "--current-commit",
    required=False,
    help="If no value is given the HEAD commit of branch is used.",
)
@click.option(
    "-p",
    "--previous-commit",
    required=False,
    help="""If no value is given, the value is retrieved from the lastest
    deploy at flow application.""",
)
@click.option(
    "-r",
    "--repository-dir",
    required=False,
    type=click.Path(exists=True, resolve_path=True),
    default='.',
    show_default=True,
    help="Repository directory.",
)
@click.option(
    "--asset-id",
    required=False,
    envvar=("CONVISO_ASSET_ID", "FLOW_ASSET_ID"),
    help="Asset ID on Conviso Platform",
)
@click.pass_context
def values(context, repository_dir, current_commit, previous_commit, asset_id):
    try:
        if context.params['asset_id'] is not None and asset_id is None:
            asset_id = context.params['asset_id']

        git_adapter = GitAdapter(repository_dir)
        commits = deploys_from_asset(asset_id=asset_id)
        current_commit = current_commit or git_adapter.head_commit
        last_commit = commits[0]['currentCommit'] if commits else git_adapter.empty_repository_tree_commit

        if last_commit == current_commit:
            raise SameCommitException(
                "Previous commit ({0}) and Current commit ({1}) are the same, nothing to do."
                .format(last_commit, current_commit)
            )

        if not previous_commit:
            previous_commit = commits[0]['currentCommit'] if commits else git_adapter.empty_repository_tree_commit

            if previous_commit != '4b825dc642cb6eb9a060e54bf8d69288fbee4904':
                try:
                    git_adapter._repo.commit(previous_commit)
                except (git.exc.BadName, ValueError):
                    commits = deploys_from_asset(asset_id=asset_id)
                    previous_commit = None

                    for commit in commits:
                        commit_hash = commit['currentCommit']
                        try:
                            git_adapter._repo.commit(commit_hash)
                            previous_commit = commit_hash
                            break
                        except (git.exc.BadName, ValueError):
                            continue

                    if previous_commit is None:
                        previous_commit = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'

        commit_history_file = git_adapter.get_commit_history()
        commit_history_file.seek(0)

        return {
            "previous_commit": previous_commit,
            "current_commit": current_commit,
            "commit_history": commit_history_file.name,
        }

    except SameCommitException as e:
        LOGGER.warning(str(e))

        return None

    except git.exc.GitError as e:
        LOGGER.error(f"Git error: {str(e)}")
        raise click.ClickException(f"Git error: {str(e)}") from e

    except Exception as e:
        if "GraphqlController" in str(e):
            LOGGER.error(f"GraphQL API error: {str(e)}")
            raise click.ClickException(f"Error communicating with Conviso API: {str(e)}") from e

        LOGGER.warning("There was an error. Our team has been notified.")
        full_trace = traceback.format_exc()
        LOGGER.error(full_trace)
        on_http_error(e)
        raise click.ClickException(str(e)) from e

@pass_flow_context
def deploys_from_asset(flow_context, asset_id, max_retries=3):
    """ Returns all deploys from an asset with retry logic """
    for attempt in range(max_retries):
        try:
            conviso_api = flow_context.create_conviso_graphql_client()
            deploys = conviso_api.deploys.get_deploys_by_asset(asset_id=asset_id)

            return deploys
        except Exception as e:
            if attempt == max_retries - 1:
                LOGGER.error(f"Failed to fetch deploys for asset {asset_id} after {max_retries} attempts: {str(e)}")
                raise
            LOGGER.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
            time.sleep(2 ** attempt)
    return None
