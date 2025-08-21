# simplex/foundation/cli/commands.py

import click
import simplex.foundation.model.project

@click.group()
@click.help_option('-h', '--help')
def foundation_cli():
    """Foundation analysis and design commands"""
    pass

@foundation_cli.command()
@click.option("--input", "-i", type=click.Path(exists=True), help="Path to project excel input file")
@click.option("--output", "-o", type=click.Path(), help="Where to save the foundation results", default="foundation.json")
def from_excel(input, output):
    """Run foundation analysis from excel input file""" 
    click.echo(f"Running foundation analysis for: {input}")

    project = simplex.foundation.model.project.Project.from_excel(input)

    project.save_as_json(output)


    # TODO: 
    click.echo(f"Saving project to: {output}")
    click.echo("✅ Analysis complete.")