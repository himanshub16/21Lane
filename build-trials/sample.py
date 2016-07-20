#!/usr/bin/python3
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit, QPushButton, QLabel, QApplication


class Example(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		btn = QPushButton("Click", self)
		lbl = QLabel(self); lbl.setText("details")
		btn1 = QPushButton("Click", self)
		lbl1 = QLabel(self); lbl.setText("details")

		boxl = QHBoxLayout()
		gridl = QGridLayout()
		boxl.addWidget(btn)
		boxl.addWidget(lbl)
		gridl.addWidget(btn1, 0, 0)
		gridl.addWidget(lbl1, 0, 1)

		vboxl = QVBoxLayout()
		vboxl.addLayout(gridl)
		vboxl.addLayout(boxl)
		# btn.move(100, 100)
		# lbl.move(100, 50)
		self.setLayout(vboxl)

		self.setWindowTitle("Hello from India")
		self.setGeometry(100, 100, 200, 200)
		self.show()


if __name__=="__main__":
	app = QApplication([])
	ex = Example()
	app.exec_()