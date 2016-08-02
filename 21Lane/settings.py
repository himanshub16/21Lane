# This module manages FTP settings 
try:
	os
	sys
except NameError:
	try:
		import os, sys
		from datetime import datetime
		from tinydb import TinyDB, where
	except ImportError as e:
		print (e," Cannot import required modules")


def mylog(ar):
	f = open('log.txt', 'a')
	f.write(str(datetime.now()) + " " + ar + "\n")
	f.close()


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
		dbase.insert(rec)
		dbase.close()
		mylog("Settings modified")

	def restore_default_settings(self):
		dbase = TinyDB('settings.json')
		dbase.purge()
		dbase.close()
		self.__init__()



from PyQt5.QtWidgets import (QWidget, QAction, qApp, QPushButton, QApplication,
	QMainWindow, QTextEdit, QMessageBox, QInputDialog, QLabel, QLineEdit,
	QGridLayout, QSpinBox, QSlider)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QCoreApplication


class SettingsUI(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		grid = QGridLayout()
		self.setLayout(grid)
		grid.setSpacing(10)

		# this is the FTPSettings object we will handle throughout
		self.sett = FTPSettings()

		# all the labels
		self.nameLabel = QLabel(self); self.nameLabel.setText("Public Name");
		self.portLabel = QLabel(self); self.portLabel.setText("Port")
		self.bannerLabel = QLabel(self); self.bannerLabel.setText("Welcome Message")
		self.maxconLabel = QLabel(self); self.maxconLabel.setText("Max. connections (total) allowed")
		self.maxconperipLabel = QLabel(self); self.maxconperipLabel.setText("Max. connections per IP allowed")
		self.uploadLabel = QLabel(self); self.uploadLabel.setText("Maximum upload speed")
		self.downloadLabel = QLabel(self); self.downloadLabel.setText("Maximum download speed")
		self.exchangeLabel = QLabel(self); self.exchangeLabel.setText("Exchange URL")
		self.uploadDisplay = QLabel(self)
		self.downloadDisplay = QLabel(self)

		# all the inputs
		self.nameInput = QLineEdit(self); self.nameInput.setPlaceholderText("Max. 16 characters"); self.nameInput.setMaxLength(16)
		self.portInput = QSpinBox(self); self.portInput.setRange(0, 65535); self.portInput.setValue(2121)
		self.bannerInput = QLineEdit(self); self.bannerInput.setPlaceholderText("Greet people in your way")
		self.maxconInput = QSpinBox(self)
		self.maxconperipInput = QSpinBox(self)
		self.uploadInput = QSlider(Qt.Horizontal, self); self.uploadInput.setFocusPolicy(Qt.NoFocus)
		self.downloadInput = QSlider(Qt.Horizontal, self); self.downloadInput.setFocusPolicy(Qt.NoFocus)
		self.exchangeInput = QLineEdit(self); self.exchangeInput.setPlaceholderText("Get it from the exchange website.")

		# control buttons
		self.restoreBtn = QPushButton("Restore Defaults", self)
		self.exitBtn = QPushButton("Close", self)
		self.saveBtn = QPushButton("Save settings", self)

		# event listeners
		self.exitBtn.clicked.connect(QCoreApplication.instance().quit)
		self.uploadInput.valueChanged[int].connect(self.upSpeedChanged)
		self.downloadInput.valueChanged[int].connect(self.downSpeedChanged)
		self.restoreBtn.clicked.connect(self.restoreDefaults)
		self.saveBtn.clicked.connect(self.saveData)

		# adding widgets to grid
		grid.addWidget(self.nameLabel, 0, 0, 1, 2); grid.addWidget(self.nameInput, 0, 2); grid.addWidget(self.portLabel, 0, 4); grid.addWidget(self.portInput, 0, 5)
		grid.addWidget(self.bannerLabel, 1, 0, 1, 2); grid.addWidget(self.bannerInput, 1, 2, 1, 4)
		grid.addWidget(self.maxconLabel, 2, 0, 1, 4); grid.addWidget(self.maxconInput, 2, 3, 1, 1)
		grid.addWidget(self.maxconperipLabel, 3, 0, 1, 4); grid.addWidget(self.maxconperipInput, 3, 3, 1, 1)
		grid.addWidget(self.uploadLabel, 4, 0, 1, 3); grid.addWidget(self.uploadInput, 4, 3, 1, 2); grid.addWidget(self.uploadDisplay, 4, 5)
		grid.addWidget(self.downloadLabel, 5, 0, 1, 3); grid.addWidget(self.downloadInput, 5, 3, 1, 2); grid.addWidget(self.downloadDisplay, 5, 5)
		grid.addWidget(self.exchangeLabel, 6, 0, 1, 2); grid.addWidget(self.exchangeInput, 6, 2, 1, 4)

		grid.addWidget(self.restoreBtn, 8, 0)
		grid.addWidget(self.exitBtn, 8, 3)
		grid.addWidget(self.saveBtn, 8, 5)

		# setting other properties
		self.nameInput.setToolTip("Your name on the network")
		self.portInput.setToolTip("Between 0 and 65535 (integer only)")
		self.bannerInput.setToolTip("This message is displayed whenever someone connects to your system")
		self.maxconInput.setToolTip("Total users which can connect to your system")
		self.maxconperipInput.setToolTip("Total connections one user can make to your system")
		self.uploadInput.setToolTip("This is the max.speed at which \nyou allow uploads from your system \nHigher values can freeze your system.")
		self.downloadInput.setToolTip("This is the max.speed at which \nyou allow download to your system \n(For users with write permission) \nHigher values can freeze your system.")

		self.maxconInput.setMinimum(1); self.maxconInput.setMaximum(100)
		self.maxconperipInput.setMinimum(1); self.maxconperipInput.setMaximum(10)
		self.uploadInput.setMinimum(10); self.downloadInput.setMinimum(10)
		self.uploadInput.setMaximum(5632); self.downloadInput.setMaximum(5632)

		self.populateForm()

		# starting the main application
		self.move(200, 100)
		self.setFixedSize(500, 300)
		self.setWindowTitle("Settings")
		self.show()


	def closeEvent(self, event):
		reply = QMessageBox.question(self, 'Message', "Are you sure to exit ?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

		if reply == QMessageBox.Yes:
			event.accept()
		else:
			event.ignore()


	def populateForm(self):
		if not 'settings.json' in os.listdir(os.getcwd()):
			QMessageBox.information(self, "Settings missing", "No settings are present on your system.\nDefault settings have been loaded.", QMessageBox.Ok, QMessageBox.Ok)
			self.restoreDefaults()
		else:
			self.nameInput.setText(self.sett.server_name)
			self.portInput.setValue(self.sett.port)
			self.bannerInput.setText(self.sett.server_banner)
			self.maxconInput.setValue(self.sett.max_cons)
			self.maxconperipInput.setValue(self.sett.max_cons_per_ip)
			self.uploadInput.setValue(self.sett.max_upload_speed/1024) # display in kilobytes
			self.downloadInput.setValue(self.sett.max_download_speed/1024) # display in kilobytes
			self.exchangeInput.setText(self.sett.exchange_url)


	def getSpeedText(self, value):
		if value < 1024:
			return str(value)+" KBps"
		elif value < 5220:
			return str(round(value/1024, 2))+" MBps"
		else:
			return "No Limit"

	def upSpeedChanged(self, value):
		self.uploadDisplay.setText(self.getSpeedText(value))
		if value > 5220:
			self.uploadInput.setValue(5220)
			self.uploadDisplay.setToolTip("May slow down your system.")
			QMessageBox.warning(self, 'Message', "No Limits on Upload speed.\nThis may slow down your system if many people connect to it.", QMessageBox.Ok, QMessageBox.Ok)
		else:
			self.uploadDisplay.setToolTip("")

	def downSpeedChanged(self, value):
		self.downloadDisplay.setText(self.getSpeedText(value))
		if value > 5220:
			self.downloadInput.setValue(5220)
			self.uploadDisplay.setToolTip("May slow down your system.")
			QMessageBox.warning(self, 'Message', "No Limits on Download speed.\nThis may slow down your system if many people connect to it.", QMessageBox.Ok, QMessageBox.Ok)
		else:
			self.uploadDisplay.setToolTip("")


	def saveData(self):
		self.sett.server_name = self.nameInput.text()
		self.sett.server_banner = self.bannerInput.text()
		self.sett.port = self.portInput.value()
		self.sett.max_cons = self.maxconInput.value()
		self.sett.max_cons_per_ip = self.maxconperipInput.value()
		self.sett.exchange_url = self.exchangeInput.text()

		if self.uploadInput.value() > 5220:
			self.sett.max_upload_speed = 0
		else:
			self.sett.max_upload_speed = self.uploadInput.value() * 1024

		if self.downloadInput.value() > 5220:
			self.sett.max_download_speed = 0
		else:
			self.sett.max_download_speed = self.downloadInput.value() * 1024

		self.sett.save_settings()
		QMessageBox.information(self, 'Settings saved', "Restart sharing to load new settings.", QMessageBox.Ok, QMessageBox.Ok)


	def restoreDefaults(self):
		self.sett.restore_default_settings()

		self.nameInput.setText(self.sett.server_name)
		self.portInput.setValue(self.sett.port)
		self.bannerInput.setText(self.sett.server_banner)
		self.maxconInput.setValue(self.sett.max_cons)
		self.maxconperipInput.setValue(self.sett.max_cons_per_ip)
		self.uploadInput.setValue(self.sett.max_upload_speed/1024)
		self.downloadInput.setValue(self.sett.max_download_speed/1024)
		self.exchangeInput.setText(self.sett.exchange_url)

		QMessageBox.information(self, 'Message', "Default settings are displayed\nEdit if you want.\nClick Save to save them.", QMessageBox.Ok, QMessageBox.Ok)


if __name__=="__main__":
	app = QApplication([])
	app.setWindowIcon(QIcon('icons/1468025381_shining_mix_wrench.png'))
	ex = SettingsUI()
	sys.exit(app.exec_())
