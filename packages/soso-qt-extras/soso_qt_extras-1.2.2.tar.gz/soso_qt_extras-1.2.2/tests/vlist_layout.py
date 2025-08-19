#  qt_extras/tests/vlist_layout.py
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
import logging
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QShortcut, QHBoxLayout, QVBoxLayout, \
							QMainWindow, QWidget, QLabel, QPushButton, QSpinBox, QFrame
from qt_extras.list_layout import VListLayout


class MainWindow(QMainWindow):

	def __init__(self):
		super().__init__()
		self.quit_shortcut = QShortcut(QKeySequence('Ctrl+Q'), self)
		self.quit_shortcut.activated.connect(self.close)

		wid = QWidget(self)
		self.setCentralWidget(wid)
		main_layout = QVBoxLayout()
		wid.setLayout(main_layout)

		button = QPushButton('Add widget', self)
		button.clicked.connect(self.slot_add_widget)
		main_layout.addWidget(button)

		lo = QHBoxLayout()
		lo.setSpacing(6)

		lo.addWidget(QLabel('Index to add/remove:', self))

		self.spinbox = QSpinBox(self)
		self.spinbox.setMinimum(-1)
		self.spinbox.setMaximum(-1)
		lo.addWidget(self.spinbox)

		main_layout.addItem(lo)

		button = QPushButton('Insert widget', self)
		button.clicked.connect(self.slot_insert_widget)
		lo.addWidget(button)

		button = QPushButton('Remove widget', self)
		button.clicked.connect(self.slot_remove_widget)
		lo.addWidget(button)

		lo = QHBoxLayout()
		lo.setSpacing(6)

		self.swap_button = QPushButton('Swap first and last', self)
		self.swap_button.clicked.connect(self.slot_swap_extents)
		self.swap_button.setEnabled(False)
		lo.addWidget(self.swap_button)

		button = QPushButton('Clear list', self)
		button.clicked.connect(self.slot_clear_list)
		lo.addWidget(button)

		main_layout.addItem(lo)

		frm = QFrame(self)
		self.list = VListLayout()
		self.list.sig_len_changed.connect(self.slot_len_changed)
		frm.setLayout(self.list)
		main_layout.addWidget(frm)

	def make_thing(self):
		thing = Thing(self)
		thing.sig_move_up.connect(self.slot_move_widget_up)
		thing.sig_move_down.connect(self.slot_move_widget_down)
		return thing

	@pyqtSlot()
	def slot_len_changed(self):
		self.swap_button.setEnabled(len(self.list) > 1)
		self.spinbox.setMaximum(len(self.list) - 1)

	@pyqtSlot()
	def slot_add_widget(self):
		self.list.append(self.make_thing())

	@pyqtSlot()
	def slot_insert_widget(self):
		if self.spinbox.value() > -1:
			self.list.insert(self.spinbox.value(), self.make_thing())

	@pyqtSlot()
	def slot_remove_widget(self):
		if self.spinbox.value() > -1:
			self.list.remove(self.list[self.spinbox.value()])

	@pyqtSlot()
	def slot_swap_extents(self):
		self.list.swap(self.list[0], self.list[-1])

	@pyqtSlot(QWidget)
	def slot_move_widget_up(self, thing):
		try:
			self.list.move_up(thing)
		except Exception as e:
			logging.error(e)

	@pyqtSlot(QWidget)
	def slot_move_widget_down(self, thing):
		try:
			self.list.move_down(thing)
		except Exception as e:
			logging.error(e)

	@pyqtSlot()
	def slot_clear_list(self):
		self.list.clear()
		self.spinbox.setMaximum(-1)


class Thing(QWidget):

	sig_move_up = pyqtSignal(QWidget)
	sig_move_down = pyqtSignal(QWidget)
	minimum_width = 120
	ord = 1

	def __init__(self, parent):
		super().__init__(parent)
		self.setMinimumWidth(self.minimum_width)
		self.setLayout(QHBoxLayout())
		self.label = QLabel('Thing %d' % Thing.ord, self)
		self.layout().addWidget(self.label)
		self.up_button = QPushButton('Move up', self)
		self.up_button.clicked.connect(self.slot_trigger_up)
		self.layout().addWidget(self.up_button)
		self.down_button = QPushButton('Move down', self)
		self.down_button.clicked.connect(self.slot_trigger_down)
		self.layout().addWidget(self.down_button)
		Thing.ord += 1

	@pyqtSlot()
	def slot_trigger_up(self):
		self.sig_move_up.emit(self)

	@pyqtSlot()
	def slot_trigger_down(self):
		self.sig_move_down.emit(self)

	def __str__(self):
		return self.label.text()

if __name__ == "__main__":
	logging.basicConfig(
		level = logging.DEBUG,
		format = "[%(filename)24s:%(lineno)-4d] %(message)s"
	)
	app = QApplication([])
	window = MainWindow()
	window.show()
	app.exec()

#  end qt_extras/tests/vlist_layout.py
