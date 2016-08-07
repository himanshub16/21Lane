 #!/usr/bin/python3
# Program to create a skeleton calculator using QGridLayout

import sys
from PyQt5.QtWidgets import (QWidget, QGridLayout, QPushButton,
		QApplication, QMainWindow)
from PyQt5.QtCore import Qt

class Example(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		self.grid = QGridLayout()
		self.setLayout(self.grid)

		
		self.btn1 = QPushButton('btn1')
		self.btn2 = QPushButton('btn2')
		self.btn3 = QPushButton('btn3')

		btn = QPushButton('Bar')
		self.grid.addWidget(self.btn1, 1, 1)
		self.grid.addWidget(self.btn2, 2,2)
		self.grid.addWidget(self.btn3, 3, 3)
		self.grid.addWidget(btn, 5, 1, 4, 3)
		self.move(300, 150)
		self.setWindowTitle('Calculator')
		self.show()

if __name__=="__main__":
	app =  QApplication(sys.argv)
	ex = Example()
	sys.exit(app.exec_())
