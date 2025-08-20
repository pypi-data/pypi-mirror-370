.. _getlino.install:

==================
Installing getlino
==================

Install
=======

The easiest way to install getlino is via pip::

  $ pip install getlino

To update your getlino to the newest version simply run::

  $ pip install -U getlino`


More options
============

You can optionally install your own local clone of getlino::

   $ cd ~/lino/env/repositories
   $ git clone git@gitlab.com:lino-framework/getlino.git
   $ pip install -e getlino

In that last use case don't forget to manually add getlino to your
:xfile:`./atelier/config.py` file.
