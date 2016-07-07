from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.handlers import ThrottledDTPHandler
from pyftpdlib.servers import FTPServer

# import additions
import sys
import auth
import settings

userbase = auth.Userbase()

def load_settings():
	return settings.FTPSettings()

def load_users():
	""" creates a new DummyAuthorizer object at every call
	"""
	authorizer = DummyAuthorizer()
	for username in userbase.get_user_list():
		userobj = userbase.get_user_info(username)
		if username == 'anonymous':
			authorizer.add_anonymous(userobj.homedir, perm=userobj.permission, msg_login=userobj.msg_login, msg_quit=userobj.msg_quit)
		else:
			authorizer.add_user(userobj.name, userobj.password, userobj.homedir, perm=userobj.perm, msg_login=userobj.msg_login, msg_quit=userobj.msg_quit)
	return authorizer


# def create_server():
# 	conf = load_settings()
# 	authorizer = load_users()
# 	ThrottledDTPHandler.write_limit = conf.max_upload_speed
# 	ThrottledDTPHandler.read_limit = conf.max_download_speed
# 	FTPHandler.dtp_handler = ThrottledDTPHandler
# 	FTPHandler.banner = conf.server_banner
# 	FTPServer.max_cons = conf.max_cons
# 	FTPServer.max_cons_per_ip = conf.max_cons_per_ip
# 	FTPHandler.authorizer = authorizer
# 	FTPHandler.permit_foreign_addresses = conf.permit_outside_lan
# 	global server
# 	server = FTPServer(('127.0.0.1', 2121), FTPHandler)
# 	# try:
# 	# 	server.serve_forever()
# 	# finally:
# 	# 	server.close_all()
# 	# 	del conf, authorizer

def start_server():
	server.serve_forever()

def stop_server():
	server.close_all()


import threading

class myserver(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		conf = load_settings()
		authorizer = load_users()
		ThrottledDTPHandler.write_limit = conf.max_upload_speed
		ThrottledDTPHandler.read_limit = conf.max_download_speed
		FTPHandler.dtp_handler = ThrottledDTPHandler
		FTPHandler.banner = conf.server_banner
		FTPServer.max_cons = conf.max_cons
		FTPServer.max_cons_per_ip = conf.max_cons_per_ip
		FTPHandler.authorizer = authorizer
		FTPHandler.permit_foreign_addresses = conf.permit_outside_lan
		global server
		server = FTPServer(('127.0.0.1', 2121), FTPHandler)
		# try:
		server.serve_forever()
		# finally:
		# 	server.close_all()
		# 	del conf, authorizer

# while True:
# 	try:
# 		if (sys.version_info.major == 3):
# 			i = str(input("Start server? "))
# 		else:
# 			i = str(raw_input("Start server? "))
# 		if (i.lower() == 'yes'):
# 			create_server()
# 		else:
# 			break
# 	except (EOFError, KeyboardInterrupt):
# 		print("\rPlease enter yes or no")
# 		continue


# handling with GUI
import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication

class Example(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		btn = QPushButton("Click me", self)
		btn.setCheckable(True)
		btn.move(10, 10)
		btn.clicked[bool].connect(self.check_server)
		self.setGeometry(300, 300, 280, 170)
		self.setWindowTitle("FTP server")
		self.show()

	def check_server(self, pressed):
		global server
		if pressed:
			# server.serve_forever()
			self.srv = myserver()
			self.srv.start()
		else:
			server.close_all()
			del self.srv


server = None
app = QApplication([])
ex = Example()
sys.exit(app.exec_())


# conf = load_settings()

# authorizer = DummyAuthorizer()
# authorizer.add_user("user", "12345", "/home/himanshu", perm="elradfmw")
# authorizer.add_anonymous("/media/himanshu/himanshu")
#
# tdtp = ThrottledDTPHandler
# tdtp.write_limit = 1000000	# maximum download speed from server
# FTPHandler.dtp_handler = ThrottledDTPHandler
# FTPHandler.banner = "Welcome to python powered service"
# handler = FTPHandler
# handler.authorizer = authorizer
# server = FTPServer(("127.0.0.1", 2121), handler)
#
# try:
# 	server.serve_forever()
# finally:
# 	server.close_all()
