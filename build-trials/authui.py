# restart_program method : credits : https://www.daniweb.com/programming/software-development/code/260268/restart-your-python-program

import sys
import auth
import os
import subprocess
import threading

from datetime import datetime

from PyQt5.QtWidgets import (QWidget, QAction, qApp, QPushButton, QApplication,
	QMainWindow, QTextEdit, QMessageBox, QInputDialog, QLabel, QLineEdit, QHBoxLayout,
	QGridLayout, QSpinBox, QSlider, QCheckBox, QVBoxLayout, QSplitter, QFrame)
from PyQt5.QtGui import QIcon, QFont, QPainter, QPen
from PyQt5.QtCore import Qt, QCoreApplication


def mylog(ar):
	f = open('log.txt', 'a')
	f.write(str(datetime.now()) + " " + ar + "\n")
	f.close()

class ListUserUI(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		# self.grid = QGridLayout()
		# self.setLayout(self.grid)
		# self.grid.setSpacing(10)
		# self.grid.setVerticalSpacing(10)

		self.userdb = auth.Userbase()

		blankLabel = QLabel(self)
		blankLabel.setText("")

		self.anonLabel = QLabel(self); self.anonLabel.setText("Allow Anonymous Login")
		self.anonLabel.setToolTip("Any general user can login to anyone without password")

		self.anonCheck = QCheckBox("", self);
		
		self.anonCheck.setObjectName("anonymous")
		self.anonCheck.setToolTip("Enable/Disable anonymous users")
		if 'anonymous' in self.userdb.get_user_list():
			self.anonCheck.toggle()
		self.anonCheck.stateChanged.connect(self.removeUser)
		self.anonSettings = QPushButton('', self)
		self.anonSettings.setIcon(QIcon("icons/ic_create_black_24dp_1x.png"))
		self.anonSettings.setFlat(True)
		self.anonSettings.setToolTip("Modify anonymous user settings")
		self.anonSettings.setObjectName("anonymous")
		self.anonSettings.clicked.connect(self.modify_user)

		self.usersHeading = QLabel(self); self.usersHeading.setText("Verified users : ")
		self.usersHeading.setStyleSheet("font-weight: bold")

		self.addUserButton = QPushButton('', self)
		self.addUserButton.setIcon(QIcon("icons/ic_add_circle_outline_black_24dp_2x.png"))
		self.addUserButton.setFlat(True)
		self.addUserButton.setToolTip("Add user")
		self.addUserButton.clicked.connect(self.add_user)

		# self.grid.addWidget(self.anonLabel, 0, 0, 1, 2)
		# self.grid.addWidget(blankLabel, 0, 2)
		# self.grid.addWidget(self.anonCheck, 0, 3)
		# self.grid.addWidget(blankLabel, 0, 4)
		# self.grid.addWidget(self.anonSettings, 0, 5)

		# self.grid.addWidget(self.usersHeading, 2, 0, 2, 2)
		# self.grid.addWidget(self.addUserButton, 2, 4, 2, 1)

		self.anonLayout = QHBoxLayout()
		self.userHeadingLayout = QHBoxLayout()
		self.grid = QGridLayout()
		self.topFrame = QFrame()
		self.usersFrame = QFrame()

		# self.anonLayout.setStyleSheet("border-bottom: 1px solid black")
		self.anonLayout.addWidget(self.anonLabel)
		self.anonLayout.addWidget(self.anonCheck)
		self.anonLayout.addWidget(self.anonSettings)

		self.userHeadingLayout.addWidget(self.usersHeading)
		self.userHeadingLayout.addWidget(self.addUserButton)

		self.topFrame.setWindowTitle("Anonymous settings")
		self.topFrame.setLayout(self.anonLayout)
		# self.topFrame.setStyleSheet("border-bottom: 1px solid")
		self.topFrame.setFrameShape(QFrame.StyledPanel)
		self.topFrame.setFrameShadow(QFrame.Plain)
		self.usersFrame.setWindowTitle("Verified users ")
		self.usersFrame.setLayout(self.userHeadingLayout)
		self.usersFrame.setFrameShape(QFrame.StyledPanel)
		self.usersFrame.setFrameShadow(QFrame.Plain)

		self.mainLayout = QVBoxLayout()

		self.mainLayout.addWidget(self.topFrame)
		self.mainLayout.addWidget(self.usersFrame)
		self.mainLayout.addLayout(self.grid)
		self.mainLayout.setSpacing(10)

		self.setLayout(self.mainLayout)

		self.addUsers()

		# starting the main application
		self.move(200, 100)
		self.setWindowTitle("Users Settings")
		self.show()


	def rebuildUI(self):
		while self.grid.count():
			item = self.grid.takeAt(0)
			widget = item.widget()
			if widget == self.anonLabel or \
				widget == self.anonCheck or \
				widget == self.anonSettings or \
				widget == self.addUserButton or \
				widget == self.usersHeading:
				continue
			widget.deleteLater()
		self.addUsers()

	def closeEvent(self, e):
		QMessageBox.information(self, "Message", "Restart sharing for changes to be effective.", QMessageBox.Ok, QMessageBox.Ok)

	# def paintEvent(self, e):
	# 	qp = QPainter()
	# 	qp.begin(self)
	# 	self.drawLines(qp)
	# 	qp.end()

	# def drawLines(self, qp):
	# 	pen = QPen(Qt.black, 2, Qt.SolidLine)
	# 	# created a QPen object, black, 2px wide, black

	# 	qp.setPen(pen)
	# 	qp.drawLine(10, 40, 280, 40)


	def anon_state_changed(self, state):
		if not state == Qt.Checked:
			print('removing anonymous')
			self.modify_user()
		else:
			print('adding anonymous')
			self.add_user()

	def addUsers(self):
		l = self.userdb.get_user_list()

		self.userRows = []
		self.gridRow = 0 # start entries from here
		
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

				usereditBtn.clicked.connect(self.modify_user)
				userremoveBtn.clicked.connect(self.removeUser)

				self.userRows.append([i, indexLabel, usernameLabel, usereditBtn, userremoveBtn])

				self.grid.addWidget(indexLabel, self.gridRow, 0)
				self.grid.addWidget(usernameLabel, self.gridRow, 1)
				self.grid.addWidget(usereditBtn, self.gridRow, 4)
				self.grid.addWidget(userremoveBtn, self.gridRow, 5)
				self.gridRow += 1


	def add_user(self):
		subprocess.call([sys.executable, 'get_user_data.py'])
		self.rebuildUI()

	def modify_user(self):
		username = self.sender().objectName()
		subprocess.call([sys.executable, 'get_user_data.py', username])

	def removeUser(self):
		username = self.sender().objectName()
		self.userdb.remove_user(username)
		self.rebuildUI()


class mythread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		app = QApplication([])
		ex = ListUserUI()
		app.exec_()

# def restart_program():
	# python = sys.executable
	# thisProg = os.path.realpath(__file__)
	# os.execl(python, thisProg, *sys.argv)



if __name__ == "__main__":
	th = mythread()
	th.start()
