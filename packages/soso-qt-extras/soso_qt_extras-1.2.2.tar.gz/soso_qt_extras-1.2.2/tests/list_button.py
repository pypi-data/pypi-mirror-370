#  qt_extras/tests/menu_button.py
#
#  Copyright 2024 liyang <liyang@veronica>
#
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QVariant
from PyQt5.QtWidgets import QMainWindow, QPushButton
from qt_extras.list_button import QtListButton


class MainWindow(QMainWindow):

	def __init__(self):
		super().__init__()
		self.quit_shortcut = QShortcut(QKeySequence('Ctrl+Q'), self)
		self.quit_shortcut.activated.connect(self.close)

		wid = QWidget(self)
		self.setCentralWidget(wid)
		lo = QVBoxLayout()
		wid.setLayout(lo)

		self.menu_button = QtListButton(self)
		font = self.menu_button.font()
		self.menu_button.setPointSize(10)
		self.label_1 = QLabel('THIS IS LABEL 1', self)
		self.label_2 = QLabel('THIS IS LABEL 2', self)

		self.menu_button.setText('Click for menu')
		self.menu_button.addItem("item 1", self.label_1)
		self.menu_button.addItem("item 2", self.label_2)
		self.menu_button.sig_item_selected.connect(self.item_selected)

		select_data_value_button = QPushButton('Test select_data (Choose <label_1>)', self)
		select_data_value_button.clicked.connect(self.select_data_value_button_click)

		set_text_button = QPushButton('Test select_text (Choose "item 2")', self)
		set_text_button.clicked.connect(self.set_text_button_click)

		lo.addWidget(self.label_1)
		lo.addWidget(self.label_2)
		lo.addWidget(self.menu_button)
		lo.addWidget(select_data_value_button)
		lo.addWidget(set_text_button)

	@pyqtSlot(str, QVariant)
	def item_selected(self, text, data):
		# "data" is one of the labels
		data.setText('SELECTED')

	@pyqtSlot()
	def select_data_value_button_click(self):
		self.menu_button.select_data(self.label_1)

	@pyqtSlot()
	def set_text_button_click(self):
		self.menu_button.select_text('item 2')

if __name__ == "__main__":
	from PyQt5.QtGui import QKeySequence
	from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QShortcut, QVBoxLayout
	app = QApplication([])
	window = MainWindow()
	window.show()
	app.exec()

#  end qt_extras/tests/menu_button.py
