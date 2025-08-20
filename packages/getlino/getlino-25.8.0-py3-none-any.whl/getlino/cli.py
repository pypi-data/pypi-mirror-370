# Copyright 2019-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""The main entry point for the :cmd:`getlino` command.
"""

import click
import distro

from getlino import __version__

from .configure import configure
from .startsite import startsite
from .startproject import startproject
from .list import list


@click.group(help="""
``getlino`` is a command-line tool for installing Lino in different environments.
See https://getlino.lino-framework.org for more information.

This is getlino version {} running on {}.
""".format(__version__, distro.name(pretty=True)))
def main():
    pass


main.add_command(configure)
main.add_command(startsite)
main.add_command(startproject)
main.add_command(list)

if __name__ == '__main__':
    main()
    # main(auto_envvar_prefix='GETLINO')
