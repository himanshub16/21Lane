#!/usr/bin/python3
from tinydb import TinyDB, Query, where
import cgi, cgitb
import http.cookies as cookie
import time, os, sys, hashlib

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
		return
	db = TinyDB(dbname)
	db.remove(where('SESSION_ID')==sessid)
	db.close()


def login_user(sessid, ip_addr, share_size=10):
	if not os.path.isfile(dbname):
		return
	if is_logged_in(sessid):
		logout_user(sessid)
	db = TinyDB(dbname)
	db.insert({'SESSION_ID':sessid, 'IP_ADDRESS':ip_addr, 'SHARED_SIZE':float(share_size), 'FILENAME':sessid+'.json'})
	if not sessid+'.json' in ls(datadir):
		f = open(os.path.join(datadir, sessid+'.json'), 'w')
		f.close()
	db.close()


def create_sessid(ip_addr):
	mystr = str(time.time()) + str(ip_addr)
	sessid = hashlib.md5(mystr.encode()).hexdigest()
	return sessid


# here, the script starts
ip = os.environ['REMOTE_ADDR'].strip()

ckstr = os.environ.get('HTTP_COOKIE').strip()
ck = cookie.SimpleCookie()

form = cgi.FieldStorage()
sharesize = form.getvalue('sharesize')
action = form.getvalue('action')

if not action:
	print('Content-type:text/plain')
	print()
	print('Action required')

if not sharesize:
	sharesize = 0

if action=='connect':
	if not ckstr:
		# first visit
		sessid = create_sessid(ip)
		login_user(sessid, ip, sharesize)
	else:
		ck.load(ckstr)
		sessid = str(ck['session_id'].value)

	print('Set-Cookie:session_id=', sessid, "\r\n", sep='')
	print(sessid)

elif action=='disconnect':
	if not ckstr:
		sys.exit()

	ck.load(ckstr)
	sessid = str(ck['session_id'].value)
	# if is_logged_in(sessid):
	# not checked because tinydb raises no error if record is not present
	# check was required at login to prevent duplicate entries
	logout_user(sessid)
	print('Set-Cookie: session_id=""; expires=Thu, 01 Jan 1970 00:00:00 GMT;\r\n')

else:
	print("Content-type:text/plain")
	print()
	print("Invalid action")
