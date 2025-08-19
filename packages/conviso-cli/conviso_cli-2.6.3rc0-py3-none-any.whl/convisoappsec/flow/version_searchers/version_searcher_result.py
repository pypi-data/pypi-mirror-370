class VersionSearcherResult(object):

    def __init__(self, **karg):
        self.current_tag = karg.get('current_tag')
        self.previous_tag = karg.get('previous_tag')
        self.current_commit = karg.get('current_commit')
        self.previous_commit = karg.get('previous_commit')

        if not (self.current_commit and self.previous_commit):
            raise ValueError(
                "The values of current_commit and previous_commit are required"
            )

    @property
    def current_version(self):
        return self.create_version_dict(
            self.current_commit,
            self.current_tag,
        )

    @property
    def previous_version(self):
        return self.create_version_dict(
            self.previous_commit,
            self.previous_tag,
        )

    @staticmethod
    def create_version_dict(commit, tag):
        return {
            'commit': commit,
            'tag': tag,
        }
