import yaml
import tempfile

from .source_code_scanner import SourceCodeScanner
from .exceptions import SourceCodeScannerException


class SCC(SourceCodeScanner):

    def __init__(
        self, 
        source_code_dir, 
        container_source_dir = '/code', 
        create_source_code_volume = True
    ):
        super().__init__(
            source_code_dir, 
            create_source_code_volume=create_source_code_volume
        )
        self.__scan_result = {}
        self.__container_source_dir = container_source_dir

    @property
    def repository(self):
        return 'convisoappsec/scc'

    @property
    def tag(self):
        return 'latest'

    @property
    def container_source_dir(self):
        return self.__container_source_dir

    def _read_scan_stdout(self, stdout_generator):
        with tempfile.TemporaryFile() as yaml_output:
            for chunk in stdout_generator:
                yaml_output.write(chunk)

            yaml_output.seek(0)

            self.__scan_result = yaml.load(
                yaml_output,
                Loader=yaml.FullLoader
            )

    @property
    def summary(self):
        summary = self.__scan_result.get('SUM')
        if not summary:
            raise SourceCodeScannerException(
                'Unexpected error retrienving source code summary metrics'
            )

        return summary

    @property
    def total_source_code_lines(self):
        return self.summary.get('code')

    @property
    def command(self):
        return [
            '--no-cocomo',
            '--no-complexity',
            '--format',
            'cloc-yaml'
        ]
