import json
import tempfile
import re
import yaml
import git
import os
import zipfile
import shutil
import subprocess
from contextlib import suppress
from convisoappsec.logger import LOGGER
from git.exc import GitCommandError


class GitAdapter(object):
    LIST_OPTION = '--list'
    SORT_OPTION = '--sort'
    FORMAT_OPTION = '--format'
    ANCESTRY_PATH_OPTION = '--ancestry-path'
    HEAD_COMMIT = 'HEAD'
    OPTION_WITH_ARG_FMT = '{option}={value}'
    EMPTY_REPOSITORY_HASH = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'

    def __init__(self, repository_dir='.', load_remote_repositories_heads=True, unshallow_repository=True):
        LOGGER.debug('Unshallow: {}'.format(unshallow_repository))
        LOGGER.debug('Load remote: {}'.format(load_remote_repositories_heads))

        self._git_client = git.cmd.Git(repository_dir)
        self._git_client.config('--global', '--add', 'safe.directory', repository_dir)
        self._first_commit = None
        self._repo = git.Repo(repository_dir)
        self._git_client.config('--global', '--add', 'safe.directory', repository_dir)

        if load_remote_repositories_heads:
            self.__load_remote_repositories_heads()

        if unshallow_repository:
            self.__unshallow_repository()

    def repo_url(self):
        """
        Function to get the repository URL and convert it to an HTTPS format if necessary.

        Returns:
            str: The repository URL in HTTPS format, or None if the URL cannot be determined.
        """
        repos_url = self._repo.remotes.origin.url

        if repos_url.startswith('git@'):
            return repos_url.replace(':', '/').replace('git@', 'https://').replace('.git', '')

        elif repos_url.startswith('ssh://git@ssh.dev.azure.com'):
            parts = repos_url.split('/')
            if len(parts) >= 7:
                organization = parts[4]
                project = parts[5]
                repo = parts[6].replace('.git', '')
                return f"https://dev.azure.com/{organization}/{project}/_git/{repo}"

        return repos_url

    def get_branch_name(self):
        """retrieves the branch name"""
        return self._repo.active_branch.name


    def get_commit_history(self):
        """
        Retrieves the commit history (including stashes) of the repository and saves it to a temporary JSON file.

        Returns:
            str: The path to the temporary JSON file.
        """
        commits = self._repo.iter_commits()

        commit_info_list = [
            {
                'commit': commit.hexsha,
                'author': "{author_name} <{author_email}>".format(
                    author_name=commit.author.name, author_email=commit.author.email
                ),
                'date': commit.authored_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                'message': commit.message
            }
            for commit in commits
        ]

        # Include information about stashes
        stashes = self._repo.git.stash("list", "--format=%H|%gd|%ci|%P|%gs", "--date=iso").splitlines()
        stash_info_list = [
            {
                'commit': stash_info.split('|')[0],
                'stash_ref': stash_info.split('|')[1],
                'date': stash_info.split('|')[2],
                'parent_commits': stash_info.split('|')[3].split(),
                'message': stash_info.split('|')[4],
                'contributors': self.get_contributors_for_stash_merge(stash_info.split('|')[0])
            }
            for stash_info in stashes
        ]

        commit_info_list.extend(stash_info_list)

        temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        json.dump(commit_info_list, temp_file, indent=2)
        temp_file.seek(0)

        return temp_file

    def get_contributors_for_stash_merge(self, stash_commit):
        """
        Get contributors involved in a stash merge.

        Args:
            stash_commit (str): The commit hash of the stash.

        Returns:
            list: List of contributors involved in the stash merge.
        """
        contributors = set()
        stash_diff = self._repo.git.diff(stash_commit + "^", stash_commit, "--name-only").splitlines()

        for file_path in stash_diff:
            blame_output = self._repo.git.blame(stash_commit, "--", file_path).splitlines()
            for line in blame_output:
                commit_hash = line.split()[0]
                contributor_name = (self._repo.git.show("-s", "--format=%aN|%ae", commit_hash)).split('|')[0]
                contributor_email = (self._repo.git.show("-s", "--format=%aN|%ae", commit_hash)).split('|')[1]
                contributor = "{name} {email}".format(name=contributor_name, email=contributor_email)
                contributors.add(contributor)

        return list(contributors)

    def tags(self, sort='-committerdate'):
        sort_option = self.OPTION_WITH_ARG_FMT.format(
            option=self.SORT_OPTION,
            value=sort,
        )

        args = (self.LIST_OPTION, sort_option)
        client_output = self._git_client.tag(args)
        tags = client_output.splitlines()
        return tags

    def diff(self, version, another_version):
        version = version or self.EMPTY_REPOSITORY_HASH

        if version == self.EMPTY_REPOSITORY_HASH:
            msg_fmt = """Creating diff comparing revision[{0}] and the repository beginning"""
            LOGGER.warning(msg_fmt.format(another_version))

        diff_file = tempfile.TemporaryFile()
        self._git_client.diff(version, another_version, output_stream=diff_file)

        return diff_file

    def diff_stats(self, version, another_version):
        version = version or self.EMPTY_REPOSITORY_HASH

        if version == self.EMPTY_REPOSITORY_HASH:
            msg_fmt = """Creating diff stats comparing revision[{0}] and the repository beginning"""
            LOGGER.warning(msg_fmt.format(another_version))

        stats_output = tempfile.TemporaryFile()
        self._git_client.diff(version, another_version, '--numstat', output_stream=stats_output)

        stats_summary = GitDiffNumStatSummary.load(stats_output)
        stats_output.close()

        return stats_summary

    @property
    def first_commit(self):
        if self._first_commit:
            return self._first_commit

        command_output = tempfile.TemporaryFile()

        args = [
            '--reverse',
            "--pretty=%H",
        ]

        self._git_client.log(args, output_stream=command_output)
        command_output.seek(0)
        first_in_bytes = command_output.readline()
        command_output.close()
        first = first_in_bytes.decode()

        return first.strip()

    def commit_is_first(self, commit):
        return commit == self.first_commit

    @property
    def head_commit(self):
        client_output = self._git_client.rev_parse(self.HEAD_COMMIT)
        return client_output.strip()

    @property
    def current_commit(self):
        return self.head_commit

    @property
    def previous_commit(self):
        return self.previous_commit_from(self.current_commit)

    def previous_commit_from(self, commit, offset=1):
        if self.commit_is_first(commit):
            return self.EMPTY_REPOSITORY_HASH

        command_fmt = "{commit}~{offset}"

        command = command_fmt.format(
            commit=commit,
            offset=offset,
        )

        client_output = self._git_client.rev_parse(
            command
        )

        return client_output.strip()

    def show_commit_refs(self, commit):
        with tempfile.TemporaryFile() as client_output:
            self._git_client.show_ref(
                "--head", "--heads", "--tags", output_stream=client_output
            )
            refs = _read_file_lines_generator(client_output)
            refs = list(
                filter(
                    lambda ref: re.search(commit, ref),
                    refs,
                )
            )

            return refs

    def show_commit_from_tag(self, tag):
        client_output = self._git_client.rev_parse(
            tag
        )

        return client_output.strip()

    def get_commit_author(self, commit_hash):
        if self.EMPTY_REPOSITORY_HASH == commit_hash:
            default_commit = {
                'name': 'Default',
                'email': 'Default',
                'commit': commit_hash
            }
            return default_commit

        delimiter = '|;|'
        fmt_author_name = '%an'
        fmt_author_email = '%ae'
        fmt_long_commit_hash = '%H'

        row_fmt = '{name}{delimiter}{email}{delimiter}{commit}'.format(
            name=fmt_author_name,
            delimiter=delimiter,
            email=fmt_author_email,
            commit=fmt_long_commit_hash
        )
        format_option = self.OPTION_WITH_ARG_FMT.format(
            option=self.FORMAT_OPTION,
            value=row_fmt,
        )

        author = self._git_client.show(
            '-s', format_option, commit_hash
        ).split(delimiter)

        author_data = {
            'name': author[0],
            'email': author[1],
            'commit': author[2],
        }

        return author_data

    def get_commits_by_range(self, start_commit, end_commit):
        tmp_commits = tempfile.TemporaryFile()

        self._git_client.rev_list(
            self.ANCESTRY_PATH_OPTION, start_commit + '..' + end_commit, output_stream=tmp_commits
        )

        return _read_file_lines_generator(tmp_commits)

    def get_commit_authors_by_range(self, start_commit, end_commit):
        start_commit_range = start_commit
        author_file = CommitAuthorFile()

        if self.EMPTY_REPOSITORY_HASH == start_commit_range:
            start_commit_range = self.first_commit

        commit_list = self.get_commits_by_range(start_commit_range, end_commit)

        for commit in commit_list:
            author = self.get_commit_author(commit)
            author_file.add_author(author)

        return author_file.get_file_descriptor()

    @property
    def empty_repository_tree_commit(self):
        return self.EMPTY_REPOSITORY_HASH

    @property
    def remote_repositories_name(self):
        args = ("show")
        client_output = self._git_client.remote(args)
        repositories = client_output.splitlines()
        return repositories

    def __load_remote_repositories_heads(self):
        heads_refspec_format = "refs/heads/*:refs/remotes/{remote_repository_name}/*"

        for remote_repository_name in self.remote_repositories_name:
            try:
                heads_refspec = heads_refspec_format.format(
                    remote_repository_name=remote_repository_name
                )

                args = (remote_repository_name, heads_refspec)
                print(self._git_client.fetch(args))

            except GitCommandError:
                raw_msg = "We can't ensure that the refspec refs/heads/* from repository {repository} were loaded."
                msg = raw_msg.format(repository=remote_repository_name)
                LOGGER.warning(msg)

    @property
    def is_shallow_repository(self):
        import os.path

        args = ('--git-dir')
        git_dir = self._git_client.rev_parse(args)

        working_dir = self._git_client.working_dir
        shallow_file = os.path.join(working_dir, git_dir, 'shallow')

        return os.path.isfile(shallow_file)

    def __unshallow_repository(self):
        if not self.is_shallow_repository:
            return

        args = ('--unshallow')
        self._git_client.fetch(args)


def _read_file_lines_generator(file):
    file.seek(0)

    while True:
        line = file.readline()
        line = line.decode().strip()

        if line:
            yield line
        else:
            break


class InvalidGitDiffNumStatLineValueException(ValueError):
    pass


class GitDiffNumStatLine(object):
    ADDED_LINES_POSITION = 1
    DELETED_LINES_POSITION = 2
    FILE_PATH_POSITION = 3

    # (added_lines) (deleted_lines) (file_path)
    SRC_LINE_REGEX = r'(\d+)\s+(\d+)\s+(.*)'
    BIN_LINE_REGEX = r'(-)\s+(-)\s+(.*)'

    def __init__(self, added_lines, deleted_lines, file_path):
        self.added_lines = added_lines
        self.deleted_lines = deleted_lines
        self.file_path = file_path

    @classmethod
    def parse(cls, raw_line):
        with suppress(AttributeError):
            match = re.match(cls.SRC_LINE_REGEX, raw_line)
            group = match.group

            added_lines_str = group(cls.ADDED_LINES_POSITION)
            deleted_lines_str = group(cls.DELETED_LINES_POSITION)
            file_path = group(cls.FILE_PATH_POSITION)

            added_lines = int(added_lines_str)
            deleted_lines = int(deleted_lines_str)

            return cls(added_lines, deleted_lines, file_path)

        with suppress(AttributeError):
            match = re.match(cls.BIN_LINE_REGEX, raw_line)

            file_path = match.group(cls.FILE_PATH_POSITION)

            return cls(0, 0, file_path)

        error_msg_fmt = '\n'.join([
            'The expected git diff numstat line format are:',
            'Expected format: {src_fmt}',
            'Expected format: {bin_fmt}',
            'Given value: {given}',
        ])

        msg = error_msg_fmt.format(
            src_fmt=cls.SRC_LINE_REGEX,
            bin_fmt=cls.BIN_LINE_REGEX,
            given=raw_line
        )

        raise InvalidGitDiffNumStatLineValueException(msg)

    @classmethod
    def load(cls, numstat_fh):
        numstat_fh.seek(0)

        while True:
            line = numstat_fh.readline()

            with suppress(AttributeError):
                line = line.decode()

            if line:
                yield cls.parse(line)
                continue

            break


class GitDiffNumStatSummary(object):

    def __init__(self):
        self.added_lines = 0
        self.deleted_lines = 0
        self.changed_files = []

    def _add_numstat_lines(self, numstat_lines):
        for numstat_line in numstat_lines:
            self._add_numstat_line(numstat_line)

    def _add_numstat_line(self, numstat_line):
        self._add_added_lines(numstat_line.added_lines)
        self._add_deleted_lines(numstat_line.deleted_lines)
        self._add_changed_files(numstat_line.file_path)

    def _add_added_lines(self, added_lines):
        self.added_lines += added_lines

    def _add_deleted_lines(self, deleted_lines):
        self.deleted_lines += deleted_lines

    def _add_changed_files(self, changed_file):
        self.changed_files.append(
            changed_file
        )

    @property
    def changed_lines(self):
        return self.added_lines + self.deleted_lines

    @classmethod
    def load(cls, numstat_fh):
        git_diffnumstat_lines = GitDiffNumStatLine.load(numstat_fh)
        summary = cls()
        summary._add_numstat_lines(git_diffnumstat_lines)

        return summary

    @property
    def dict(self):
        field_names = [
            'added_lines',
            'deleted_lines',
            'changed_lines',
            'changed_files',
        ]

        fields = {
            name: getattr(self, name) for name in field_names
        }

        return fields


def quoted_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')


yaml.add_representer(str, quoted_presenter)


class CommitAuthorFile:
    def __init__(self):
        self._tmp_authors = tempfile.NamedTemporaryFile()

    def add_author(self, author):
        yaml_str = yaml.dump(author, explicit_start=True)
        yaml_bytes = yaml_str.encode()
        self._tmp_authors.write(yaml_bytes)

    def get_file_descriptor(self):
        self._tmp_authors.seek(0)
        return self._tmp_authors
