#!/usr/bin/env python3
"""
flyer_composer.cli - command line interface for flyer-composer
"""
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

__author__ = "Hartmut Goebel <h.goebel@crazy-compilers.com>"
__copyright__ = "Copyright 2008-2025 by Hartmut Goebel <h.goebel@crazy-compilers.com>"
__licence__ = "GNU Affero General Public License v3 or later (AGPLv3+)"

import re
import pypdf.errors
import argparse

from . import (main, __version__, DEFAULT_MEDIASIZE,
               Box, papersizes, DecryptionError)
from .i18n import _

# pattern for parsing user textual box spec
pat_box = re.compile(r'''
     ( (?P<width>  (\d*\.)? \d+) x                 # width "x" height
       (?P<height> (\d*\.)? \d+) )?
     (?P<offset> \+                                # "+" offset_x "," offset_y
                 (?P<offset_x> \d+\.? | \d*\.\d+)
                 ,
                 (?P<offset_y> \d+\.? | \d*\.\d+) ) ?
     (?P<unit> [a-z][a-z0-9\-\\_]*)                # unit
     ''', re.X+re.I)


def __parse_box(value, allow_offset=False):
    m = pat_box.match(value)
    if not m:
        raise argparse.ArgumentTypeError(
            _("I don't understand your box specification %r") % value)
    res = m.groupdict()
    if not allow_offset and res['offset'] is not None:
        raise argparse.ArgumentTypeError(
            _("Offset not allowed in box definition"))
    # res['offset'] is only used for error checking, remove it
    del res['offset']

    # get meassures of unit
    unit = res['unit'].lower()
    if unit not in papersizes:
        unit = [name for name in papersizes.keys()
                if name.startswith(unit)]
        if len(unit) == 0:
            raise argparse.ArgumentTypeError(
                _("I don't understand your papersize name %r") % res['unit'])
        elif len(unit) != 1:
            raise argparse.ArgumentTypeError(
                _("Your papersize name %r is not unique, give more chars")
                % res['unit'])
        unit = unit[0]
    unit_x, unit_y = papersizes[unit]
    res2 = Box({
        'width'   : float(res['width'] or 1) * unit_x,
        'height'  : float(res['height'] or 1) * unit_y,
        'offset_x': float(res['offset_x'] or 0) * unit_x,
        'offset_y': float(res['offset_y'] or 0) * unit_y,
        'unit': unit,
        'units_x': float(res['width'] or 1),
        'units_y': float(res['height'] or 1),
        })
    return res2


class HelpMediaNames(argparse.Action):
    def __call__(*args, **kw):
        import textwrap
        print('Available media and distance names:')
        names = list(papersizes.keys())
        names.sort()
        for l in textwrap.wrap(' '.join(names), width=65):
            print(' ', l)
        raise SystemExit(0)


def run(args=None):

    parser = argparse.ArgumentParser()
    parser.add_argument('--help-media-names', action=HelpMediaNames,
                        nargs=0,
                        help=_("list available media and distance names"))
    parser.add_argument('--version', action='version',
                        help=_("show program's version number and exit"),
                        version="%(prog)s " + __version__)
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help=_("show what would have been done, but do not "
                               "generate files"))

    group = parser.add_argument_group(_("Define Input"))
    group.add_argument('-F', '--front', type=int, dest='front_page',
                       metavar=_("INTEGER"), default=1,  # 1-based user input
                       help=_("front page of flyer (default: first page)"))
    group.add_argument('-B', '--back', type=int, dest='back_page',
                       metavar=_("INTEGER"),
                       help=_("back page of flyer (default: no back page)"))
    group.add_argument('-A', '--art-box',
                       action='store_true', dest='use_ArtBox',
                       help=_("use the content area defined by the ArtBox "
                              '(default: use the area defined by '
                              'the TrimBox)'))

    group = parser.add_argument_group(_("Define Output"))
    group.add_argument('-f', '--flyer-size',
                       type=__parse_box, metavar=_("BOX"),
                       help=_("specify the finished flyer size "
                              "(defaults to media size)"))
    group.add_argument('-m', '--media-size',
                       default=__parse_box(DEFAULT_MEDIASIZE),
                       type=__parse_box, metavar=_("BOX"),
                       help=_("specify the page size of the output media "
                              '(default: %s)') % DEFAULT_MEDIASIZE)

    parser.add_argument('infilename', metavar=_("InputFile"))
    parser.add_argument('outfilename', metavar=_("OutputFile"))

    args = parser.parse_args(args)

    if not args.flyer_size:
        args.flyer_size = args.media_size.copy()

    args = vars(args)
    del args["help_media_names"]
    # bounds-checks are done in `main()`
    args['front_page'] -= 1
    if args['back_page'] is not None:
        args['back_page'] -= 1
    try:
        main(**args)
    except DecryptionError as e:  # pragma: no cover
        raise SystemExit(str(e))
    except pypdf.errors.PdfReadError as e:
         raise SystemExit(
             _('The input-file is either corrupt or no PDF at all: %s') % e)


if __name__ == '__main__':  # pragma: no cover
    run()
