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
		self.userdb = auth.Userbase()

		blankLabel = QLabel(self)
		blankLabel.setText("")

		self.anonLabel = QLabel(self); self.anonLabel.setText("Allow Pubilc Share")
		self.anonLabel.setToolTip("Any general user can login to anyone without password")

		self.anonCheck = QCheckBox("", self);
		
		self.anonCheck.setObjectName("anonymous")
		self.anonCheck.setToolTip("Enable/Disable anonymous users")
		if 'anonymous' in self.userdb.get_user_list():
			self.anonCheck.toggle()
		self.anonCheck.stateChanged.connect(self.anon_state_changed)
		self.anonSettings = QPushButton('', self)
		self.anonSettings.setIcon(QIcon("icons/ic_create_black_24dp_1x.png"))
		self.anonSettings.setFlat(True)
		self.anonSettings.setToolTip("Modify anonymous user settings")
		self.anonSettings.setObjectName("anonymous")
		self.anonSettings.clicked.connect(self.modify_user)

		self.anonHelp = QPushButton('', self)
		self.anonHelp.setIcon(QIcon("icons/ic_help_outline_black_24dp_2x.png"))
		self.anonHelp.setFlat(True)
		self.anonHelp.setToolTip("Know what anonymous user means")
		self.anonHelp.clicked.connect(self.display_help_anon)

		self.usersHeading = QLabel(self); self.usersHeading.setText("Verified users : ")
		self.usersHeading.setStyleSheet("font-weight: bold")

		self.addUserButton = QPushButton('', self)
		self.addUserButton.setIcon(QIcon("icons/ic_add_circle_outline_black_24dp_2x.png"))
		self.addUserButton.setFlat(True)
		self.addUserButton.setToolTip("Add user")
		self.addUserButton.clicked.connect(self.add_user)

		self.userHelp = QPushButton('', self)
		self.userHelp.setIcon(QIcon("icons/ic_help_outline_black_24dp_2x.png"))
		self.userHelp.setFlat(True)
		self.userHelp.setToolTip("Know what users are")
		self.userHelp.clicked.connect(self.display_help_user)

		self.anonLayout = QHBoxLayout()
		self.userHeadingLayout = QHBoxLayout()
		self.grid = QGridLayout()
		self.topFrame = QFrame()
		self.usersFrame = QFrame()

		self.anonLayout.addWidget(self.anonLabel)
		self.anonLayout.addWidget(self.anonCheck)
		self.anonLayout.addWidget(self.anonSettings)
		self.anonLayout.addWidget(self.anonHelp)

		self.userHeadingLayout.addWidget(self.usersHeading)
		self.userHeadingLayout.addWidget(self.addUserButton)
		self.userHeadingLayout.addWidget(self.userHelp)

		self.topFrame.setWindowTitle("Anonymous settings")
		self.topFrame.setLayout(self.anonLayout)
		self.topFrame.setFrameShape(QFrame.Box)
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

	def anon_state_changed(self, state):
		if state == Qt.Checked:
			self.modify_user()
		else:
			self.removeUser()

	def addUsers(self):
		l = self.userdb.get_user_list()

		self.userRows = []
		self.gridRow = 0 # start entries from here
		
		if 'anonymous' in l: l.remove('anonymous')
		for i in range(len(l)):
			indexLabel = QLabel(self); indexLabel.setText(str(i+1))
			indexLabel.setStyleSheet('border: 1px')
			usernameLabel = QLabel(self); usernameLabel.setText(l[i])
			usereditBtn = QPushButton('', self)
			usereditBtn.setIcon(QIcon('icons/ic_create_black_24dp_1x.png'))
			usereditBtn.setFlat(True)
			usereditBtn.setObjectName(l[i])
			usereditBtn.setToolTip("Edit user settings")

			userremoveBtn = QPushButton('', self)
			userremoveBtn.setIcon(QIcon('icons/ic_delete_sweep_black_24dp_2x.png'))
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
		if 'anonymous' in self.userdb.get_user_list():
			if not self.anonCheck.isChecked():
				self.anonCheck.toggle()
		else:
			if self.anonCheck.isChecked():
				self.anonCheck.toggle()

	def removeUser(self):
		username = self.sender().objectName()
		self.userdb.remove_user(username)
		self.rebuildUI()


	def display_help_anon(self):
		QMessageBox.information(self, "Help", "Public users access your share without any id or password.", QMessageBox.Ok, QMessageBox.Ok)

	def display_help_user(self):
		QMessageBox.information(self, "Help", "Users are the users you set up.\nThey can access your share only using the set of username and password you create.\nClick on plus sign to add users.", QMessageBox.Ok, QMessageBox.Ok)


class mythread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		app = QApplication([])
		app.setWindowIcon(QIcon('icons/ic_account_box_black_48dp_2x.png'))
		ex = ListUserUI()
		app.exec_()


if __name__ == "__main__":
	th = mythread()
	th.start()
