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

__author__ = "Hartmut Goebel <h.goebel@crazy-compilers.com>"
__copyright__ = "Copyright 2019-2025 by Hartmut Goebel <h.goebel@crazy-compilers.com>"
__licence__ = "GNU Affero General Public License v3 or later (AGPLv3+)"

__all__ = ["PDFDocument"]

from PyQt5.QtGui import QPixmap, QImage
import fitz  # PyMuPDF


class PDFDocument():

    @classmethod
    def load(cls, filename):
        doc = fitz.open(filename)
        if not doc:
            return None
        obj = cls()
        obj._doc = doc
        obj.filename = filename
        return obj

    def numPages(self):
        return self._doc.page_count

    def get_page_pixmap(self, pageno, width, height):
        page = self._doc.load_page(pageno-1)  # 0-based
        page_width = page.rect.width
        page_height = page.rect.height

        # PyMuPdf renders with 1 pt = 1 px, thus a A4 page would be only
        # 596x840 pixel, which does not take much memory and wound be fine. On
        # the other hand, a A7 page would be rendered 210x298 pixel, which is
        # smaller then the default preview size. Thus scale in any case.
        if page_width > page_height:
            # landscape: width is the limiting factor
            scale = width / page_width
        else:
            # height is the limiting factor
            scale = height / page_height

        # Get a pixmap of the PDF page. Qt5 does not allow setting the
        # pixels/bytes directly, thus we need to use a QImage indirection
        pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale),
                              alpha=False, annots=False)
        # set the correct QImage format depending on alpha
        fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
        pimg = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
        return QPixmap.fromImage(pimg)
