====================================
The :cmd:`getlino list` command
====================================

.. command:: getlino list

.. program:: getlino list

Show the list of Lino applications known to :cmd:`getlino startsite`.

>>> from atelier.sheller import Sheller
>>> shell = Sheller()
>>> shell("getlino list")  #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
min1 : lino_book.projects.min1.settings
min2 : lino_book.projects.min2.settings
cosi4 : a Lino Così for Uruguay
cosi5 : a Lino Così for Bangladesh
tera2 : A customized Lino Voga site
cosi3 : A Lino Così for Estonia
cosi2 : A Lino Così for Belgium (FR)
cosi1 : A Lino Così for Belgium (DE)
tera1 : A customized Lino Tera site
noi1r : noi1e with React front end
chatter : an instant messaging system
polly : A little polls manager
amici (Lino Amici) : Manage your family contacts
avanti (Lino Avanti) : Manage the integration course of immigrants in East Belgium
cms (Lino CMS) : A content management system.
prima (Lino Prima) : Manage evaluation results and certificates in a primary school
care (Lino Care) : Manage a network of helpers.
cosi (Lino Così) : A simple accounting application.
mentori (Lino Mentori) : A Lino Django application for managing internships, mentors and students
noi (Lino Noi) : Manage support tickets and working time.
presto (Lino Presto) : Manage home services given to private persons
pronto (Lino Pronto) : A Lino for assembling and selling products
tera (Lino Tera) : A Lino for managing therapeutic centres
shop (Lino Shop) : A Lino for managing a webshop
vilma (Lino Vilma) : Manage contacts, resources and skills of a village community
voga (Lino Voga) : A Lino Django application for managing courses, participants and meeting rooms
weleup (Lino Welfare Eupen) : A Lino Django application for the PCSW of Eupen
welcht (Lino Welfare Châtelet) : A Lino Django application for the PCSW of Châtelet


More detailed descriptions are available in the Lino
Developer Guide page :ref:`getlino.apps`.
