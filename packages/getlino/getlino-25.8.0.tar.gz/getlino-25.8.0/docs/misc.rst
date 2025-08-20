.. doctest docs/misc.rst

=============
Miscellaneous
=============

>>> from getlino.utils import perm2text
>>> print(perm2text(0o3777))
rwxrwsrwt
>>> print(perm2text(0o2775))
rwxrwsr-x
>>> print(perm2text(1533))
rwxrwsr-x
>>> print(perm2text(509))
rwxrwxr-x
>>> print(perm2text(436))
rw-rw-r--

>>> print(perm2text(1))
--------x

>>> print(perm2text(0o123456))
Traceback (most recent call last):
...
Exception: value must be less than 0o7777


Reproduce Johana's first bug:

>>> import requests
>>> from synodal import KNOWN_REPOS
>>> for repo in KNOWN_REPOS:
...     if not repo.git_repo:
...         continue
...     r = requests.get(repo.git_repo)
...     if r.status_code == 200:
...         print(repo.git_repo, "OK")
...     else:
...         print("Oops: {} --> {}".format(repo.git_repo, r.status_code))
... #doctest: +REPORT_UDIFF +NORMALIZE_WHITESPACE
https://gitlab.com/lino-framework/atelier.git OK
https://github.com/lino-framework/etgen OK
https://github.com/lino-framework/eidreader OK
https://github.com/lsaffre/commondata OK
https://gitlab.com/lino-framework/getlino.git OK
https://gitlab.com/lino-framework/lino.git OK
https://gitlab.com/lino-framework/xl.git OK
https://gitlab.com/lino-framework/welfare.git OK
https://gitlab.com/lino-framework/react.git OK
https://gitlab.com/lino-framework/openui5.git OK
https://gitlab.com/lino-framework/book.git OK
https://gitlab.com/lino-framework/cg.git OK
https://gitlab.com/lino-framework/ug.git OK
https://gitlab.com/lino-framework/hg.git OK
https://gitlab.com/lino-framework/lf.git OK
https://gitlab.com/synodalsoft/ss.git OK
https://gitlab.com/lino-framework/algus.git OK
https://gitlab.com/lino-framework/amici.git OK
https://gitlab.com/lino-framework/avanti.git OK
https://gitlab.com/lino-framework/cms.git OK
https://gitlab.com/synodalsoft/prima.git OK
https://gitlab.com/lino-framework/care.git OK
https://gitlab.com/lino-framework/cosi.git OK
https://gitlab.com/lino-framework/mentori.git OK
https://gitlab.com/lino-framework/noi.git OK
https://gitlab.com/lino-framework/presto.git OK
https://gitlab.com/lino-framework/pronto.git OK
https://gitlab.com/lino-framework/tera.git OK
https://gitlab.com/lino-framework/shop.git OK
https://gitlab.com/lino-framework/vilma.git OK
https://gitlab.com/lino-framework/voga.git OK
https://gitlab.com/lino-framework/weleup.git OK
https://gitlab.com/lino-framework/welcht.git OK
