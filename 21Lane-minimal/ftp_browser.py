import sys, os
from ftpclient import FTPClient
from downloader import Downloader

from PyQt5.QtWidgets import (QWidget, QApplication, QPushButton, QLabel, QAction, \
		QGroupBox, QHBoxLayout, QVBoxLayout, QFormLayout, QLineEdit, QFileDialog, \
		QScrollArea, QMessageBox, QGridLayout, QSpacerItem, QSizePolicy )
from PyQt5.QtGui import QIcon, QCloseEvent, QPixmap
from PyQt5.QtCore import Qt

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
				

class FTPBrowser(QWidget):
	def __init__(self, hostname, port, server_name):
		super().__init__()
		try:
			self.hostname = hostname
			self.port = int(port)
			self.windowTitle = server_name
			self.pwd = '/'
			self.oldpwd = '/'
			self.client = FTPClient(hostname=self.hostname, port=self.port)
		except Exception as e:
			print("Some error occured")
		self.initUI()
		self.downman = Downloader()
		self.downman.execute = True
	
	def initUI(self):

		self.addressBar = QGroupBox()
		self.aBLayout = QHBoxLayout()
		self.addressBox = QLineEdit()
		self.addressBox.setPlaceholderText("Enter path to continue")
		self.goBtn = QPushButton(QIcon('icons/go.png'), '')
		self.goBtn.clicked[bool].connect(self.changeBaseURI)
		self.addressBox.returnPressed.connect(self.goBtn.click)
		self.backBtn = QPushButton(QIcon('icons/back.png'), '')
		self.backBtn.clicked[bool].connect(self.changeBaseURI)
		self.homeBtn = QPushButton(QIcon('icons/home.png'), '')
		self.homeBtn.clicked[bool].connect(self.changeBaseURI )
		self.aBLayout.addWidget(self.backBtn)
		self.aBLayout.addWidget(self.homeBtn)
		self.aBLayout.addWidget(self.addressBox)
		self.aBLayout.addWidget(self.goBtn)
		self.addressBar.setLayout(self.aBLayout)


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
		mainLayout.addWidget(self.addressBar)
		mainLayout.addWidget(self.vscroll)
		mainLayout.addWidget(self.hscroll)
		self.setWindowTitle(self.windowTitle)

		self.setMinimumHeight(500)
		self.setMinimumWidth(300)

		self.homeBtn.click()
		self.show()

	def closeEvent(self, event):
		reply = QMessageBox.question(self, 'Close', 'Any queued downloads will canel. Do you want to close?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
		if reply == QMessageBox.Yes:
			self.downman.execute = False
			event.accept()
		else:
			event.ignore()

	def changeBaseURI(self):
		sender = self.sender()
		if (self.addressBox.text() == ''):
			self.addressBox.setText('/')
		if (sender == self.goBtn):
			self.pwd, self.oldpwd = self.addressBox.text(), self.pwd
		elif (sender == self.backBtn):
			self.pwd, self.oldpwd = self.oldpwd, self.pwd
		elif (sender == self.homeBtn):
			self.pwd, self.oldpwd = '/', self.pwd
		else:
			QMessageBox.critical(self, "Err!", "I have no idea what happended and how!", QMessageBox.Ok, QMessageBox.Ok)
			return
		self.client.pwd = self.pwd
		
		try:
			self.repopulateList()
		except ConnectionRefusedError:
			QMessageBox.critical(self, "Failed", "Cannot connect to the host", QMessageBox.Ok, QMessageBox.Ok)
			sys.exit(1)

	def folderEnter(self, path):
		def callChangeURI():
			self.addressBox.setText(self.pwd + path + '/')
			self.goBtn.click()
		return callChangeURI

	def openDownloadLocation(self, pathname):
		def dummyFunction():
			self.addressBox.setText(pathname)
			self.goBtn.click()
		return dummyFunction

	def downloadFile(self, filename, pathname, filesize):
		def makeDownloadEntry():
			downloadItem = QGroupBox(filename)
			downloadItem.setFixedWidth(200)
			dilayout = QHBoxLayout()
			downloadItem.setLayout(dilayout)
			statusIcon = QLabel()
			statusIcon.setPixmap(QPixmap('icons/wait.svg'))
			statusIcon.setFixedSize(25, 25)
			completionLabel = QLabel('In Queue')
			dilayout.addWidget(statusIcon)
			dilayout.addWidget(completionLabel)
			btn = QPushButton(QIcon('icons/cancel.png'), '')
			btn.setMaximumSize(25,25)
			btn.clicked.connect(downloadItem.deleteLater)
			browserbtn = QPushButton(QIcon('icons/browse.png'), '')
			browserbtn.setToolTip("Open Location containing this item.")
			browserbtn.clicked.connect(self.openDownloadLocation(pathname))
			browserbtn.setFixedSize(25, 25)
			dilayout.addWidget(browserbtn)
			dilayout.addWidget(btn)
			self.dbLayout.addWidget(downloadItem)
			self.downman.addEntry(hostname=self.hostname, port=self.port, pathname=pathname, filesize=filesize, filename=filename, guiwidget={"state":'in queue', "statusicon":statusIcon, 'groupbox':downloadItem, 'btn':btn, 'label':completionLabel })

		return makeDownloadEntry
	
	def downloadDirectory(self, dirpath):
		def callDownloadClient():
			self.client.ftprecur(dirpath)
			filelist = self.client.filelist

			downloadItem = QGroupBox(dirpath)
			downloadItem.setFixedWidth(150)
			dilayout = QHBoxLayout()
			downloadItem.setLayout(dilayout)
			statusIcon = QLabel('')
			self.statusIcon.setPixmap(QPixmap('icons/wait.svg'))
			completionLabel = QLabel('In Queue')
			dilayout.addWidget(statusIcon)
			dilayout.addWidget(completionLabel)
			btn = QPushButton(QIcon('icons/cancel.png'), '')
			btn.setMaximumSize(25,25)
			btn.clicked.connect(downloadItem.deleteLater)
			browserbtn = QPushButton(QIcon('icons/browse.png'), '')
			browserbtn.setToolTip("Open Location containing this item.")
			browserbtn.clicked.connect(self.openDownloadLocation(dirpath))
			dilayout.addWidget(browserbtn)
			dilayout.addWidget(btn)
			self.dbLayout.addWidget(downloadItem)

			for file in filelist:
				self.downman.addEntry(pathname=file['pathname'], destpath=file['pathname'], filesize=file['filesize'], filename=file['filename'], guiwidget={"state":'in queue', "statusicon":statusIcon, 'btn':btn, 'label':completionLabel })
			
		return callDownloadClient
		

	def repopulateList(self):
		filelist = self.client.ftplist()
		if (not filelist):
			QMessageBox.critical(self, 'Error', "Network Error", QMessageBox.Ok, QMessageBox.Ok)
			return
		while(self.cBLayout.count()):
			try:
				self.cBLayout.takeAt(0).widget().deleteLater()
			except Exception as e:
				pass

		# for widget in self.cBLayout.children():
		# 	print(widget)
		# 	widget.deleteLater()
		self.cBLayout.sizeHint()
		headerAction = QLabel('')
		headerSize = QLabel('Size')
		headerName = QLabel('Name')
		headerName.setStyleSheet("font-weight: bold")
		headerSize.setStyleSheet("font-weight: bold")
		self.cBLayout.addWidget(headerAction, 0, 0)
		self.cBLayout.addWidget(headerSize, 0, 1)
		self.cBLayout.addWidget(headerName, 0, 2)
		counter = 1
		for entry in list(filelist.values()):
			if (entry['isDir']):
				folderAction = QPushButton(QIcon('icons/folder.png'), '')
				folderAction.clicked[bool].connect(self.folderEnter(entry['filename']))
				dirDownloadAction = QPushButton(QIcon('icons/download.png'), '')
				dirDownloadAction.clicked[bool].connect(self.downloadDirectory(os.path.join(self.client.pwd, entry['filename'])))
				namelabel = QLabel(entry['filename']+'/')
				folderAction.setMaximumWidth(25)
				dirDownloadAction.setMaximumWidth(25)
				self.cBLayout.addWidget(dirDownloadAction, counter, 0)
				self.cBLayout.addWidget(folderAction, counter, 1)
				self.cBLayout.addWidget(namelabel, counter, 2)

			else:
				downloadAction = QPushButton(QIcon('icons/download.png'), '')
				downloadAction.clicked[bool].connect(self.downloadFile(filename=entry['filename'], filesize=entry['filesize'], pathname=entry['pathname']))
				sizeLabel = QLabel(convertSize((entry['filesize'])))
				namelabel = QLabel(entry['filename'])
				downloadAction.setMaximumWidth(25)
				sizeLabel.setMaximumWidth(100)
				self.cBLayout.addWidget(downloadAction, counter, 0)
				self.cBLayout.addWidget(sizeLabel, counter, 1)
				self.cBLayout.addWidget(namelabel, counter, 2)

			counter += 1
		self.cBLayout.addItem(self.cBSpacer, counter, 0, Qt.AlignTop)
			

if __name__=="__main__":
	if (len(sys.argv) < 4):
		print('insufficient arguments')
		sys.exit(1)
	app = QApplication([])
	app.setWindowIcon(QIcon('icons/favicon.ico'))
	ui = FTPBrowser(hostname=sys.argv[1], port=sys.argv[2], server_name=sys.argv[3])
	sys.exit(app.exec_())

