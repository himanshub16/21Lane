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
import mimetypes
from tinydb import TinyDB, where, Query

from datetime import datetime


# these are my global variables
userbase = auth.Userbase()
python = sys.executable

PORT = 2121
server = None
gen_snapshot = False
exchange_connect_status = False
exchange_url = ''
server_running_status = False

ls = os.listdir
pwd = os.getcwd()


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
		print(e)
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
		mylog ("Socket out of range")
	except (ConnectionError, ConnectionRefusedError):
		# Connection refused error to handle windows systems:(
		return True
	except Exception as e:
		mylog('error while port check')

	return result==0


def get_ip_address():
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8",80))
		ip = s.getsockname()[0]
		s.close()
		return ip
	except Exception as e:
		return 'localhost'


class generate_system_snapshot(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def do_the_job(self):
		global exchange_connect_status, gen_snapshot
		
		if not 'anonymous' in userbase.get_user_list():
			mylog("No anonymous user, cannot generate sharing snapshot")
			return

		self.dbdict = {}
		self.dbdict["filedata"] = {}
		self.dbtable = self.dbdict["filedata"]
		# self.dic = dict()
		self.totalsize = 0
		self.filecount = 0
		def path_to_dict(path, l):
			if not gen_snapshot:
				return
			try:
				if os.path.isdir(path):
					for x in ls(path):
						path_to_dict(os.path.join(path, x), l)
				else:
					self.filecount += 1
					size = os.path.getsize(path)
					filename = os.path.basename(path)
					self.dbtable[str(self.filecount)] = { "filename":filename, "size":size, "fullpath":path[l:], "mimetype":mimetypes.guess_type(filename)[0] }
					# self.dic[os.path.basename(path)] = { "size" : os.path.getsize(path), "fullpath" : path[l:] }
					self.totalsize += size
			except Exception as e:
				pass

		if not gen_snapshot:
			return
		shared_dir = userbase.get_user_info('anonymous').homedir
		p = os.path.abspath(shared_dir)
		path_to_dict(p, len(p))
		self.dbdict["metadata"] = {}
		self.metadata = self.dbdict["metadata"]
		self.metadata['1'] = { "totalfiles":self.filecount, "totalsize":self.totalsize }

		# earlier, tinydb insert function was used to insert records into database in json format
		# which was extremely slow
		# now, the database is created manually, in the format tinydb keeps them.

		f = open('snapshot.json', 'w')
		f.write(json.dumps(self.dbdict, indent=2))
		f.close()
		mylog("Snapshot generated")


	def upload_file(self): 
		global userbase, exchange_url
		mylog("Starting upload")
		try:
			if 'anonymous' in userbase.get_user_list():
				dest_dir = userbase.get_user_info('anonymous').homedir
				dest_path = os.path.join(dest_dir, 'snapshot.json')
				dest_file = open(dest_path, 'wb')
				source_file = open('snapshot.json', 'rb')
				dest_file.write(source_file.read())
				source_file.close()
				dest_file.close()

				# now notify you dad to take the parcel
				mylog('Asking dad to take the parcel')
				f = open('session_id', 'r')
				sessionid = f.read().strip()
				f.close()
				r = requests.post(url=exchange_url, data={'action':'snapshot'}, cookies={'session_id':sessionid}, timeout=5, proxies=None)
				# print(r.text, 'is the response for snapshot')
				if r.status_code==200 and r.text.strip()=='ok':
					mylog('Snapshot file uploaded successfully.')
					os.remove(dest_path)
				else:
					mylog("Some error occured while uploading snapshot.")

		except (requests.exceptions.ConnectionError, ConnectionAbortedError, requests.exceptions.Timeout) as e:
			mylog("Network error while periodical uploads.")
			# raise e
		except Exception as e:
			# first close any open file to avoid permissions error in windows, and other similar errors
			try:
				if not f.closed:
					f.close()
				if not dest_file.closed:
					dest_file.close()
				if not source_file.closed:
					source_file.close
			except NameError:
				pass

			if 'session_id' in ls(pwd):
				os.remove('session_id')
			mylog(str(e) + ' ' + 'is the error')
			raise e

	def getThreadName(self):
		return self.thread_name

	def run(self):
		self.thread_name = self.getName()
		global gen_snapshot
		cur_time = time.time()
		wait_time = 60*60 # one hour gap
		next_time = cur_time
		upload_time = time.time()
		while (True):
			if not gen_snapshot:
				mylog("Ending snapshot thread")
				break
			if cur_time >= next_time:
				mylog('Generating snapshot')
				self.do_the_job()
				next_time += wait_time
				if exchange_connect_status == True:
					self.upload_file()
	
			# breathe, don't choke while you run
			time.sleep(1)
			cur_time += 1
		mylog("Snapshot creator Thread quits")




class myserver(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		self.thread_name = self.getName()
		global server, PORT, server_running_status, exchange_url
		conf = load_settings()
		exchange_url = conf.exchange_url
		try:
			authorizer = load_users()
		except Exception as e:
			mylog("My server caught an exception")
			sys.exit(1)

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
		mylog('server status ' + str(server_running_status))
		server.serve_forever()

	def getport(self):
		return str(PORT)

	def getThreadName(self):
		return self.thread_name


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
		mylog ("Starting ui")

		self.mainbtn = QPushButton("Start sharing", self)
		self.mainbtn.setStyleSheet("background-color: blue; color: white; border: none")
		self.mainbtn.setCheckable(True)
		self.mainbtn.move(85, 100)
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
		self.exchange = QAction(QIcon('icons/disconnect.png'), 'Connect to &Exchange...', self)
		self.exchange.setShortcut('Ctrl+E')
		self.exchange.setToolTip("Connect to exchange  :  Ctrl+E")
		self.exchange.setStatusTip("Connect to 21Exchange servers on local network.")
		self.exchange.triggered.connect(self.exchange_connect)

		# disconnect from 21exchange
		self.disconnect = QAction(QIcon('icons/ic_wb_cloudy_black_48dp_2x.png'), 'Connect to &Exchange...', self)
		self.disconnect.setShortcut('Ctrl+E')
		self.disconnect.setToolTip("Connect to exchange  :  Ctrl+E")
		self.disconnect.setStatusTip("Connect to 21Exchange servers on local network.")
		self.disconnect.triggered.connect(self.exchange_disconnect)

		self.menubar = self.menuBar()
		self.appMenu = self.menubar.addMenu('&App')
		self.appMenu.addAction(portCheck)
		self.appMenu.addAction(self.exchange)
		# appMenu.addAction(exitAction)
		configMenu = self.menubar.addMenu('&Config')
		configMenu.addAction(sett_conf)
		configMenu.addAction(userui)


		self.toolbar = self.addToolBar("Quick Access")
		self.toolbar.setToolTip("Controls toolbar")
		# self.toolbar.addAction(exitAction)
		self.toolbar.addAction(portCheck)
		self.toolbar.addAction(sett_conf)
		self.toolbar.addAction(userui)
		self.toolbar.addAction(self.exchange)

		# self.snapshot_thread = None
		# self.srv = None

		self.setGeometry(200, 100, 280, 170)
		self.setFixedSize(280, 170)
		self.setWindowTitle("21Lane")
		self.statusBar().showMessage("Welcome")
		self.show()


	def quitapp(self):
		global server, gen_snapshot
		mylog("quit event caught", gen_snapshot)
		if server:
			server.close_all()
			print(threading.Thread.isAlive(self.srv))
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
				time.sleep(0.5)
			self.mainbtn.setText("Stop Sharing")
			self.mainbtn.setStyleSheet("background-color: #ff7373; color: black; border: none")
			self.statusBar().showMessage(msg)

			gen_snapshot = True
			self.snapshot_thread = generate_system_snapshot()
			self.snapshot_thread.start()

		elif server and server_running_status:
			self.statusBar().showMessage("Stopping, please wait...")
			server.close_all()
			server_running_status = False
			
			# wait for the thread to exit
			# if it doesn't within given time, close it forcibly
			count = 4
			mylog("Waiting for server thread to end")
			while( threading.Thread.isAlive(self.srv) and count > 0):
				time.sleep(0.5)
				count -= 1
			
			if count == 0:
				mylog("Shit happens! Shutting down server forcibly.")
			del self.srv, server
			self.srv = None
			server = None
			# end snapshot generation thread
			if gen_snapshot:
				gen_snapshot = False
				# wait for the thread to exit
				while( threading.Thread.isAlive(self.snapshot_thread) ):
					mylog("Waiting for snapshot thread to end.")
					time.sleep(1)
				self.snapshot_thread = None
			self.statusBar().showMessage("Stopped")
			server_running_status = False
			self.mainbtn.setText("Start Sharing")
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


	def exchange_disconnect(self):
		global exchange_url, exchange_connect_status
		reply = QMessageBox.question(self, '21Exchange', "You are connected. Do you want to log out from the server?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
		if reply == QMessageBox.Yes:
			if 'session_id' in ls(pwd):
				f = open('session_id', 'r')
				sessionid = f.read().strip()
				f.close()
			else:
				sessionid = None
			
			post_data = { 'action':'disconnect' }
			r = requests.post(exchange_url, data=post_data, cookies={'session_id':sessionid}, proxies=None)
			if r.status_code == 200 and r.text.strip() == 'ok':
				exchange_connect_status = False
				QMessageBox.information(self, '21Exchange', "You have been logged out.")
				if 'session_id' in ls(pwd):
					os.remove('session_id')
					mylog("session_id file removed")
			self.toolbar.removeAction(self.disconnect)
			self.appMenu.removeAction(self.disconnect)
			self.toolbar.addAction(self.exchange)
			self.appMenu.addAction(self.exchange)



	def exchange_connect(self):
		global server, exchange_url, PORT, exchange_connect_status
		if not server:
			QMessageBox.warning(self, 'Sorry', "You must have sharing enabled to connect to an exchange.", QMessageBox.Ok, QMessageBox.Ok)
			return
		inp, ok = QInputDialog.getText(self, 'Connect to servers', 'Enter the link obtained from 21Exchange on your network\n', QLineEdit.Normal, exchange_url)
		try:
			if ok:
				inp = inp.split(' ')
				exchange_url = inp[0]
				if not exchange_url.startswith('http'):
					exchange_url = 'http://'+exchange_url
				if len(inp) == 1:
					u, pwd = None, None
				else:
					u, pwd = inp[1], inp[2]

				# url = '+str(p)
				server_name = load_settings().server_name
				post_data = { 'username':u, 'password':pwd, 'action':'connect', 'server_name':server_name, 'port':PORT }

				if 'session_id' in ls(pwd):
					f = open('session_id', 'r')
					ckstr = f.read()
					f.close()
					ck = {'session_id':ckstr.strip()}
				else:
					ck = None
				r = requests.post(exchange_url, data=post_data, cookies=ck, proxies=None)
				sessionid = None
				# print(r.status_code, r.text)
				if r.status_code == 200:
					f = open('session_id', 'w')
					f.write(r.cookies['session_id'])
					sessionid = r.cookies['session_id']
					f.close()
				if r.status_code == 404:
					QMessageBox.warning(self, "Invalid URL", "Oops... You entered an invalid URL / host.", QMessageBox.Ok, QMessageBox.Ok)
					return

				# modify menubar and toolbar accordingly
				self.appMenu.removeAction(self.exchange)
				self.appMenu.addAction(self.disconnect)
				self.toolbar.removeAction(self.exchange)
				self.toolbar.addAction(self.disconnect)
				exchange_connect_status = True
				# now upload the snapshot file, if any like a good boy
				# this didn't work
				# if ('snapshot.json' in ls(pwd) and exchange_url):
				# 	f = open('snapshot.json', 'rb')
				# 	print("uploading snapshot file")
				# 	r = requests.post(url=exchange_url, files={'filecontent':f.read()}, stream=True)
				# 	f.close()
				# 	print("snapshot file uploaded")

				# check whether the file is ready to be uploaded and
				# send a message to exchange_url, indicating the file is ready to be uploaded
				# if 'snapshot.json' in ls(pwd) and exchange_url:
				# 	r = requests.post(url='http://localhost:8000/cgi-bin/get_snapshot_file.py')
				# 	print(r.textn)

				# now trying to place the snapshot file in anonymous user's directory
				# to be uploaded to the exchange.
				# oh boy, you worked graciously, i'll keep you
				# fuck all the above methods..
				# let them be in comments for future references
				if 'anonymous' in userbase.get_user_list():
					dest_dir = userbase.get_user_info('anonymous').homedir
					dest_path = os.path.join(dest_dir, 'snapshot.json')
					dest_file = open(dest_path, 'wb')
					source_file = open('snapshot.json', 'rb')
					dest_file.write(source_file.read())
					source_file.close()
					dest_file.close()

					# now notify you dad to take the parcel
					mylog('Asking dad to take the parcel')
					r = requests.post(url=exchange_url, data={'action':'snapshot'}, cookies={'session_id':sessionid}, timeout=5, proxies=None)
					# print(r.text, 'is the response for snapshot')
					if r.status_code==200 and r.text.strip()=='ok':
						mylog('Snapshot file uploaded successfully.')
						os.remove(dest_path)
					else:
						mylog("Some error occured while uploading snapshot.")


		except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError, ConnectionAbortedError, requests.exceptions.Timeout) as e:
			QMessageBox.critical(self, 'Error', 'Network error!', QMessageBox.Ok, QMessageBox.Ok)
			# raise e
		except Exception as e:
			# first close any open file to avoid permissions error in windows, and other similar errors
			try:
				if not f.closed:
					f.close()
				if not dest_file.closed:
					dest_file.close()
				if not source_file.closed:
					source_file.close
			except NameError:
				pass

			if 'session_id' in ls(pwd):
				os.remove('session_id')
			QMessageBox.critical(self, 'Error', "Some error occured!", QMessageBox.Ok, QMessageBox.Ok)
			mylog(str(e) + ' ' + 'is the error')
			raise e



if __name__ == "__main__":
	app = QApplication([])
	app.setWindowIcon(QIcon('icons/favicon.ico'))
	ex = MainUI()
	sys.exit(app.exec_())
