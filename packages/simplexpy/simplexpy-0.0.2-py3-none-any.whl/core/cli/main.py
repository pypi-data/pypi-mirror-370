# simplex/core/cli/main.py

import click
from simplex import __version__
from simplex.core.cli.auth_commands import auth_cli
from simplex.foundation.cli.commands import foundation_cli
from simplex.beam.cli.commands import beam_cli

@click.group()
@click.help_option('-h', '--help')
@click.version_option(version=__version__, prog_name='simplex')
def cli():
    """Simplex command line interface."""
    pass

cli.add_command(auth_cli, name="auth")
cli.add_command(foundation_cli, name="foundation")
#cli.add_command(beam_cli, name="beam")

def main():
    cli()