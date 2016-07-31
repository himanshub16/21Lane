#!/usr/bin/python3 
# this script either creates a new user, or modifies current user
# for modifying, the username is sent as command-line argument
# else, there is not command line argument.

from PyQt5.QtWidgets import (QWidget, QAction, qApp, QPushButton, QApplication,
	QMainWindow, QTextEdit, QMessageBox, QInputDialog, QLabel, QLineEdit, QCheckBox,
	QGridLayout, QSpinBox, QSlider, QFileDialog)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QCoreApplication

import sys, os
import auth

from datetime import datetime


def mylog(ar):
	f = open('log.txt', 'a')
	f.write(str(datetime.now()) + " " + ar + "\n")
	f.close()


class userconfigUI(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		grid = QGridLayout()
		self.setLayout(grid)
		grid.setSpacing(10)

		self.isanonuser = False
		if len(sys.argv) > 1:
			if sys.argv[1] == 'anonymous':
				self.isanonuser = True

		self.usernameLabel = QLabel(self); self.usernameLabel.setText("Username *")
		self.permissionsLabel = QLabel(self); self.permissionsLabel.setText("Permissions *")
		self.loginmsgLabel = QLabel(self); self.loginmsgLabel.setText("Login message")
		self.logoutmsgLabel = QLabel(self); self.logoutmsgLabel.setText("Logout message")


		self.usernameInput = QLineEdit(self); self.usernameInput.setMaxLength(16)
		self.usernameInput.setToolTip("Don't user spaces or special characters")
		self.usernameInput.setPlaceholderText("No spaces or special characters")
		self.usernameInput.textEdited.connect(self.nameChanged)
		if not self.isanonuser:
			self.passwordLabel = QLabel(self); self.passwordLabel.setText("Password *")
			self.passwordInput = QLineEdit(self); self.passwordInput.setEchoMode(QLineEdit.PasswordEchoOnEdit)

		self.homedirSelect = QPushButton('Home directory', self)
		self.homedirInput = QLineEdit(self);
		self.homedirSelect.setToolTip("Click this button to choose directory \nor type the compelete path \nin the adjoining input")
		self.homedirSelect.clicked.connect(self.showDirChooser)

		self.permissions = ""

		self.readPerm = QCheckBox("Download", self); self.readPerm.setToolTip("Read and download files from the folder selected")
		self.writePerm = QCheckBox("Upload", self); self.writePerm.setToolTip("Upload files inside the directory selected")
		self.modifyPerm = QCheckBox("Modfiy", self); self.modifyPerm.setToolTip("Rename files / \nCreate folders / \nAppend to file")
		self.readPerm.stateChanged.connect(self.handle_perm)
		self.writePerm.stateChanged.connect(self.handle_perm)
		self.modifyPerm.stateChanged.connect(self.handle_perm)

		self.loginmsgInput = QLineEdit(self);
		self.logoutmsgInput = QLineEdit(self);

		self.saveBtn = QPushButton("Save", self)
		self.cancelBtn = QPushButton("Cancel", self)

		self.cancelBtn.clicked.connect(qApp.quit)
		self.saveBtn.clicked.connect(self.saveData)

		if not self.isanonuser:
			grid.addWidget(self.passwordLabel, 1, 0, 1, 2)
			grid.addWidget(self.passwordInput, 1, 2, 1, 2)
		else:
			self.usernameInput.setText("anonymous")

		grid.addWidget(self.usernameLabel, 0, 0, 1, 2)
		grid.addWidget(self.usernameInput, 0, 2, 1, 2)
		# grid.addWidget(self.homedirLabel, 2, 0, 1, 2)
		grid.addWidget(self.homedirSelect, 2, 0, 1, 1)
		grid.addWidget(self.homedirInput, 2, 1, 1, 4)
		grid.addWidget(self.permissionsLabel, 3, 0, 1, 2)
		grid.addWidget(self.readPerm, 3, 2)
		grid.addWidget(self.writePerm, 3, 3)
		grid.addWidget(self.modifyPerm, 3, 4)
		grid.addWidget(self.loginmsgLabel, 4, 0, 1, 2)
		grid.addWidget(self.loginmsgInput, 4, 2, 1, 3)
		grid.addWidget(self.logoutmsgLabel, 5, 0, 1, 2)
		grid.addWidget(self.logoutmsgInput, 5, 2, 1, 3)
		grid.addWidget(self.saveBtn, 6, 3)
		grid.addWidget(self.cancelBtn, 6, 4)


		if len(sys.argv) > 1:
			self.populateForm(sys.argv[1])

		self.set_perms()

		# starting the main application
		self.move(200, 100)
		self.setWindowTitle("User Configuration")
		self.show()

	def set_perms(self):
		"""This function sets permissions"""
		if self.usernameInput.text():
			if "elr" in self.permissions:
				if not self.readPerm.isChecked():
					self.readPerm.toggle()
			else:
				if self.readPerm.isChecked():
					self.readPerm.toggle()

			if "w" in self.permissions:
				if not self.writePerm.isChecked():
					self.writePerm.toggle()
			else:
				if self.writePerm.isChecked():
					self.writePerm.toggle()

			if "adfm" in self.permissions:
				if not self.modifyPerm.isChecked():
					self.modifyPerm.toggle()
			else:
				if self.modifyPerm.isChecked():
					self.modifyPerm.toggle()


	def handle_perm(self, state):
		if self.sender() == self.readPerm:
			if state == Qt.Checked:
				if not "elr" in self.permissions:
					self.permissions += "elr"
			else:
				self.permissions = self.permissions.replace('elr', '')

		elif self.sender() == self.writePerm:
			if state == Qt.Checked:
				if not "w" in self.permissions:
					self.permissions += "w"
			else:
				self.permissions = self.permissions.replace('w', '')

		elif self.sender() == self.modifyPerm:
			if state == Qt.Checked:
				if not "adfm" in self.permissions:
					self.permissions += "adfm"
			else:
				self.permissions = self.permissions.replace('adfm', '')


	def showDirChooser(self):
		dirname = QFileDialog.getExistingDirectory(self, "Select Directory")
		if dirname:
			self.homedirInput.setText(dirname)

	def closeEvent(self, event):
		# QMessageBox.question(self, message_label, text_in_dialog, combination_of_buttons_appearing_in_dialog, default_button)
		# closing the widget generates QCloseEvent
		# to modify the widget behavior, we need to reimplement closeEvent() event handler
		reply = QMessageBox.question(self, 'Message', "Are you sure to exit ?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

		if reply == QMessageBox.Yes:
			event.accept()
		else:
			event.ignore()

# todo.. get separations for anonymous and only if user is demanded
# QCheckBox.isChecked() gives check value

	def populateForm(self, usr):
		usrobj = auth.Userbase().get_user_info(usr)
		if usrobj is None:
			return
		if not self.isanonuser:
			self.passwordInput.setText(usrobj.password)
		else:
			self.usernameInput.setReadOnly(True)
			self.usernameInput.setHidden(True)
			self.usernameLabel.setHidden(True)
		self.usernameInput.setText(usrobj.name)
		self.homedirInput.setText(usrobj.homedir)
		self.loginmsgInput.setText(usrobj.msg_login)
		self.logoutmsgInput.setText(usrobj.msg_quit)
		self.permissions = usrobj.permission


	def nameChanged(self):
		if self.usernameInput.text() == "anonymous" and not self.isanonuser:
			QMessageBox.critical(self, "Error", "Please choose a name other than 'anonymous'", QMessageBox.Ok, QMessageBox.Ok)

	def saveData(self):
		# code a form validator before saving
		if len(self.usernameInput.text()) == 0 \
			or len(self.homedirInput.text()) == 0:
			QMessageBox.critical(self, 'Message', "Incomplete details!", QMessageBox.Ok, QMessageBox.Ok)
			return

		if len(self.usernameInput.text().split()) > 1:
			QMessageBox.critical(self, 'Error', "Don't use spaces or special characters.", QMessageBox.Ok, QMessageBox.Ok)

		dic = { 'name':self.usernameInput.text(), 'homedir':self.homedirInput.text(), \
					'permission':self.permissions, 'msg_login':self.loginmsgInput.text(), 'msg_quit':self.logoutmsgInput.text() }
		if dic['name'] == 'anonymous':
			if not self.isanonuser:
				QMessageBox.critical(self, "Error", "Please choose a name other than 'anonymous'", QMessageBox.Ok, QMessageBox.Ok)
				return
			dic.pop('name')
			userobj = auth.AnonymousUser(dic)
			userobj.save_details()
		else:
			dic['password'] = self.passwordInput.text()
			userobj = auth.User(dic)
			userobj.save_details()
		QMessageBox.information(self, 'Message', "Settings Saved.", QMessageBox.Ok, QMessageBox.Ok)
		qApp.quit()


if __name__=="__main__":
	app = QApplication([])
	app.setWindowIcon(QIcon("icons/ic_create_black_24dp_2x.png"))
	ui = userconfigUI()
	sys.exit(app.exec_())
