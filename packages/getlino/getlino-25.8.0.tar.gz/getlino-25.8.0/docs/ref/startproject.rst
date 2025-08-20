.. doctest docs/specs/getlino/startproject.rst

=======================================
The :cmd:`getlino startproject` command
=======================================

.. command:: getlino startproject

.. program:: getlino startproject

Create a new :term:`Lino application` using the :ref:`algus` repository as
template.


.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from atelier.sheller import Sheller
>>> shell = Sheller()

>>> shell("getlino startproject --help")  #doctest: +NORMALIZE_WHITESPACE
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
Usage: getlino startproject [OPTIONS] PROJECTNAME
<BLANKLINE>
  Start a new Lino application project.
<BLANKLINE>
  Takes one mandatory argument `projectname`, which is the nickname for the
  code repository to create.
<BLANKLINE>
Options:
  -p, --prefix TEXT       Name prefix to use on the app name. Ex.
                          `lino_algus`, here: `lino` is the prefix and `algus`
                          is the app name.
<BLANKLINE>
  -c, --core              If `True`, `startproject` will treat the new project
                          as one of the lino core projects. Implications are
                          like using, `lino` as the project prefix and such.
<BLANKLINE>
  -a, --author TEXT       Author name
  -e, --email TEXT        Author email
  -d, --description TEXT  Project description
  --no-input              Whether to ask the user for inputs for unspecified
                          options such as '--author', '--email', '--
                          description'.
<BLANKLINE>
  --help                  Show this message and exit.


>>> shell("getlino startproject foo --no-input")
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
Fetching project template...
Creating project foo from lino_algus...
Renamed 3 directories and 1 files.
Found 55 files and modified 39 files.
Done.


This command creates a new local Git repository named "example" as a clone from
https://gitlab.com/lino-framework/algus, then renames all files and directories
containing "algus" in their name to "example", then  replaces all occurences of
"algus" by "example" (and "Algus" by "Example") in all the source files (`.py`,
`.rst`, `.html`, `.toml`).
