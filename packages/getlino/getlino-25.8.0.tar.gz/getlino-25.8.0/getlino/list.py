# Copyright 2021-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import os
import shutil
import secrets
import click

from os.path import join
from importlib import import_module

from synodal import KNOWN_REPOS

STARTSITE_APPS = [r for r in KNOWN_REPOS if r.settings_module]


@click.command()
@click.pass_context
def list(ctx):
    """
    List the available choices for getlino startsite.

    """

    for r in STARTSITE_APPS:
        # r: nickname package_name git_repo settings_module front_end
        # print(r.settings_module)
        if r.verbose_name and r.description:
            tpl = "{r.nickname} ({r.verbose_name}) : {r.description}"
        elif r.description:
            tpl = "{r.nickname} : {r.description}"
        elif r.public_url:
            tpl = "{r.nickname} : {r.public_url}"
        else:
            tpl = "{r.nickname} : {r.settings_module}"
        click.echo(tpl.format(**locals()))
