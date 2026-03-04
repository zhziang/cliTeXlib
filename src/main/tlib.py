from .search import search
from .new import new
from .open import open
from .remove import remove

import click

@click.group()
def tlib():
    pass

tlib.add_command(new)
tlib.add_command(open)
tlib.add_command(remove)
tlib.add_command(search)
