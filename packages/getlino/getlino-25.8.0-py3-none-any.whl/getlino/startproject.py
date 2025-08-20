# Copyright 2021-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import os
import shutil
import re
from datetime import datetime

import click


def replace_str(s, name, hist):
    rv = [s]
    def replace(old, new):
        rv[0] = rv[0].replace(old, new)
    replace('algus', name)
    replace('Algus', name.capitalize())
    if hist['prefix']:
        replace(f'lino_{name}', hist['prefix'] + "_" + name)
        replace(f'lino-{name}', hist['prefix'] + "-" + name)
        replace(f'Lino {name.capitalize()}',
                hist['prefix'].capitalize() + " " + name.capitalize())
        replace(f'lino {name}', hist['prefix'] + " " + name)
    else:
        replace(f'lino_{name}', name)
        replace(f'lino-{name}', name)
        replace(f"lino {name}", name)
        replace(f'Lino {name.capitalize()}', name.capitalize())

    replace("A template for new Lino applications", hist['description'])
    if s != rv[0] or not hist['core']:
        found = re.findall(hist['patterns'], rv[0])
        if len(found):
            cr, yr1, yr2 = found[0]
            if hist['core']:
                if yr2 == "":
                    cr_info = cr.replace(yr1, yr1 + '-' + hist['year'])
                else:
                    cr_info = cr.replace(yr2, hist['year'])
            else:
                cr_info = cr + "\n# Copyright " + hist['year'] + " " + hist[
                    'author']
                if "@" in hist['email']:
                    cr_info += " <" + hist['email'] + ">"
            replace(cr, cr_info)

    return rv[0]


def rename_dir(name, dr, hist):
    for path in os.listdir(dr):
        path = os.path.join(dr, path)
        if os.path.isdir(path):
            d = path
            if '__pycache__' in d or '.git' in d:
                shutil.rmtree(d)
                continue
            new_d = replace_str(d, name, hist)
            if new_d != d:
                hist['dir_changed'] += 1
                shutil.move(d, new_d, copy_function=shutil.copytree)
                d = new_d
            rename_dir(name, d, hist)
        else:
            assert os.path.isfile(path)
            f = path
            if f.split('.')[-1] not in [
                    'py', 'html', 'rst', 'pot', 'po', 'txt', 'js', 'toml'
            ]:
                continue
            hist['files'] += 1
            if 'README.rst' in f:
                with open(f, "w") as f:
                    f.write(hist['description'])
                hist['edited'] += 1
                continue
            new_f = replace_str(f, name, hist)
            if new_f != f:
                hist['f_changed'] += 1
                shutil.move(f, new_f, copy_function=shutil.copy2)
                f = new_f
            with open(f, 'r+') as f:
                try:
                    c = f.read()
                    content = replace_str(c, name, hist)
                    f.seek(0)
                    f.write(content)
                    f.truncate()
                    if content != c:
                        hist['edited'] += 1
                except UnicodeDecodeError as e:
                    print(f, e)


CORE_HELP = """\
If `True`, `startproject` will treat the new project as one of the lino core
projects. Implications are like using, `lino` as the project prefix and such.
"""

PREFIX_HELP = """\
Name prefix to use on the app name. Ex. `lino_algus`, here: `lino` is the prefix
and `algus` is the app name.
"""

NO_INPUT = """\
Whether to ask the user for inputs for unspecified options such as '--author',
'--email', '--description'.
"""


@click.command()
@click.argument('projectname')
@click.option('--prefix', '-p', default=None, help=PREFIX_HELP)
@click.option('--core', '-c', default=False, is_flag=True, help=CORE_HELP)
@click.option('--author', '-a', help="Author name")
@click.option('--email', '-e', help="Author email")
@click.option('--description', '-d', help="Project description")
@click.option('--no-input',
              'no_input',
              default=False,
              is_flag=True,
              help=NO_INPUT)
@click.pass_context
def startproject(ctx, projectname, prefix, core, author, email, description,
                 no_input):
    """

    Start a new Lino application project.

    Takes one mandatory argument `projectname`, which is the nickname for the
    code repository to create.

    """
    # local import to avoid traceback in "pip install getlino" when git system
    # package is not installed
    import git
    if " " in projectname:
        projectname = projectname.replace(" ", "_")

    if core and not prefix:
        prefix = 'lino'

    if not core:
        if no_input:
            author = ""
            email = ""
        else:
            if not author: author = input("Author name: ").strip()
            if not email: email = input("Author email: ").strip()

    if not description:
        if no_input:
            description = ""
        else:
            description = input("Project description: ").strip()

    algus_backup = False
    lsdr = os.listdir()
    if projectname in lsdr:
        if len(os.listdir(projectname)):
            print(
                f"Failed to start project '{projectname}': Directory not empty."
            )
            return
    if "algus" in lsdr:
        print("Creating backup for algus...")
        shutil.move(os.path.join('.', 'algus'),
                    os.path.join('.', 'algus_bak'),
                    copy_function=shutil.copytree)
        algus_backup = True

    print("Fetching project template...")
    git.Git().clone('https://gitlab.com/lino-framework/algus')

    pn = projectname
    if prefix:
        pn = prefix + "_" + projectname
    print(f"Creating project {pn} from lino_algus...")

    hist = dict(
        patterns=r'(Copyright ([0-9]{4})(?:-([0-9]{4}))? Rumma & Ko Ltd)',
        year=str(datetime.today().year),
        dir_changed=0,
        f_changed=0,
        files=0,
        edited=0,
        prefix=prefix,
        core=core,
        author=author,
        email=email,
        description=description)
    shutil.move('algus', projectname, copy_function=shutil.copytree)
    rename_dir(projectname, projectname, hist)

    print(
        f"Renamed {hist['dir_changed']} directories and {hist['f_changed']} files."
    )
    print(f"Found {hist['files']} files and modified {hist['edited']} files.")
    if algus_backup:
        print("Restoring algus from backup...")
        shutil.move(os.path.join('.', 'algus_bak'),
                    os.path.join('.', 'algus'),
                    copy_function=shutil.copytree)
    print("Done.")
