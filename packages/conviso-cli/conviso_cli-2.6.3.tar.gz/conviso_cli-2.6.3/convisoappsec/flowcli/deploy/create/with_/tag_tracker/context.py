import click


class TagTrackerWith(object):
    def __init__(self):
        self.repository_dir = None


pass_tag_tracker_context = click.make_pass_decorator(
    TagTrackerWith, ensure=True
)
