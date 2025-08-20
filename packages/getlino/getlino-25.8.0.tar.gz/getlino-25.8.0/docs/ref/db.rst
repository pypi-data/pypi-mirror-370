.. doctest docs/ref/db.rst
.. _getlino.db:

=============================
Getlino and database settings
=============================

Getlino knows the following Django database engines:

>>> from getlino.utils import DB_ENGINES
>>> import rstgen
>>> cols = "name python_packages service default_port needs_root"
>>> print(rstgen.attrtable(DB_ENGINES, cols))  #doctest: +ELLIPSIS
============ ================= ============ ============== ============
 name         python_packages   service      default_port   needs_root
------------ ----------------- ------------ -------------- ------------
 mysql        mysqlclient       mysql        3306           True
 postgresql   psycopg2          postgresql   5432           True
 sqlite3                        None                        False
============ ================= ============ ============== ============
<BLANKLINE>

A dbengine also has an attribute :attr:`apt_packages`, but we don't print it
here because its value can depend on the environment.


.. _getlino.db.settings:

Database settings
=================

Getlino fills values to the items `user`, `password`, `password` and `engine` of
Django's :setting:`DATABASES` setting.



Multiple database engines on a same server
==========================================

Note that :cmd:`getlino startsite` does not install any db engine because this
is done by :cmd:`getlino configure`.

When you maintain a Lino server, you don't want to decide for each new site
which database engine to use. You decide this once during :cmd:`getlino
configure`. In general, `apt-get install` is called only during :cmd:`getlino
configure`, never during :cmd:`getlino startsite`. If you have a server with
some mysql sites and exceptionally want to install a site with postgres, you
simply call :cmd:`getlino configure` before calling :cmd:`getlino startsite`.

You may use multiple database engines on a same server by running configure
between startsite invocations.
