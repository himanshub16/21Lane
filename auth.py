try:
	os
	shelve
except NameError:
	try:
		import os, shelve
	except ImportError as e:
		print e," Cannot import required modules"


ls = os.listdir
pwd = os.getcwd()

class User:
	"""Each instance of this class represents a user"""
	def __init__(self, dic):
		 self.name = dic['name']
		 self.password = dic['password']
		 self.homedir = dic['homedir']
		 self.permission = dic['permission']
		 self.msg_login = dic['msg_login']
		 self.msg_quit = dic['msg_quit']
		 self.filepath = os.path.join(pwd, 'users', self.name)

	def save_details(self):
		dbase = shelve.open(self.filepath)
		dbase['name'] = self.name
		dbase['password'] = self.password
		dbase['homedir'] = self.homedir
		dbase['permission'] = self.permission
		dbase['msg_login'] = self.msg_login
		dbase['msg_quit'] = self.msg_quit
		dbase.close()


class AnonymousUser:
	"""AnonymousUser"""
	def __init__(self, dic):
		self.name = 'anonymous'
		self.homedir = dic['homedir']
		self.permission = dic['permission']
		self.msg_login = dic['msg_login']
		self.msg_quit = dic['msg_quit']
		self.filepath = os.path.join(pwd, 'users', self.name)

	def save_details(self):
		dbase = shelve.open(self.filepath)
		dbase['name'] = 'anonymous'
		dbase['homedir'] = self.homedir
		dbase['permission'] = self.permission
		dbase['msg_login'] = self.msg_login
		dbase['msg_quit'] = self.msg_quit
		dbase.close()


class Userbase:
	"""Base class that handles users on whole"""

	def __init__(self):
		self.userdir = os.path.join(pwd, 'users')
		self.userlist = ls(self.userdir)

	def get_user_list(self):
		"""Refresh the user list"""
		self.userlist = ls(self.userdir)
		return self.userlist

	def get_user_info(self, username):
		if username in self.get_user_list():
			if username == 'anonymous':
				dbase = shelve.open(os.path.join(self.userdir, 'anonymous'), 'r')
				tmpuser = AnonymousUser({'name':dbase['name'], 'homedir':dbase['homedir'], 'permission':dbase['permission'], 'msg_login':dbase['msg_login'], 'msg_quit':dbase['msg_quit']})
				dbase.close()
				return tmpuser
			else:
				dbase = shelve.open(os.path.join(self.userdir, username), 'r')
				tmpuser = User({'name':dbase['name'], 'password':dbase['password'], 'homedir':dbase['homedir'], 'permission':dbase['permission'], 'msg_login':dbase['msg_login'], 'msg_quit':dbase['msg_quit']})
				dbase.close()
				return tmpuser

	def remove_user(self, username):
		if username in self.get_user_list():
			os.remove(os.path.join(self.userdir, username))
