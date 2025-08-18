# -*- mode: python -*-
"""
flyer_composer - rearrange PDF pages to print as "flyers" on one page
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
__version__ = '1.0'

APPLICATION_ID = "flyer-composer"
APPLICATION_NAME = "Flyer Composer"

import io
from pypdf import PdfWriter, PdfReader, PageObject, Transformation
from pypdf.generic import ContentStream, NameObject, RectangleObject

DEFAULT_MEDIASIZE = 'a4'

POINTS_PER_INCH = 72
mm = POINTS_PER_INCH / 25.4

# Taken from poster.c
papersizes = {
    'pt'  : (1, 1),
    'inch': (72, 72),
    'ft'  : (12 * 72, 12 * 72),  # 12 inch
    'mm'  : (mm, mm),
    'cm'  : (10 * mm, 10 * mm),
    'm'   : (1000 * mm, 1000 * mm),

    # American page sizes (taken from psposter.c)
    "monarch"  : (279, 540),
    "statement": (396, 612),
    "executive": (540, 720),
    "quarto"   : (610, 780),
    "letter"   : (612, 792),
    "folio"    : (612, 936),
    "legal"    : (612, 1008),
    "tabloid"  : (792, 1224),
    "ledger"   : (792, 1224),

    # ISO page sizes
    "a0" : (841*mm, 1189*mm),
    "a1" : (594*mm, 841*mm),
    "a2" : (420*mm, 594*mm),
    "a3" : (297*mm, 420*mm),
    "a4" : (210*mm, 297*mm),
    "a5" : (148*mm, 210*mm),
    "a6" : (105*mm, 148*mm),
    "a7" : (74*mm, 105*mm),
    "a8" : (52*mm, 74*mm),
    "a9" : (37*mm, 52*mm),
    "a10": (26*mm, 37*mm),

    # DIN lang is considered to be a landscape format
    "dinlang"   : (210*mm, 297*mm / 3),  # 1/3 a4
    "envdinlang": (220*mm, 110*mm),  # envelope for Din lang

    "b0" : (2835, 4008),
    "b1" : (2004, 2835),
    "b2" : (1417, 2004),
    "b3" : (1001, 1417),
    "b4" : (709, 1001),
    "b5" : (499, 709),
    "b6" : (354, 499),
    "b7" : (249, 354),
    "b8" : (176, 249),
    "b9" : (125, 176),
    "b10": (88, 125),

    "c4" : (649, 918),
    "c5" : (459, 649),
    "c6" : (323, 459),

    # Japanese page sizes (taken from psposter.c)
    "jb0" : (2920, 4127),
    "jb1" : (2064, 2920),
    "jb2" : (1460, 2064),
    "jb3" : (1032, 1460),
    "jb4" : (729, 1032),
    "jb5" : (516, 729),
    "jb6" : (363, 516),
    "jb7" : (258, 363),
    "jb8" : (181, 258),
    "jb9" : (128, 181),
    "jb10": (91, 128),

    # Envelope No. 10 is considered to be a landscape format
    "comm10": (684, 298),
    "com10" : (684, 298),
    "env10" : (684, 298),
    }


class DecryptionError(ValueError):
    pass


PAGE_BOXES = ("/MediaBox", "/CropBox", "/BleedBox", "/TrimBox", "/ArtBox")


class Box(dict):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def copy(self):
        return Box(**self)

    def rotate(self):
        for a, b in (('width', 'height'),
                     ('offset_x', 'offset_y'),
                     ('units_x', 'units_y')):
            self[a], self[b] = self[b], self[a]

    @property
    def is_landscape(self):
        return (self['width']-self['offset_x']
                > self['height']-self['offset_y'])

    def ensure_portrait(self):
        """if box is landscape spec, rotate to portrait.
        """
        if self.is_landscape:
            self.rotate()
            return True

    @staticmethod
    def from_pdfbox(pdfbox):
        return Box({
            'width'   : pdfbox.width,
            'height'  : pdfbox.height,
            'offset_x': pdfbox.left,
            'offset_y': pdfbox.bottom,
            # the following are unused, but need to be set to make
            # `rotate_box()` work
            'units_x' : None,
            'units_y' : None,
            })

    @staticmethod
    def from_papersize(name):
        return Box({
            'width': papersizes[name][0],
            'height': papersizes[name][1],
            'offset_x': 0,
            'offset_y': 0,
            'unit': name,
            'units_x': 1,
            'units_y': 1,
            })


def decide_num_cols_rows(flyerbox, mediabox):
    """Calculate how many flyers fit on one sheet.
    Return flyerbox (eventually rotated and adjusted),
    number of rows, number of cols.
    """
    # avoid changing original flyerbox
    flyerbox = flyerbox.copy()
    cutmargin   = {'x': 0, 'y': 0}  # todo
    whitemargin = {'x': 0, 'y': 0}  # todo
    # media and image sizes (inbox) are fixed already
    # available drawing area per sheet
    drawable_x = mediabox['width' ] - 2 * cutmargin['x']
    drawable_y = mediabox['height'] - 2 * cutmargin['y']

    size_x = flyerbox["width"]
    size_y = flyerbox["height"]

    # num flyers on page without rotation
    ncols0 = int(drawable_x / size_x)
    nrows0 = int(drawable_y / size_y)
    # num flyers on page with rotation
    ncols1 = int(drawable_y / size_x)
    nrows1 = int(drawable_x / size_y)

    # Decide whether we get more flysers on one sheet if rotating the
    # flyerbox.
    rotate = (ncols0*nrows0) < (ncols1*nrows1)

    if rotate:
        flyerbox.rotate()
        ncols = nrows1
        nrows = ncols1
    else:
        ncols = ncols0
        nrows = nrows0
    return flyerbox, ncols, nrows


def decide_scale(inbox, flyerbox):
    """decide on scale factor and rotation of input page
    The flyerbox defines the descrionation size and orientation
    """
    inbox = inbox.copy()

    # If the inbox orientation differs from the flyerbox orentation, rotate
    # the inbox.
    rotate = False
    if inbox.is_landscape != flyerbox.is_landscape:
        rotate = True
        inbox.rotate()
    inbox_x = float(inbox['width'])
    inbox_y = float(inbox['height'])
    # calculate scale factor from output size
    scale = min(flyerbox['width'] / inbox_x,
                flyerbox['height'] / inbox_y)
    return scale, rotate


def copyPage(page):
    newpage = PageObject()
    newpage.update(page)
    # Copy Rectangles to be manipulatable
    for attr in PAGE_BOXES:
        if attr in page:
            newpage[NameObject(attr)] = RectangleObject(list(page[attr]))
    return newpage


def _clip_pdf_page(page, x, y, width, height):
    content = ContentStream(page["/Contents"].get_object(), None)
    content.operations[:0] = [
        ([], b'q'),  # save graphic state
        (RectangleObject((x, y, width, height)), b're'),  # rectangle path
        ([], b'W*'),  # clip
        ([], b'n'),   # cancel path w/ filling or stroking
        ]
    content.operations.append([[], b'Q'])  # restore graphic state
    page[NameObject('/Contents')] = content


def flyerize(outpdf, inpage, flyerbox, mediabox, use_ArtBox=False):
    """
    inpage: input page
    flyerbox: size secs of the resulting flyer
    mediabox: size secs of the media to print on
    """
    if use_ArtBox: # pragma: no cover
        inbox = Box.from_pdfbox(inpage.artbox)
    else:
        inbox = Box.from_pdfbox(inpage.trimbox)
    _clip_pdf_page(inpage, inbox['offset_x'], inbox['offset_y'],
                   inbox['width'], inbox['height'])
    mediabox = mediabox.copy()
    flyerbox, ncols, nrows = decide_num_cols_rows(flyerbox, mediabox)
    scale, rotate = decide_scale(inbox, flyerbox)

    # area to put on each page (allows for overlay of margin)
    h_step = flyerbox['width' ] - flyerbox['offset_x']
    v_step = flyerbox['height'] - flyerbox['offset_y']

    if rotate:
        mediabox.rotate()
        ncols, nrows = nrows, ncols
        h_step, v_step = v_step, h_step

    if use_ArtBox: # pragma: no cover
        trimbox = Box.from_pdfbox(inpage.artbox)
    else:
        trimbox = Box.from_pdfbox(inpage.trimbox)
    newpage = outpdf.add_blank_page(mediabox['width' ] - mediabox['offset_x'],
                                    mediabox['height'] - mediabox['offset_y'])
    assert newpage is not None
    for col in range(ncols):
        h_pos = col * h_step
        for row in range(nrows):
            v_pos = row * v_step
            pagecopy = copyPage(inpage)
            __mergeScaledTranslatedPage(
                newpage, pagecopy, scale=scale, tx=h_pos, ty=v_pos)


# Keep old PyPDF2 interface for the tests
def __mergeScaledTranslatedPage(page1, page2, scale, tx, ty, expand=False):
    page1.merge_transformed_page(
        page2, Transformation().scale(scale).translate(tx, ty), expand=expand)


def password_hook():  # pragma: no cover
    import getpass
    return getpass.getpass()


def main(infilename, outfilename, flyer_size, media_size,
         front_page=0, back_page=None, infilename_back=None,
         use_ArtBox=False, dry_run=False,
         password_hook=password_hook):
    """page-numbers are zero-based"""
    if not isinstance(flyer_size, Box):
        flyer_size = Box.from_papersize(flyer_size)
    if not isinstance(media_size, Box):
        media_size = Box.from_papersize(media_size)

    page_nums = [(infilename, front_page)]
    if infilename_back and back_page is not None:
        page_nums.append((infilename_back, back_page))
    elif infilename_back:
        page_nums.append((infilename_back, front_page))
    elif back_page is not None:
        page_nums.append((infilename, back_page))
    merger = PdfWriter()
    for filename, pn in page_nums:
        with open(filename, 'rb') as fh:
            inpdf = PdfReader(fh)
            if inpdf.is_encrypted:
                # try empty password first
                if not inpdf.decrypt(''):  # pragma: no cover
                    if not inpdf.decrypt(password_hook()):
                        raise DecryptionError("Can't decrypt PDF. Wrong Password?")
            merger.append(inpdf, pages=(pn, pn+1), import_outline=False)

    # write merges PDF to a buffer to be able
    buffer = io.BytesIO()
    merger.write(buffer)
    merger.close()  # free resources

    inpdf = PdfReader(buffer)
    outpdf = PdfWriter()
    for page in inpdf.pages:
        flyerize(outpdf, page, flyer_size, media_size, use_ArtBox)

    if not dry_run:
        outpdf.compress_identical_objects()
        with open(outfilename, 'wb') as fh:
            outpdf.write(fh)
