#  qt_extras/tests/autofit.py
#
#  Copyright 2024 liyang <liyang@veronica>
#
import qt_extras.autofit
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QShortcut, QPushButton, QLineEdit, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QKeySequence


class MainWindow(QMainWindow):

	def __init__(self):
		super().__init__()

		pb = QPushButton(self)
		pb.autoFit()
		pb.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

		ed = QLineEdit()

		layout = QVBoxLayout()
		layout.addWidget(pb)
		layout.addWidget(ed)

		w = QWidget()
		w.setLayout(layout)
		self.setCentralWidget(w)

		ed.textChanged.connect(pb.setText)

		self.quit_shortcut = QShortcut(QKeySequence('Ctrl+Q'), self)
		self.quit_shortcut.activated.connect(self.close)


if __name__ == "__main__":
	app = QApplication([])
	window = MainWindow()
	window.show()
	app.exec()


#  end qt_extras/tests/autofit.py
