#  qt_extras/qt_extras/autofit.py
#
#  Copyright 2025 Leon Dionne <ldionne@dridesign.sh.cn>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
"""
Override's widget's setText() function.
Stores original text as "_unabbreviated_text", abbreviates it,
and sets it. anytime afterwards when the widget is resized, it
updates the abbreviated text.

Apply this effect using:

	QWidget.autoFit(<padding>)

"""
from functools import partial
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QWidget, QMainWindow

__keepers = list("bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ0123456789")

def abbreviated_text(widget, text, padding=2, fixed_width=None):
	"""
	Standard routine for shortening text to fit buttons, labels, etc.
	Padding is applied to both left and right sides.
	"""
	if len(text) == 1:
		return text
	available_width = widget.size().width() - padding * 2 if fixed_width is None else fixed_width
	metrics = QFontMetrics(widget.font())
	if available_width >= metrics.boundingRect(text).width():
		return text
	rchars = list(text)
	rchars.reverse()			# rchars is reversed list of characters
	while len(rchars) > 1 and available_width < metrics.boundingRect(text).width():
		delindex = -1
		if len(rchars) > 2:
			for i in range(1, len(rchars) - 1):
				if not rchars[i] in __keepers:
					delindex = i
					break
		if delindex < 0:
			delindex = 1
		del rchars[delindex]
		tlist = rchars.copy()
		tlist.reverse()
		text = "".join(tlist)
	return text

def __set_abbreviated_text(widget, text):
	widget._unabbreviated_text = text
	super(type(widget), widget).setText(abbreviated_text(widget, text, widget._abbreviated_text_padding))

def __resize_abbreviated_text(widget, event):
	super(type(widget), widget).resizeEvent(event)
	super(type(widget), widget).setText(abbreviated_text(widget, widget._unabbreviated_text))

def __autofit_widget_text(widget, padding=2):
	if	not hasattr(widget, 'text') or \
		not hasattr(widget, 'setText') or \
		not hasattr(widget, 'size') or \
		not hasattr(widget, 'font'):
		raise Exception("Cannot autofit this widget's text")
	widget._unabbreviated_text = ""
	widget._abbreviated_text_padding = padding
	widget.setText = partial(__set_abbreviated_text, widget)
	widget.resizeEvent = partial(__resize_abbreviated_text, widget)

QWidget.autoFit = __autofit_widget_text



#  end qt_extras/qt_extras/autofit.py
