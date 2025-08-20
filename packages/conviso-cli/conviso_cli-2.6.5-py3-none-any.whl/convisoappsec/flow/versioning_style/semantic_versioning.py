import semantic_version
import re


class Version(semantic_version.Version):
    PREFIXED_VERSION_RE_FMT = '^{prefix}(.+)'

    def __init__(self, version_string, prefix=None):
        super().__init__(
            self.__remove_prefix(prefix, version_string)
        )

        self.__version_string = version_string

    def __str__(self):
        return self.__version_string

    @classmethod
    def __remove_prefix(cls, prefix, version_string):
        if not prefix:
            return version_string

        version_re = cls.PREFIXED_VERSION_RE_FMT.format(
            prefix=re.escape(prefix)
        )

        match = re.match(version_re, version_string)

        if match:
            return match.group(1)

        return version_string

    def find_previous(self, versions):
        previous_tags = list(
            filter(lambda v: v < self, versions)
        )

        return self.find_latest(previous_tags)

    @staticmethod
    def find_latest(versions):
        if len(versions) > 0:
            return max(versions)
