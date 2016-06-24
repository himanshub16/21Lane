from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.handlers import ThrottledDTPHandler
from pyftpdlib.servers import FTPServer

# import additions
import auth
import settings

userbase = auth.Userbase()

def load_settings():
	return settings.FTPSettings()

def load_users():
	for username in userbase.get_user_list():
		userobj = userbase.get_user_info(username)

conf = load_settings()

authorizer = DummyAuthorizer()
authorizer.add_user("user", "12345", "/home/himanshu", perm="elradfmw")
authorizer.add_anonymous("/media/himanshu/himanshu")

tdtp = ThrottledDTPHandler
tdtp.write_limit = 1000000	# maximum download speed from server
FTPHandler.dtp_handler = ThrottledDTPHandler
FTPHandler.banner = "Welcome to python powered service"
handler = FTPHandler
handler.authorizer = authorizer
server = FTPServer(("127.0.0.1", 2121), handler)

try:
	server.serve_forever()
finally:
	server.close_all()
