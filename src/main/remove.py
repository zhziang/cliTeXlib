import click
import os
import shutil

@click.command()
@click.argument('names', nargs=-1)
def remove(names):
    """Remove specified TeX projects from ./.texs directory."""
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if not names:
        click.echo("No project names provided.")
        return
    for name in names:
        project_path = os.path.join(os.path.join(base_path, "texs"), name)
        if os.path.exists(project_path):
            try:
                if os.path.isdir(project_path):
                    shutil.rmtree(project_path)
                    click.echo(f"Removed project directory: {name}")
                else:
                    os.remove(project_path)
                    click.echo(f"Removed project file: {name}")
            except Exception as e:
                click.echo(f"Error removing {name}: {e}")
        else:
            click.echo(f"Project {name} does not exist in texs")

if __name__ == '__main__':
    remove()