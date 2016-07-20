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
import time
import requests
import json

from datetime import datetime


# these are my global variables
userbase = auth.Userbase()
python = sys.executable

PORT = 2121
server = None
gen_snapshot = False
exchange_connect_status = True
server_running_status = False


# here the global key functions 

def mylog(ar):
	f = open('log.txt', 'a')
	f.write(str(datetime.now()) + " " + ar + "\n")
	f.close()


def load_settings():
	return settings.FTPSettings()

def load_users():
	""" creates a new DummyAuthorizer object at every call
	"""
	try:
		authorizer = DummyAuthorizer()
		if len(userbase.get_user_list()) == 0:
			mylog("There are no users available.")
			sys.exit(1)

		for username in userbase.get_user_list():
			userobj = userbase.get_user_info(username)
			if username == 'anonymous':
				if authorizer.has_user(username):
					authorizer.remove_user(username)
				authorizer.add_anonymous(userobj.homedir, perm=userobj.permission, msg_login=userobj.msg_login, msg_quit=userobj.msg_quit)
			else:
				if authorizer.has_user(username):
					authorizer.remove_user(username)
				authorizer.add_user(userobj.name, userobj.password, userobj.homedir, perm=userobj.permission, msg_login=userobj.msg_login, msg_quit=userobj.msg_quit)
		return authorizer
	except Exception as e:
		mylog("Error while creating authorizer object")
		raise e
		sys.exit(1)


def start_server():
	server.serve_forever()

def stop_server():
	server.close_all()


def is_port_available(port):
	port = int(port)
	try:
		# connecting on localhost, previously it was 0.0.0.0, to satisfy Windows
		result = socket.create_connection(('localhost', port), 2)
	except OverflowError:
		print ("Socket out of range")
	except (ConnectionError, ConnectionRefusedError):
		# Connection refused error to handle windows systems:(
		return True
	except Exception as e:
		mylog('error while port check')

	return result==0


def get_ip_address():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8",80))
	ip = s.getsockname()[0]
	s.close()
	return ip


class generate_system_snapshot(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def do_the_job(self):
		global exchange_connect_status, gen_snapshot
		if not exchange_connect_status:
			mylog("Not connected to exchange, cannot generate sharing snapshot")
			return

		if not 'anonymous' in userbase.get_user_list():
			print("No anonymous user, cannot generate sharing snapshot")
			return

		self.dic = dict()
		self.totalsize = 0
		def path_to_dict(path, l):
			try:
				if os.path.isdir(path):
					for x in os.listdir(path):
						path_to_dict(os.path.join(path, x), l)
				else:
					self.dic[os.path.basename(path)] = { "size" : os.path.getsize(path), "fullpath" : path[l:] }
					self.totalsize += os.path.getsize(path)
			except Exception as e:
				pass

		shared_dir = userbase.get_user_info('anonymous').homedir
		p = os.path.abspath(shared_dir)
		path_to_dict(p, len(p))
		self.dic['total_shared_size'] = self.totalsize

		# write to file
		f = open('snapshot.json', 'w')
		f.write(json.dumps(self.dic, indent=2))
		f.close()
		mylog("Snapshot generated")
		gen_snapshot = True

	def run(self):
		global gen_snapshot
		cur_time = time.time()
		wait_time = 60*60 # one hour gap
		next_time = cur_time
		while (True):
			if not gen_snapshot:
				break
			if cur_time >= next_time:
				self.do_the_job()
				next_time += wait_time
			# breathe, don't choke while you run
			time.sleep(1)
			cur_time += 1
		mylog("Snapshot creator Thread quits")



class myserver(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		global server, PORT, server_running_status
		conf = load_settings()
		try:
			authorizer = load_users()
		except Exception as e:
			mylog("My server caught an exception")
			return 1
		ThrottledDTPHandler.write_limit = conf.max_upload_speed
		ThrottledDTPHandler.read_limit = conf.max_download_speed
		FTPHandler.dtp_handler = ThrottledDTPHandler
		FTPHandler.banner = conf.server_banner
		FTPServer.max_cons = conf.max_cons
		FTPServer.max_cons_per_ip = conf.max_cons_per_ip
		FTPHandler.authorizer = authorizer
		# FTPHandler.permit_foreign_addresses = conf.permit_outside_lan

		if is_port_available(conf.port):
			server = FTPServer(('0.0.0.0', conf.port), FTPHandler)
		else:
			return
		server_running_status = True
		print(server_running_status)
		server.serve_forever()

	def getport(self):
		return str(PORT)


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


# class filesystem_snapshot(threading.Thread):



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
		mylog ("Starting ui")

		self.mainbtn = QPushButton("Start sharing", self)
		self.mainbtn.setStyleSheet("background-color: blue; color: white; border: none")
		self.mainbtn.setCheckable(True)
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
		sett_conf.setStatusTip("Modify sharing settings")
		sett_conf.triggered.connect(self.setttingsUI)

		# user management tool
		userui = QAction(QIcon('icons/ic_account_box_black_48dp_2x.png'), '&Users...', self)
		userui.setShortcut('Ctrl+U')
		userui.setToolTip("Manage users :  Ctrl+U")
		userui.setStatusTip("Manage the list of users which connect to you.")
		userui.triggered.connect(self.userui_init)

		# connect to 21exchange
		exchange = QAction(QIcon('icons/ic_wb_cloudy_black_48dp_1x.png'), 'Connect to &Exchange...', self)
		exchange.setShortcut('Ctrl+E')
		exchange.setToolTip("Connect to exchange  :  Ctrl+E")
		exchange.setStatusTip("Connect to 21Exchange servers on local network.")
		exchange.triggered.connect(self.exchange_connect)

		menubar = self.menuBar()
		appMenu = menubar.addMenu('&App')
		appMenu.addAction(portCheck)
		appMenu.addAction(exchange)
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
		self.toolbar.addAction(exchange)


		self.setGeometry(200, 100, 280, 170)
		self.setFixedSize(280, 170)
		self.setWindowTitle("FTP server")
		self.statusBar().showMessage("Welcome")
		self.show()


	def quitapp(self):
		global server, gen_snapshot
		mylog("quit event caught", gen_snapshot)
		if server:
			server.close_all()
		del self.srv
		mylog(self.snapshot_thread)
		if self.snapshot_thread:
			gen_snapshot = False
			del self.snapshot_thread
		sys.exit()

	def check_server(self, pressed):
		if len(userbase.get_user_list()) == 0:
			QMessageBox.critical(self, "No users", "There are no users available.\nPlease add at least one user.", QMessageBox.Ok, QMessageBox.Ok)
			return


		global server, gen_snapshot, server_running_status, PORT
		PORT = load_settings().port
		self.mainbtn.setEnabled(False)

		if not server and not server_running_status:
			if not is_port_available(PORT):
				mylog("\nPort : " + str(PORT) + " is not available\n")
				QMessageBox.critical(self, "Port error", "Port " + str(PORT) + " is not available.\nPlease change the port in settings.\n", QMessageBox.Ok, QMessageBox.Ok)
				return
			self.statusBar().showMessage("Starting, please wait...")
			# if not server_running_status:
			# 	QMessageBox.critical(self, "Error", "Error while starting sharing.", QMessageBox.Ok, QMessageBox.Ok)
			# 	self.statusBar().showMessage("Error occured.")
			# 	return
			self.srv = myserver()
			self.srv.start()
			msg = "Sharing on " + get_ip_address() + ":" + str(self.srv.getport())
			while not server_running_status:
				time.sleep(1)
			self.mainbtn.setText("Stop Sharing")
			self.mainbtn.setStyleSheet("background-color: #ff7373; color: black; border: none")
			self.statusBar().showMessage(msg)

			self.snapshot_thread = generate_system_snapshot()
			gen_snapshot = True
			self.snapshot_thread.start()

		elif server and server_running_status:
			server.close_all()
			del self.srv
			self.srv = None
			server = None
			# end snapshot generation thread
			if gen_snapshot:
				gen_snapshot = False
				del self.snapshot_thread
			self.statusBar().showMessage("Stopped")
			server_running_status = False
			self.mainbtn.setText("Start Server")
			self.mainbtn.setStyleSheet("background-color: #40e0d0; color: black; border: none")
		else:
			return

		self.mainbtn.setEnabled(True)


	def closeEvent(self, event):
		try:
			if self.srv is not None:
				self.statusBar().showMessage("Cleaning up")
				server.close_all()
				del self.srv
				global gen_snapshot
				if self.snapshot_thread:
					gen_snapshot = False
					del self.snapshot_thread
				mylog("Cleaned up")
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


	def exchange_connect(self):
		global server
		if not server:
			QMessageBox.warning(self, 'Sorry', "You must have sharing enabled to connect to an exchange.", QMessageBox.Ok, QMessageBox.Ok)
			return
		inp, ok = QInputDialog.getText(self, 'Connect to server', 'Enter details as in given examples\n\n192.168.1.2:2020 user password (OR)\nexchange.url.com:2020 user password\n')
		try:
			if ok:
				inp = inp.split()
				url = inp[0]
				if len(inp) == 1:
					u, pwd = inp[0][0], inp[1], None, None
				else:
					u, pwd = inp[1], inp[2]
					
				url = str(h)+str(p)
				post_data = { 'username':u, 'password':pwd, 'action':'connect' }
				r = requests.post(url, data=post_data)
				if r.status_code == 200:
					print(r.text)
		except Exception as e:
			QMessageBox.critical(self, 'Error', "Some error occured!", QMessageBox.Ok, QMessageBox.Ok)



if __name__ == "__main__":
	app = QApplication([])
	app.setWindowIcon(QIcon('icons/1468025361_cmyk-03.png'))
	ex = MainUI()
	sys.exit(app.exec_())
	