#!/usr/bin/python3

import cgi, cgitb
import http.cookies as cookie
import sqlite3 as lite
import time, os, sys, hashlib

def is_logged_in(sessid):
	try:
		db = lite.connect('connected_users.db')
		db.row_factory = lite.Row
		cur = db.cursor()
		cur.execute('SELECT count(SESSION_ID) from Users where SESSION_ID=?', (sessid,))
		data = cur.fetchall()[0] 
		if len(data) == 0:
			return False
		return True
	except Exception as e:
		db.rollback()
		raise e
	finally:
		db.close()


def logout_user(sessid):
	try:
		db = lite.connect('connected_users.db')
		db.row_factory = lite.Row
		cur = db.cursor()
		sessid = str(sessid)
		cur.execute('DELETE from Users where SESSION_ID=?', (sessid,))
		db.commit()
		return True
	except Exception as e:
		db.rollback()
		raise e
	finally:
		db.close()


def login_user(sessid, ip_addr, share_size=10):
	try:
		# dbpath = os.path.join(os.getcwd(), 'connected_users.db')
		dbpath = 'connected_users.db'
		db = lite.connect(dbpath)
		db.row_factory = lite.Row
		cur = db.cursor()
		sessid = str(sessid)
		share_size = float(share_size)
		ip_addr = str(ip_addr)
		cur.execute('''INSERT INTO Users (SESSION_ID, IP_ADDRESS, SHARED_SIZE, FILENAME) VALUES (?,?,?,?);''',(sessid, ip_addr, share_size, sessid))
		db.commit()
		return True
	except Exception as e:
		db.rollback()
		raise e
	finally:
		db.close()


def create_sessid(ip_addr):
	mystr = str(time.time()) + str(ip_addr)
	sessid = hashlib.md5(mystr.encode()).hexdigest()
	return sessid



# here, the script starts
ck = cookie.SimpleCookie()
ip = os.environ['REMOTE_ADDR'].strip()

ckstr = os.environ.get('HTTP_COOKIE').strip()

form = cgi.FieldStorage()
sharesize = form.getvalue('sharesize')

if not ckstr:
	# first visit
	sessid = create_sessid(ip)
	login_user(sessid, ip, sharesize)
	print('Set-Cookie:session_id=', sessid, ';\r\n')
	print("Content-type:text/html\r\n\r\n")
	print("you are logged in")
else:
	sessid = ckstr
	logout_user(sessid)
	print('Set-Cookie:Expires=Thu, 01 Jan 1970 00:00:00 GMT;\r\n')
	print("Content-type:text/html\r\n\r\n")
	print("You have been logged out")


print(sessid)
# print(ip)
print(sharesize)


# print("Content-type:text/plain\r\n")
# print('hello ', ip, create_sessid(ip))

# try:
# 	for key in form.keys():
# 		var = str(key)
# 		val = str(form.getvalue(var))
# 		print(var, ' ', val)
# 	print('form value ', form.getvalue('sharesize'))
# 	print(form['sharesize'])
# except Exception as e:
# 	print("nothing passed ", e)

