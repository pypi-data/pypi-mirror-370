import os
import click
import pkgutil


__version__ = pkgutil.get_data(__package__, 'VERSION.txt').decode('ascii').strip()


@click.group()
def cli():
    pass


try:
    with open(os.path.join(os.path.expanduser('~'), '.mgquant', 'notice'), 'r') as f:
        msg = f.read()
        msg and print(msg)
except FileNotFoundError:
    pass
