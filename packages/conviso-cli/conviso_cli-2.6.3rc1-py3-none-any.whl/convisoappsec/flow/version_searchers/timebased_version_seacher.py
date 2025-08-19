from .version_searcher_result import VersionSearcherResult


class TimeBasedVersionSearcher(object):
    def __init__(self, version_control_system_adapter):
        self.version_control_system_adapter = version_control_system_adapter

    def find_current_and_previous_version(self):
        tags = self.version_control_system_adapter.tags()

        current_tag = None
        previous_tag = None

        tags = tags[:2]

        if len(tags) >= 2:
            (current_tag, previous_tag) = tags
        elif len(tags) == 1:
            current_tag = tags[0]
        else:
            raise Exception("Was not possible find the current tag")

        current_commit = self.version_control_system_adapter.show_commit_from_tag(  # noqa: E501
            current_tag
        )

        previous_commit = self.version_control_system_adapter.empty_repository_tree_commit  # noqa: E501

        if previous_tag:
            previous_commit = self.version_control_system_adapter.show_commit_from_tag(  # noqa: E501
                previous_tag
            )

        return VersionSearcherResult(
            current_commit=current_commit,
            previous_commit=previous_commit,
            current_tag=current_tag,
            previous_tag=previous_tag,
        )
