import docker
import tarfile
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

from transitions import Machine
from transitions.extensions.states import Timeout, add_state_features

from convisoappsec.common.docker import SCSCommon
from convisoappsec.logger import LOGGER

RAW_STATE_MSG = 'Scanner {} entered on {} state'


class SARIFParsingError(BaseException):
    pass


class PropertyRequiredError(SARIFParsingError):
    def __init__(self, stderr_log=''):
        pretty_error = self.__parse_pretty_property_error(stderr_log)
        print('Error:', pretty_error)

    def __parse_pretty_property_error(self, stderr_logs):
        expected_error_line = ''

        for log_line in stderr_logs.split('\n'):
            expected_error_text = 'PropertyRequiredError'
            if expected_error_text in log_line:
                expected_error_line = log_line
                break

        error = self.__extract_text_after_colon(expected_error_line)

        return error.strip()

    def __extract_text_after_colon(self, text):
        try:
            return text.split(':', 3)[-1]
        except IndexError:
            return ''


@add_state_features(Timeout)
class ScannerMachine(Machine):
    pass


class ScannerEntity:

    def __init__(self, token, scanner, logger=None, timeout=7200):
        self.logger = logger or LOGGER
        self.token = token

        self.scanner = self.__setup_scanner(scanner)
        self.name = self.scanner.name
        self.results = None

        self.states = [
            'waiting',
            {'name': 'pulling', 'timeout': timeout, 'on_timeout': self._on_timeout},
            {'name': 'running', 'timeout': timeout, 'on_timeout': self._on_timeout},
            {'name': 'sending', 'timeout': timeout, 'on_timeout': self._on_timeout},
            'done'
        ]
        self.machine = ScannerMachine(
            model=self,
            states=self.states,
            initial='waiting'
        )
        self.machine.add_ordered_transitions()
        self._set_callbacks()
        self.to_waiting()

    def __setup_scanner(self, scanner):
        if isinstance(scanner, SCSCommon):
            return scanner
        else:
            return self._instanciate_scanner(scanner)

    def _set_callbacks(self):
        self.machine.on_enter_waiting('_on_waiting')
        self.machine.on_enter_pulling('_on_pulling')
        self.machine.on_enter_running('_on_running')
        self.machine.on_enter_sending('_on_sending')
        self.machine.on_enter_done('_on_done')

    def _instanciate_scanner(self, data):
        return SCSCommon(
            **data,
            token=self.token,
            logger=self.logger,
        )

    def _on_timeout(self):
        self.logger.debug('Scanner {} timeout on state {}'.format(
            self.name, self.state
        ))

    def _on_waiting(self):
        self.logger.debug(RAW_STATE_MSG.format(
            self.name, self.state
        ))

    def _on_pulling(self):
        self.logger.debug(RAW_STATE_MSG.format(
            self.name, self.state
        ))
        image = self.scanner.pull()
        if image:
            self.logger.debug('Image: {}'.format(image))
            self.next_state()
        else:
            raise RuntimeError("Image not found.")

    def _on_running(self):
        self.scanner.run()
        self.end_time = time.time()
        self.logger.debug('Total execution time for {} was {:2f}'.format(
            self.scanner.repository_name,
            self.end_time - self.start_time
        ))
        self.next_state()

    def _on_sending(self):
        self.logger.debug(RAW_STATE_MSG.format(
            self.name, self.state
        ))
        self.results = self.scanner.get_container_reports()
        self.next_state()

    def _on_done(self):
        self.logger.debug(RAW_STATE_MSG.format(
            self.scanner.repository_name, self.state
        ))
        self.scanner.container.remove(v=True, force=True)

    def start(self):
        self.start_time = time.time()
        self.to_pulling()


class ContainerWrapper:

    def __init__(self, token, containers_map, logger, timeout, max_workers=5):
        self.token = token
        self.logger = logger or LOGGER
        self.max_workers = max_workers
        self.scanners = [
            ScannerEntity(
                token=token,
                scanner=scanner,
                logger=logger,
                timeout=timeout
            )
            for scanner in containers_map.values()
        ]

    def run(self):
        self.logger.debug("Starting Execution")
        with ThreadPoolExecutor(max_workers=self.max_workers) as exeggutor:
            for scanner in self.scanners:
                exeggutor.submit(scanner.start)


def convert_sarif_to_sastbox1(report_filepath, repository_dir, container_registry_token, scanner_timeout=7200):
    """
    Args:
        report_filepath (str): filepath to the report to be converted
        repository_dir (str): filepath to the repository being tested
        token (str): Conviso container registry token
        scanner_timeout (int): container timeout

    Returns:
        string: filepath to the converted report
    """
    CONTAINER_IMAGE_NAME = 'sastbox-converter-tool'
    CONTAINER_IMAGE_TAG = 'cc50dee'

    CONTAINER_INPUT_FILEPATH = '/code{}'.format(
        report_filepath.replace(repository_dir, '')
    )
    CONTAINER_OUTPUT_FILENAME = CONTAINER_INPUT_FILEPATH.replace(
        'sarif', 'json'
    )

    CONTAINERS_MAP = {
        CONTAINER_IMAGE_NAME: {
            'repository_dir': repository_dir,
            'repository_name': CONTAINER_IMAGE_NAME,
            'tag': CONTAINER_IMAGE_TAG, 
            'command': [
                '--format', 'sastbox1',
                '--input', CONTAINER_INPUT_FILEPATH,
                '--output', CONTAINER_OUTPUT_FILENAME
            ],
        },
    }
    converter_wrapped = ContainerWrapper(
        token=container_registry_token,
        containers_map=CONTAINERS_MAP,
        logger=None,
        timeout=scanner_timeout
    )

    converter_wrapped.logger.setLevel('WARN')
    converter_wrapped.run()
    converter_wrapped.logger.setLevel('INFO')

    scanner = converter_wrapped.scanners[0].scanner
    last_scan_name = scanner.name
    last_container = scanner.docker.containers.get(
        last_scan_name
    )

    try:
        chunks, _ = last_container.get_archive(CONTAINER_OUTPUT_FILENAME)
        output_filepath = __extract_tarball_chunks(
            chunks, report_filepath.replace('sarif', 'json')
        )
    except docker.errors.APIError as error:
        stderr_log = last_container.logs(stderr=True).decode('utf-8')
        raise PropertyRequiredError(stderr_log)

    return output_filepath


def __extract_tarball_chunks(tarball_chunks, report_absolute_filepath):
    """

    Args:
        tarball_chunks (int): The number of bytes returned by each iteration of the generator
        report_filename (string): The name of the extracted report

    Returns:
        string: Report absolute filepath in local filesystem
    """
    output_dirpath = report_absolute_filepath[
        :report_absolute_filepath.rfind('/')
    ]

    with tempfile.TemporaryFile() as tmp_wrapper_file:
        for chunk in tarball_chunks:
            tmp_wrapper_file.write(chunk)
        tmp_wrapper_file.seek(0)

        with tarfile.open(mode="r|", fileobj=tmp_wrapper_file) as talball_file:
            talball_file.extractall(path=output_dirpath)

    return report_absolute_filepath
