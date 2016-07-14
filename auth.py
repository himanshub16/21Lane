try:
	from tinydb import TinyDB, where
except ImportError as e:
	print (e," Cannot import required modules")


class User:
	"""Each instance of this class represents a user
	* name		|	* password
	* homedir	| 	* permission
	* msg_login	| 	* msg_quit
	* filepath : path to user configuration filepath
	*
	* save_details() : save current details
	"""
	def __init__(self, dic):
		k = list(dic.keys())
		if 'name' in k and \
			'password' in k and \
			'homedir' in k and \
			'permission' in k and \
			'msg_login' in k and \
			'msg_quit' in k:
			self.record = k

	def save_details(self):
		dbase = TinyDB('user_database.json')
		dbase.insert(self.record)
		dbase.close()


class AnonymousUser:
	"""Each instance of this class represents an anonymous user
	* name 		: anonymous (as both kinds of users are in same database)
	* homedir	| 	* permission
	* msg_login	| 	* msg_quit
	* filepath : path to user configuration filepath
	*
	* save_details() : save current details
	"""
	def __init__(self, dic):
		k = list(dic.keys())
		if 'password' in k and \
			'homedir' in k and \
			'permission' in k and \
			'msg_login' in k and \
			'msg_quit' in k:
			self.record = k
		self.record['name'] = 'anonymous'

	def save_details(self):
		dbase = TinyDB('user_database.json')
		dbase.insert(self.record)
		dbase.close()


class Userbase:
	"""Base class that handles users on whole
	* userdir : path to directory where user configuration files are located
	* userlist : list of available userlist
	* get_user_list : refresh userlist variable
	* get_user_info : get user object for a user in userlist (AnonymousUser for anonymous and User for normal user)
	* remove_user : remove a user
	"""

	def __init__(self):
		self.userlist = self.get_user_list()

	def get_user_list(self):
		"""Refresh the user list"""
		self.userlist = []
		dbase = TinyDB('user_database.json')
		for rec in dbase.all():
			self.userlist.append(rec['name'])
		dbase.close()
		return self.userlist

	def get_user_info(self, username):
		"""get user object for a user in userlist"""
		if username in self.get_user_list():
			# in following either case tmpuser is of respective user type
			dbase = TinyDB('user_database.json')
			usr = dbase.search(where('name') == username)
			if username == 'anonymous':
				# dbase = shelve.open(os.path.join(self.userdir, 'anonymous'), 'r')
				# tmpuser = AnonymousUser({'name':dbase['name'], 'homedir':dbase['homedir'], 'permission':dbase['permission'], 'msg_login':dbase['msg_login'], 'msg_quit':dbase['msg_quit']})
				tmpuser = AnonymousUser(usr)
				dbase.close()
				return tmpuser
			else:
				# dbase = shelve.open(os.path.join(self.userdir, username), 'r')
				# tmpuser = User({'name':dbase['name'], 'password':dbase['password'], 'homedir':dbase['homedir'], 'permission':dbase['permission'], 'msg_login':dbase['msg_login'], 'msg_quit':dbase['msg_quit']})
				tmpuser = AnonymousUser(usr)
				dbase.close()
				return tmpuser

	def remove_user(self, username):
		if username in self.get_user_list():
			dbase = TinyDB('user_database.json')
			dbase.remove(where('name') == username)
		else:
			print ("No such user exists!")
