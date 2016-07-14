#!/usr/bin/python3
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.handlers import ThrottledDTPHandler
from pyftpdlib.servers import FTPServer

# import additions
import sys
import os
import auth
import settings
import errno
import socket
import threading
import subprocess

from datetime import datetime

userbase = auth.Userbase()
python = sys.executable

def mylog(ar):
	f = open('log.txt', 'a')
	f.write(str(datetime.now()) + " " + ar + "\n")
	f.close()


def load_settings():
	return settings.FTPSettings()

def load_users():
	""" creates a new DummyAuthorizer object at every call
	"""
	authorizer = DummyAuthorizer()
	if len(userbase.userlist) == 0:
		# there are no users, so at least one anonymous user should be authorized
		authorizer.add_anonymous(os.getcwd())
		return authorizer

	for username in userbase.get_user_list():
		userobj = userbase.get_user_info(username)
		if username == 'anonymous':
			authorizer.add_anonymous(userobj.homedir, perm=userobj.permission, msg_login=userobj.msg_login, msg_quit=userobj.msg_quit)
		else:
			authorizer.add_user(userobj.name, userobj.password, userobj.homedir, perm=userobj.permission, msg_login=userobj.msg_login, msg_quit=userobj.msg_quit)
	return authorizer


def start_server():
	server.serve_forever()

def stop_server():
	server.close_all()


def is_port_available(port=2121):
	port = int(port)
	try:
		# connecting on localhost, previously it was 0.0.0.0, to satisfy Windows
		result = socket.create_connection(('localhost', port), 2)
	except OverflowError:
		print ("Socket out of range")
	except (ConnectionError, ConnectionRefusedError):
		# Connection refused error to handle windows systems:(
		return True

	return result==0

port = 2121
server = None


class myserver(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		global server, port
		conf = load_settings()
		authorizer = load_users()
		ThrottledDTPHandler.write_limit = conf.max_upload_speed
		ThrottledDTPHandler.read_limit = conf.max_download_speed
		FTPHandler.dtp_handler = ThrottledDTPHandler
		FTPHandler.banner = conf.server_banner
		FTPServer.max_cons = conf.max_cons
		FTPServer.max_cons_per_ip = conf.max_cons_per_ip
		FTPHandler.authorizer = authorizer
		# FTPHandler.permit_foreign_addresses = conf.permit_outside_lan

		port = conf.port
		if is_port_available(port):
			server = FTPServer(('0.0.0.0', port), FTPHandler)
		else:
			return

		server.serve_forever()

	def getport(self):
		return str(port)


class settings_ui_thread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		subprocess.call([python, "settings.py"])


class userui_thread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		subprocess.call([python, "authui.py"])



# handling with GUI
from PyQt5.QtWidgets import (QWidget, QAction, qApp, QPushButton, QApplication,
	QMainWindow, QTextEdit, QMessageBox, QInputDialog, QLineEdit)
from PyQt5.QtGui import QIcon, QFont


class MainUI(QMainWindow, QWidget):
	def __init__(self):
		super().__init__()
		self.srv = None
		self.initUI()

	def initUI(self):
		mylog ("Creating ui")
		self.mainbtn = QPushButton("Start server", self)
		self.mainbtn.setStyleSheet("background-color: blue; color: white; border: none")
		# self.mainbtn.setCheckable(True)
		self.mainbtn.move(90, 100)
		self.mainbtn.clicked[bool].connect(self.check_server)

		# exit action
		# exitAction = QAction(QIcon('icons/exit.png'), '&Exit', self)
		# exitAction.setShortcut('Alt+F4')
		# exitAction.setStatusTip('Exit Application')
		# exitAction.setToolTip("Exit :  Alt+F4")
		# # exitAction.triggered.connect(qApp.quit)
		# exitAction.triggered.connect(self.quitapp)

		# port check tool
		portCheck = QAction(QIcon('icons/ic_search_black_48dp_1x.png'), 'Port &Check', self)
		portCheck.setShortcut('Ctrl+F')
		portCheck.setToolTip("Port Scan :  Ctrl+F")
		portCheck.setStatusTip("Check whether a port is available")
		portCheck.triggered.connect(self.checkPortUI)
		# portCheck.triggered.connect(portCheckUI())

		# settings configuration tool
		sett_conf = QAction(QIcon('icons/ic_settings_black_48dp_1x.png'), '&Settings', self)
		sett_conf.setShortcut('Ctrl+S')
		sett_conf.setToolTip("Settings :  Ctrl+S")
		sett_conf.setStatusTip("Modify server settings")
		sett_conf.triggered.connect(self.setttingsUI)

		# user management tool
		userui = QAction(QIcon('icons/ic_account_box_black_48dp_2x.png'), '&Users...', self)
		userui.setShortcut('Ctrl+U')
		userui.setToolTip("Manage users :  Ctrl+U")
		userui.setStatusTip("Manage the list of users which connect to you.")
		userui.triggered.connect(self.userui_init)

		menubar = self.menuBar()
		appMenu = menubar.addMenu('&App')
		appMenu.addAction(portCheck)
		# appMenu.addAction(exitAction)
		configMenu = menubar.addMenu('&Config')
		configMenu.addAction(sett_conf)
		configMenu.addAction(userui)


		self.toolbar = self.addToolBar("Quick Access")
		self.toolbar.setToolTip("Controls toolbar")
		# self.toolbar.addAction(exitAction)
		self.toolbar.addAction(portCheck)
		self.toolbar.addAction(sett_conf)
		self.toolbar.addAction(userui)


		self.setGeometry(200, 100, 280, 170)
		self.setWindowTitle("FTP server")
		self.statusBar().showMessage("Welcome")
		self.show()


	def quitapp(self):
		global Server
		if server:
			server.close_all()
		del self.srv
		sys.exit()

	def check_server(self, pressed):
		global server
		if not server:
			global port
			port = load_settings().port
			if not is_port_available(port):
				mylog("\nPort : " + str(port) + " is not available\n")
				QMessageBox.critical(self, "Port error", "The port requested is not available.\nPlease change the port in settings.\n", QMessageBox.Ok, QMessageBox.Ok)
				return
			self.srv = myserver()
			self.srv.start()
			msg = "Running on port " + str(self.srv.getport())
			self.mainbtn.setText("Stop Server")
			self.mainbtn.setStyleSheet("background-color: #ff7373; color: black; border: none")
			self.statusBar().showMessage(msg)
		else:
			server.close_all()
			del self.srv
			self.srv = None
			server = None
			self.statusBar().showMessage("Stopped")
			self.mainbtn.setText("Start Server")
			self.mainbtn.setStyleSheet("background-color: #40e0d0; color: black; border: none")


	def closeEvent(self, event):
		try:
			if self.srv is not None:
				self.statusBar().showMessage("Cleaning up")
				server.close_all()
				del self.srv
				print("Cleaned up")
		except:
			pass
		finally:
			reply = QMessageBox.question(self, 'Close', "Are you sure to exit ?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
			if reply == QMessageBox.Yes:
				event.accept()
			else:
				event.ignore()


	def checkPortUI(self):
		text, ok = QInputDialog.getText(self, "Input Dialog", "Enter any port")
		try:
			port = int(text)
			if port < 0 or port > 65535:
				raise ValueError
			if ok:
				if is_port_available(int(text)):
					QMessageBox.information(self, 'Message', "Port is available", QMessageBox.Ok, QMessageBox.Ok)
				else:
					QMessageBox.critical(self, 'Message', "Port is unavailable", QMessageBox.Ok, QMessageBox.Ok)
		except ValueError:
			QMessageBox.warning(self, 'Error', "Port number should be a number between 0 and 65535", QMessageBox.Ok, QMessageBox.Ok)


	def setttingsUI(self):
		th = settings_ui_thread()
		th.start()


	def userui_init(self):
		th = userui_thread()
		th.start()


if __name__ == "__main__":
	app = QApplication([])
	app.setWindowIcon(QIcon('icons/1468025361_cmyk-03.png'))
	ex = MainUI()
	sys.exit(app.exec_())
