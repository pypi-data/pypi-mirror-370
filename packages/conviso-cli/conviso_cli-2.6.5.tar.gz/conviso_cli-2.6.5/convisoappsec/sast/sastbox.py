import tempfile
import tarfile
import docker
import os
import click
import json
import docker.errors
from io import BytesIO
from contextlib import suppress
from pathlib import Path
from convisoappsec.flowcli.context import pass_flow_context
from convisoappsec.flow import GitAdapter

bitbucket = os.getenv('BITBUCKET_CLONE_DIR')


class SASTBox(object):
    REGISTRY = 'public.ecr.aws/convisoappsec'
    REPOSITORY_NAME = 'sastbox_v2'
    DEFAULT_TAG = 'unstable'
    CONTAINER_CODE_DIR = bitbucket or '/code'
    CONTAINER_REPORTS_DIR = '/tmp'
    WORKSPACE_REPORT_PATH = CONTAINER_CODE_DIR
    JSON_REPORT_PATTERN = 'output.json'
    SUCCESS_EXIT_CODE = 1
    USER_ENV_VAR = "USER"

    def __init__(self, registry=None, repository_name=None, tag=None):
        self.docker = docker.from_env(
            version="auto"
        )
        self.container = None
        self.registry = registry or self.REGISTRY
        self.repository_name = repository_name or self.REPOSITORY_NAME
        self.tag = tag or self.DEFAULT_TAG

    def login(self, password, username='AWS'):
        login_args = {
            'registry': self.REGISTRY,
            'username': username,
            'password': password,
            'reauth': True,
        }

        login_result = self.docker.login(**login_args)
        return login_result

    def run_scan_diff(self, code_dir, current_commit, previous_commit, log=None):
        return self._scan_diff(code_dir, current_commit, previous_commit, log)

    @property
    def size(self):
        try:
            registry_data = self.docker.images.get_registry_data(
                self.image
            )
            descriptor = registry_data.attrs.get('Descriptor', {})
            return descriptor.get('size') * 1024 * 1024
        except docker.errors.APIError:
            return 6300 * 1024 * 1024

    def pull(self):
        size = self.size
        layers = {}
        for line in self.docker.api.pull(
                self.repository, tag=self.tag, stream=True, decode=True
        ):
            status = line.get('status', '')
            detail = line.get('progressDetail', {})

            if status == 'Downloading':
                with suppress(Exception):
                    layer_id = line.get('id')
                    layer = layers.get(layer_id, {})
                    layer.update(detail)
                    layers[layer_id] = layer

                    for layer in layers.values():
                        current = layer.get('current')
                        total = layer.get('total')

                        if (current / total) > 0.98 and not layer.get('done'):
                            yield current
                            layer.update({'done': True})

        yield size

    def _scan_diff(self, code_dir, current_commit, previous_commit, log):
        environment = {
            'PREVIOUS_COMMIT': previous_commit,
            'CURRENT_COMMIT': current_commit,
            'SASTBOX_REPORTS_DIR': self.CONTAINER_REPORTS_DIR,
            'SASTBOX_REPORT_DIR': '/tmp',
            'SASTBOX_REPORT_PATTERN': '*.sarif',
            'SASTBOX_CODE_DIR': self.CONTAINER_CODE_DIR,
        }

        command_parts = [
            'ruby', 'manager/sastbox_cli.rb',
            '-c', self.CONTAINER_CODE_DIR,
            '-a',
            '-o', '/tmp/output.sarif',
            f'--diff={previous_commit},{current_commit}',
            '&&',
            'cp', '$(find "$SASTBOX_REPORT_DIR" -name "$SASTBOX_REPORT_PATTERN")', '$SASTBOX_REPORTS_DIR'
        ]
        command = ' '.join(command_parts)

        # Configure container creation
        create_args = {
            'image': self.image,
            'entrypoint': ['sh', '-c'],
            'command': [command],
            'tty': True,
            'detach': True,
            'environment': environment,
        }

        try:
            try:
                self.container = self.docker.containers.create(**create_args)
            except docker.errors.APIError as e:
                raise RuntimeError(f"Failed to create container: {e}")

            # Create and upload source code tarball
            source_code_tarball_file = tempfile.TemporaryFile()
            try:
                source_code_tarball = tarfile.open(mode="w|gz", fileobj=source_code_tarball_file)
                source_code_tarball.add(
                    name=code_dir,
                    arcname=self.CONTAINER_CODE_DIR,
                    filter=lambda tarinfo: tarinfo if not tarinfo.name.endswith('.zip') else None
                )
                source_code_tarball.close()
                source_code_tarball_file.seek(0)
                try:
                    self.container.put_archive("/", source_code_tarball_file)
                except docker.errors.APIError as e:
                    raise RuntimeError(f"Failed to upload tarball: {e}")
            finally:
                source_code_tarball_file.close()

            # Start the container and stream logs
            try:
                self.container.start()
            except docker.errors.APIError as e:
                raise RuntimeError(f"Failed to start container: {e}")

            for line in self.container.logs(stream=True):
                if log:
                    log(line, new_line=False)

            self.recovery_technologies_file()

            wait_result = self.container.wait()
            status_code = wait_result.get('StatusCode')

            if status_code != self.SUCCESS_EXIT_CODE:
                logs = self.container.logs().decode('utf-8')
                raise RuntimeError(f"SASTBox exited with status code {status_code}\nLogs:\n{logs}")

            # Retrieve and extract reports
            try:
                chunks, _ = self.container.get_archive(self.CONTAINER_REPORTS_DIR)
            except docker.errors.APIError as e:
                raise RuntimeError(f"Failed to retrieve reports: {e}")

            reports_tarball_file = tempfile.TemporaryFile()
            try:
                for chunk in chunks:
                    reports_tarball_file.write(chunk)
                tempdir = tempfile.mkdtemp()
                reports_tarball_file.seek(0)
                reports_tarball = tarfile.open(mode="r|", fileobj=reports_tarball_file)
                reports_tarball.extractall(path=tempdir)
                reports_tarball.close()
            finally:
                reports_tarball_file.close()

            # Verify reports exist and return their paths
            reports = self._list_reports_paths(tempdir)
            if not reports:
                raise RuntimeError("No reports found in the container")

        except docker.errors.APIError as e:
            raise RuntimeError(f"Failed to retrieve reports: {e}")

        return reports

    @property
    def repository(self):
        return "{registry}/{repository_name}".format(
            registry=self.registry,
            repository_name=self.repository_name,
        )

    @property
    def image(self):
        return "{repository}:{tag}".format(
            repository=self.repository,
            tag=self.tag,
        )

    def __del__(self):
        with suppress(Exception):
            self.container.remove(v=True, force=True)

    @classmethod
    def _list_reports_paths(cls, root_dir):
        root_dir = root_dir + cls.CONTAINER_REPORTS_DIR
        sastbox_reports_dir = Path(root_dir)

        for report in sastbox_reports_dir.glob(cls.JSON_REPORT_PATTERN):
            yield report

    def recovery_technologies_file(self):
        """ Method to recover a fingerprint file inside the container with founded technology """
        try:
            generator_object, _ = self.container.get_archive('/tmp/')
            file_content = b"".join(generator_object)
            file_content_stream = BytesIO(file_content)
            tar = tarfile.open(fileobj=file_content_stream)
            file_names = tar.getnames()

            fingerprint_file = next(
                (file for file in file_names if file.startswith('tmp/fingerprint') and file.endswith('.json')), None)

            if not fingerprint_file:
                log_func("No file starting with 'fingerprint' and ending with '.json' found.")
                return

            actual_filename = fingerprint_file.split('/')[-1]

            generator_object, _ = self.container.get_archive(f'/tmp/{actual_filename}')
            file_content = b"".join(generator_object)
            file_content_stream = BytesIO(file_content)
            tar = tarfile.open(fileobj=file_content_stream)
            file_data = tar.extractfile(actual_filename)
            content = json.loads(file_data.read())
            technologies = content['result']['technologies']
        except Exception as error:
            msg = "\U0001F4AC Something goes wrong when trying to recover the technologies, continuing ..."
            log_func(msg)
            technologies = []

        if technologies is None:
            return

        self.update_asset_technologies(technologies=technologies)

    @staticmethod
    @pass_flow_context
    @click.pass_context
    def update_asset_technologies(flow_context, context, technologies):
        """
        Update technologies on asset.
        Args:
            flow_context (dict): Flow context containing parameters.
            context (object): Object containing necessary methods (e.g., create_conviso_graphql_client).
            technologies (list): List of technologies to be updated.
        Returns:
            dict: Response from the API call.
        """

        # this prevents a broken execution when something goes wrong.
        try:
            git_adapter = GitAdapter(flow_context.params['repository_dir'])
            repo_url = git_adapter.repo_url()

            company_id = flow_context.params.get('company_id')
            asset_id = flow_context.params.get('asset_id')
            asset_name = flow_context.params.get('asset_name')
            unwanted_technologies = {
                'unknown', 'json', 'text', 'ini', 'diff', 'xml', 'markdown', 'csv', 'gemfile.lock', 'html+erb',
                'javascript+erb', 'robots.txt', 'yaml', 'batchfile', 'java properties', 'svg', 'json with comments'
            }
            updated_technologies = [tech for tech in technologies if tech not in unwanted_technologies]
            conviso_api = context.create_conviso_graphql_client()

            response = conviso_api.assets.update_asset(
                company_id=int(company_id),
                asset_id=asset_id,
                asset_name=asset_name,
                technologies=updated_technologies,
                repo_url=repo_url
            )
        except Exception as error:
            msg = "\U0001F4AC Something goes wrong when trying to send technologies to the CP, continuing... {error}".format(error=error)
            log_func(msg)

            response = None

        return response

def log_func(msg, new_line=True):
    click.echo(msg, nl=new_line, err=True)
