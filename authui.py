import sys

from PyQt5.QtWidgets import (QWidget, QAction, qApp, QPushButton, QApplication,
	QMainWindow, QTextEdit, QMessageBox, QInputDialog, QLabel, QLineEdit,
	QGridLayout, QSpinBox, QSlider, QCheckBox)
from PyQt5.QtGui import QIcon, QFont, QPainter, QPen
from PyQt5.QtCore import Qt, QCoreApplication


class ListUserUI(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		self.grid = QGridLayout()
		self.setLayout(self.grid)
		self.grid.setSpacing(10)

		blankLabel = QLabel(self)
		blankLabel.setText("")

		self.anonLabel = QLabel(self); self.anonLabel.setText("Allow Anonymous Login")
		self.anonLabel.setToolTip("Any general user can login to anyone without password")

		self.anonCheck = QCheckBox("", self); self.anonCheck.toggle() # unchecked by default
		self.anonSettings = QPushButton('', self)
		self.anonSettings.setIcon(QIcon("icons/ic_settings_black_48dp_1x.png"))
		self.anonSettings.setStyleSheet("border: none")

		self.grid.addWidget(self.anonLabel, 0, 0, 1, 2)
		self.grid.addWidget(blankLabel, 0, 2, 1, 3)
		self.grid.addWidget(self.anonCheck, 0, 5, 1, 1)
		self.grid.addWidget(blankLabel, 0, 6)
		self.grid.addWidget(self.anonSettings, 0, 7)


		# starting the main application
		self.move(200, 100)
		self.setWindowTitle("Users Settings")
		self.show()


	def paintEvent(self, e):
		qp = QPainter()
		qp.begin(self)
		self.drawLines(qp)
		qp.end()

	def drawLines(self, qp):
		pen = QPen(Qt.black, 2, Qt.SolidLine)
		# created a QPen object, black, 2px wide, black

		qp.setPen(pen)
		qp.drawLine(20, 40, 250, 40)


if __name__ == "__main__":
	app = QApplication([])
	ex = ListUserUI()
	sys.exit(app.exec_())
