import warnings

from convisoappsec.flow.versioning_style import semantic_versioning

from .version_searcher_result import VersionSearcherResult


class SortedByVersioningStyle(object):
    SEMANTIC_VERSIONING_STYLE = 'semantic-versioning'
    STYLES = [
        SEMANTIC_VERSIONING_STYLE,
    ]

    def __init__(
        self, version_control_system_adapter,
        ignore_prefix, style, current_tag, **kargs
    ):
        self.version_control_system_adapter = version_control_system_adapter
        self.ignore_prefix = ignore_prefix
        self.style = style
        self.current_tag = current_tag
        self.suppress_warnings = kargs.get('suppress_warnings', True)

    def find_current_and_previous_version(self):
        tags = self.version_control_system_adapter.tags()

        versions = []

        for tag in tags:
            try:
                versions.append(
                    semantic_versioning.Version(
                      tag,
                      prefix=self.ignore_prefix,
                    )
                )
            except ValueError as e:
                if not self.suppress_warnings:
                    warnings.warn(str(e))

        current_version = None

        if not self.current_tag:
            current_version = semantic_versioning.Version.find_latest(
                versions
            )

            if not current_version:
                raise RuntimeError("No current_version was found")
        else:
            current_version = semantic_versioning.Version(
                self.current_tag,
                prefix=self.ignore_prefix,
            )

            if current_version not in versions:
                raise ValueError(
                    "Current version[%s] not exists on repository"
                    %
                    current_version
                )

        previous_version = current_version.find_previous(versions)

        current_tag = str(current_version)
        current_commit = self.version_control_system_adapter.show_commit_from_tag(  # noqa: E501
            current_tag
        )

        previous_tag = None
        previous_commit = self.version_control_system_adapter.empty_repository_tree_commit  # noqa: E501

        if previous_version:
            previous_tag = str(previous_version)
            previous_commit = self.version_control_system_adapter.show_commit_from_tag(  # noqa: E501
                previous_tag
            )

        return VersionSearcherResult(
            current_commit=current_commit,
            previous_commit=previous_commit,
            current_tag=current_tag,
            previous_tag=previous_tag,

        )
