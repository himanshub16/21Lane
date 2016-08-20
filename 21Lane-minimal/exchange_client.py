import sys, os, subprocess
from ftpclient import FTPClient
from downloader import Downloader
import requests, json
from datetime import datetime
import time

from PyQt5.QtWidgets import (QWidget, QApplication, QPushButton, QLabel, QAction, \
		QGroupBox, QHBoxLayout, QVBoxLayout, QFormLayout, QLineEdit, QFileDialog, \
		QScrollArea, QMessageBox, QGridLayout, QSpacerItem, QSizePolicy )
from PyQt5.QtGui import QIcon, QCloseEvent, QPixmap
from PyQt5.QtCore import Qt

python = sys.executable


def mylog(ar):
	f = open('log.txt', 'a')
	f.write(str(datetime.now()) + " " + ar + "\n")
	f.close()


def convertSize(size):
	# size is in bytes
	size = int(size)
	kb = 1024
	mb = 1024*1024
	gb = 1024*1024*1024
	size_kb = size//kb
	abs_kb = "%.2f" % (size/kb)
	size_mb = size//mb
	abs_mb = "%.2f" % (size/mb)
	size_gb = size//gb
	abs_gb = "%.2f" % (size/gb)
	if (size//gb) == 0:
		if (size//mb) == 0:
			if (size//kb) == 0:
				return str(size) + " B"
			else:
				return str(abs_kb) + "kB"
		else:
			return str(abs_mb) + " MB"
	else:
		return str(abs_gb) + " GB"
				

class ExchangeClient(QWidget):
	def __init__(self, exchange_uri):
		super().__init__()
		try:
			self.windowTitle = exchange_uri
			self.exchange_url = exchange_uri
			dummy = open('session_id', 'r')
			self.session_id = dummy.read().strip()
			dummy.close()
		except FileNotFoundError:
			QMessageBox.critical(self, 'Not connected', 'Make sure you are connected to the exchange.', QMessageBox.Ok, QMessageBox.Ok)
			sys.exit(1)
		except Exception as e:
			QMessageBox.critical(self, "Err", "Some error occured", QMessageBox.Ok, QMessageBox.Ok)
			mylog("Exchange Client : Some error occured")
			sys.exit(1)
		self.initUI()
		self.downman = Downloader()
		self.downman.execute = True
		self.browser_process = None
	
	def initUI(self):
		self.configBar = QGroupBox()
		self.configLayout = QHBoxLayout()
		self.configBox = QLineEdit()
		self.configBox.setPlaceholderText("This is where files are downloaded")
		config = open('ftp-client.conf')
		dirname = config.read().strip()
		self.configBox.setText(dirname)
		config.close()
		self.configBtn = QPushButton('Select')
		self.configBtn.clicked[bool].connect(self.updateDownloadPath)
		self.configLayout.addWidget(self.configBox)
		self.configLayout.addWidget(self.configBtn)
		self.configBar.setLayout(self.configLayout)

		self.actionsBox = QGroupBox()
		self.aBLayout = QHBoxLayout()
		self.searchbox = QLineEdit()
		self.listbtn = QPushButton("List connected users")
		self.listbtn.clicked[bool].connect(self.listUsers)
		self.searchbox.setPlaceholderText("Search for file")
		self.goBtn = QPushButton(QIcon('icons/search.png'), '')
		self.goBtn.clicked[bool].connect(self.searchQuery)
		self.searchbox.returnPressed.connect(self.goBtn.click)
		self.aBLayout.addWidget(self.listbtn)
		self.aBLayout.addWidget(self.searchbox)
		self.aBLayout.addWidget(self.goBtn)
		self.actionsBox.setLayout(self.aBLayout)


		self.clientBox = QGroupBox("File listing")
		self.cBLayout = QGridLayout()
		self.clientBox.setLayout(self.cBLayout)
		self.cBSpacer = QSpacerItem(5, 5, QSizePolicy.Minimum, QSizePolicy.Expanding)
		self.vscroll = QScrollArea()
		self.vscroll.setWidget(self.clientBox)
		self.vscroll.setWidgetResizable(True)


		self.downloadBox = QGroupBox("Downloads")
		self.dbLayout = QHBoxLayout()
		self.downloadBox.setLayout(self.dbLayout)
		self.dbLayout.setAlignment(Qt.AlignLeft)
		self.hscroll = QScrollArea()
		self.hscroll.setWidget(self.downloadBox)
		self.hscroll.setFixedHeight(120)
		self.hscroll.setWidgetResizable(True)

		mainLayout = QVBoxLayout(self)
		mainLayout.addWidget(self.configBar)
		mainLayout.addWidget(self.actionsBox)
		mainLayout.addWidget(self.vscroll)
		mainLayout.addWidget(self.hscroll)
		self.setWindowTitle(self.windowTitle)
		self.setMinimumWidth(200)
		self.setMinimumHeight(500)

		if (self.session_id == ''):
			self.session_not_available()

		self.show()
	
	def session_not_available(self, message=None):
		if not message:
			QMessageBox.warning(self, 'Unauthorized', "You are not connected to the exchange.\nRestart sharing please.", QMessageBox.Ok, QMessageBox.Ok)
		else:
			QMessageBox.warning(self, 'Unauthorized', "You are not connected to the exchange.\nRestart sharing please.", QMessageBox.Ok, QMessageBox.Ok)
		sys.exit(1)

	def closeEvent(self, event):
		try:
			self.downman.execute = False

			if self.browser_process:
				self.browser_process.poll()
				if not self.browser_process.returncode:
					self.browser_process.kill()
				del self.browser_process
				self.browser_process = None
				mylog('Browser UI closed.')

		except KeyboardInterrupt:
			pass
		except Exception as e:
			raise e
		finally:
			reply = QMessageBox.question(self, 'Close', "Are you sure to exit ?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
			if reply == QMessageBox.Yes:
				event.accept()
				raise KeyboardInterrupt
			else:
				event.ignore()

	def listUsers(self):
		try:
			uri = self.exchange_url + '/cgi-bin/get_connected_users.py'
			headers = {'user-agent':'21Lane'}
			r = requests.post(uri, cookies={'session_id':self.session_id}, proxies=None, headers=headers, timeout=5)
			if r.status_code == 200:
				if r.text.strip() == 'unauthorized':
					QMessageBox.warning(self, 'Unauthorized', "You are not connected to this exchange.", QMessageBox.Ok, QMessageBox.Ok)
					return 

				if r.text.strip() == '':
					QMessageBox.information(self, "No one's there", "There are no users available at the moment", QMessageBox.Ok, QMessageBox.Ok)
					return

				try:
					responseJSON = json.loads(r.text)
				except JSONDecodeError:
					QMessageBox.critical(self, 'Decode error', "Couldn't understand response. Please report at the exchange.", QMessageBox.Ok, QMessageBox.Ok)
					return

				while(self.cBLayout.count()):
					try:
						self.cBLayout.takeAt(0).widget().deleteLater()
					except Exception as e:
						pass
				
				self.cBLayout.sizeHint()

				headerAction = QLabel('')
				headerSize = QLabel('Shared Size')
				headerName = QLabel('Name')
				headerName.setStyleSheet("font-weight: bold")
				headerSize.setStyleSheet("font-weight: bold")
				self.cBLayout.addWidget(headerAction, 0, 0)
				self.cBLayout.addWidget(headerSize, 0, 1)
				self.cBLayout.addWidget(headerName, 0, 2)
				counter = 1

				for entry in list(responseJSON.values()):
					browseAction = QPushButton(QIcon('icons/browse.png'), '')
					sizeLabel = QLabel(convertSize((entry['SHARED_SIZE'])))
					nameLabel = QLabel(entry['SERVER_NAME'])
					browseAction.setMaximumWidth(25)
					browseAction.clicked.connect(self.open_exchange(entry['IP_ADDRESS'], entry['PORT'], entry['SERVER_NAME']))
					sizeLabel.setMaximumWidth(100)
					self.cBLayout.addWidget(browseAction, counter, 0)
					self.cBLayout.addWidget(sizeLabel, counter, 1)
					self.cBLayout.addWidget(nameLabel, counter, 2)
					
					counter += 1

				self.cBLayout.addItem(self.cBSpacer, counter, 0, Qt.AlignTop)
				self.cBLayout.setHorizontalSpacing(30)


		except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError, ConnectionAbortedError, requests.exceptions.Timeout) as e:
			QMessageBox.critical(self, 'Error', 'Network error!', QMessageBox.Ok, QMessageBox.Ok)
			# raise e
		except Exception as e:
			# first close any open file to avoid permissions error in windows, and other similar errors
			QMessageBox.critical(self, 'Error', "Some error occured!", QMessageBox.Ok, QMessageBox.Ok)
			mylog(str(e) + ' ' + 'is the error')
			raise e


	def updateDownloadPath(self):
		path = self.configBox.text()
		config = open('ftp-client.conf', 'r')
		savedPath = config.read().strip()
		config.close()
		if os.path.exists(savedPath):
			dirname = QFileDialog.getExistingDirectory(directory=savedPath)
		else:
			dirname = QFileDialog.getExistingDirectory(directory=os.path.expanduser('~'))
		self.configBox.setText(dirname)
		config = open('ftp-client.conf', 'w')
		config.write(dirname)
		config.close()

	def folderEnter(self, path):
		def callChangeURI():
			self.addressBox.setText(self.pwd + path + '/')
			self.goBtn.click()
		return callChangeURI

	def openDownloadLocation(self, pathname):
		def dummyFunction():
			self.configBox.setText(pathname)
			self.goBtn.click()
		return dummyFunction

	def downloadFile(self, hostname, port, filename, pathname, filesize):
		def makeDownloadEntry():
			downloadItem = QGroupBox(filename)
			downloadItem.setFixedWidth(200)
			dilayout = QHBoxLayout()
			downloadItem.setLayout(dilayout)
			statusIcon = QLabel('')
			statusIcon.setPixmap(QPixmap('icons/wait.svg'))
			completionLabel = QLabel('In Queue')
			dilayout.addWidget(statusIcon)
			dilayout.addWidget(completionLabel)
			btn = QPushButton(QIcon('icons/cancel.png'), '')
			btn.setMaximumSize(25,25)
			btn.clicked.connect(downloadItem.deleteLater)
			browserbtn = QPushButton(QIcon('icons/browse.png'), '')
			browserbtn.setToolTip("Open location containing this item.")
			
			browserbtn.clicked.connect(self.openDownloadLocation(pathname))
			browserbtn.setMaximumSize(25, 25)
			dilayout.addWidget(browserbtn)
			dilayout.addWidget(btn)
			self.dbLayout.addWidget(downloadItem)
			# make sure port is an integer
			self.downman.addEntry(hostname=hostname, port=int(port), pathname=pathname, filesize=filesize, filename=filename, guiwidget={"state":'in queue', "statusicon":statusIcon, 'groupbox':downloadItem, 'btn':btn, 'label':completionLabel })

		return makeDownloadEntry
	
	def searchQuery(self):
		try:
			if len(self.searchbox.text()) < 3:
				QMessageBox.information(self, "Oops", "That's an absurd search!", QMessageBox.Ok, QMessageBox.Ok)
				return  

			uri = self.exchange_url + '/cgi-bin/search.py'
			headers = {'user-agent':'21Lane'}
			r = requests.post(uri, data={'q':self.searchbox.text()}, cookies={'session_id':self.session_id}, headers=headers, proxies=None, timeout=5)
			responseJSON = ''
			if r.status_code == 200:
				if r.text.strip() == 'unauthorized':
					QMessageBox.warning(self, 'Unauthorized', "You are not connected to this exchange.", QMessageBox.Ok, QMessageBox.Ok)
					return

				try:
					responseJSON = json.loads(r.text)
				except JSONDecodeError:
					QMessageBox.critical(self, 'Decode error', "Couldn't understand response. Please report at the exchange.", QMessageBox.Ok, QMessageBox.Ok)
					return

				if len(responseJSON) == 0:
					QMessageBox.information(self, "Aww", "No results found", QMessageBox.Ok, QMessageBox.Ok)
					return

				while(self.cBLayout.count()):
					try:
						self.cBLayout.takeAt(0).widget().deleteLater()
					except Exception as e:
						pass
				
				self.cBLayout.sizeHint()

				headerAction = QLabel('')
				headerSize = QLabel('Shared Size')
				headerName = QLabel('Name')
				headerMime = QLabel('Mime Type')
				headerName.setStyleSheet("font-weight: bold")
				headerSize.setStyleSheet("font-weight: bold")
				headerMime.setStyleSheet("font-weight: bold")
				self.cBLayout.addWidget(headerAction, 0, 0)
				self.cBLayout.addWidget(headerSize, 0, 1)
				self.cBLayout.addWidget(headerMime, 0, 2)
				self.cBLayout.addWidget(headerName, 0, 3)
				counter = 1

				for sessid in list( responseJSON.keys() ):
					host, server_name = sessid.split('#')
					ip, port = host.split(':')
					
					for entry in responseJSON[sessid]:
						downloadAction = QPushButton(QIcon('icons/download.png'), '')
						downloadAction.clicked.connect(self.downloadFile(hostname=ip, port=port, filename=entry['filename'], pathname=entry['fullpath'], filesize=entry['size']))
						sizeLabel = QLabel(convertSize((entry['size'])))
						mimeLabel = QLabel(entry['mimetype'])
						nameLabel = QLabel(entry['filename'])
						downloadAction.setMaximumWidth(25)
						sizeLabel.setMaximumWidth(100)
						self.cBLayout.addWidget(downloadAction, counter, 0)
						self.cBLayout.addWidget(sizeLabel, counter, 1)
						self.cBLayout.addWidget(mimeLabel, counter, 2)
						self.cBLayout.addWidget(nameLabel, counter, 3)
						
						counter += 1

				self.cBLayout.addItem(self.cBSpacer, counter, 5, Qt.AlignTop)
				self.cBLayout.setColumnStretch(3, 1)
				self.cBLayout.setHorizontalSpacing(30)


		except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError, ConnectionAbortedError, requests.exceptions.Timeout) as e:
			QMessageBox.critical(self, 'Error', 'Network error!', QMessageBox.Ok, QMessageBox.Ok)
			# raise e
		except Exception as e:
			# first close any open file to avoid permissions error in windows, and other similar errors
			QMessageBox.critical(self, 'Error', "Some error occured!", QMessageBox.Ok, QMessageBox.Ok)
			mylog(str(e) + ' ' + 'is the error')
			raise e


	def open_exchange(self, host, port, server_name):
		def openBrowser():
			c = FTPClient(hostname=host, port=port)
			if not c.ping():
				print("ping failed")
				QMessageBox.critical(self, "Aww", "Cannot connect to the machine.\nOne of the network or remote machine is down.", QMessageBox.Ok, QMessageBox.Ok)
				return
			self.browser_process = subprocess.Popen([python, "ftp_browser.py", host, str(port), server_name])
		return openBrowser


if __name__=="__main__":
	if (len(sys.argv) < 2):
		sys.exit(1)
	app = QApplication([])
	app.setWindowIcon(QIcon('icons/favicon.ico'))
	ui = ExchangeClient(exchange_uri=sys.argv[1])
	sys.exit(app.exec_())
