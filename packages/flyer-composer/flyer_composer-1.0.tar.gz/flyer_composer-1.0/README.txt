==========================
Flyer Composer
==========================

-------------------------------------------------------------
Rearrange PDF pages to print as flyers on one paper
-------------------------------------------------------------

:Author:    Hartmut Goebel <h.goebel@crazy-compilers.com>
:Version:   Version 1.0
:Copyright: 2008-2025 by Hartmut Goebel
:Licence:   GNU Affero General Public License v3 or later (AGPLv3+)
:Homepage:  http://crazy-compilers.com/flyer-composer

`Flyer Composer` can be used to prepare one- or two-sided flyers for
printing on one sheet of paper.

Imagine you have designed a flyer in A6 format and want to print it using your
A4 printer. Of course, you want to print four flyers on each sheet. This is
where `Flyer Composer` steps in, creating a PDF which holds your flyer
four times. If you have a second page, `Flyer Composer` can arrange it
the same way - even if the second page is in a separate PDF file.

This also work if your input file was designed for e.g. A2: it will simply be
scaled down to A6 and placed four times in the sheet. And, of course,  `PDF
Flyer Composer` supports other flyer sizes or paper sizes, too.

This is much like `pdfnup` (or `psnup`), except that the *same* page is
put the paper several times.

`Flyer Composer` contains two programs: a Qt-based GUI one
(`flyer-composer-gui`) and a command line one (`flyer-composer`).

For more information please refer to the manpage or visit
the `project homepage <http://crazy-compilers.com/flyer-composer>`_.


Download
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Flyer Composer` for Windows and Linux can be downloaded from
http://crazy-compilers.com/flyer-composer.


Installing from PyPI
~~~~~~~~~~~~~~~~~~~~~~~

If you have Python installed on your system,
`Flyer Composer` can easily be installed using::

  pip install flyer_composer

If you also want the Qt GUI, run::

  pip install flyer_composer[gui]

Please help translating
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Flyer Composer` and its siblings are continually being translated
using `Codeberg Translate`__.
Feel free to take your part in the effort of making `Flyer Composer` available
in as many human languages as possible.
It brings `Flyer Composer` closer to its users!

__ https://translate.codeberg.org/projects/pdftools/


Requirements when Installating from Source
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to install `Flyer Composer` from source, make sure you have the
following software installed:

* `Python 3`__  (tested with Python 3.8–3.13),
* `pip`__ for installation, and
* `pypdf`__ (5.5 or newer, tested with 5.8.0)

For the Qt GUI additionally:

* `PyQt5`__ and
* `python-poppler-qt5`__ or `PyMuPDF`__.

For further information please refer to the `Installation instructions
<https://flyer-composer.readthedocs.io/en/latest/Installation.html>`_.

__ https://www.python.org/download/
__ https://pypi.org/project/pip
__ https://pypi.org/project/pypdf
__ https://pypi.org/project/PyQt5/
__ https://pypi.python.org/pypi/python-poppler-qt5/
__ https://pypi.org/project/PyMuPDF/

.. This file is part of flyer-composer.
   Copyright (C) 2019-2025 Hartmut Goebel
   Licensed under the GNU Free Documentation License v1.3 or any later version.
   SPDX-License-Identifier: GFDL-1.3-or-later

.. Emacs config:
 Local Variables:
 mode: rst
 End:
