# This module manages FTP settings
try:
	os
	shelve
except NameError:
	try:
		import os, shelve
	except ImportError as e:
		print e," Cannot import required modules"


class FTPSettings:
	"""Class to handle FTP Settings
	There are following attributes that are saved in settings file
	* server_name			|	name of the server
	* server_banner			|	message displayed on connecting first time (FTPHandler)
	* max_cons				|	maximum connections to the server (FTPServer)
	* max_cons_per_ip		|	maximum connections per ip address (FTPServer)
	* max_upload_speed		|	maximum upload speed on server (take care of hard drive i/o and network speed) (ThrottledDTPHandler)
	* max_download_speed	|	maximum download speed (auto_sized_buffers are True by default) (ThrottledDTPHandler)
	* permit_outside_lan	|	FTPHandler (permit_foreign_addresses)
	"""
	
	def __init__(self):
		"""read data from settings file"""
		if 'settings' in os.listdir(os.getcwd()):
			f = shelve.open('settings')
			self.server_name = f['server_name']
			self.server_banner = f['server_banner']
			self.max_cons = f['max_cons']
			self.max_cons_per_ip = f['max_cons_per_ip']
			self.max_upload_speed = f['max_upload_speed']
			self.max_download_speed = f['max_download_speed']
			self.permit_outside_lan = f['permit_outside_lan']
			f.close()
		else:
			print 'Settings file missing'
			# f = open('settings', 'w')
			# f.close()
			self.server_name = 'Unnamed server'
			self.server_banner = "Welcome to dFTP server"
			self.max_cons = 10
			self.max_cons_per_ip = 2
			self.max_upload_speed = 2097152 	# approximately 2 Mbps in bytes
			self.max_download_speed = 1	# to resrtict uploads from public on server,
											# when write permission is allowed
			self.permit_outside_lan = False
			print 'Blank file created in lieu with default settings.'
			self.save_settings()
			print 'Default setttings saved'

	def reload_settings(self):
		self.__init__()

	def save_settings(self):
		"""save settings to settings file"""
		print 'saving settings '
		# os.remove('settings')
		f = shelve.open('settings')
		print 'file opened'
		f['server_name'] = self.server_name
		f['server_banner'] = self.server_banner
		f['max_cons'] = self.max_cons
		f['max_cons_per_ip'] = self.max_cons_per_ip
		f['max_upload_speed'] = self.max_upload_speed
		f['max_download_speed'] = self.max_download_speed
		f['permit_outside_lan'] = self.permit_outside_lan
		f.close()

	def restore_default_settings(self):
		os.remove('settings')
		self.__init__()
