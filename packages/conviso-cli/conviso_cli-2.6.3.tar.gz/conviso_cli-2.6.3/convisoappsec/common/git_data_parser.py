
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
from giturlparse import parse as gitparse
from hashlib import sha256
import os

from convisoappsec.flow.version_control_system_adapter import GitAdapter
from convisoappsec.logger import LOGGER


class DescriptionParsingError(GitCommandError):
    pass


class GitDataParser:
    def __init__(self, repository_dir):
        try:
            self.__validate_git_repo(repository_dir)

            self.repository_dir = repository_dir
            self._git_adapter = GitAdapter(repository_dir)

        except InvalidGitRepositoryError as exp:
            LOGGER.error(
                'Invalid Git repository: "{}".'.format(repository_dir)
            )
            raise exp

        except Exception as exp:
            LOGGER.error("An unxpected error occurred.")
            raise exp

    def parse_name(self):
        try:
            git_remote_url = self._git_adapter._git_client.ls_remote(
                '--get-url'
            )

            return self.__parse_name_from_git_url(git_remote_url)
        except GitCommandError:
            dirname = os.path.dirname(self.repository_dir)
            basename = os.path.basename(self.repository_dir)
            digest = sha256(dirname.encode('utf-8')).hexdigest()

            return basename + '-' + digest
        except Exception as exception:
            raise exception

    def __parse_description(self):
        try:
            readme = self._git_adapter._git_client.show(':README.md')
            readme = readme.replace('\n', '\n<br>')

            return readme

        except DescriptionParsingError as exception:
            raise exception

        except Exception as exception:
            raise exception

    def __parse_name_from_git_url(self, git_url):
        parser = gitparse(git_url)

        return '{} ({}/{})'.format(
            parser.name,
            parser.resource,
            parser.owner,
        )

    def __validate_git_repo(self, repository_dir):
        repo = Repo(repository_dir)
        repo.git.config("--global", "--add", "safe.directory", repository_dir)

        return repo
