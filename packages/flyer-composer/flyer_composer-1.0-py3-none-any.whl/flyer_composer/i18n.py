# -*- mode: python -*-
#
# Copyright 2008-2025 by Hartmut Goebel <h.goebel@crazy-compilers.com>
#
# This file is part of flyer-composer.
#
# flyer-composer is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# flyer-composer is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with flyer-composer. If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

__all__ = ["_"]

import gettext
import os

from . import APPLICATION_ID as _domain


def install_in_argparse(translate):
    import argparse
    argparse.__dict__['_'] = translate.gettext
    for name in {'gettext', 'lgettext', 'lngettext',
                 'ngettext', 'npgettext', 'pgettext'}:
        if name in argparse.__dict__:
            argparse.__dict__[name] = getattr(translate, name)


localedir = os.path.join(os.path.dirname(__file__), 'locale')
translate = gettext.translation(_domain, localedir, fallback=True)
_ = translate.gettext

# required to make our translations work in argparse
install_in_argparse(translate)

# Additional string for Python < 3.10:
_('optional arguments')
