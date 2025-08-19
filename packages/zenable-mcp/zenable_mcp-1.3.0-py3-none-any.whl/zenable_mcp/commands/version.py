import click


@click.command()
def version():
    """Show the zenable-mcp version"""
    from zenable_mcp import __version__

    click.echo(__version__)
