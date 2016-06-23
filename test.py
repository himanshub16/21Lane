class sample:
	def __init__(self, dic):
		 self.name = dic['name']
		 self.password = dic['password']
		 self.homedir = dic['homedir']
		 self.permission = dic['permission']
		 self.msg_login = dic['msg_login']
		 self.msg_quit = dic['msg_quit']
		 self.filepath = os.path.join(os.getcwd, 'users', self.name)


a = sample({'name':'himanshu'})
print a
print a.name
print a.password
print a.filepath
