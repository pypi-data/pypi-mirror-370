#  qt_extras/menu_button.py
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
Pushbutton with an integrated drop-down menu.

For convenience, the "Action" -related attributes of the pushbutton are
delegated to the integrated menu. These include:

	actions
	addAction
	addActions
	insertAction
	insertActions
	removeAction
	addSeparator
	clear


Typical use (in a dialog created by QtDesigner):

	menu_button = QtMenuButton(self)
	self.layout().replaceWidget(self.b_menu, menu_button)
	self.b_menu.deleteLater()
	self.b_menu = menu_button

	action = QAction('Do the first thing', self.b_menu)
	action.triggered.connect(self.slot_first_thing)
	self.b_menu.addAction(action)

	action = QAction('Do the second thing', self.b_menu)
	action.triggered.connect(self.slot_second_thing)
	self.b_menu.addAction(action)

"""
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QPoint, QVariant
from PyQt5.QtWidgets import QMenu, QPushButton


class QtMenuButton(QPushButton):

	def __init__(self, parent, fill_callback = None, constrain_width = False):
		"""
		fill_callback is called when the menu button is clicked, to allow you to fill
		the menu before it is shown.

		If constrain_width is set, the width of the menu will be constrained to the
		width of the pushbutton which triggers it.
		"""
		super().__init__(parent)
		self.fill_callback = fill_callback
		self.constrain_width = constrain_width
		self.menu = QMenu(self)
		self.setObjectName('qt_menu_button')
		self.menu.setObjectName('qt_menu_button_menu')

		self.actions = self.menu.actions
		self.addAction = self.menu.addAction
		self.addActions = self.menu.addActions
		self.insertAction = self.menu.insertAction
		self.insertActions = self.menu.insertActions
		self.removeAction = self.menu.removeAction
		self.addSeparator = self.menu.addSeparator
		self.clear = self.menu.clear

		self.clicked.connect(self.click_event)

	@pyqtSlot()
	def click_event(self):
		if self.fill_callback is not None:
			self.fill_callback()
		point = self.mapToGlobal(QPoint(0, self.height()))
		if self.constrain_width:
			self.menu.setFixedWidth(self.width())
		else:
			self.menu.setMinimumWidth(self.width())
		self.menu.exec(point)

	def setFont(self, font):
		super().setFont(font)
		self.menu.setFont(self.font())

	def setPointSize(self, size):
		font = self.font()
		font.setPointSize(size)
		self.setFont(font)


#  end qt_extras/menu_button.py
