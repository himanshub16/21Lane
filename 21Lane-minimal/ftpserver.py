#!/usr/bin/python3
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.handlers import ThrottledDTPHandler
from pyftpdlib.servers import FTPServer
 
# import additions
import sys
import os
import errno
import socket
import threading
import subprocess
import time
import requests
import json
import mimetypes
from tinydb import TinyDB, where, Query
from urllib.parse import urlparse 
from copy import deepcopy

from datetime import datetime


# these are my global variables
# userbase = auth.Userbase()
python = sys.executable

PORT = 2121
server = None
gen_snapshot = False
exchange_connect_status = False
CAPERROR = False
exchange_url = ''
total_share_size = 0
server_running_status = False

app_is_running = True

ls = os.listdir
pwd = os.getcwd()

# anonymous user class
# class AnonymousUser:

# 	"""Each instance of this class represents an anonymous user
# 	* name 		: anonymous (as both kinds of users are in same database)
# 	* homedir	| 	* permission
# 	* msg_login	| 	* msg_quit
# 	*
# 	* save_details() : save current details
# 	"""
# 	def __init__(self, dic):
# 		k = list(dic.keys())
# 		if	'homedir' in k and \
# 			'permission' in k:
# 			self.record = deepcopy(dic)
# 		if not 'msg_quit' in k:
# 			self.record['msg_quit'] = ''
# 		if not 'msg_login' in k:
# 			self.record['msg_login'] = ''
# 		self.record['name'] = 'anonymous'

# 		self.name = self.record['name']
# 		self.homedir = self.record['homedir']
# 		self.permission = self.record['permission']
# 		self.msg_login = self.record['msg_login']
# 		self.msg_quit = self.record['msg_quit']

# 	def save_details(self):
# 		dbase = TinyDB('user_database.json')
# 		if not (dbase.count(where('name') == self.record['name'])) == 0:
# 			dbase.remove(where('name') == self.record['name'])
# 		dbase.insert(self.record)
# 		dbase.close()


class FTPSettings:
	"""Class to handle FTP Settings
	There are following attributes that are saved in settings file
	* server_name			|	name of the server
	* server_banner			|	message displayed on connecting first time (FTPHandler)
	* port					| 	port (default 2121)
	* max_cons				|	maximum connections to the server (FTPServer)
	* max_cons_per_ip		|	maximum connections per ip address (FTPServer)
	* max_upload_speed		|	maximum upload speed on server (take care of hard drive i/o and network speed) (ThrottledDTPHandler)
	* max_download_speed	|	maximum download speed (auto_sized_buffers are True by default) (ThrottledDTPHandler)
	* permit_outside_lan	|	FTPHandler (permit_foreign_addresses) [ Not handling due to lack of knowledge ]
	* homedir 	            |   Anonymous home directory (added for this minimal version)
	"""

	def __init__(self):
		"""read data from settings file"""
		dbase = TinyDB('settings.json')
		if len(dbase.all()) == 0:
			self.server_name = 'whoami'
			self.server_banner = "Welcome..."
			self.port = 2121
			self.max_cons = 10
			self.max_cons_per_ip = 2
			self.max_upload_speed = 2097152 	# approximately 2 Mbps in bytes
			self.max_download_speed = 10	# to resrtict uploads from public on server,
											# when write permission is allowed
			# self.permit_outside_lan = False
			self.exchange_url = ""
			self.homedir = ""

		else:
			try:
				rec = dbase.all()[0]
				self.server_name = rec['server_name']
				self.server_banner = rec['server_banner']
				self.port = rec['port']
				self.max_cons = rec['max_cons']
				self.max_cons_per_ip = rec['max_cons_per_ip']
				self.max_upload_speed = rec['max_upload_speed']
				self.max_download_speed = rec['max_download_speed']
				self.exchange_url = rec['exchange_url']
				self.homedir = rec['homedir']
			except KeyError:
				self.restore_default_settings()
			# permit outside lan has not been included
		dbase.close()
		
	def reload_settings(self):
		self.__init__()

	def save_settings(self):
		"""save settings to settings file"""
		dbase = TinyDB('settings.json')
		dbase.purge()
		rec={}
		rec['server_name'] = self.server_name
		rec['server_banner'] = self.server_banner
		rec['port'] = self.port
		rec['max_cons'] = self.max_cons
		rec['max_cons_per_ip'] = self.max_cons_per_ip
		rec['max_upload_speed'] = self.max_upload_speed
		rec['max_download_speed'] = self.max_download_speed
		# f['permit_outside_lan'] = self.permit_outside_lan
		rec['exchange_url'] = self.exchange_url
		rec['homedir'] = self.homedir
		dbase.insert(rec)
		dbase.close()
		mylog("Settings modified")

	def restore_default_settings(self):
		dbase = TinyDB('settings.json')
		dbase.purge()
		dbase.close()
		self.__init__()



# here the global key functions

def mylog(ar):
	f = open('log.txt', 'a')
	f.write(str(datetime.now()) + " " + ar + "\n")
	f.close()


def load_settings():
	return FTPSettings()

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
		try:
			ip = socket.gethostbyname(socket.getfqdn())
			return ip
		except Exception as e:
			mylog("cannot determine ip address" + str(e))
			return ""
		return ""


class generate_system_snapshot(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def do_the_job(self):
		global exchange_connect_status, gen_snapshot, total_share_size, app_is_running

		self.dbdict = {}
		self.dbdict["filedata"] = {}
		self.dbtable = self.dbdict["filedata"]
		# self.dic = dict()
		self.totalsize = 0
		self.filecount = 0
		def path_to_dict(path, l):
			if ( not gen_snapshot ) or (not app_is_running ):
				# not generating snapshot
				return
			try:
				if os.path.isdir(path):
					for x in ls(path):
						path_to_dict(os.path.join(path, x), l)
				else:
					self.filecount += 1
					size = os.path.getsize(path)
					filename = os.path.basename(path)
					self.dbtable[str(self.filecount)] = { "filename":filename, "size":size, "fullpath":path[l:-len(filename)], "mimetype":mimetypes.guess_type(filename)[0] }
					# self.dic[os.path.basename(path)] = { "size" : os.path.getsize(path), "fullpath" : path[l:] }
					self.totalsize += size
			except Exception as e:
				raise e

		if not gen_snapshot:
			return
		shared_dir = load_settings().homedir
		p = os.path.abspath(shared_dir)
		path_to_dict(p, len(p))
		self.dbdict["metadata"] = {}
		self.metadata = self.dbdict["metadata"]
		self.metadata['1'] = { "totalfiles":self.filecount, "totalsize":self.totalsize }
		total_share_size = self.totalsize


		# earlier, tinydb insert function was used to insert records into database in json format
		# which was extremely slow
		# now, the database is created manually, in the format tinydb keeps them.

		f = open('snapshot.json', 'w')
		f.write(json.dumps(self.dbdict, indent=2))
		f.close()
		mylog("Snapshot generated")


	def upload_file(self): 
		global exchange_url, CAPERROR
		mylog("Starting upload")
		try:
			dest_dir = load_settings().homedir
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
			uri=exchange_url+'/cgi-bin/actions.py'
			headers = {'user-agent':'21Lane'}
			r = requests.post(url=uri, data={'action':'snapshot'}, cookies={'session_id':sessionid}, headers=headers, timeout=5, proxies=None)
			# print(r.text, 'is the response for snapshot')
			if r.status_code==200:
				if r.text.strip() == 'ok':
					mylog('Snapshot file uploaded successfully.')
					os.remove(dest_path)
				elif r.text.strip() == 'CAPERROR':
					CAPERROR = True
			else:
				mylog("Some error occured while uploading snapshot.")

		except (requests.exceptions.ConnectionError, ConnectionAbortedError, requests.exceptions.Timeout) as e:
			mylog("Network error while periodical uploads.")
			raise e
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
		global gen_snapshot, app_is_running
		cur_time = time.time()
		wait_time = 60*60 # one hour gap
		next_time = cur_time
		upload_time = time.time()
		while True and app_is_running:
			if not gen_snapshot:
				mylog("Ending snapshot thread")
				break
			if cur_time >= next_time:
				mylog('Generating snapshot')
				self.do_the_job()
				next_time += wait_time
				if exchange_connect_status == True:
					self.upload_file()
				else:
					print("not uploading file")
	
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
			authorizer = DummyAuthorizer()
			authorizer.add_anonymous(conf.homedir, msg_login="Welcome to 21Lane sharing.", msg_quit="Thanks for using.")
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



# handling with GUI
from PyQt5.QtWidgets import (QWidget, QAction, qApp, QPushButton, QApplication,
	QMainWindow, QTextEdit, QMessageBox, QInputDialog, QLineEdit, QLabel, QVBoxLayout,
	QHBoxLayout, QGridLayout, QFrame, QSlider, QSpinBox, QFileDialog, QSplitter)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.Qt import QDesktopServices, QUrl
from PyQt5.QtCore import Qt, QCoreApplication


class MainUI(QWidget):
	def __init__(self):
		super().__init__()
		self.srv = None
		self.exchange_process = None
		self.capThread = None
		self.initUI()

	def initUI(self):
		mylog ("Starting ui")

		self.itHurtsLabel = QLabel(self)
		self.itHurtsLabel.setText("Don't randomly hit your mouse. It hurts!'")
		self.itHurtsLabel.setFont(QFont('SansSerif', 10))
		self.itHurtsLabel.setStyleSheet("padding: 5px;")
		self.itHurtsLabel.setWordWrap(False)

		self.mainbtn = QPushButton("Start sharing", self)
		self.mainbtn.setStyleSheet("background-color: #22a7f0; color: white; border: none; padding: 5px;")
		self.mainbtn.setCheckable(True)
		self.mainbtn.clicked[bool].connect(self.check_server)

		self.exchangebtn = QPushButton("Walk the lane", self)
		self.exchangebtn.setStyleSheet("background-color: #bdc3c7; color: white; border: none; padding: 5px 15px;")
		self.exchangebtn.setCheckable(True)
		self.exchangebtn.setEnabled(False)


		# port check tool
		portCheck = QAction(QIcon('icons/ic_search_black_48dp_1x.png'), 'Port &Check', self)
		portCheck.setShortcut('Ctrl+F')
		portCheck.setToolTip("Port Scan :  Ctrl+F")
		portCheck.setStatusTip("Check whether a port is available")
		portCheck.triggered.connect(self.checkPortUI)
		# portCheck.triggered.connect(portCheckUI())

		# connect to 21Exchange
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

		# help 
		self.helpAction = QAction(QIcon('icons/ic_help_outline_black_24dp_2x.png'), '&Help', self)
		self.helpAction.setToolTip("Help")
		self.helpAction.setShortcut("F1")
		self.helpAction.setStatusTip("Help")
		self.helpAction.triggered.connect(self.show_help)

		# git action
		self.gitAction = QAction(QIcon('icons/GitHub-Mark-64px.png'), 'View on &Github', self)
		self.gitAction.setToolTip("See code")
		self.gitAction.setStatusTip("Github repo")
		self.gitAction.triggered.connect(self.show_git)


		# self.toolbar = self.addToolBar("Quick Access")
		# self.toolbar.setToolTip("Controls toolbar")
		# # self.toolbar.addAction(exitAction)
		# self.toolbar.addAction(portCheck)
		# self.toolbar.addAction(self.gitAction)
		# self.toolbar.addAction(self.helpAction)
		# self.toolbar.addAction(self.exchange)


		# self.snapshot_thread = None
		# self.srv = None

		# Configuration options
		self.nameLabel = QLabel(self); self.nameLabel.setText("Public Name");
		self.portLabel = QLabel(self); self.portLabel.setText("Port")
		self.maxconLabel = QLabel(self); self.maxconLabel.setText("Max. connections (total) allowed")
		self.maxconperipLabel = QLabel(self); self.maxconperipLabel.setText("Max. connections per IP allowed")
		self.speedLabel = QLabel(self); self.speedLabel.setText("Bandwidth limit")
		self.exchangeLabel = QLabel(self); self.exchangeLabel.setText("Exchange URL")
		self.speedDisplay = QLabel(self)

		self.nameInput = QLineEdit(self); self.nameInput.setPlaceholderText("Max. 16 characters"); self.nameInput.setMaxLength(16)
		self.portInput = QSpinBox(self); self.portInput.setRange(0, 65535); self.portInput.setValue(2121)
		self.maxconInput = QSpinBox(self)
		self.maxconperipInput = QSpinBox(self)
		self.speedInput = QSlider(Qt.Horizontal, self); self.speedInput.setFocusPolicy(Qt.NoFocus)
		self.exchangeInput = QLineEdit(self); self.exchangeInput.setPlaceholderText("Get it from the exchange website.")

		self.speedInput.valueChanged[int].connect(self.downSpeedChanged)
		

		self.nameInput.setToolTip("Your name on the network")
		self.portInput.setToolTip("Between 0 and 65535 (integer only)")
		self.maxconInput.setToolTip("Total users which can connect to your system")
		self.maxconperipInput.setToolTip("Total connections one user can make to your system")
		self.speedInput.setToolTip("This is the max.speed at which \nyou allow download to your system \n(For users with write permission) \nHigher values can freeze your system.")

		self.maxconInput.setMinimum(3); self.maxconInput.setMaximum(100)
		self.maxconperipInput.setMinimum(3); self.maxconperipInput.setMaximum(10)
		self.speedInput.setMinimum(1536); 
		self.speedInput.setMaximum(5632);


		self.homedirSelect = QPushButton('Select shared folder', self)
		self.homedirInput = QLineEdit(self);
		self.homedirSelect.setToolTip("Click this button to choose folder to share")
		self.homedirSelect.clicked.connect(self.showDirChooser)

		
		# setting up the layout
		# self.settingsFrame = QFrame()
		# self.buttonsFrame = QFrame()
		# self.settingsFrame.setFrameShape(QFrame.Box); self.settingsFrame.setFrameShadow(QFrame.Plain)
		# self.buttonsFrame.setFrameShape(QFrame.StyledPanel); self.buttonsFrame.setFrameShadow(QFrame.Plain)

		# self.settingsLayout = QGridLayout()
		# self.settingsFrame.setLayout(self.settingsLayout)
		# self.buttonsLayout = QHBoxLayout()
		# self.buttonsFrame.setLayout(self.buttonsLayout)

		self.grid = QGridLayout()
		self.setLayout(self.grid)

		self.statusTip = QLabel(self);
		self.statusTip.setText("Welcome")
		self.statusTip.setStyleSheet("border: 1px solid black; padding-top: 10px;")

		self.grid.addWidget(self.nameLabel, 0, 0, 1, 2); self.grid.addWidget(self.nameInput, 0, 2, 1, 2)
		self.grid.addWidget(self.portLabel, 0, 5); self.grid.addWidget(self.portInput, 0, 6)
		self.grid.addWidget(self.homedirSelect, 3, 0, 1, 2); self.grid.addWidget(self.homedirInput, 3, 2, 1, 5)
		self.grid.addWidget(self.maxconLabel, 1, 0, 1, 4); self.grid.addWidget(self.maxconInput, 1, 5, 1, 1)
		self.grid.addWidget(self.maxconperipLabel, 2, 0, 1, 4); self.grid.addWidget(self.maxconperipInput, 2, 5, 1, 1)
		self.grid.addWidget(self.speedLabel, 4, 0, 1, 2); self.grid.addWidget(self.speedInput, 4, 2, 1, 4); self.grid.addWidget(self.speedDisplay, 4, 6)
		self.grid.addWidget(self.exchangeLabel, 5, 0, 1, 2); self.grid.addWidget(self.exchangeInput, 5, 2, 1, 5)

		self.grid.addWidget(self.itHurtsLabel, 6, 1, 1, 5)
		self.grid.addWidget(self.mainbtn, 7, 1, 1, 2)
		self.grid.addWidget(self.exchangebtn, 7, 4, 1, 2)

		self.grid.addWidget(self.statusTip, 8, 0, 1, 7)


		self.sett = load_settings()
		self.populateForm()
		# self.setFixedSize(450, 300)
		self.setFixedSize(self.minimumSizeHint())
		self.setWindowTitle("21Lane")
		# self.statusBar().showMessage("Welcome")

		# start cap monitoring thread
		self.mainbtn.setEnabled(True)
		self.capThread = threading.Thread(target=self.capMonitor)
		self.capThread.start()
		self.show()


	def setStatusTip(self, txt):
		self.statusTip.setText(txt)

	def showDirChooser(self):
		dirname = QFileDialog.getExistingDirectory(self, "Select Directory")
		if dirname:
			self.homedirInput.setText(dirname)
			
	def getSpeedText(self, value):
		if value < 1024:
			return str(value)+" KBPS"
		elif value < 5625:
			return str(round(value/1024, 2))+" MBPS"
		else:
			self.speedInput.setValue(5620)
			return "No Limit"

	

	def downSpeedChanged(self, value):
		self.speedDisplay.setText(self.getSpeedText(value))
		if value > 5625:
			if self.speedDisplay.text() == 'No Limit':
				return
			self.speedInput.setValue(5220)
			self.speedDisplay.setToolTip("May slow down your system.")
			QMessageBox.warning(self, 'Message', "No Limits on Download speed.\nThis may slow down your system if many people connect to it.", QMessageBox.Ok, QMessageBox.Ok)
		else:
			self.speedDisplay.setToolTip("")

	
	def populateForm(self):
		self.nameInput.setText(self.sett.server_name)
		self.portInput.setValue(self.sett.port)
		self.maxconInput.setValue(self.sett.max_cons)
		self.maxconperipInput.setValue(self.sett.max_cons_per_ip)
		self.speedInput.setValue(self.sett.max_upload_speed/1024) # display in kilobytes
		self.exchangeInput.setText(self.sett.exchange_url)
		self.homedirInput.setText(self.sett.homedir)
	
	
	def saveData(self):
		# form validator
		if ( (len(self.nameInput.text())==0) or \
			 (len(self.portInput.text())==0) or \
			 (len(self.homedirInput.text())==0) ):
			 QMessageBox.information(self, "Missed it", "Please fill all the settings before starting sharing", QMessageBox.Ok, QMessageBox.Ok)
			 return False
		
		if (not os.path.exists(self.homedirInput.text())):
			QMessageBox.information(self, "Caught you!", "You are trying to share a path which does not exist.\nCaught you!", QMessageBox.Ok, QMessageBox.Ok)
			return False

		self.sett.server_name = self.nameInput.text()
		self.sett.port = self.portInput.value()
		self.sett.max_cons = self.maxconInput.value()
		self.sett.max_cons_per_ip = self.maxconperipInput.value()
		self.sett.exchange_url = self.exchangeInput.text()
		self.sett.homedir = self.homedirInput.text()

		
		if self.speedInput.value() > 5220:
			self.sett.max_upload_speed = 0
		else:
			self.sett.max_upload_speed = self.speedInput.value() * 1024
		self.sett.max_download_speed = 1
		
		self.sett.save_settings()
		return True

	def quitapp(self):
		global server, gen_snapshot, app_is_running
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

		global server, gen_snapshot, server_running_status, PORT
		PORT = self.sett.port
		self.mainbtn.setEnabled(False)
		if not server and not server_running_status:
			if (self.saveData() == False):
				self.mainbtn.setEnabled(True)
				return
			if not is_port_available(PORT):
				mylog("\nPort : " + str(PORT) + " is not available\n")
				QMessageBox.critical(self, "Port error", "Port " + str(PORT) + " is not available.\nPlease change the port in settings.\n", QMessageBox.Ok, QMessageBox.Ok)
				self.mainbtn.setEnabled(True)
				return
			self.setStatusTip("Starting, please wait...")
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
			self.mainbtn.setStyleSheet("background-color: #f62459; color: white; border: none; padding: 5px;")
			self.setStatusTip(msg)

			gen_snapshot = True
			self.exchange_connect()
			self.snapshot_thread = generate_system_snapshot()
			self.snapshot_thread.start()

		elif server and server_running_status:
			mylog("stopping server")
			self.setStatusTip("Stopping, please wait...")
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


			self.setStatusTip("Stopped")
			server_running_status = False
			self.exchange_disconnect()
			self.mainbtn.setText("Start Sharing")
			self.mainbtn.setStyleSheet("background-color: #40e0d0; color: black; border: none; padding: 5px;")\

		else:
			print('doing nothing')
			return
		self.mainbtn.setEnabled(True)


	def closeEvent(self, event):
		global app_is_running
		app_is_running = False
		try:
			if self.srv is not None:
				self.setStatusTip("Cleaning up")
				server.close_all()
				del self.srv
				global gen_snapshot
				if self.snapshot_thread:
					gen_snapshot = False
					del self.snapshot_thread
				if self.exchange_process:
					self.exchange_process.poll()
					if not self.exchange_process.returnCode:
						self.exchange_process.kill()
					del self.exchange_process
					self.exchange_process = None
					mylog('Exchange UI closed.')

				mylog("Cleaned up")

		except:
			pass
		finally:
			reply = QMessageBox.question(self, 'Close', "Are you sure to exit ?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
			if reply == QMessageBox.Yes:
				event.accept()
				raise KeyboardInterrupt
			else:
				event.ignore()

	def capMonitor(self):
		global CAPERROR
		while True and app_is_running:
			if CAPERROR:
				self.setStatusTip("You must satisfy the minimum cap as per your exchange.")
			# don't choke while you run
			time.sleep(1)
		mylog("Cap monitor thread quits.")


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


	def show_help(self):
		url = QUrl("https://21lane.github.io/howto.html")
		QDesktopServices.openUrl(url)

	def show_git(self):
		url = QUrl("https://github.com/21lane/21Lane")
		QDesktopServices.openUrl(url)

	def open_exchange(self):
		global exchange_url 		
		uri = exchange_url
		self.exchange_process = subprocess.Popen([python, "exchange_client.py", uri])
	

	def exchange_disconnect(self, signalFrom=None):
		global exchange_url, exchange_connect_status
		if not exchange_connect_status:
			return
		if not signalFrom:
			reply = QMessageBox.question(self, '21Exchange', "You are connected. Do you want to log out from the server?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
		else:
			reply = QMessageBox.information(self, '21Exchange', "You will now be disconnected from the exchange.", QMessageBox.Ok, QMessageBox.Ok)
		if (reply == QMessageBox.Yes) or (reply == QMessageBox.Ok):
			if 'session_id' in ls(pwd):
				f = open('session_id', 'r')
				sessionid = f.read().strip()
				f.close()
			else:
				sessionid = ''
			
			post_data = { 'action':'disconnect' }
			uri = exchange_url+'/cgi-bin/actions.py'
			try:
				headers = {'user-agent':'21Lane'}
				r = requests.post(url=uri, data=post_data, cookies={'session_id':sessionid}, headers=headers, proxies=None, timeout=5)
				if r.status_code == 200 and r.text.strip() == 'ok':
					exchange_connect_status = False
					QMessageBox.information(self, '21Exchange', "You have been logged out.")
					if 'session_id' in ls(pwd):
						os.remove('session_id')
						mylog("session_id file removed")

				if self.exchangebtn.isEnabled():
					self.exchangebtn.setEnabled(False)
					self.exchangebtn.setStyleSheet("background-color: #bdc3c7; color: white; border: none; padding: 5px 15px;")
					self.exchangebtn.disconnect()
					
				
			except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError, ConnectionAbortedError, requests.exceptions.Timeout) as e:
				QMessageBox.critical(self, 'Network error', 'Cannot connect to exchange. Sharing is up!', QMessageBox.Ok, QMessageBox.Ok)
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



	def exchange_connect(self):
		global server, exchange_url, PORT, exchange_connect_status
		if len(self.sett.exchange_url) == 0:
			return
		if not server:
			QMessageBox.warning(self, 'Sorry', "You must have sharing enabled to connect to an exchange.", QMessageBox.Ok, QMessageBox.Ok)
			return
		try:
			exchange_url = self.sett.exchange_url
			url = exchange_url+"/cgi-bin/actions.py"

			server_name = self.sett.server_name
			post_data = { 'action':'connect', 'server_name':server_name, 'port':PORT, 'IP':get_ip_address() }

			if 'session_id' in ls(pwd):
				f = open('session_id', 'r')
				ckstr = f.read()
				f.close()
				ck = ckstr.strip()
			else:
				ck = None
			if not ck is None:
				cookie_dic = {'session_id':ck}
			else:
				cookie_dic = None

			headers = {'user-agent':'21Lane'}			
			r = requests.post(url, data=post_data, cookies=cookie_dic, headers=headers, proxies=None, timeout=5)
			sessionid = None
			if r.status_code == 200:
				f = open('session_id', 'w')
				f.write(r.text.strip())
				f.close()
			if r.status_code == 404:
				QMessageBox.warning(self, "Invalid URL", "Oops... You entered an invalid URL / host.", QMessageBox.Ok, QMessageBox.Ok)
				return

			exchange_connect_status = True

			if not self.exchangebtn.isEnabled():
				self.exchangebtn.setEnabled(True)
				self.exchangebtn.setStyleSheet("background-color: #0a2c9b; color: white; border: none; padding: 5px 15px;")
				self.exchangebtn.clicked.connect(self.open_exchange)

			# self.exchangebtn.setEnabled(True)
			# self.exchangebtn.setStyleSheet("background-color: blue; color: white; border: none; padding: 5px;")
			# self.exchangebtn.clicked[bool].connect(self.open_exchange)

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
			# dest_dir = self.sett.homedir
			# dest_path = os.path.join(dest_dir, 'snapshot.json')
			# dest_file = open(dest_path, 'wb')
			# source_file = open('snapshot.json', 'rb')
			# dest_file.write(source_file.read())
			# source_file.close()
			# dest_file.close()

			# # now notify you dad to take the parcel
			# mylog('Asking dad to take the parcel')
			# r = requests.post(url=exchange_url, data={'action':'snapshot'}, cookies={'session_id':sessionid}, timeout=5, proxies=None)
			# # print(r.text, 'is the response for snapshot')
			# if r.status_code==200 and r.text.strip()=='ok':
			# 	mylog('Snapshot file uploaded successfully.')
			# 	os.remove(dest_path)
			# else:
			# 	mylog("Some error occured while uploading snapshot.")

			# uploading of snapshot is to be handled solely by snapshot thread


		except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError, ConnectionAbortedError, requests.exceptions.Timeout) as e:
			QMessageBox.critical(self, 'Error', 'Network error!', QMessageBox.Ok, QMessageBox.Ok)
			raise e
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
