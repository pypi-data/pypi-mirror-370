import click


def print_help(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(ctx.get_help())
    ctx.exit()


help_option = click.option(
    '-h', '--help',
    is_flag=True,
    callback=print_help,
    expose_value=False,
    is_eager=True,
    help="Show this message and exit."
)
