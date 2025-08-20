====================================
The :cmd:`getlino startsite` command
====================================

This page is about the :cmd:`getlino startsite` command.
Used for example in :ref:`lino.tutorial.hello` and in :ref:`lino.admin.install`.

.. command:: getlino startsite

.. program:: getlino startsite

Create a new :term:`Lino site` on a :term:`Lino server` that has previously been
configured using :cmd:`getlino configure`. Optionally reinstall an existing site
or finish an interrupted installation.

.. contents::
   :depth: 1
   :local:


Usage
=====

Usage: getlino startsite [OPTIONS] APPNAME [PRJNAME]

Two mandatory arguments must be given unless :option:`--ini-file` is specified:

- ``APPNAME`` : The application to run on the new site.
  Run :cmd:`getlino list` to get a list of available choices.

- ``PRJNAME`` : The nickname for the new site. We recommend lower-case only and
  digits but no "-" or "_". Examples:  foo, foo2, mysite, first, The name must
  be unique for this Lino server and  will become a subdirectory of the
  `--sites-base` directory specified by `getlino configure`.

.. rubric:: Run-time behaviour options:

.. option:: --ini-file

  Existing :xfile:`lino.ini` file to read options from.

.. option:: --batch

  Whether to run in batch mode, i.e. without asking any questions.  Assume
  yes to all questions. Don't use this on a machine that is already being
  used.

.. rubric:: Settings for the new site

.. The script will ask you some questions unless :option:`--batch` is specified.

.. option:: --site-domain

  Fully qualified domain name for this site (without 'http(s)://' prefix).

.. option:: --db-user

    See :ref:`getlino.db.settings`. If this is empty or not specified,
    :cmd:`getlino startsite` will use the server-wide default value specified
    by :option:`getlino configure --db-user`.

.. option:: --db-engine

    See :ref:`getlino.db.settings`. If this is empty or not specified,
    :cmd:`getlino startsite` will use the server-wide default value specified by
    :option:`getlino configure --db-engine`.

.. option:: --db-port

    See :ref:`getlino.db.settings`. If this is empty or not specified,
    :cmd:`getlino startsite` will use the server-wide default value specified by
    :option:`getlino configure --db-port`.

.. option:: --db-password

    See :ref:`getlino.db.settings`. If this is empty or not specified,
    :cmd:`getlino startsite` will use the server-wide default value specified by
    :option:`getlino configure --db-password`.


.. option:: --dev-repos

    A space-separated list of repositories for which this site uses the
    development version (i.e. not the PyPI release).

    Usage example::

        $ getlino startsite avanti mysite --dev-repos "lino xl"

    Not that the sort order is important. The following would not work::

        $ getlino startsite avanti mysite --dev-repos "xl lino"

.. option:: --shared-env

    Full path to the shared virtualenv to use for this site.
    Default value is the value specified during :option:`getlino configure --shared-env`
    If this is empty, the new site will get its own virgin environment.


.. _getlino.startsite.troubleshooting:

Troubleshooting
===============

When :cmd:`getlino startsite` was interrupted, then it gets interesting.

- Save the console output for further reference.

- Keep in mind that you can invoke :cmd:`getlino startsite` with the name of an
  existing site in order to **re-install** that site.

- If you aren't sure whether the database has been set up correctly, use the
  :ref:`mysql.cheat_sheet`

- Use the `source code
  <https://gitlab.com/lino-framework/getlino/-/blob/master/getlino/startsite.py>`__.


The getlino site.ini file
=========================

If your applications is not listed in the applications known by getlino or if
you'd like to install/deploy django application you can define a
**filename.ini** file (use the example template `here
<https://gitlab.com/lino-framework/getlino/-/blob/master/getlino/templates/lino.ini>`__).
Where `appname`, `prjname`, `git_repo` and `settings_module` are mandatory
options in the `getlino` section. Everything else is optional. If you are
deploying a django (non-lino) you must specify `use_django_settings` as `True`.

Then run the command::

    # getlino startsite --ini-file filename.ini


Tested section
==============

>>> from atelier.sheller import Sheller
>>> shell = Sheller()
>>> shell("getlino startsite --help")  #doctest: +NORMALIZE_WHITESPACE
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
Usage: getlino startsite [OPTIONS] APPNAME [PRJNAME]
<BLANKLINE>
  Create a new Lino site.
<BLANKLINE>
  Two mandatory arguments must be given unless `--ini-file` is specified:
<BLANKLINE>
  APPNAME : The application to run on the new site. Say `getlino list` to see
  a list of choices.
<BLANKLINE>
  PRJNAME : The nickname for the new site. We recommend lower-case only and
  digits but no "-" or "_". Examples:  foo, foo2, mysite, first, The name must
  be unique for this Lino server and  will become a subdirectory of the
  `--sites-base` directory specified by `getlino configure`.
<BLANKLINE>
Options:
  --ini-file FILENAME             Read options from an existing lino.ini file.
  --batch / --no-batch            Whether to run in batch mode, i.e. without
                                  asking any questions.  Don't use this on a
                                  machine that is already being used.
  --dev-repos TEXT                List of packages for which to install
                                  development version
  --shared-env TEXT               Directory with shared virtualenv
  --site-domain TEXT              FQDN for this site (without 'http(s)://'
                                  prefix).
  --db-engine [mysql|postgresql|sqlite3]
                                  Database engine to use.
  --db-port TEXT                  Database port to use.
  --db-host TEXT                  Database host name to use.
  --db-user TEXT                  Database user name to use. Leave empty to
                                  use the project name.
  --db-password TEXT              Password for database user. Leave empty to
                                  generate a secure password.
  --help                          Show this message and exit.
