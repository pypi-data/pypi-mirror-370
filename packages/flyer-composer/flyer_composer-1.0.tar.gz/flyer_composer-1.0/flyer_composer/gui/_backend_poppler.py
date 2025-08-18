#
# Copyright 2019-2025 by Hartmut Goebel <h.goebel@crazy-compilers.com>
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

# The idea on how to load PDF documents using popplerqt5 and the
# load-callback is based on code
#   Copyright 2018 by Akkana Peck: share and enjoy under the GPLv2 or later.

__author__ = "Hartmut Goebel <h.goebel@crazy-compilers.com>"
__copyright__ = "Copyright 2019-2025 by Hartmut Goebel <h.goebel@crazy-compilers.com>"
__licence__ = "GNU Affero General Public License v3 or later (AGPLv3+)"

__all__ = ["PDFDocument"]

from PyQt5.QtGui import QPixmap
from popplerqt5 import Poppler

from .. import POINTS_PER_INCH


class PDFDocument(Poppler.Document):

    @classmethod
    def load(cls, filename):
        doc = Poppler.Document.load(filename)
        if not doc:
            return doc
        doc.setRenderHint(PDFDocument.TextAntialiasing)
        doc.filename = filename
        doc.__class__ = cls
        return doc

    def get_page_pixmap(self, pageno, width, height):
        page = self.page(pageno-1)
        ps = page.pageSize()
        page_width = ps.width()
        page_height = ps.height()

        if page_width > page_height:
            # landscape: width is the limiting factor
            dpi = POINTS_PER_INCH * width / page_width
        else:
            # height is the limiting factor
            dpi = POINTS_PER_INCH * height / page_height

        # Get a pixmap of the PDF page
        pimg = page.renderToImage(dpi, dpi)
        return QPixmap.fromImage(pimg)
