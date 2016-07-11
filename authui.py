# restart_program method : credits : https://www.daniweb.com/programming/software-development/code/260268/restart-your-python-program

import sys
import auth
import os
import threading

from PyQt5.QtWidgets import (QWidget, QAction, qApp, QPushButton, QApplication,
	QMainWindow, QTextEdit, QMessageBox, QInputDialog, QLabel, QLineEdit,
	QGridLayout, QSpinBox, QSlider, QCheckBox)
from PyQt5.QtGui import QIcon, QFont, QPainter, QPen
from PyQt5.QtCore import Qt, QCoreApplication


class dummyUI(QWidget):
	def __init__(self):
		print("dummyUI initiated")
		super().__init__()
		self.move(200, 100)
		self.setWindowTitle("another window")
		self.show()

class ListUserUI(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		self.grid = QGridLayout()
		self.setLayout(self.grid)
		self.grid.setSpacing(10)
		self.grid.setVerticalSpacing(10)

		self.userdb = auth.Userbase()

		blankLabel = QLabel(self)
		blankLabel.setText("")

		self.anonLabel = QLabel(self); self.anonLabel.setText("Allow Anonymous Login")
		self.anonLabel.setToolTip("Any general user can login to anyone without password")

		self.anonCheck = QCheckBox("", self); self.anonCheck.toggle() # unchecked by default
		self.anonCheck.setObjectName("anonymous")
		self.anonCheck.setToolTip("Enable/Disable anonymous users")
		self.anonSettings = QPushButton('', self)
		self.anonSettings.setIcon(QIcon("icons/ic_create_black_24dp_1x.png"))
		self.anonSettings.setFlat(True)
		self.anonSettings.setToolTip("Modify anonymous user settings")

		self.usersHeading = QLabel(self); self.usersHeading.setText("Verified users : ")
		self.usersHeading.setStyleSheet("font-weight: bold")

		self.addUserButton = QPushButton('', self)
		self.addUserButton.setIcon(QIcon("icons/ic_add_circle_outline_black_24dp_2x.png"))
		self.addUserButton.setFlat(True)
		self.addUserButton.setToolTip("Add user")

		self.grid.addWidget(self.anonLabel, 0, 0, 1, 2)
		self.grid.addWidget(blankLabel, 0, 2)
		self.grid.addWidget(self.anonCheck, 0, 3)
		self.grid.addWidget(blankLabel, 0, 4)
		self.grid.addWidget(self.anonSettings, 0, 5)

		self.grid.addWidget(self.usersHeading, 2, 0, 2, 2)
		self.grid.addWidget(self.addUserButton, 2, 4, 2, 1)

		self.addUsers()

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
		qp.drawLine(10, 40, 240, 40)


	def addUsers(self):
		l = self.userdb.get_user_list()
		self.userRows = []
		self.gridRow = 4 # start entries from here
		for i in range(len(l)):
			if not l[i]=='anonymous':
				indexLabel = QLabel(self); indexLabel.setText(str(i+1))
				indexLabel.setStyleSheet('border: 1px')
				usernameLabel = QLabel(self); usernameLabel.setText(l[i])
				usereditBtn = QPushButton('', self)
				usereditBtn.setIcon(QIcon('icons/ic_create_black_24dp_1x.png'))
				usereditBtn.setFlat(True)
				usereditBtn.setObjectName(l[i])
				usereditBtn.setToolTip("Edit user settings")

				userremoveBtn = QPushButton('', self)
				userremoveBtn.setIcon(QIcon('icons/ic_remove_circle_outline_black_24dp_1x.png'))
				userremoveBtn.setFlat(True)
				userremoveBtn.setObjectName(l[i])
				userremoveBtn.setToolTip("Remove user")

				usereditBtn.clicked.connect(self.editUser)
				userremoveBtn.clicked.connect(self.removeUser)

				self.userRows.append([i, indexLabel, usernameLabel, usereditBtn, userremoveBtn])

				self.grid.addWidget(indexLabel, self.gridRow, 0)
				self.grid.addWidget(usernameLabel, self.gridRow, 1)
				self.grid.addWidget(usereditBtn, self.gridRow, 4)
				self.grid.addWidget(userremoveBtn, self.gridRow, 5)
				self.gridRow += 1




	def editUser(self):
		username = QApplication.sender(self).objectName()
		a = dummyUI()
		p = QApplication([])
		p.exec_()


	def removeUser(self):
		username = QApplication.sender(self).objectName()
		self.userdb.remove_user(username)
		restart_program()
		# snd = QApplication.sender(self)
		# row = 0
		# # get the row
		# for r in (self.userRows):
		# 	if snd in r:
		# 		row = r

		# manage addition and removal using userrow variable
		# remove all widgets and repopulate all rows in userrows

		# remove the widgets from the row
		# for wid in row[1:]:
		# 	self.grid.removeWidget(wid)
			# wid.hide()
		# removing widgets from the grid
		# for i in range(self.userRows)

		# removing all widgets
		# for r in self.userRows:
		# 	for wid in r[1:]:
		# 		self.grid.removeWidget(wid)
		# self.addUsers()


class mythread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		app = QApplication([])
		ex = ListUserUI()
		app.exec_()

def restart_program():
	python = sys.executable
	os.execl(python, python, *sys.argv)



if __name__ == "__main__":
	th = mythread()
	th.start()
	# app = QApplication([])
	# ex = ListUserUI()
	# sys.exit(app.exec_())
