#  qt_extras/qt_extras/list_layout.py
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
"Collection" layouts which act like lists.
"""
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLayout, QBoxLayout, QHBoxLayout, QVBoxLayout, QGridLayout, QWidget

HORIZONTAL_FLOW = 0
VERTICAL_FLOW = 1


class _ListLayout:
	"""
	Abstract class which is the base of the list layouts.
	"""

	sig_len_changed = pyqtSignal()

	def __iter__(self):
		return self.items.__iter__()

	def __reversed__(self):
		return self.items.__reversed__()

	def __contains__(self, item):
		return item in self.items

	def __len__(self):
		return len(self.items)

	def __bool__(self):
		return bool(self.items)

	def __getitem__(self, idx):
		return self.items[idx]

	def append(self, item):
		if self.end_space is None:
			self.addWidget(item)
		else:
			self.insertWidget(len(self.items), item)
		self.items.append(item)
		self.sig_len_changed.emit()

	def insert(self, index, item):
		if not (0 <= index <= len(self.items)):
			raise IndexError()
		if index == len(self.items):
			self.append(item)
		else:
			self.items.insert(index, item)
			self.insertWidget(index, item)
		self.sig_len_changed.emit()

	def remove(self, item):
		if item not in self.items:
			raise ValueError("Item not in list layout")
		index = self.items.index(item)
		del self.items[index]
		item.deleteLater()
		self.sig_len_changed.emit()

	def swap(self, item_a, item_b):
		if not item_a in self.items or not item_b in self.items:
			raise ValueError("Item not in list layout")
		index_a = self.items.index(item_a)
		index_b = self.items.index(item_b)
		if index_a < index_b:
			self.replaceWidget(item_a, item_b)
			self.insertWidget(index_b, item_a)
		else:
			self.replaceWidget(item_b, item_a)
			self.insertWidget(index_a, item_b)
		self.items[index_a] = item_b
		self.items[index_b] = item_a

	def move_up(self, item):
		if item not in self.items:
			raise ValueError("Item not in list layout")
		index = self.items.index(item)
		if index == 0:
			raise ValueError("Item is first in layout")
		self.swap(item, self.items[index - 1])

	def move_down(self, item):
		if item not in self.items:
			raise ValueError("Item not in list layout")
		index = self.items.index(item)
		if index == len(self.items) - 1:
			raise ValueError("Item is last in layout")
		self.swap(item, self.items[index + 1])

	def clear(self):
		for iter_index in reversed(range(len(self.items))):
			item = self.takeAt(iter_index)
			item.widget().deleteLater()
		self.items = []
		self.sig_len_changed.emit()

	def count(self):
		return len(self.items)

	def index(self, item):
		return self.items.index(item)


class _ListBoxLayout(_ListLayout):

	def __init__(self, parent = None, /, end_space = None):
		"""
		"end_space" is optional spacing with the given stretch factor
		to append to the end of the list.
		"""
		super().__init__(parent)
		self.setSizeConstraint(QLayout.SetMinimumSize)
		self.items = []
		self.end_space = end_space
		if self.end_space is not None:
			self.addStretch(self.end_space)



class HListLayout(QHBoxLayout, _ListBoxLayout):

	pass


class VListLayout(QVBoxLayout, _ListBoxLayout):

	pass



class GListLayout(_ListLayout, QGridLayout):
	"""
	Extends QGridLayout.
	By default, adds items left-to-right, top-to-bottom.
	Change this using one of the direction constants.
	"""

	def __init__(self, columns_or_rows, flow = HORIZONTAL_FLOW):
		"""
		The meaning of columns_or_rows depends on "flow".
		If the flow is horizontal, items are added left to right, then top to bottom.
		If the flow is vertical, items are added top to bottom, then left to right.
		"""
		super().__init__()
		self.items = []
		self.columns_or_rows = columns_or_rows
		self.flow = flow

	def append(self, item):
		tup = self._place_widget(item, len(self.items))
		self.items.append(item)
		self.sig_len_changed.emit()
		return tup

	def insert(self, index, item):
		if not (0 <= index <= len(self.items)):
			raise IndexError()
		if index == len(self.items):
			tup = self.append(item)
		else:
			self._take_all_from(index)
			tup = self._place_widget(item, index)
			self.items.insert(index, item)
			self._add_all_from(index + 1)
		self.sig_len_changed.emit()
		return tup

	def remove(self, item):
		if item not in self.items:
			raise ValueError('Item not in list layout')
		index = self.items.index(item)
		self._take_all_from(index)
		del self.items[index]
		item.deleteLater()
		self._add_all_from(index)
		self.sig_len_changed.emit()

	def set_columns(self, columns):
		if columns != self.columns_or_rows or self.flow != HORIZONTAL_FLOW:
			self._take_all_from(0)
			self.columns_or_rows = columns
			self.flow = HORIZONTAL_FLOW
			self._add_all_from(0)
			self.sig_len_changed.emit()

	def set_rows(self, rows):
		if rows != self.columns_or_rows or self.flow != VERTICAL_FLOW:
			self._take_all_from(0)
			self.columns_or_rows = rows
			self.flow = VERTICAL_FLOW
			self._add_all_from(0)
			self.sig_len_changed.emit()

	def _place_widget(self, item, index):
		"""
		Puts the given widget in the correct cell for the given index
		"""
		if self.flow == HORIZONTAL_FLOW:
			row = index // self.columns_or_rows
			column = index - row * self.columns_or_rows
		else:
			column = index // self.columns_or_rows
			row = index - column * self.columns_or_rows
		self.addWidget(item, row, column)
		return row, column

	def _add_all_from(self, index):
		"""
		Puts items in the list back into the layout after insert / other.
		"""
		for iter_index in range(index, len(self.items)):
			self._place_widget(self.items[iter_index], iter_index)

	def _take_all_from(self, index):
		"""
		Takes items from the layout but leaves them in the list.
		"""
		for iter_index in reversed(range(index, len(self.items))):
			self.takeAt(iter_index)


#  end qt_extras/qt_extras/list_layout.py
