import tarfile


class SourceCodeCompressor(object):
    TAR_WRITE_MODE = 'w|'
    TAR_ROOT_DIR = '.'

    def __init__(self, source_code_dir="."):
        self.source_code_dir = source_code_dir

    def write_to(self, fileobj):
        tarball_filehandler = tarfile.open(
            mode=self.TAR_WRITE_MODE,
            fileobj=fileobj
        )

        tarball_filehandler.add(
            name=self.source_code_dir,
            arcname=self.TAR_ROOT_DIR,
        )

        tarball_filehandler.close()
