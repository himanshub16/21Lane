#!/usr/bin/python3

from tinydb import TinyDB, Query, where
import cgi, cgitb
import os, sys
import json

cgitb.enable()
ls = os.listdir
pwd = os.getcwd()
datadir = os.path.join(pwd, 'data')
dbname = os.path.join(datadir, 'connected_users.json')

# here, the script starts
form = cgi.FieldStorage()
search_arg = form.getvalue('q')
if not search_arg:
	print('Content-type:text/html')
	print()
	print('Invalid')
	sys.exit()

query_str = "(?i)"+search_arg
print("Content-type:text/html")
print()

result = {}
count = 0
q = Query()
db = TinyDB(dbname)
for rec in db.all():
	filename = rec['FILENAME']
	sessid = rec['SESSION_ID']
	ip = rec['IP_ADDRESS']
	filepath = os.path.join(datadir, filename)
	userdb = TinyDB(filepath)
	tbl = userdb.table('filedata')
	resp = [ rec for rec in tbl.all() if search_arg.lower() in ''.join(rec['filename'].lower().split(' ')) ]
	# resp = tbl.search(q.filename.matches(query_str))
	if len(resp) is not 0:
		result[ip] = resp
	db.close()
	del tbl, filepath, sessid, filename

print(json.dumps(result, indent=2))
