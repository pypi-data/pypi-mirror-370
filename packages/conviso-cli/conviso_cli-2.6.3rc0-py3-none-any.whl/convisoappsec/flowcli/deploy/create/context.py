import click


class CreateContext(object):

    def __init__(self):
        self.output_formatter = None


pass_create_context = click.make_pass_decorator(
    CreateContext, ensure=True
)
