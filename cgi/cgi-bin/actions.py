#!/usr/bin/python3

from tinydb import TinyDB, Query, where
import cgi, cgitb
import http.cookies as cookie
import time, os, sys, hashlib
import ftplib

cgitb.enable()
ls = os.listdir
pwd = os.getcwd()
datadir = os.path.join(pwd, 'data')
dbname = os.path.join(datadir, 'connected_users.json')

def is_logged_in(sessid):
	if not os.path.isfile(dbname):
		return
	db = TinyDB(dbname)
	status = db.search(where('SESSION_ID') == sessid)
	db.close()
	if len(status) != 0:
		return True
	else:
		return False


def logout_user(sessid):
	if not os.path.isfile(dbname):
		return False
	db = TinyDB(dbname)
	db.remove(where('SESSION_ID')==sessid)
	db.close()
	userfile = os.path.join(datadir, str(sessid)+'.json')
	if os.path.isfile(userfile):
		os.remove(userfile)
	return True


def login_user(sessid, ip_addr, share_size=0, server_name="Not Available", port=2121):
	if not os.path.isfile(dbname):
		return
	if is_logged_in(sessid):
		logout_user(sessid)
	db = TinyDB(dbname)
	db.insert({'SESSION_ID':sessid, 'SERVER_NAME':server_name, 'PORT':port, 'IP_ADDRESS':ip_addr, 'SHARED_SIZE':float(share_size), 'FILENAME':sessid+'.json'})
	if not sessid+'.json' in ls(datadir):
		f = open(os.path.join(datadir, sessid+'.json'), 'w')
		f.close()
	db.close()


def create_sessid(ip_addr):
	mystr = str(time.time()) + str(ip_addr)
	sessid = hashlib.md5(mystr.encode()).hexdigest()
	return sessid


def get_snapshot_file(sessid):
	db = TinyDB(dbname)
	rec = db.search(where('SESSION_ID') == sessid)[0]
	filename = os.path.join(datadir, rec['FILENAME'])
	ip = rec['IP_ADDRESS']
	port = rec['PORT']
	if ip and port and os.path.isfile(filename):
		f = open(filename, 'wb')
		ftp = ftplib.FTP()
		ftp.connect(ip, port)
		ftp.login('anonymous')
		ftp.retrbinary('RETR '+'snapshot.json', f.write)
		ftp.quit()
		f.close()
	else:
		db.close()
		return
	# update user information
	userdb = TinyDB(dbname)
	db = TinyDB(filename)
	filedb = db.table('metadata')
	data = filedb.all()[0]
	sharesize = data['totalsize']
	q = Query()
	userdb.update({"SHARED_SIZE":float(sharesize)}, q.SESSION_ID == sessid)
	userdb.close()
	db.close()


# here, the script starts
ip = os.environ['REMOTE_ADDR'].strip()

ckstr = os.environ.get('HTTP_COOKIE').strip()
ck = cookie.SimpleCookie()

form = cgi.FieldStorage()
sharesize = form.getvalue('sharesize')
action = form.getvalue('action')
server_name = form.getvalue('server_name')
port = form.getvalue('port')
# if not action:
# 	print('Content-type:text/plain')
# 	print()
# 	print('Action required')

if not sharesize:
	sharesize = 0

print("Content-type:text/plain")
if action=='connect':
	if not ckstr:
		# first visit
		sessid = create_sessid(ip)
		login_user(sessid, ip, sharesize, server_name, port)
	else:
		ck.load(ckstr)
		sessid = str(ck['session_id'].value)
		if not is_logged_in(ckstr):
			login_user(sessid, ip, sharesize, port)

	print('Set-Cookie:session_id=', sessid, "\r\n", sep='')
	print(sessid)

elif action=='disconnect':
	if not ckstr:
		print()
		print('ok')
		# sys.exit()
	else:
		ck.load(ckstr)
		if 'session_id' in ck.keys():
			sessid = str(ck['session_id'].value)
		# if is_logged_in(sessid):
		# not checked because tinydb raises no error if record is not present
		# check was required at login to prevent duplicate entries
		print('Set-Cookie: session_id=""; expires=Thu, 01 Jan 1970 00:00:00 GMT')
		print()
		print('ok')

elif action=='snapshot':
	print()
	ck.load(ckstr)
	if ckstr:
		sessid = str(ck['session_id'].value)
		if is_logged_in(sessid):
			get_snapshot_file(sessid)
	print('ok')

else:
	print()
	print("Invalid action")
