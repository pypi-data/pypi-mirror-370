#  qt_extras/qt_extras/__init__.py
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
Provides various extras for PyQt.
"""
import logging
from PyQt5.QtWidgets import QMessageBox

__version__ = "1.2.1"

class SigBlock:
	"""
	A context manager which blocks widgets from generating signals.
	Pass one or more objects which extend QObject to the constructor,
	and while in this context, their signals are blocked. For example:

		with SigBlock(button):
			button.setChecked(True)

	"""

	def __init__(self, *qtcontrols):
		self.qtcontrols = qtcontrols

	def __enter__(self):
		for control in self.qtcontrols:
			control.blockSignals(True)

	def __exit__(self, *_):
		for control in self.qtcontrols:
			control.blockSignals(False)


class ShutUpQT(object):
	"""
	A context manager for temporarily supressing DEBUG level messages.
	Primarily used when loading a Qt graphical user interface using uic.
	"""

	def __init__(self, level=logging.ERROR):
		self.level = level

	def __enter__(self):
		self.root = logging.getLogger()
		self.previous_log_level = self.root.getEffectiveLevel()
		self.root.setLevel(self.level)

	def __exit__(self, *_):
		self.root.setLevel(self.previous_log_level)	# Carry on ...


class WidgetDisabler:
	"""
	A context manager that disables every widget in a window.

		with WidgetDisabler(window):
			...do something

	"""

	def __init__(self, window):
		self.window = window

	def __enter__(self):
		for widget in self.window.findChildren(QWidget):
			if hasattr(widget, 'isEnabled') and hasattr(widget, 'setEnabled'):
				widget.qt_extra_previous_enabled_state = widget.isEnabled()
				widget.setEnabled(False)

	def __exit__(self, *_):
		for widget in self.window.findChildren(QWidget):
			if hasattr(widget, 'qt_extra_previous_enabled_state'):
				widget.setEnabled(widget.qt_extra_previous_enabled_state)


class DevilBox(QMessageBox):
	"""
	A MessageBox for when bad stuff happens.
	"""
	def __init__(self, message):
		super().__init__()
		self.setWindowTitle('Something bad happened')
		self.setIcon(QMessageBox.Critical)
		if isinstance(message, Exception):
			tb = message.__traceback__
			self.setText('%s: %s in %s %s, line %d' % (
				type(message).__name__,
				str(message),
				tb.tb_frame.f_code.co_filename,
				tb.tb_frame.f_code.co_name,
				tb.tb_lineno
			))
		else:
			self.setText(str(message))
		self.exec_();


#  end qt_extras/qt_extras/__init__.py
